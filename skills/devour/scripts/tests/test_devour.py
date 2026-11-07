"""Unit tests for devour's scripts: run with `python3 -m unittest discover -s scripts/tests`.
They cover the parts that fail quietly: caption parsing, track choice, the treg token guard,
chunking, and the document checker. Nothing here touches the network.
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import assemble_doc
import check_doc
import chunk_transcripts
import common
import fetch_transcripts as ft
import list_videos as lv
import transcribe_local as tl
import treg_client


class Channels(unittest.TestCase):
    def test_forms(self):
        expected = "https://www.youtube.com/@abc"
        for raw in ("@abc", "abc", "https://www.youtube.com/@abc", "https://www.youtube.com/@abc/videos",
                    "youtube.com/@abc/", "https://www.youtube.com/@abc/featured?x=1"):
            self.assertEqual(lv.normalize_channel(raw), (expected, False), raw)

    def test_channel_id_and_playlist(self):
        self.assertEqual(lv.normalize_channel("https://www.youtube.com/channel/UCabc")[0],
                         "https://www.youtube.com/channel/UCabc")
        self.assertTrue(lv.normalize_channel("https://www.youtube.com/playlist?list=PL1")[1])

    def test_single_video_refused(self):
        for raw in ("https://www.youtube.com/watch?v=abc", "https://youtu.be/abc"):
            with self.assertRaises(SystemExit):
                lv.normalize_channel(raw)

    def test_flat_rows_use_timestamp_for_date(self):
        rows = lv.rows_from_ytdlp({"entries": [{"id": "a", "title": "t", "timestamp": 1792281600, "view_count": 5}]}, "videos")
        self.assertEqual(rows[0]["date"], "2026-10-18")


    def test_folder_comes_from_handle_so_non_latin_names_stay_distinct(self):
        self.assertEqual(lv.folder_name({"handle": "@AnufrievNikita", "channel": "Хедлайнеры"}), "anufrievnikita")
        self.assertEqual(lv.folder_name({"handle": None, "channel_id": "UCabc", "channel": "Хедлайнеры"}), "ucabc")
        self.assertEqual(lv.folder_name({"handle": None, "channel": "Good Talks"}), "good-talks")


class Captions(unittest.TestCase):
    def test_json3_auto_words_join_and_newlines_vanish(self):
        data = {"events": [{"tStartMs": 0, "dDurationMs": 5},
                           {"tStartMs": 1000, "segs": [{"utf8": "Well,"}, {"utf8": " let's"}, {"utf8": " talk"}]},
                           {"tStartMs": 2390, "aAppend": 1, "segs": [{"utf8": "\n"}]}]}
        self.assertEqual(ft.parse_json3(data), [{"start": 1.0, "text": "Well, let's talk"}])

    def test_srt(self):
        text = "1\n00:01:01,500 --> 00:01:03,040\nHello there\n\n2\n00:01:04,000 --> 00:01:05,000\nagain"
        self.assertEqual(ft.parse_srt(text), [{"start": 61.5, "text": "Hello there"}, {"start": 64.0, "text": "again"}])

    def test_manual_beats_auto(self):
        meta = {"language": "en", "subtitles": {"en-US": ["m"]}, "automatic_captions": {"en-orig": ["a"], "en": ["b"]}}
        self.assertEqual(ft.pick_track(meta, "auto"), ("manual", "en-US", ["m"]))

    def test_original_asr_beats_machine_translation(self):
        meta = {"language": "ru", "subtitles": {}, "automatic_captions": {"ru-orig": ["o"], "en": ["t"], "ru": ["r"]}}
        self.assertEqual(ft.pick_track(meta, "auto")[1], "ru-orig")

    def test_asked_language_then_original(self):
        meta = {"language": "ru", "subtitles": {"ru": ["m"]}, "automatic_captions": {}}
        self.assertEqual(ft.pick_track(meta, "de")[1], "ru")

    def test_regional_language_finds_base_tracks(self):
        meta = {"language": "en-US", "subtitles": {}, "automatic_captions": {"en-orig": ["o"], "en": ["t"], "fr": ["f"]}}
        self.assertEqual(ft.pick_track(meta, "auto"), ("auto", "en-orig", ["o"]))

    def test_live_chat_is_not_a_transcript(self):
        self.assertIsNone(ft.pick_track({"subtitles": {"live_chat": ["x"]}, "automatic_captions": {}}, "auto"))

    def test_provider_shapes(self):
        self.assertEqual(ft.segments_from_scrapecreators({"transcript": [{"text": " hi ", "startMs": "1500"}]}),
                         [{"start": 1.5, "text": "hi"}])
        self.assertEqual(ft.segments_from_scrapecreators({"transcript": None}), [])
        self.assertEqual(ft.segments_from_anyapi({"output": {"data": {"segments": [{"startSeconds": 2, "text": "x"}]}}}),
                         [{"start": 2.0, "text": "x"}])

    def test_whisper_shape(self):
        data = {"transcription": [{"offsets": {"from": 2500, "to": 3000}, "text": " Hello"}, {"offsets": {"from": 1}, "text": " "}]}
        self.assertEqual(tl.parse_whisper(data), [{"start": 2.5, "text": "Hello"}])


class TregGuard(unittest.TestCase):
    def test_refuses_anything_off_the_list(self):
        for bad in ("https://evil.example/x", "intercom/me", "scrapecreators.fake", "../tools"):
            with self.assertRaises(treg_client.TregError):
                treg_client.build_url(bad, {}, "GET")
            with self.assertRaises(treg_client.TregError):
                treg_client.call(bad, {})

    def test_url_is_built_on_the_treg_host(self):
        url = treg_client.build_url("scrapecreators.x.v1-youtube-video-transcript", {"url": "https://y.t/?v=1&b=2"}, "GET")
        self.assertTrue(url.startswith("https://treg.to/call/scrapecreators.x.v1-youtube-video-transcript?url="))
        self.assertNotIn("&b=2", url)


    def test_empty_balance_is_recognised(self):
        self.assertTrue(treg_client.TregError("x", status=402).out_of_funds)
        self.assertFalse(treg_client.TregError("x", status=500).out_of_funds)


class Text(unittest.TestCase):
    def test_paragraphs_break_on_time_and_chapter(self):
        segments = [{"start": s, "text": str(s)} for s in (0, 10, 31, 40, 95)]
        blocks = common.paragraphs(segments, [{"start": 40, "title": "Two"}])
        self.assertEqual(blocks[0], {"start": 0, "text": "0 10"})
        self.assertEqual(blocks[1], {"start": 31, "text": "31"})
        self.assertEqual(blocks[2]["chapter"], "Two")
        self.assertEqual(blocks[-1], {"start": 95, "text": "95"})

    def test_chunks_respect_limit_and_keep_everything(self):
        blocks = [f"[0:0{i}] " + "word " * 40 for i in range(10)]
        chunks = chunk_transcripts.chunk_blocks(blocks, 100)
        self.assertTrue(all(sum(len(b.split()) for b in c) <= 100 for c in chunks))
        self.assertEqual([b for c in chunks for b in c], blocks)

    def test_chapter_starts_a_chunk_when_far_enough_along(self):
        blocks = ["a " * 70, "## CHAPTER [1:00] Next", "b " * 10]
        self.assertEqual(len(chunk_transcripts.chunk_blocks(blocks, 100)), 2)

    def test_times(self):
        self.assertEqual(common.fmt_time(75), "1:15")
        self.assertEqual(common.fmt_time(3675), "1:01:15")


PAGE = """<!DOCTYPE html><html><head><title>T</title></head><body>
<p>Idea <a href="https://www.youtube.com/watch?v=AAA&t=90s">V1</a> <a href="https://youtu.be/BBB?t=10">V2</a></p>
<figure class="diagram"><svg aria-label="x"><text>not counted</text></svg></figure>
<section id="sources"><a href="https://www.youtube.com/watch?v=AAA">a</a> <a href="https://youtu.be/BBB">b</a> <a href="https://youtu.be/CCC">c</a></section>
</body></html>"""
STATUS = {"AAA": {"state": "done"}, "BBB": {"state": "done"}, "CCC": {"state": "skipped"}}


class Checker(unittest.TestCase):
    def run_check(self, text, status=STATUS, durations=None, starts=None):
        return check_doc.check(text, status, durations or {"AAA": 100, "BBB": 100}, starts or {})

    def test_good_page_passes(self):
        errors, warnings, doc = self.run_check(PAGE)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(doc.figures, 1)
        self.assertEqual(doc.words, 3)  # the sources list and page title are not reading text

    def test_chip_label_must_match_its_link(self):
        text = PAGE.replace('t=90s">V1</a>', 't=90s" class="cite">V1 · 2:00</a>')
        self.assertTrue(any("does not match" in e for e in self.run_check(text)[0]))

    def test_stamp_must_exist_in_the_transcript(self):
        text = PAGE.replace('t=90s">V1</a>', 't=90s" class="cite">V1 · 1:30</a>')
        self.assertEqual(self.run_check(text, starts={"AAA": [88.0]})[0], [])
        errors = self.run_check(text, starts={"AAA": [10.0, 300.0]})[0]
        self.assertTrue(any("no caption near" in e for e in errors))

    def test_timestamp_past_end(self):
        self.assertTrue(any("past the end" in e for e in self.run_check(PAGE, durations={"AAA": 50})[0]))

    def test_invented_video(self):
        text = PAGE.replace("<svg", '<a href="https://youtu.be/ZZZ?t=1">z</a><svg')
        self.assertTrue(any("never fetched" in e for e in self.run_check(text)[0]))

    def test_outside_script_and_placeholder(self):
        text = PAGE.replace("<body>", '<body><script src="https://cdn.example/x.js"></script>{{TITLE}}')
        errors = self.run_check(text)[0]
        self.assertTrue(any("outside resource" in e for e in errors))
        self.assertTrue(any("placeholders" in e for e in errors))

    def test_video_missing_from_sources(self):
        text = PAGE.replace('<a href="https://youtu.be/CCC">c</a>', "")
        self.assertTrue(any("missing from the sources" in e for e in self.run_check(text)[0]))

    def test_links_outside_sources_do_not_count(self):
        text = PAGE.replace('<a href="https://youtu.be/CCC">c</a></section>', '</section><a href="https://youtu.be/CCC">c</a>')
        self.assertTrue(any("missing from the sources" in e for e in self.run_check(text)[0]))


class Assembly(unittest.TestCase):
    NUMBERS = {"V1": "AAA", "V2": "BBB"}
    STARTS = {"AAA": [0.0, 90.2, 3725.0], "BBB": [10.0]}
    TITLES = {"AAA": 'A "quoted" title', "BBB": "B"}

    def expand(self, text):
        return assemble_doc.expand_citations(text, self.NUMBERS, self.STARTS, self.TITLES)

    def test_expands_to_a_linked_chip(self):
        html, errors = self.expand("Idea [[V1 1:30]].")
        self.assertEqual(errors, [])
        self.assertIn('href="https://www.youtube.com/watch?v=AAA&amp;t=90s"', html)
        self.assertIn(">V1 · 1:30</a>", html)
        self.assertIn("&quot;quoted&quot;", html)

    def test_hours(self):
        self.assertIn("t=3725s", self.expand("[[V1 1:02:05]]")[0])

    def test_rejects_unknown_video_and_invented_stamp(self):
        self.assertTrue(self.expand("[[V9 0:10]]")[1])
        self.assertTrue(self.expand("[[V1 9:59]]")[1])

    def test_one_video_needs_no_number(self):
        html, errors = assemble_doc.expand_citations("[[0:10]]", {"V1": "BBB"}, self.STARTS, self.TITLES)
        self.assertEqual(errors, [])
        self.assertIn("V1 · 0:10", html)

    def test_sources_table_marks_how_each_video_was_read(self):
        status = {"AAA": {"state": "done", "source": "local-whisper"}, "BBB": {"state": "skipped", "reason": "private"}}
        records = {"AAA": {"title": "T<1>", "url": "u", "date": "2026-01-02", "duration": 60}}
        videos = {"BBB": {"title": "Gone", "url": "https://youtu.be/BBB"}}
        html = assemble_doc.sources_html({"V1": "AAA"}, ["AAA", "BBB"], status, records, videos)
        self.assertIn("transcribed locally", html)
        self.assertIn("T&lt;1&gt;", html)
        self.assertIn("Gone", html)
        self.assertIn("private", html)


class Selection(unittest.TestCase):
    def test_only_this_runs_videos_count(self):
        with tempfile.TemporaryDirectory() as folder:
            common.set_status(folder, "OLD", state="done")
            common.set_status(folder, "NEW", state="done")
            common.save_selection(folder, ["NEW"])
            self.assertEqual(list(common.selected_status(folder)), ["NEW"])
            self.assertEqual(common.video_numbers(folder), {"V1": "NEW"})


class Dates(unittest.TestCase):
    def test_rough_dates_do_not_pretend_to_be_exact(self):
        self.assertEqual(lv.rough_date("2023-11-08", "2026-11-08"), "~2023")
        self.assertEqual(lv.rough_date("2026-10-08", "2026-11-08"), "~2026-10")
        self.assertEqual(lv.rough_date(None, "2026-11-08"), "?")


class Sizing(unittest.TestCase):
    def test_cyrillic_counts_heavier_than_english(self):
        self.assertGreater(chunk_transcripts.estimate_tokens("привет" * 100), chunk_transcripts.estimate_tokens("hello!" * 100))

    def test_gaps(self):
        segments = [{"start": 0, "text": "a"}, {"start": 10, "text": "b"}, {"start": 100, "text": "c"}]
        self.assertEqual(chunk_transcripts.caption_gaps(segments), [(10, 100)])


class Storage(unittest.TestCase):
    def test_transcript_round_trip_and_status(self):
        with tempfile.TemporaryDirectory() as folder:
            record = {"id": "A", "title": "T", "url": "u", "source": "s", "duration": 60,
                      "segments": [{"start": 5, "text": "hello"}]}
            common.save_transcript(folder, record)
            self.assertTrue(common.has_transcript(folder, "A"))
            self.assertIn("[0:05] hello", (Path(folder) / "transcripts" / "A.txt").read_text())
            common.set_status(folder, "A", state="done")
            common.set_status(folder, "A", source="x")
            self.assertEqual(common.load_status(folder)["A"], {"state": "done", "source": "x"})


if __name__ == "__main__":
    unittest.main()
