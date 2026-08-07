# Checklist by Category

Pull the 3-6 items per relevant category that actually matter for the specific project — don't dump the whole list into the plan. Categories are not mutually exclusive; most projects touch 3-5 of these.

## Web apps / frontend
- Loading, empty, and error states designed for every screen — not just the "happy path with data" state
- Form validation on both client and server (client-side alone can be bypassed)
- What happens on slow/flaky network — does the UI hang, show stale data, or give feedback?
- Browser back/refresh behavior — does state survive a refresh where it should?
- Mobile/responsive behavior if there's any chance this is viewed on a phone
- Session/auth expiry mid-use — does the user lose unsaved work?
- Double-submit protection on forms/buttons (double-click, double-tap)

## Backend / API design
- Idempotency for anything that creates or charges — retries and double-calls happen
- Rate limiting and pagination on any endpoint that returns lists
- Input validation and sanitization at the boundary, not just deep in business logic
- Timeouts and retries with backoff for any outbound call — a hung dependency shouldn't hang everything
- Versioning strategy if this API will have external consumers
- Consistent error response shape so clients can actually handle failures

## Databases / data model
- What's the actual concurrency need — single user, a few, or many at once? This decides SQLite vs. Postgres/MySQL, not preference
- Migrations: is there a real plan for changing the schema later, or will this require a rewrite?
- Backups — where do they live, how often, has restore ever been tested?
- Uniqueness/foreign key constraints enforced at the DB level, not just in application code
- What happens to related data when something is deleted (cascade vs. orphaned records)
- Timezones stored consistently (store UTC, convert for display)

## Auth & security
- Secrets/API keys never in source control — env vars or a secrets manager, and confirm .gitignore actually excludes them
- Password/token storage uses proper hashing, never plaintext or reversible encryption for passwords
- Authorization checked per-request (a logged-in user isn't automatically allowed to see/edit everything)
- Rate limiting or lockout on auth endpoints to blunt brute-force attempts
- HTTPS everywhere it matters; cookies marked secure/httpOnly where applicable
- Third-party OAuth token refresh handled — tokens expire, and silent failure here is a classic gotcha

## AI agents / LLM-powered features
- Hallucination risk on anything factual — does the system have a way to ground answers or flag uncertainty?
- Cost per call at expected usage volume — metered LLM APIs can surprise you at scale
- Rate limits and latency of the underlying model provider, and a fallback/retry plan
- Prompt injection risk if the agent reads untrusted content (web pages, emails, user-uploaded files) before taking actions
- Tool-use safety: does the agent confirm before irreversible actions (sending, deleting, spending)?
- Context window limits — what happens when input exceeds it?
- Non-determinism: same input can give different output — does anything downstream assume determinism that isn't there?

## Automations / bots / scheduled jobs
- Overlapping runs — does a job that takes longer than its interval double up, and is there a lock to prevent that?
- What happens if the job fails halfway — is it safely re-runnable, or does it leave things half-done?
- Alerting on silent failure — a cron job that stops running with no notification can fail for weeks unnoticed
- Timezone handling for schedules (server time vs. user's local time)
- API/service outages on the far end — does the automation retry, skip, or crash the whole pipeline?

## Third-party integrations / external APIs
- Rate limits and what happens when they're hit (backoff, queue, fail loud)
- Pricing at realistic usage — free tier limits are a common surprise in production
- Webhook reliability — webhooks can be delayed, duplicated, or missed; don't treat them as guaranteed
- What happens if the third-party service changes its API or goes down entirely — is there a fallback or does everything stop?
- Terms of service limits (some APIs prohibit certain uses, e.g. bulk scraping, resale of data)

## Deployment / infrastructure
- Environment parity — does "works on my machine" actually reflect the deploy target?
- Logging/observability — when something breaks in production, is there any way to see what happened?
- Rollback plan if a deploy breaks something
- Cost at realistic scale, not just at zero usage (serverless, hosted DB, LLM APIs can all scale in cost unexpectedly)
- Cold start behavior if using serverless functions

## General UX
- What the very first use looks like with zero data/history — is it a helpful empty state or a confusing blank screen?
- Feedback for every action that takes more than ~1 second (spinners, progress, disabled states)
- Undo or confirmation for anything destructive
- Accessible error messages — "something went wrong" without any next step frustrates users
- Does the happy-path demo hide a step that will be awkward for a first-time real user (e.g. requires an API key they don't have yet)?

## Mobile apps specifically
- Offline/poor connectivity behavior
- App store review requirements if this will be distributed (can add real time to the plan)
- Push notification permission flow and what happens if denied
- Battery/background execution limits on iOS/Android for anything expected to run in the background