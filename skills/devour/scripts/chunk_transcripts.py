#!/usr/bin/env python3
"""Split saved transcripts into reading-sized chunks in <channel dir>/chunks.
Breaks at paragraph boundaries, preferring chapter starts, and prints how much there is to read.

  chunk_transcripts.py --dir <channel dir> [--words 6000]
Only this run's selection is chunked. Chunking is repeatable, so notes from an earlier run stay valid.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import fmt_time, read_json, transcript_text, video_numbers


GAP_SECONDS = 40


def estimate_tokens(text):
    """Rough reading cost. Non-Latin scripts take far more tokens per word than English."""
    latin = sum(1 for char in text if ord(char) < 128)
    return latin // 4 + (len(text) - latin) // 2


def caption_gaps(segments):
    """Stretches with no captions, which may be missing speech rather than silence."""
    return [(a["start"], b["start"]) for a, b in zip(segments, segments[1:]) if b["start"] - a["start"] > GAP_SECONDS]


def split_blocks(text):
    """Separate the header lines from the transcript blocks that follow them."""
    header, _, body = text.partition("\n\n")
    return header, [block for block in body.split("\n\n") if block.strip()]


def chunk_blocks(blocks, limit):
    chunks, current, count = [], [], 0
    for block in blocks:
        words = len(block.split())
        chapter_break = block.startswith("## CHAPTER") and count > limit * 0.6
        if current and (count + words > limit or chapter_break):
            chunks.append(current)
            current, count = [], 0
        current.append(block)
        count += words
    if current:
        chunks.append(current)
    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", required=True)
    parser.add_argument("--words", type=int, default=6000)
    args = parser.parse_args()

    root = Path(args.dir)
    out = root / "chunks"
    out.mkdir(exist_ok=True)
    for old in out.glob("*.txt"):
        old.unlink()
    total_words, total_chunks, total_tokens = 0, 0, 0
    for label, video_id in video_numbers(root).items():
        record = read_json(root / "transcripts" / f"{video_id}.json")
        text = transcript_text(record)
        header, blocks = split_blocks(text)
        chunks = chunk_blocks(blocks, args.words)
        words = sum(len(block.split()) for block in blocks)
        total_words += words
        total_chunks += len(chunks)
        total_tokens += estimate_tokens(text)
        for number, chunk in enumerate(chunks, 1):
            first = next((m.group(1) for b in chunk if (m := re.match(r"\[([\d:]+)\]", b))), "?")
            title = f"CITE AS: {label}\nCHUNK {number} of {len(chunks)}, starting at {first}"
            (out / f"{video_id}-{number:02d}.txt").write_text("\n\n".join([header, title, *chunk]) + "\n", encoding="utf-8")
        print(f"{label:<4} {video_id}  {words:>7,} words  {len(chunks):>3} chunks  {record['title'][:56]}")
        for start, end in caption_gaps(record["segments"]):
            print(f"     no captions from {fmt_time(start)} to {fmt_time(end)}: check whether speech is missing")
    print(f"\nTotal: {total_words:,} words, about {total_tokens:,} tokens, in {total_chunks} chunks at {out}")


if __name__ == "__main__":
    main()
