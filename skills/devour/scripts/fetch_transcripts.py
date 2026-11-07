#!/usr/bin/env python3
"""Fetch transcripts for chosen videos into <channel dir>/transcripts, skipping any already saved.
The --ids list becomes this run's selection, so always pass the full list, also on a rerun.
yt-dlp picks one exact caption track per video. With --treg, paid treg endpoints retry the failures.
Videos with no captions end as status no_captions, ready for transcribe_local.py.

  fetch_transcripts.py --dir <channel dir> --ids id1,id2 [--lang auto] [--treg]
"""
import argparse
import html
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import treg_client
from common import (fmt_time, has_transcript, load_status, load_videos, parse_ids, save_selection, save_transcript,
                    set_status)

# Alternate YouTube player clients: "confirm you're not a bot" is usually a rate limit on one client.
CLIENTS = ["default", "android_vr", "tv_embedded", "web_embedded"]
UNAVAILABLE = re.compile(r"private video|members.only|join this channel|video unavailable|has been removed|"
                         r"premieres in|live event will begin|offline|not available in your country", re.I)
BACKOFF_SECONDS = (20, 60)


def parse_json3(data):
    segments = []
    for event in data.get("events") or []:
        text = "".join(seg.get("utf8", "") for seg in event.get("segs") or [])
        text = " ".join(html.unescape(text).split())
        if text:
            segments.append({"start": event.get("tStartMs", 0) / 1000, "text": text})
    return segments


