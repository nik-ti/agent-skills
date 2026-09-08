---
name: analyze-channel
description: Analyze any YouTube or Telegram channel — content strategy, cadence, topics, tone, monetization, what performs and why. Use this skill whenever the user pastes a YouTube channel link/@handle or a t.me link and asks to analyze, research, break down, study, reverse-engineer, audit, or "see what they're doing" — and also when they ask softer things like "what kind of content does this channel post?", "how often do they upload?", "what's their strategy?", "what are they promoting?", or "can you look at this channel for me". Applies even when the user doesn't use the word "analyze". For YouTube it can optionally watch videos via the `watch` skill for a deeper read. Do NOT use for analyzing a single video (use `watch` directly).
allowed-tools: Bash, Read, Write, Edit, Skill, AskUserQuestion, Artifact
user-invocable: true
---

# Analyze Channel

Channel analysis is only useful when it answers a real question. The same channel yields
a completely different report depending on whether the user is deciding to subscribe,
studying a competitor, hunting for a specific technique, or planning their own content.
So the first job is always to find out what the user actually wants — then collect data
deterministically with the bundled scripts, then publish a report they can read and share.

## The three steps

1. **Scope** — establish what the user is looking for (rules differ by platform, below)
2. **Collect** — run the bundled script for that platform; never hand-scrape
3. **Report** — publish a polished Artifact page

Read the reference file for the platform you're working with. Don't try to work from
memory — the reference files carry the exact commands, the gotchas, and the report shape:

- **`references/telegram.md`** — Telegram channels. Read this when the link is `t.me/...`.
- **`references/youtube.md`** — YouTube channels. Read this when the link is
  `youtube.com/@...`, `/channel/...`, `/c/...`, or a bare `@handle`.

If the user names both platforms in one request, treat them as two analyses and read both.

## Step 1 — Scope, and how hard to push on it

The instinct to be helpful by just diving in produces a generic report the user has to
re-request. But interrogating them about a simple ask is worse. The right amount of
questioning differs sharply between the two platforms, because the cost of guessing
differs.

**Telegram — do not ask, just run it.** A Telegram channel exposes a small, fixed
surface: name, subscriber count, description, and the last N posts. There is no
meaningful choice to make, so a question would be pure friction. Take the link and
produce the standard profile (last 100 posts) described in `references/telegram.md`.
The only reason to ask anything is if the user's request contains a specific question
the standard profile wouldn't answer.

**YouTube — ask, unless the request is already specific.** A channel can be 500 videos
and years of strategy shifts, and "analyze this channel" could mean a dozen things at
wildly different costs — from a 2-minute metadata pass to watching five videos. Guessing
wrong wastes real time and tokens.

Use `AskUserQuestion` to settle two things, but **only what's still genuinely open** —
if the user already said "just a quick overview" or "find their pricing strategy", that
half is answered, so don't re-ask it:

- **Depth** — metadata-only (fast, no videos watched), or deep (watch videos too)
- **Focus** — a general strategy read, or something specific they're hunting for
  (a technique, a tool stack, resources, a monetization model, a content formula)

Offer concrete options rather than open-ended prompts. Good options look like
"Quick overview — titles, cadence, topics, what performs (~2 min)" and "Deep dive —
same, plus watch 5 videos to extract their actual method". When you propose a deep dive,
say what it costs in plain terms so the choice is informed.

Once the user picks, don't ask again mid-run. If something ambiguous surfaces during
collection, note it and resolve it in the report rather than stopping.

## Step 2 — Collect

Both platforms have a bundled script that does the fetching. Use them. They exist because
this data is fiddly to gather correctly — Telegram's HTML bleeds reaction bars into post
text, and YouTube rate-limits and lies about it with a bot-detection error — and those
fixes are already solved inside the scripts. Rewriting the scraping inline reintroduces
bugs that are invisible in the output.

Work in the session scratchpad, not the user's project directory. Raw data files are
intermediate artifacts; the report is the deliverable.

The exact invocations are in the reference files.

## Step 3 — Report as a published Artifact

The deliverable is a **published Artifact page** — modern, minimal, well-designed. Not a
terminal dump, not a local markdown file. The user wants something they can actually read
and send to someone.

**Load the `artifact-design` skill before writing the page.** Design quality is the point
here, and that skill calibrates it. If the report leans on charts (view distributions,
cadence over time, topic mix), load `dataviz` too before writing chart code.

What makes these reports good:

- **Lead with the answer.** Open with the 3–5 findings that actually matter, not with
  methodology or a wall of counts. If the user asked something specific, the top of the
  page answers that specific thing.
- **Numbers need interpretation.** "Median 78K views" is a fact; "median views jumped
  2.5x after they pivoted from n8n to Claude Code" is a finding. Always reach for the
  second. Cite the number, then say what it means.
- **Quote the source.** Real post text, real video titles, real description snippets.
  Specifics are what make a report credible and useful.
- **Say what's uncertain.** Note the limits honestly — see the reference files for the
  known ones per platform. A report that hides its blind spots is worse than one that
  names them.
- **Explain jargon in a clause.** The user is newer to technical material and reads these
  to build a mental model, so unpack terms like "affiliate funnel", "UTM tag", or "n8n"
  inline rather than assuming them.

Give the page a real title (the channel's name, not "Channel Analysis Report"), and pass
a one-line `description`.

After publishing, give the user the link plus a short summary of the top findings in
chat — enough that they know what's in it without opening it.

## Watching videos (YouTube deep dives)

The `watch` skill is what turns a metadata report into a real analysis — it's the only
way to see what a creator actually *does* inside a video rather than what they titled it.
`references/youtube.md` covers when to reach for it, how to pick which videos, and how to
invoke it. Don't try to infer a channel's method from titles and descriptions alone when
the user asked for depth.

## Scaling and cost awareness

Metadata collection is cheap; watching videos is not. A full metadata pass on a
300-video channel takes a few minutes and modest tokens. Watching five videos costs
substantially more of both, because each pull includes frames and a transcript.

So: collect metadata for the whole channel by default, and be selective about what gets
watched. If the user asks to watch something like 20 videos, tell them the tradeoff and
suggest a smaller sample plus a wider metadata pass — usually that answers the question
just as well.

## Reusing prior work

If the user asks a follow-up about a channel already analyzed this session, reuse the
saved data files rather than re-scraping. The scripts cache per-video JSON, so re-running
is cheap, but re-reading a local file is free.
