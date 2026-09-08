# Telegram channel analysis

## How access works

Public Telegram channels expose a plain HTML web preview at **`t.me/s/<username>`** —
the `/s/` is what matters. No API key, no bot token, no phone number, no account.

- `t.me/<name>` → a small "Open in Telegram" splash page with no posts. Useless.
- `t.me/s/<name>` → the actual post feed. This is what the script reads.

Pagination works via `?before=<post_id>`, which walks backwards through history about
15–20 posts at a time. The script handles this loop.

If `t.me/s/<name>` returns no posts, the channel is private, doesn't exist, or has
disabled its web preview. The script exits with a clear error — report that to the user
plainly rather than trying workarounds. A private channel genuinely cannot be read this
way, and there is no fix short of the user's own Telegram account.

## Collect

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/telegram_scrape.py" "<t.me link or @handle>" \
  --limit 100 --out tg.json
```

Defaults to the last 100 posts, which is the standard profile depth. Raise `--limit` only
if the user wants a longer history; each extra ~18 posts is one more request with a 1s
pause, so 500 posts takes roughly half a minute.

The script prints the channel metadata and a computed `stats` block to stdout, and writes
everything (including full post objects) to the `--out` file. **Read the stats block from
stdout first** — it already contains the aggregates, so don't recompute them. Then read
individual posts from the JSON when you need actual text to quote or to judge tone.

## What comes back

Channel level: `title`, `username`, `description`, `subscribers`, plus lifetime `photos`,
`videos`, and `links` counts.

Per post: `id`, `url`, `date` (ISO/UTC), `views`, `text`, `chars`, `has_photo`,
`has_video`, `is_forwarded`, `reactions` (emoji → count), `reactions_total`,
`external_links`, `emojis`.

Precomputed stats: `posts_per_day`, `median_views`, `median_chars`, media percentages,
`top_link_domains`, `hour_histogram_utc`, `top_emojis`, `median_emojis_per_post`,
`top_reactions`, `median_reactions`.

## The standard profile

Unless the user asked for something narrower, answer all of these. This set exists
because it's what actually characterizes a channel:

1. **Identity** — name, @username, subscriber count, description (translate it if it's
   not in English), and what the channel claims to be about.
2. **Cadence** — posts per day, and the daily rhythm from `hour_histogram_utc`. A tight
   spread suggests scheduling or a team; a wide erratic one suggests a single person
   posting live. Note which timezone the peak hours imply.
3. **Content type** — what they actually post about. Read the post texts and group them
   into themes with rough proportions. Resist the channel's self-description; go by what
   the posts show. A "crypto" channel that posts 50% politics and memes is a different
   product than its name implies.
4. **Language and tone** — what language, and *how* they write: formal or slangy, hype or
   analytical, first-person or wire-service neutral. Quote a representative line.
5. **Media** — the photo/video/text-only split, and how media is used (screenshots?
   memes? charts? short clips?).
6. **Emoji use** — `top_emojis` and `median_emojis_per_post`. Look for structural use —
   many channels open every post with a single topic emoji as a visual bullet, which is a
   formatting convention rather than decoration. Say which pattern it is.
7. **What they promote** — `top_link_domains` and `posts_with_external_links`. Separate
   their own properties (their other channels, a shop, a bot) from third-party links and
   affiliate/referral links. Note any contact-for-advertising handle in the description.
   If they promote almost nothing, say so — that's a finding too.
8. **Engagement** — median views against subscriber count, and median reactions. The
   reaction mix is a tone signal in itself: heavy 🤡 or 🤬 means an audience that argues
   with the channel, heavy 🔥/👍 means one that agrees with it.
9. **Anything else notable** — forwarded-post share (a high number means they aggregate
   rather than write), post length consistency, recurring formats or series, signs of
   automation.

## Interpreting engagement honestly

Compare `median_views` to the subscriber count. Healthy Telegram channels typically land
around 20–40% of subscribers per post. Substantially below ~15% suggests inflated
subscriber numbers or a large dormant audience — worth flagging, especially if the user
is evaluating the channel commercially or as a signal source. Don't state this as fraud;
state the ratio and what it commonly indicates.

Views accumulate over time, so the newest posts in the sample are always understated
relative to older ones. Use the median rather than the most recent post's number.

## Known limits — state these in the report

- **No comment threads or discussion-group replies.** The web preview doesn't expose
  them. Reading those requires a real Telegram API session (`telethon` + a phone number).
- **No forward counts** — you can see *that* a post is forwarded, not how many times a
  post was forwarded onward.
- **View counts are abbreviated** by Telegram itself ("1.59K"), so they're rounded, not
  exact. The script expands them to integers for math, but the precision isn't real.
- **Only public channels.** Private ones are inaccessible by this route.
