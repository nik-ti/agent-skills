# Gotchas: websites, landing pages, frontend-only

Pull the 3-6 that matter for this project. Write each into SPEC.md as "we handle X by doing Y".

## States nobody designs for
- Loading, empty, and error states for every screen — not just "happy path with data". A blank page while data loads reads as broken.
- Slow or flaky network: does the UI hang, show stale content, or give feedback?
- First visit with zero history: is it a helpful starting point or a confusing blank?
- Feedback for anything that takes over ~1 second (spinner, disabled button, progress).

## Forms and input
- Validate on the client for fast feedback AND on the server (or form backend) — client-only validation can be bypassed.
- Double-submit protection: double-click, double-tap, and impatient re-submits create duplicate leads.
- What the user sees after submitting: a clear success message with what happens next, and a clear error with a next step — never a silent nothing.
- Spam: a form with no protection gets bot submissions within days. Honeypot field, rate limit, or a service like Turnstile.
- Where submissions actually go (email, sheet, CRM) and what happens if that destination is down or the API key expires.

## Mobile and browsers
- Mobile first: if there's any chance it's viewed on a phone, it will be. Test at ~375px width in a real browser before calling it done.
- Tap targets big enough for thumbs; no hover-only interactions.
- Back button and refresh: does state survive where it should, and does the back button do what people expect?

## Performance and delivery
- Images: compress and size them — unoptimized photos are the #1 reason sites feel slow. Use modern formats (WebP/AVIF) with fallbacks.
- Fonts: limit to one or two families and weights; each extra one delays render.
- Hosting: static hosts (Vercel, Netlify, Cloudflare Pages, GitHub Pages) are free and handle HTTPS + CDN for you. Don't run a server for a static site.
- Custom domain and HTTPS wired up, not left as "later".

## Findability and trust
- Page title, meta description, Open Graph image (what shows when the link is shared in chat) — cheap and often forgotten.
- Contact info, privacy note if collecting personal data, and a 404 page that points back home.
- Analytics if the user wants to know if anyone visits (privacy-friendly options exist that need no cookie banner).

## Design
- Follow the frontend-design skill if available; avoid templated-default looks. Clean sans-serif fonts, no cursive/italic display fonts.
- Accessible contrast and readable font sizes — this is a real-user issue, not a nicety.
