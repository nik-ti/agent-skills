#!/usr/bin/env python3
"""List a YouTube channel's videos and save them to <library>/<channel>/videos.json.
Prints the tables shown to the user in the interview. Uses yt-dlp, then treg if yt-dlp fails.

  list_videos.py <channel url or @handle> [--tabs videos,streams,shorts] [--max 2000]
  list_videos.py <channel> --search "word|other word"
"""
import argparse
import json
import re
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import treg_client
from common import LIBRARY, fmt_time, slugify, write_json

TREG_LIST_PAGES = 3


def normalize_channel(raw):
    """Return (base_url, is_playlist). Exits with a clear message for single-video links."""
    text = raw.strip().rstrip("/")
    if re.search(r"(youtube\.com/(watch|shorts/)|youtu\.be/)", text):
        raise SystemExit("That is a link to one video, not a channel. Give me the channel link or @handle.")
    if "youtube.com" in text:
        text = "https://www.youtube.com" + text.split("youtube.com", 1)[1]
        if "/playlist" in text:
            return text, True
        text = text.split("?")[0]
        return re.sub(r"/(videos|shorts|streams|featured|playlists|community|about|podcasts)$", "", text), False
    if re.search(r"\s|/", text):
        raise SystemExit(f"I can't read {raw!r} as a YouTube channel. Paste the channel link or @handle.")
    return "https://www.youtube.com/@" + text.lstrip("@"), False


def date_from(entry):
    if entry.get("upload_date"):
        value = entry["upload_date"]
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
    if entry.get("timestamp"):
        return datetime.fromtimestamp(entry["timestamp"], timezone.utc).strftime("%Y-%m-%d")
    return None


def rows_from_ytdlp(data, tab):
    rows = []
    for entry in data.get("entries") or []:
        if not entry or not entry.get("id"):
            continue
        if entry.get("entries"):  # a channel root nests one playlist per tab
            rows += rows_from_ytdlp(entry, tab)
            continue
        rows.append({
            "id": entry["id"],
            "title": entry.get("title") or "(untitled)",
            "url": f"https://www.youtube.com/watch?v={entry['id']}",
            "duration": entry.get("duration"),
            "views": entry.get("view_count"),
            "date": date_from(entry),
            "tab": tab,
        })
    return rows


def ytdlp_tab(url, tab, limit):
    command = ["yt-dlp", "--flat-playlist", "-J", "--no-warnings", "--no-update", "--playlist-end", str(limit),
               "--extractor-args", "youtubetab:approximate_date", url]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return None, result.stderr.strip()[-300:]
    data = json.loads(result.stdout)
    return data, ""


def from_ytdlp(base, is_playlist, tabs, limit):
    info, rows, errors = None, [], []
    targets = [(base, "playlist")] if is_playlist else [(f"{base}/{tab}", tab) for tab in tabs]
    for url, tab in targets:
        data, error = ytdlp_tab(url, tab, limit)
        if data is None:
            errors.append(f"{tab}: {error}")
            continue
        info = info or data
        rows += rows_from_ytdlp(data, tab)
    if info is None:
        return None, errors
    meta = {
        "channel": info.get("channel") or info.get("uploader") or info.get("title") or "channel",
        "channel_id": info.get("channel_id"),
        "handle": info.get("uploader_id"),
        "subscribers": info.get("channel_follower_count"),
        "via": "yt-dlp",
        "dates_are_approximate": True,
    }
    return (meta, rows), errors


def treg_video(item):
    video_id = item.get("id") or item.get("video_id")
    if not video_id:
        return None
    duration = item.get("lengthSeconds") or item.get("duration")
    return {
        "id": video_id,
        "title": item.get("title") or "(untitled)",
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "duration": int(duration) if str(duration or "").isdigit() else None,
        "views": item.get("viewCountInt") or item.get("views"),
        "date": (item.get("publishedTime") or item.get("publishDate") or item.get("published") or "")[:10] or None,
        "tab": "videos",
    }


