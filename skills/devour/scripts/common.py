"""Shared helpers for devour: where a channel's files live, and the transcript file format.
Every other script reads and writes through here so the on-disk layout is defined once.
"""
import json
import os
import re
import tempfile
from pathlib import Path

LIBRARY = Path(os.environ.get("DEVOUR_DIR", Path.home() / "Documents" / "Projects" / "devour"))
PARAGRAPH_SECONDS = 20


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "channel"


def fmt_time(seconds):
    seconds = int(seconds or 0)
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}" if hours else f"{minutes}:{secs:02d}"


def write_json(path, data):
    """Write through a temp file so a crash never leaves a half-written file behind."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def read_json(path, default=None):
    path = Path(path)
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_videos(channel_dir):
    data = read_json(Path(channel_dir) / "videos.json")
    if data is None:
        raise SystemExit(f"No videos.json in {channel_dir}. Run list_videos.py first.")
    return {video["id"]: video for video in data["videos"]}


def load_status(channel_dir):
    return read_json(Path(channel_dir) / "status.json", {})


def set_status(channel_dir, video_id, **fields):
    status = load_status(channel_dir)
    status.setdefault(video_id, {}).update(fields)
    write_json(Path(channel_dir) / "status.json", status)


def load_selection(channel_dir):
    return read_json(Path(channel_dir) / "selection.json", [])


def save_selection(channel_dir, ids):
    """Record this run's videos. A channel folder keeps old transcripts, but a doc uses only these."""
    write_json(Path(channel_dir) / "selection.json", list(ids))


def selected_status(channel_dir):
    status = load_status(channel_dir)
    return {video_id: status[video_id] for video_id in load_selection(channel_dir) if video_id in status}


def video_numbers(channel_dir):
    """Map citation labels to ids: V1, V2... in selection order, counting only videos with a transcript."""
    done = [vid for vid, row in selected_status(channel_dir).items() if row.get("state") == "done"]
    return {f"V{number}": vid for number, vid in enumerate(done, 1)}


def parse_time(text):
    seconds = 0
    for part in text.split(":"):
        seconds = seconds * 60 + int(part)
    return seconds


def paragraphs(segments, chapters=(), every=PARAGRAPH_SECONDS):
    """Group caption lines into timestamped paragraphs, breaking at chapter starts."""
    chapter_starts = sorted(chapters, key=lambda c: c["start"])
    out, current, opened_at, next_chapter = [], [], None, 0
    for segment in segments:
        start = segment["start"]
        at_chapter = next_chapter < len(chapter_starts) and start >= chapter_starts[next_chapter]["start"]
        if current and (at_chapter or start - opened_at >= every):
            out.append({"start": opened_at, "text": " ".join(current)})
            current, opened_at = [], None
        while next_chapter < len(chapter_starts) and start >= chapter_starts[next_chapter]["start"]:
            out.append({"chapter": chapter_starts[next_chapter]["title"], "start": chapter_starts[next_chapter]["start"]})
            next_chapter += 1
        if opened_at is None:
            opened_at = start
        current.append(segment["text"])
    if current:
        out.append({"start": opened_at, "text": " ".join(current)})
    return out


def transcript_text(record):
    lines = [
        f"TITLE: {record['title']}",
        f"VIDEO: {record['id']}  URL: {record['url']}",
        f"DATE: {record.get('date') or 'unknown'}  LENGTH: {fmt_time(record.get('duration'))}"
        f"  SOURCE: {record['source']}  LANGUAGE: {record.get('language') or 'unknown'}",
        "",
    ]
    for block in paragraphs(record["segments"], record.get("chapters") or []):
        if "chapter" in block:
            lines += [f"## CHAPTER [{fmt_time(block['start'])}] {block['chapter']}", ""]
        else:
            lines += [f"[{fmt_time(block['start'])}] {block['text']}", ""]
    return "\n".join(lines)


def save_transcript(channel_dir, record):
    folder = Path(channel_dir) / "transcripts"
    write_json(folder / f"{record['id']}.json", record)
    (folder / f"{record['id']}.txt").write_text(transcript_text(record), encoding="utf-8")


def has_transcript(channel_dir, video_id):
    return (Path(channel_dir) / "transcripts" / f"{video_id}.json").exists()


def parse_ids(ids_arg, channel_dir):
    """Accept 'a,b,c' or @file with one id per line, keeping order and dropping repeats."""
    if ids_arg.startswith("@"):
        raw = Path(ids_arg[1:]).read_text(encoding="utf-8").split()
    else:
        raw = ids_arg.split(",")
    ids = list(dict.fromkeys(item.strip() for item in raw if item.strip()))
    known = load_videos(channel_dir)
    unknown = [item for item in ids if item not in known]
    if unknown:
        raise SystemExit(f"These ids are not in videos.json: {', '.join(unknown)}")
    return ids
