#!/usr/bin/env python3
"""Transcribe videos that have no captions, on this Mac, with whisper.cpp.
Run --estimate first and show the user the time. Each finished video is saved straight away,
so an interrupted run resumes where it stopped. Audio files are deleted after use.

  transcribe_local.py --dir <channel dir> --estimate
  transcribe_local.py --dir <channel dir> [--ids id1,id2] [--lang auto]
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import (fmt_time, has_transcript, load_videos, parse_ids, read_json, save_transcript, selected_status,
                    set_status, write_json)

CACHE = Path.home() / ".cache" / "devour"
MODEL_NAME = "ggml-large-v3-turbo-q5_0.bin"
MODEL_URL = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{MODEL_NAME}"
MODEL_MB = 547
DEFAULT_SPEED = 12.0  # seconds of audio per second of work, replaced by the measured figure after a real run


def speed():
    return read_json(CACHE / "whisper_speed.json", {}).get("audio_seconds_per_second", DEFAULT_SPEED)


def model_path():
    return CACHE / "whisper" / MODEL_NAME


def ensure_model():
    path = model_path()
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading the Whisper model once (~{MODEL_MB} MB)...", flush=True)
    partial = path.with_suffix(".part")
    urllib.request.urlretrieve(MODEL_URL, partial)
    partial.replace(path)
    return path


def download_audio(video, folder):
    template = str(Path(folder) / "audio.%(ext)s")
    result = subprocess.run(["yt-dlp", "-f", "ba[abr<=96]/wa/ba", "--no-warnings", "--no-update", "--no-playlist",
                             "-o", template, video["url"]], capture_output=True, text=True)
    files = list(Path(folder).glob("audio.*"))
    if result.returncode != 0 or not files:
        raise RuntimeError(result.stderr.strip()[-300:] or "audio download failed")
    wav = Path(folder) / "speech.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(files[0]), "-ar", "16000", "-ac", "1", str(wav)],
                   check=True)
    return wav


def parse_whisper(data):
    return [{"start": row["offsets"]["from"] / 1000, "text": row["text"].strip()}
            for row in data.get("transcription") or [] if row.get("text", "").strip()]


def transcribe(video, model, language):
    with tempfile.TemporaryDirectory(prefix="devour-") as folder:
        print("  downloading audio", flush=True)
        wav = download_audio(video, folder)
        out = Path(folder) / "result"
        print("  transcribing", flush=True)
        started = time.time()
        subprocess.run(["whisper-cli", "-m", str(model), "-f", str(wav), "-l", language, "-oj", "-of", str(out), "-np"],
                       check=True, stdout=subprocess.DEVNULL)
        elapsed = time.time() - started
        data = json.loads(Path(f"{out}.json").read_text(encoding="utf-8", errors="replace"))
    return parse_whisper(data), elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", required=True)
    parser.add_argument("--ids", help="default: every video marked no_captions")
    parser.add_argument("--lang", default="auto")
    parser.add_argument("--estimate", action="store_true", help="print the workload and stop")
    args = parser.parse_args()

    videos = load_videos(args.dir)
    status = selected_status(args.dir)
    ids = parse_ids(args.ids, args.dir) if args.ids else [
        vid for vid, row in status.items() if row.get("state") == "no_captions"]
    ids = [vid for vid in ids if not has_transcript(args.dir, vid)]
    if not ids:
        print("Nothing to transcribe.")
        return
    total = sum(videos[vid].get("duration") or 0 for vid in ids)
    print(f"{len(ids)} videos, {fmt_time(total)} of audio. Estimated time: about {fmt_time(total / speed())}"
          f" at {speed():.0f}x real time, plus audio download.")
    if not model_path().exists():
        print(f"The Whisper model is not downloaded yet (one-time ~{MODEL_MB} MB).")
    for tool in ("whisper-cli", "ffmpeg"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} is not installed. Run: brew install {'whisper-cpp' if tool != 'ffmpeg' else 'ffmpeg'}")
    if args.estimate:
        return

    model = ensure_model()
    for position, video_id in enumerate(ids, 1):
        video = videos[video_id]
        print(f"[{position}/{len(ids)}] {video['title'][:70]}", flush=True)
        try:
            segments, elapsed = transcribe(video, model, args.lang)
        except (RuntimeError, subprocess.CalledProcessError) as error:
            set_status(args.dir, video_id, state="failed", reason=f"local transcription: {error}"[:160])
            print(f"  failed: {error}", flush=True)
            continue
        record = {"id": video_id, "title": video["title"], "url": video["url"], "duration": video.get("duration"),
                  "views": video.get("views"), "date": video.get("date"), "language": args.lang,
                  "source": "local-whisper", "chapters": [], "segments": segments}
        save_transcript(args.dir, record)
        set_status(args.dir, video_id, state="done", source="local-whisper")
        if video.get("duration") and elapsed:
            write_json(CACHE / "whisper_speed.json", {"audio_seconds_per_second": video["duration"] / elapsed})
        print(f"  done in {fmt_time(elapsed)}", flush=True)


if __name__ == "__main__":
    main()
