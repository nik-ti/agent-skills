# YouTube channel analysis

Requires `yt-dlp` (`brew install yt-dlp` if missing). No API key needed.

## Collect

Two modes. Pick based on the depth the user chose in the scoping step.

**Index mode** — the whole channel's titles, IDs, and durations in ~10 seconds. No
descriptions, no dates, no view counts. Use it to size up a channel before committing, or
when the user only wants to know what topics exist.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/youtube_scrape.py" "<channel URL or @handle>" \
  --mode index --out-prefix yt
```

**Full mode** — descriptions, upload dates, view/like/comment counts, chapters, and every
link in every description. This is the default for any real analysis, since descriptions
and dates are where the strategy actually shows.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/youtube_scrape.py" "<channel URL or @handle>" \
  --mode full --out-prefix yt
```

Roughly 3 seconds per video across 4 parallel workers, so ~300 videos takes a few
minutes. Run it in the background and do other work while it finishes. Add `--limit N`
to cap it (newest first) when the user only cares about recent output.

Other flags: `--tab shorts` (or `streams`) to analyze a different tab — Shorts are often
a separate content strategy worth reporting on; `--workers N` to tune parallelism.

**Outputs:** `yt_videos.csv` and `yt_videos.json` (full rows), `yt_summary.json`
(aggregates — read this first), `yt_index.json`, and `yt_meta/` (per-video raw JSON cache,
which makes re-runs nearly free).

### The rate-limit trap

Above ~6 parallel workers, YouTube returns **"Sign in to confirm you're not a bot."**
This is a rate-limit signal, not a real authentication wall — it needs no cookies and no
login. The script already handles it by retrying through alternate player clients
(`web_embedded` is the one that usually works). If you see it anyway, lower `--workers`
and re-run; the cache means only the missing videos get refetched.

Check `failed` in `yt_summary.json`. If videos failed, say so in the report rather than
silently analyzing a partial set.

## Going deeper — watching videos

Metadata tells you what a channel *publishes*. It cannot tell you what a creator actually
*does* — their framework, their tooling, how they structure a build, what they actually
recommend. For that you have to watch, using the **`watch` skill**.

Invoke it with the Skill tool (`watch`), passing the video URL and the user's intent.
The intent matters a lot: `watch` shapes its report around it, so the same video watched
for "their n8n architecture" versus "their hook and pacing" produces different output.
Pass what the user is actually hunting for, verbatim where possible.

If the Skill tool isn't available, call it directly:

```bash
python3 ~/.claude/skills/watch/scripts/watch.py "<video URL>" --intent "<what to look for>"
```

Note that `${CLAUDE_SKILL_DIR}` points at *this* skill, not `watch` — use the path above.

### Which videos to watch

**Default: the top-viewed videos of the last ~6 months, 5 of them.** This default exists
because both halves matter. Top-viewed captures what actually worked rather than what the
creator hoped would work. The recency window guards against a trap that's common on fast-
moving channels: a channel's all-time biggest hit may be from an abandoned era. A creator
who spent 2025 on one topic and pivoted entirely in 2026 will have their all-time top
videos clustered in the dead era — watching those answers a question nobody asked.

Adjust when the situation calls for it:

- **User named a topic** → filter titles/descriptions for it first, then take the top
  performers within that subset. This is the most common real case.
- **Channel is small or new** → drop the recency window and take top-viewed overall.
- **User wants current direction** → most recent uploads instead, noting that recent
  videos have had less time to accumulate views so performance isn't yet meaningful.
- **User wants to understand a format** → pick the extremes (best and worst performer of
  a similar type); the contrast is more informative than two hits.

Always tell the user which videos you picked and why before watching them. It's a
meaningful spend of time, and they may want to redirect it.

Watch videos one at a time and read each report before moving on — later picks are often
better informed by what the earlier ones revealed.

## What to analyze

Beyond a plain content inventory, these are the patterns that make a YouTube report
worth reading:

1. **Identity** — channel name, subscriber count, video count, date of first upload,
   and the channel description (which usually states their business model outright).
2. **Cadence over time** — `uploads_per_month` in the summary. Look for step changes.
   A jump from 10 to 25 uploads a month is a strategy shift, and pairing it with median
   views per month shows whether volume helped or diluted.
3. **Topic evolution** — bucket titles and descriptions into themes *by time period*, not
   just overall. Pivots are the single most valuable finding in a channel analysis, and
   they're invisible in an aggregate topic count. Compare median views per topic per era
   to show whether a pivot worked.
4. **What performs** — top videos by views, with duration and date. Look for the format
   behind the hits: long courses? reaction-to-news? tutorials? Note that raw view
   rankings are biased toward older videos (see below).
5. **Title formula** — recurring patterns: numbers, "I built…", parenthetical tags like
   "(free template)", ALL CAPS, named tools. Quote real examples.
6. **Video structure** — `chapter_titles` are a free outline of how they build a video.
   High chapter usage signals structured tutorial content. Read a few chapter lists to
   describe their standard arc.
7. **Monetization and funnel** — `top_link_domains` is the clearest window into the
   business. Separate their own properties (community, course, newsletter, podcast) from
   sponsors and affiliate links. Note affiliate codes, UTM tags (which reveal per-video
   attribution tracking), and any sponsorship contact address. Count links per video to
   gauge how hard they push.
8. **Duration profile** — median length plus the shape of the tail. A channel with a
   17-minute median and a few 8-hour courses is running two different products.
9. **Shorts strategy** — if the Shorts tab is substantial, check whether Shorts topics
   mirror the long-form or serve a separate top-of-funnel role.

## Interpreting view counts honestly

**View counts are point-in-time snapshots, not historical data.** A two-year-old video has
had two years to accumulate; last week's has had a week. Any raw all-time ranking is
therefore biased toward old videos and systematically understates recent ones.

When comparing across time, either compare medians *within* a period (as the monthly
breakdown does) or say plainly that the ranking favors older uploads. If the user wants
genuine trend data, the honest answer is that it requires re-scraping periodically to
build a time series — a single scrape cannot recover it.

## Known limits — state these where relevant

- **Keyword tags are usually absent.** Many creators don't set them; check how many rows
  actually have tags before drawing conclusions from them.
- **No revenue, RPM, watch time, retention, CTR, or traffic sources.** Those are private
  to the channel owner. Never estimate earnings as if it were data.
- **Comment text is fetchable** (`yt-dlp --write-comments`) but slow and not included by
  the script. Offer it if the user wants audience sentiment.
- **Members-only and unlisted videos** don't appear.
- **Subscriber counts are rounded** by YouTube itself.
