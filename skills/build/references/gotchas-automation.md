# Gotchas: automations, scheduled jobs, scrapers, bots, integrations

Pull the 3-6 per section that matter. If it calls an LLM, also read `gotchas-ai-agent.md`. Write each into SPEC.md as "we handle X by doing Y".

## Running unattended
- Overlapping runs: if a job takes longer than its interval, does it double up? Use a lock or skip-if-running.
- Failing halfway: is the job safely re-runnable, or does it leave things half-done (some items sent, some not)? Prefer idempotent steps and a "processed" record.
- Silent death: a cron job that stops running with no notification can be dead for weeks. Alert on failure AND on "hasn't run when it should have" (a heartbeat). Telegram is a good cheap alert channel.
- Timezones: schedule in the user's zone explicitly; server time is usually UTC.
- Restarts and redeploys: state that lives in memory is gone. Persist what must survive (last-seen ID, cursor, dedupe set) to disk or a small DB.
- Where it runs: a laptop that sleeps is not a server. Decide — always-on machine, VPS, Railway/Fly, GitHub Actions cron, or a hosted scheduler.

## Third-party APIs and services
- Rate limits: know the number, back off when hit, and don't hammer on retry.
- Pricing at realistic volume: free tiers run out. Estimate calls per day.
- Webhooks are delayed, duplicated, or missed. Treat them as hints and dedupe by ID.
- Outages on the far end: retry with backoff, then skip or alert — don't crash the whole pipeline.
- API changes: pin versions; log clearly when a response doesn't match what's expected.
- Terms of service: some APIs forbid bulk scraping, resale, or automation. Check before building on them.

## Scrapers specifically
- Sites change their HTML without notice. Prefer an official API or RSS feed if one exists; if scraping, isolate selectors in one place and alert when they stop matching.
- Respect robots.txt and rate limits; identify yourself with a user agent; don't get the user's IP banned.
- Login walls, JavaScript-rendered pages, and bot detection change the approach entirely (headless browser vs. plain HTTP). Check early.
- Dedupe: the same item will show up again on the next run.

## Bots (Telegram / Discord / Slack)
- Use the platform's mature library (e.g. python-telegram-bot, discord.py) rather than raw HTTP.
- Polling vs. webhooks: polling is simpler for a personal bot; webhooks need a public HTTPS URL.
- Who is allowed to talk to it? A bot with no allowlist is a public bot.
- Messages fail: long messages get truncated, markdown breaks on special characters, rate limits apply per chat. Handle send errors instead of crashing.
- Errors go to the user (or the owner) as a message, not only to a log nobody reads.

## Secrets, logs, and structure
- API keys in `.env`, confirmed ignored by git; the bot token in particular is a full-access credential.
- Log enough to debug a failed run after the fact (what was fetched, what was skipped and why), but not secrets or full payloads.
- Follow the automation-building skill's node-style structure if available: one clear file per step, a README flow map, main orchestrator.