def parse_srt(text):
    segments = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().splitlines()
        match = next((re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->", line) for line in lines if "-->" in line), None)
        if not match:
            continue
        hours, minutes, seconds, millis = map(int, match.groups())
        body = " ".join(line for line in lines if "-->" not in line and not line.strip().isdigit()).strip()
        if body:
            segments.append({"start": hours * 3600 + minutes * 60 + seconds + millis / 1000, "text": body})
    return segments


def pick_track(meta, wanted):
    """Choose one track: human captions beat auto captions, and -orig beats machine translations."""
    manual = {k: v for k, v in (meta.get("subtitles") or {}).items() if k != "live_chat"}
    auto = meta.get("automatic_captions") or {}
    original = meta.get("language") or next((k[:-5] for k in auto if k.endswith("-orig")), None)
    languages = []  # "en-US" must also find tracks named "en" and "en-orig"
    for code in ((original or "en") if wanted == "auto" else wanted, original):
        for variant in (code, (code or "").split("-")[0]):
            if variant and variant not in languages:
                languages.append(variant)
    for language in languages:
        for code, formats in manual.items():
            if code == language or code.startswith(language + "-"):
                return "manual", code, formats
        for code in (f"{language}-orig", language):
            if code in auto:
                return "auto", code, auto[code]
    if manual:
        code, formats = next(iter(manual.items()))
        return "manual", code, formats
    return None


def ytdlp_meta(video_id):
    """Return (metadata, error_text). Tries alternate clients when YouTube pushes back."""
    error = ""
    for client in CLIENTS:
        command = ["yt-dlp", "-j", "--skip-download", "--ignore-no-formats-error", "--no-warnings", "--no-update"]
        if client != "default":
            command += ["--extractor-args", f"youtube:player_client={client}"]
        result = subprocess.run(command + [f"https://www.youtube.com/watch?v={video_id}"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout), ""
        error = result.stderr.strip()[-300:]
        if UNAVAILABLE.search(error):
            break
    return None, error


def download_track(formats):
    chosen = next((f for f in formats if f.get("ext") == "json3"), None)
    if chosen is None:
        raise ValueError("no json3 format on this track")
    request = urllib.request.Request(chosen["url"], headers={"User-Agent": "Mozilla/5.0"})
    for attempt in range(len(BACKOFF_SECONDS) + 1):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return parse_json3(json.loads(response.read().decode("utf-8")))
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == len(BACKOFF_SECONDS):
                raise
            print(f"  YouTube rate limit, waiting {BACKOFF_SECONDS[attempt]}s", flush=True)
            time.sleep(BACKOFF_SECONDS[attempt])


def segments_from_scrapecreators(reply):
    rows = reply.get("transcript")
    if isinstance(rows, list) and rows:
        return [{"start": float(row.get("startMs") or 0) / 1000, "text": row["text"].strip()}
                for row in rows if (row.get("text") or "").strip()]
    text = reply.get("transcript_only_text")
    return [{"start": 0, "text": text}] if text else []


def segments_from_anyapi(reply):
    data = (reply.get("output") or {}).get("data") or {}
    return [{"start": float(row.get("startSeconds") or 0), "text": row["text"].strip()}
            for row in data.get("segments") or [] if (row.get("text") or "").strip()]


def segments_from_tikhub(reply):
    return parse_srt((reply.get("data") or {}).get("content") or "")


def treg_attempts(video, language):
    url = video["url"]
    lang = {} if language == "auto" else {"language": language}
    yield "scrapecreators.x.v1-youtube-video-transcript", {"url": url, **lang}, segments_from_scrapecreators
    yield "anyapi.youtube.video_transcript_full", {"url": url, **lang}, segments_from_anyapi
    code = "en" if language == "auto" else language
    yield ("tikhub.x.youtube-web-v2-get-video-captions",
           {"video_id": video["id"], "language_code": code, "format": "srt"}, segments_from_tikhub)


def fetch_with_treg(video, language):
    """Return (segments, source, usd_spent). Empty segments means no provider had captions."""
    spent = 0.0
    for endpoint, params, parse in treg_attempts(video, language):
        try:
            reply = treg_client.call(endpoint, params)
        except treg_client.TregError as error:
            if error.out_of_funds:
                raise
            print(f"  {error}", flush=True)
            continue
        spent += treg_client.ENDPOINTS[endpoint][1]
        segments = parse(reply)
        if segments:
            return segments, f"treg:{endpoint.split('.')[0]}", spent
    return [], None, spent


def record_from(video, meta, segments, source, language):
    meta = meta or {}
    date = meta.get("upload_date")
    chapters = [{"start": c.get("start_time", 0), "title": c.get("title", "")} for c in meta.get("chapters") or []]
    return {
        "id": video["id"], "title": meta.get("title") or video["title"], "url": video["url"],
        "channel": meta.get("channel"), "duration": meta.get("duration") or video.get("duration"),
        "views": meta.get("view_count") or video.get("views"),
        "date": f"{date[:4]}-{date[4:6]}-{date[6:8]}" if date else video.get("date"),
        "language": language or meta.get("language"), "source": source, "chapters": chapters,
        "description": (meta.get("description") or "")[:1500], "segments": segments,
    }


def process(channel_dir, video, language, use_treg):
    """Fetch one video and report its final state. Returns usd spent on treg."""
    video_id = video["id"]
    meta, error = ytdlp_meta(video_id)
    if meta is None and UNAVAILABLE.search(error):
        set_status(channel_dir, video_id, state="skipped", reason=error.split("ERROR:")[-1].strip()[:160])
        return 0.0
    if meta is not None:
        track = pick_track(meta, language)
        if track is None:
            set_status(channel_dir, video_id, state="no_captions", duration=meta.get("duration"))
            return 0.0
        kind, code, formats = track
        try:
            segments = download_track(formats)
            if segments:
                save_transcript(channel_dir, record_from(video, meta, segments, f"youtube-{kind}-captions", code))
                set_status(channel_dir, video_id, state="done", source=f"youtube-{kind}-captions")
                return 0.0
            error = "caption track came back empty"
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as failure:
            error = str(failure)
    if not use_treg:
        set_status(channel_dir, video_id, state="failed", reason=error[:160])
        return 0.0
    segments, source, spent = fetch_with_treg(video, language)
    if segments:
        save_transcript(channel_dir, record_from(video, meta, segments, source, None if language == "auto" else language))
        set_status(channel_dir, video_id, state="done", source=source)
    else:
        set_status(channel_dir, video_id, state="no_captions", duration=video.get("duration"))
    return spent


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", required=True)
    parser.add_argument("--ids", required=True, help="comma list, or @file with one id per line")
    parser.add_argument("--lang", default="auto", help="caption language code, or auto for the video's own language")
    parser.add_argument("--treg", action="store_true", help="retry yt-dlp failures with paid treg endpoints")
    parser.add_argument("--sleep", type=float, default=2.0, help="seconds between videos, to stay under rate limits")
    args = parser.parse_args()
    if args.treg and not treg_client.available():
        raise SystemExit("--treg needs a key: TREG_TOKEN, or TREG_API_KEY in the workspace .env.")

    videos = load_videos(args.dir)
    ids = parse_ids(args.ids, args.dir)
    save_selection(args.dir, ids)
    spent = 0.0
    for position, video_id in enumerate(ids, 1):
        video = videos[video_id]
        print(f"[{position}/{len(ids)}] {video['title'][:70]}", flush=True)
        if has_transcript(args.dir, video_id):
            set_status(args.dir, video_id, state="done")
            print("  already saved", flush=True)
            continue
        try:
            spent += process(args.dir, video, args.lang, args.treg)
        except treg_client.TregError as error:
            set_status(args.dir, video_id, state="failed", reason="treg balance is empty")
            raise SystemExit(f"Stopping: the treg account is out of funds. Top up at https://treg.to/app#billing. ({error})")
        print(f"  {load_status(args.dir)[video_id].get('state')}", flush=True)
        if position < len(ids):
            time.sleep(args.sleep)

    status = load_status(args.dir)
    groups = {}
    for video_id in ids:
        groups.setdefault(status[video_id]["state"], []).append(video_id)
    print("\nRESULT")
    for state, members in groups.items():
        print(f"  {state}: {len(members)}" + ("" if state == "done" else f"  ({','.join(members)})"))
    if spent:
        print(f"  treg spend: ~${spent:.4f}")
    silent = sum(videos[v].get("duration") or 0 for v in groups.get("no_captions", []))
    if silent:
        print(f"  no captions: {fmt_time(silent)} of audio. Next: transcribe_local.py --dir {args.dir} --estimate")
    if groups.get("failed"):
        cost = len(groups["failed"]) * treg_client.ENDPOINTS["scrapecreators.x.v1-youtube-video-transcript"][1]
        print(f"  failed via yt-dlp: rerun with --treg (about ${cost:.3f}, more if a provider misses)")


if __name__ == "__main__":
    main()
