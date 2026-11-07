#!/usr/bin/env python3
"""Check a finished knowledge doc before it is delivered, using status.json as the source of truth.
Fails on outside resources, leftover placeholders, citations to videos or moments that do not
exist, chips whose label disagrees with their link, and videos missing from the sources list.

  check_doc.py <doc.html> --dir <channel dir>
"""
import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).parent))
from common import parse_time, read_json, selected_status

SKIP_TEXT = {"script", "style", "svg", "title"}
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "area", "base", "col", "embed", "track", "wbr"}
WORDS_PER_MINUTE = 230
STAMP_TOLERANCE_SECONDS = 5
BIG_RUN_VIDEOS = 20


class Doc(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.outside, self.sources_ids = [], [], set()
        self.words, self.figures, self.unlabelled_svgs = 0, 0, 0
        self.chips, self.open_chip = [], None
        self.stack, self.sources_depth = [], None
        self.title = ""

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        classes = (attr.get("class") or "").split()
        if "diagram" in classes or "explainer" in classes:
            self.figures += 1
        if tag == "svg" and not attr.get("aria-label") and attr.get("id") != "svg-defs":
            self.unlabelled_svgs += 1
        if tag in ("script", "img", "iframe", "video", "audio", "source") and re.match(r"(https?:)?//", attr.get("src") or ""):
            self.outside.append(attr["src"])
        if tag == "link" and "stylesheet" in (attr.get("rel") or "") and re.match(r"(https?:)?//", attr.get("href") or ""):
            self.outside.append(attr["href"])
        if tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
            if "cite" in classes:
                self.open_chip = [attr["href"], ""]
            if self.sources_depth is not None:
                video_id, _ = youtube_ref(attr["href"])
                if video_id:
                    self.sources_ids.add(video_id)
        if tag not in VOID:
            self.stack.append(tag)
            if attr.get("id") == "sources" and self.sources_depth is None:
                self.sources_depth = len(self.stack)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "a" and self.open_chip:
            self.chips.append(tuple(self.open_chip))
            self.open_chip = None
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        if self.sources_depth is not None and len(self.stack) < self.sources_depth:
            self.sources_depth = None

    def handle_data(self, data):
        if self.stack and self.stack[-1] == "title":
            self.title += data
        if self.open_chip:
            self.open_chip[1] += data
        elif not SKIP_TEXT.intersection(self.stack) and self.sources_depth is None:
            self.words += len(data.split())


def youtube_ref(href):
    """Return (video_id, seconds) for a YouTube link, or (None, None) for anything else."""
    url = urlparse(href)
    host = url.netloc.lower().removeprefix("www.").removeprefix("m.")
    query = parse_qs(url.query)
    if host == "youtu.be":
        video_id = url.path.strip("/")
    elif host == "youtube.com" and url.path == "/watch":
        video_id = (query.get("v") or [None])[0]
    else:
        return None, None
    match = re.fullmatch(r"(\d+)s?", (query.get("t") or [""])[0])
    return video_id, int(match.group(1)) if match else None


def check(text, status, durations, starts):
    doc = Doc()
    doc.feed(text)
    errors, warnings = [], []
    if not text.lstrip().lower().startswith("<!doctype html"):
        errors.append("the file must start with <!DOCTYPE html>")
    if not doc.title.strip():
        errors.append("the page has no <title>")
    if re.search(r"\{\{[A-Z_]+\}\}", text):
        errors.append("template placeholders remain: " + ", ".join(sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", text)))))
    if re.search(r"url\(\s*['\"]?https?:", text):
        errors.append("CSS loads something from the internet; the page must work offline")
    errors += [f"loads an outside resource: {item}" for item in doc.outside]

    used = {vid for vid, row in status.items() if row.get("state") == "done"}
    cited = set()  # videos with at least one timestamped citation
    for href in doc.links:
        video_id, seconds = youtube_ref(href)
        if video_id is None:
            continue
        if video_id not in status:
            errors.append(f"links to a video that was never fetched: {href}")
        elif seconds is not None:
            cited.add(video_id)
        duration = durations.get(video_id)
        if seconds is not None and duration and seconds > duration:
            errors.append(f"timestamp is past the end of the video: {href} (video is {duration}s)")

    for href, label in doc.chips:
        video_id, seconds = youtube_ref(href)
        stamp = re.search(r"\d+(?::\d\d)+", label)
        if video_id is None or seconds is None or not stamp:
            errors.append(f"citation chip without a timestamped video link: {label!r} -> {href}")
            continue
        if parse_time(stamp.group()) != seconds:
            errors.append(f"chip label {label!r} does not match its link: {href}")
        known = starts.get(video_id)
        if known and min(abs(seconds - start) for start in known) > STAMP_TOLERANCE_SECONDS:
            errors.append(f"no caption near this moment, so the stamp looks invented: {label!r} -> {href}")

    if not doc.sources_ids and status:
        errors.append('no element with id="sources" containing links to the videos')
    missing = set(status) - doc.sources_ids
    if doc.sources_ids and missing:
        errors.append("missing from the sources list: " + ", ".join(sorted(missing)))
    if used - cited and len(used) <= BIG_RUN_VIDEOS:  # a big run's doc is selective, so gaps are expected
        warnings.append("used but never cited with a timestamp: " + ", ".join(sorted(used - cited)))
    if doc.figures == 0:
        warnings.append("no diagrams in the document")
    if doc.unlabelled_svgs:
        warnings.append(f"{doc.unlabelled_svgs} diagrams have no aria-label")
    return errors, warnings, doc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("doc")
    parser.add_argument("--dir", required=True)
    args = parser.parse_args()
    root = Path(args.dir)
    status = selected_status(root)
    durations, starts = {}, {}
    for video_id in status:
        record = read_json(root / "transcripts" / f"{video_id}.json")
        if record:
            durations[video_id] = record.get("duration")
            starts[video_id] = [segment["start"] for segment in record["segments"]]
    errors, warnings, doc = check(Path(args.doc).read_text(encoding="utf-8"), status, durations, starts)
    print(f"{doc.words:,} words, about {doc.words // WORDS_PER_MINUTE} minutes to read, {doc.figures} diagrams and"
          f" explainers, {sum(1 for h in doc.links if youtube_ref(h)[1] is not None)} timestamped citations")
    for item in warnings:
        print(f"WARNING: {item}")
    for item in errors:
        print(f"ERROR: {item}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
