#!/usr/bin/env python3
"""Turn draft.html into the finished page: expand [[V1 12:34]] shorthand into citation chips
and fill {{SOURCES}} from status.json. Stops if a citation names a moment with no caption,
so an invented timestamp can't reach the reader.

  assemble_doc.py --dir <channel dir> [--draft draft.html] [--out knowledge-doc.html]
"""
import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import fmt_time, load_selection, load_videos, parse_time, read_json, selected_status, video_numbers

CITE = re.compile(r"\[\[(?:(V\d+)\s+)?(\d+(?::\d\d)+)\]\]")
TOLERANCE_SECONDS = 5
SOURCE_NAMES = {
    "youtube-manual-captions": "creator's captions",
    "youtube-auto-captions": "auto-captions",
    "local-whisper": "transcribed locally",
}


def expand_citations(text, numbers, starts, titles):
    errors = []

    def chip(match):
        label, stamp = match.group(1), match.group(2)
        if label is None and len(numbers) == 1:
            label = next(iter(numbers))
        video_id = numbers.get(label)
        if video_id is None:
            errors.append(f"unknown video in {match.group(0)}")
            return match.group(0)
        seconds = parse_time(stamp)
        if not any(abs(seconds - start) <= TOLERANCE_SECONDS for start in starts.get(video_id, [])):
            errors.append(f"no caption near {match.group(0)}")
            return match.group(0)
        href = html.escape(f"https://www.youtube.com/watch?v={video_id}&t={seconds}s")
        title = html.escape(titles.get(video_id, ""))
        return f'<a class="cite" href="{href}" title="{title}">{label} · {stamp}</a>'

    return CITE.sub(chip, text), errors


def sources_html(numbers, selection, status, records, videos):
    rows = []
    for label, video_id in numbers.items():
        record = records[video_id]
        source = status[video_id].get("source") or ""
        how = SOURCE_NAMES.get(source, "via treg" if source.startswith("treg") else source)
        rows.append(f'<tr><td>{label}</td><td><a href="{html.escape(record["url"])}">{html.escape(record["title"])}</a></td>'
                    f'<td>{record.get("date") or "?"}</td><td>{fmt_time(record.get("duration"))}</td><td>{how}</td></tr>')
    out = ['<div class="table-wrap"><table><thead><tr><th></th><th>Video</th><th>Date</th><th>Length</th><th>Transcript</th></tr>'
           "</thead><tbody>" + "".join(rows) + "</tbody></table></div>"]
    used = set(numbers.values())
    skipped = [video_id for video_id in selection if video_id not in used]
    if skipped:
        items = []
        for video_id in skipped:
            video = videos.get(video_id, {})
            row = status.get(video_id, {})
            reason = row.get("reason") or row.get("state", "not fetched").replace("_", " ")
            url = html.escape(video.get("url") or f"https://www.youtube.com/watch?v={video_id}")
            items.append(f'<li><a href="{url}">{html.escape(video.get("title", video_id))}</a>: {html.escape(reason)}</li>')
        out.append("<p><strong>Skipped</strong></p><ul>" + "".join(items) + "</ul>")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", required=True)
    parser.add_argument("--draft", default="draft.html")
    parser.add_argument("--out", default="knowledge-doc.html")
    args = parser.parse_args()
    root = Path(args.dir)

    numbers = video_numbers(root)
    records = {vid: read_json(root / "transcripts" / f"{vid}.json") for vid in numbers.values()}
    starts = {vid: [segment["start"] for segment in record["segments"]] for vid, record in records.items()}
    titles = {vid: record["title"] for vid, record in records.items()}
    text, errors = expand_citations((root / args.draft).read_text(encoding="utf-8"), numbers, starts, titles)
    if errors:
        print("\n".join(f"ERROR: {item}" for item in errors))
        sys.exit(1)
    table = sources_html(numbers, load_selection(root), selected_status(root), records, load_videos(root))
    (root / args.out).write_text(text.replace("{{SOURCES}}", table), encoding="utf-8")
    print(f"Wrote {root / args.out}")


if __name__ == "__main__":
    main()
