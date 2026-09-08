#!/usr/bin/env python3
"""Scrape a YouTube channel's video metadata with yt-dlp. No transcripts, no downloads.

Two modes:
  index  - fast, whole-channel titles/durations/ids only (~10s for 300 videos)
  full   - per-video descriptions, dates, view/like/comment counts, chapters, links

'full' fans out in parallel and falls back through alternate player clients when
YouTube returns "Sign in to confirm you're not a bot" — that error is a rate-limit
signal, not a real auth wall, and switching client usually clears it.
"""
import argparse, csv, json, os, re, subprocess, sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

CLIENTS = ["default", "web_embedded", "tv_embedded", "web_safari", "android_vr"]


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def channel_index(url, tab="videos"):
    base = url.rstrip("/")
    if not re.search(r"/(videos|shorts|streams|playlists)$", base):
        base = f"{base}/{tab}"
    r = run(["yt-dlp", "--flat-playlist", "--dump-single-json", "--no-warnings", "--no-update", base])
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return json.loads(r.stdout)


def fetch_video(vid, cache_dir):
    path = os.path.join(cache_dir, f"{vid}.json")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return True
    for client in CLIENTS:
        cmd = ["yt-dlp", "--skip-download", "--dump-json", "--no-warnings", "--no-update"]
        if client != "default":
            cmd += ["--extractor-args", f"youtube:player_client={client}"]
        cmd.append(f"https://www.youtube.com/watch?v={vid}")
        r = run(cmd)
        if r.returncode == 0 and r.stdout.strip():
            with open(path, "w") as f:
                f.write(r.stdout)
            return True
    return False


def flatten(d):
    desc = d.get("description") or ""
    return {
        "id": d.get("id"),
        "title": d.get("title"),
        "url": f"https://youtu.be/{d.get('id')}",
        "upload_date": d.get("upload_date"),
        "duration_s": d.get("duration"),
        "duration_min": round((d.get("duration") or 0) / 60, 1),
        "view_count": d.get("view_count"),
        "like_count": d.get("like_count"),
        "comment_count": d.get("comment_count"),
        "categories": ";".join(d.get("categories") or []),
        "tags": ";".join(d.get("tags") or []),
        "chapters": len(d.get("chapters") or []),
        "chapter_titles": ";".join(c.get("title", "") for c in (d.get("chapters") or [])),
        "desc_len": len(desc),
        "links": ";".join(sorted(set(re.findall(r"https?://[^\s\)\]<>]+", desc)))),
        "description": desc,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", help="channel URL or @handle")
    ap.add_argument("--mode", choices=["index", "full"], default="full")
    ap.add_argument("--limit", type=int, default=0, help="0 = all videos")
    ap.add_argument("--tab", default="videos", choices=["videos", "shorts", "streams"])
    ap.add_argument("--workers", type=int, default=4, help="parallel fetches; >6 triggers rate limiting")
    ap.add_argument("--out-prefix", default="youtube")
    a = ap.parse_args()

    url = a.channel if a.channel.startswith("http") else f"https://www.youtube.com/{a.channel.lstrip('@') and '@' + a.channel.lstrip('@')}"

    print("Fetching channel index...", file=sys.stderr)
    idx = channel_index(url, a.tab)
    if not idx:
        sys.exit(f"ERROR: could not read channel '{url}'. Check the handle/URL.")

    entries = idx.get("entries") or []
    meta = {
        "channel": idx.get("channel"),
        "channel_id": idx.get("channel_id"),
        "channel_url": idx.get("channel_url") or url,
        "subscribers": idx.get("channel_follower_count"),
        "description": idx.get("description"),
        "video_count_on_tab": len(entries),
        "tab": a.tab,
    }
    json.dump({"channel": meta, "entries": entries},
              open(f"{a.out_prefix}_index.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(meta, ensure_ascii=False, indent=1))

    if a.mode == "index":
        print(f"\nIndex only: {len(entries)} items -> {a.out_prefix}_index.json", file=sys.stderr)
        return

    ids = [e["id"] for e in entries if e.get("id")]
    if a.limit:
        ids = ids[:a.limit]
    cache = f"{a.out_prefix}_meta"
    os.makedirs(cache, exist_ok=True)

    print(f"Fetching metadata for {len(ids)} videos ({a.workers} workers)...", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        results = list(ex.map(lambda v: fetch_video(v, cache), ids))
    failed = [v for v, ok in zip(ids, results) if not ok]

    rows = []
    for vid in ids:
        p = os.path.join(cache, f"{vid}.json")
        if os.path.exists(p) and os.path.getsize(p) > 0:
            try:
                rows.append(flatten(json.load(open(p))))
            except Exception:
                pass
    rows.sort(key=lambda r: r["upload_date"] or "")

    json.dump({"channel": meta, "videos": rows},
              open(f"{a.out_prefix}_videos.json", "w"), ensure_ascii=False, indent=1)
    if rows:
        with open(f"{a.out_prefix}_videos.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    vc = sorted(r["view_count"] for r in rows if r["view_count"])
    dom = Counter()
    for r in rows:
        for l in (r["links"].split(";") if r["links"] else []):
            dom[re.sub(r"https?://(www\.)?([^/]+).*", r"\2", l)] += 1
    summary = {
        "videos_fetched": len(rows),
        "failed": len(failed),
        "date_from": rows[0]["upload_date"] if rows else None,
        "date_to": rows[-1]["upload_date"] if rows else None,
        "total_views": sum(vc),
        "median_views": vc[len(vc) // 2] if vc else None,
        "max_views": vc[-1] if vc else None,
        "median_duration_min": sorted(r["duration_min"] for r in rows)[len(rows) // 2] if rows else None,
        "uploads_per_month": sorted(Counter(r["upload_date"][:6] for r in rows if r["upload_date"]).items()),
        "top_link_domains": dom.most_common(25),
        "pct_with_chapters": round(100 * sum(1 for r in rows if r["chapters"]) / len(rows), 1) if rows else 0,
    }
    json.dump(summary, open(f"{a.out_prefix}_summary.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))
    if failed:
        print(f"\nWARNING: {len(failed)} videos failed all clients: {failed[:10]}", file=sys.stderr)
    print(f"\nSaved -> {a.out_prefix}_videos.csv / .json", file=sys.stderr)


if __name__ == "__main__":
    main()