def from_treg(base):
    match = re.search(r"/@([^/]+)", base)
    channel_id = re.search(r"/channel/(UC[\w-]+)", base)
    identity = {"handle": match.group(1)} if match else {"channelId": channel_id.group(1)} if channel_id else None
    if identity is None:
        raise treg_client.TregError("treg needs an @handle or /channel/UC... link")
    rows, spent = [], 0.0
    endpoint = "scrapecreators.x.v1-youtube-channel-videos"
    try:
        for sort, pages in (("latest", TREG_LIST_PAGES), ("popular", 1)):
            token = None
            for _ in range(pages):
                params = {**identity, "sort": sort}
                if token:
                    params["continuationToken"] = token
                reply = treg_client.call(endpoint, params)
                spent += treg_client.ENDPOINTS[endpoint][1]
                rows += [row for row in map(treg_video, reply.get("videos") or []) if row]
                token = reply.get("continuationToken")
                if not token:
                    break
    except treg_client.TregError as error:
        if not rows:
            print(f"[devour] {error}; trying crawl4ai (latest 30 only, no durations)", file=sys.stderr)
            endpoint = "crawl4ai.youtube.channel.videos"
            reply = treg_client.call(endpoint, {"channel": base, "limit": 30})
            spent += treg_client.ENDPOINTS[endpoint][1]
            rows = [row for row in map(treg_video, reply.get("rows") or []) if row]
    name = match.group(1) if match else identity["channelId"]
    meta = {"channel": name, "channel_id": identity.get("channelId"), "handle": "@" + name if match else None,
            "subscribers": None, "via": f"treg (~${spent:.4f})", "dates_are_approximate": True}
    return meta, rows


def folder_name(meta):
    """The handle is unique and Latin, so non-English channel names can't collide on disk."""
    return slugify(meta.get("handle") or meta.get("channel_id") or meta["channel"])


def dedupe(rows):
    return list({row["id"]: row for row in reversed(rows)}.values())[::-1]


def rough_date(date, today=None):
    """YouTube's list only says "2 years ago", so show no more precision than that really has."""
    if not date:
        return "?"
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    months_old = (int(today[:4]) - int(date[:4])) * 12 + int(today[5:7]) - int(date[5:7])
    return f"~{date[:4]}" if months_old >= 12 else f"~{date[:7]}"


def table(rows):
    lines = [f"{'date':<8} {'views':>11} {'length':>8}  title  [id]"]
    for row in rows:
        views = f"{row['views']:,}" if row.get("views") else "?"
        length = fmt_time(row["duration"]) if row.get("duration") else "?"
        lines.append(f"{rough_date(row.get('date')):<8} {views:>11} {length:>8}  {row['title'][:72]}  [{row['id']}]")
    return "\n".join(lines)


def summary(meta, rows, folder, truncated):
    durations = [row["duration"] for row in rows if row.get("duration")]
    print(f"Channel: {meta['channel']} ({meta.get('handle') or meta.get('channel_id') or '?'})"
          + (f", {meta['subscribers']:,} subscribers" if meta.get("subscribers") else ""))
    print(f"Listed: {len(rows)} videos via {meta['via']}" + (" (list was cut off at --max)" if truncated else ""))
    if durations:
        print(f"Lengths: median {fmt_time(statistics.median(durations))}, longest {fmt_time(max(durations))},"
              f" total {sum(durations) / 3600:.1f} hours")
    print(f"Saved to: {folder}/videos.json  (dates here are rough; exact ones arrive with each transcript)")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("channel")
    parser.add_argument("--tabs", default="videos", help="comma list of videos,streams,shorts")
    parser.add_argument("--max", type=int, default=2000, help="most videos to list per tab")
    parser.add_argument("--show", type=int, default=15, help="rows per table")
    parser.add_argument("--search", help="regex to match against titles, for picking by topic")
    args = parser.parse_args()

    base, is_playlist = normalize_channel(args.channel)
    found, errors = from_ytdlp(base, is_playlist, args.tabs.split(","), args.max)
    if found is None:
        print("[devour] yt-dlp could not list this channel:\n  " + "\n  ".join(errors), file=sys.stderr)
        if not treg_client.available():
            print("[devour] No treg key found, so the treg fallback is unavailable.", file=sys.stderr)
            sys.exit(2)
        try:
            found = from_treg(base)
        except treg_client.TregError as error:
            print(f"[devour] treg failed too: {error}", file=sys.stderr)  # includes the empty-balance message
            sys.exit(2)
    meta, rows = found
    rows = dedupe(rows)
    if not rows:
        print("[devour] The channel exists but no videos came back. Try --tabs videos,streams,shorts.", file=sys.stderr)
        sys.exit(3)

    folder = LIBRARY / folder_name(meta)
    write_json(folder / "videos.json", {**meta, "source_url": base, "videos": rows})
    summary(meta, rows, folder, len(rows) >= args.max)
    if args.search:
        matches = [row for row in rows if re.search(args.search, row["title"], re.I)]
        print(f"\nMATCHING /{args.search}/ ({len(matches)})\n" + table(matches[:args.show * 3]))
        return
    print("\nLATEST\n" + table(sorted(rows, key=lambda r: r.get("date") or "", reverse=True)[:args.show]))
    print("\nMOST POPULAR\n" + table(sorted(rows, key=lambda r: r.get("views") or 0, reverse=True)[:args.show]))


if __name__ == "__main__":
    main()
