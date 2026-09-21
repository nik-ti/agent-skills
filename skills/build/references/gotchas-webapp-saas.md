# Gotchas: web apps and SaaS (backend, accounts, database, payments, deployment)

Pull the 3-6 per section that matter. Also read `gotchas-website.md` for the frontend half. Write each into SPEC.md as "we handle X by doing Y".

## Hard to change later — decide deliberately
- Database choice is decided by concurrency, not preference: single user or a few → SQLite is fine; many people writing at once → Postgres/MySQL. Say which and why.
- Data model: think through what gets deleted and what happens to related records (cascade vs. orphans). Enforce uniqueness and foreign keys at the database level, not just in app code.
- Migrations: have a real way to change the schema later (a migration tool), or accept that a schema change means a rewrite.
- Store timestamps in UTC; convert for display.
- Auth approach: rolling your own is the classic mistake. Use a maintained library or a hosted provider (Clerk, Auth0, Supabase Auth, NextAuth, etc.).

## Auth and security
- Secrets never in git: `.env` + confirm `.gitignore` actually excludes it. Reference variable names in SPEC.md, never values.
- Passwords hashed with a proper algorithm (bcrypt/argon2) — never plaintext, never reversible.
- Authorization checked on every request: being logged in doesn't mean allowed to see or edit *this* record.
- Rate limit or lock out auth endpoints to blunt brute force.
- HTTPS everywhere; cookies `secure` and `httpOnly`.
- Third-party OAuth tokens expire — handle refresh, because silent failure here is a classic.
- Session expiry mid-use: does the user lose unsaved work?

## Backend and API
- Idempotency for anything that creates or charges — retries and double-calls happen.
- Input validation and sanitization at the boundary, not deep in business logic.
- Pagination and rate limiting on anything returning lists.
- Timeouts and retries with backoff on every outbound call — one hung dependency shouldn't hang everything.
- Consistent error shape so the frontend can actually handle failures; 400 for bad input, not 500.
- API versioning only if there will be external consumers.

## Payments (if any)
- Use Stripe (or equivalent) Checkout/hosted pages; don't touch card numbers yourself.
- Webhooks can be delayed, duplicated, or missed — make handlers idempotent and reconcile rather than trusting them blindly.
- Test mode vs. live mode keys are different; make it impossible to mix them up.
- What happens on failed renewal, refund, chargeback, and plan downgrade — decide now.

## Deployment and operations
- Environment parity: "works on my machine" must match the deploy target. Prefer a platform (Vercel, Railway, Fly, Render) over a hand-managed server unless there's a reason.
- Logging/observability: when it breaks in production, can anyone see what happened? At minimum, structured logs and an error tracker (Sentry has a free tier).
- Backups: where, how often, and has a restore ever been tested?
- Rollback plan if a deploy breaks things.
- Cost at realistic usage — hosted DB, serverless, LLM APIs, and email providers all scale in price. Estimate it.
- Cold starts if serverless.

## General UX
- Undo or confirmation for anything destructive.
- Error messages with a next step — "something went wrong" is a dead end.
- Onboarding: does first use require something the user doesn't have yet (an API key, a connected account)? Plan that flow.
- Email deliverability: transactional emails from a new domain land in spam without SPF/DKIM. Use a provider (Resend, Postmark, SES) and set up the DNS records.

## Mobile apps (if the SaaS has one)
- Offline / poor connectivity behavior.
- App store review requirements add real time to the plan.
- Push notification permission flow and what happens when denied.
- Background execution limits on iOS/Android.
