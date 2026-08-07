---
name: project-preflight
description: >
  Use this BEFORE writing any code whenever the user asks to build, create, or make an app, website, script, automation, bot, or AI agent from scratch — even if they phrase it casually like "make me a tool that..." or "I want an agent that...". Also use when starting a significant new feature on an existing project. Do NOT skip this because the request sounds simple — the user is non-technical and relies on this skill to surface research and edge cases they wouldn't know to ask for. This skill forces two things before any implementation, first researching existing libraries, frameworks, APIs, and open-source projects that already solve part or all of the problem so nothing is rebuilt from scratch unnecessarily, and second a full-stack plus UX gotcha pass covering edge cases, failure modes, security, and rough edges. Skip this skill only if the user explicitly says to skip planning and just write code.
---

# Project Preflight

Most coding agents jump straight to writing code. That's the failure mode this skill exists to stop. The user is not a developer — they cannot tell you upfront about auth edge cases, rate limits, race conditions, or empty-state UX, because they've never hit them. That means the burden is on you, before you write a single line of code, to think like a senior engineer AND a product designer AND a researcher who already spent an hour looking for prior art.

Do this every time this skill triggers, in order. Don't shortcut it because the request "sounds simple" — simple requests are exactly where undiscovered gotchas cause the most pain later, because nobody was looking for them.

## Step 1: Pin down what's actually being built

Before researching or planning, make sure you can state in one or two sentences: what the thing does, who uses it, and where it runs (local script, web app, mobile, backend service, Telegram/Discord bot, browser extension, AI agent with tool access, etc.). If this isn't clear from the request, ask — briefly, in plain language, no jargon. Don't ask more than 2-3 questions; infer sensible defaults for the rest and state your assumptions instead of interrogating the user.

## Step 2: Research prior art (don't skip this even if you're confident)

The goal is to find anything that already solves part of the problem, so the build is "assemble and adapt" instead of "invent from zero." Search before you plan the architecture, not after.

Search for, in this order:
1. **Purpose-built libraries/SDKs** for the core task (e.g. an official API client, a parsing library, an auth library) — using a maintained library beats hand-rolling the same logic.
2. **Frameworks or boilerplates** that already scaffold this category of project (e.g. a Next.js SaaS starter, a Telegram bot framework, a LangChain/agent framework, a CLI tool template).
3. **Full open-source projects** doing something close to the whole thing — even if not a perfect fit, they reveal what the actual hard parts turned out to be for people who already built this.
4. **Known gotchas for the specific APIs/services involved** — search things like "[service name] API rate limit gotchas", "[library] common issues", "[service] webhook reliability". This is where you catch the stuff that isn't in the docs.

For each promising find, note: what it gives you, its maintenance status (recent commits/releases — don't recommend something abandoned), license, and the tradeoff of using it vs. building that piece yourself. Bias toward using well-maintained existing tools for anything not core to what makes this project unique — reinvent only the part that's actually the point of the project.

If research turns up a project or library that changes the recommended approach, say so plainly in the plan — this is often the most valuable thing you find.

## Step 3: Full-stack + UX gotcha pass

Read `references/checklist.md` and go through the categories relevant to what's being built (not every category applies to every project — a CLI script doesn't need an auth section, an AI agent doesn't need a payments section). For each relevant category, pull out the 3-6 items that actually matter for this specific project. The point isn't to produce a generic checklist — it's to catch the handful of things that would otherwise only surface after the user hits them in production.

Think specifically about:
- **The unhappy paths**: what happens when the network fails, an API returns an error, a user submits garbage input, two things happen at once, the service is rate-limited, a scheduled job overlaps with the previous run, an external dependency is down.
- **The first-run and empty-state experience**: what does this look like before there's any data, on the very first use, when something is loading, when a list is empty.
- **The boring-but-critical stuff**: where secrets/API keys live and how they're kept out of git, what gets logged, what happens on restart/redeploy, what the cost profile looks like if a third-party API is metered.
- **Anything that's genuinely hard to change later**: data model choices, choice of database, auth approach, anything with lock-in. Flag these explicitly since a wrong early call here is expensive to unwind.

## Step 4: Write the plan (before touching code)

Produce a short plan and share it with the user before implementing. Structure:

```markdown
## What we're building
[1-2 sentences]

## Recommended approach
[Chosen stack/libraries, and WHY — including anything found in research that changes the approach]

## Built on top of
[Existing libraries/frameworks/repos being used or adapted, with a one-line note on what each saves us from building]

## Edge cases & gotchas this plan accounts for
[The specific, non-generic list from Step 3 — framed as "we're handling X by doing Y", not just a bare list of risks]

## Open questions for you
[Anything genuinely ambiguous, translated into plain-language tradeoffs, not technical jargon. E.g. instead of "REST vs GraphQL?", ask "do you need this to update in real time, or is refreshing on load fine?"]

## Build sequence
[Ordered phases — what gets built first so there's something testable early, rather than one big-bang implementation]
```

Keep this readable by someone non-technical: name the tradeoff and its real-world consequence, not just the technical term for it. E.g. "using SQLite instead of Postgres means this won't handle multiple people writing at the same time — fine for a personal tool, a problem if this grows into something with real concurrent users."

## Step 5: Confirm, then build

Wait for a quick go-ahead or corrections on the plan before writing code, unless the user has clearly signaled "just build it, don't ask." If they push back on a recommendation, take it seriously — but if you think the pushback will cause a problem down the line, say so once, plainly, and let them decide.

Once confirmed, build in the phases laid out in the plan rather than everything at once — this surfaces problems while they're still cheap to fix.

## When to abbreviate this process

For genuinely trivial asks (a 10-line script, a one-off data transform, a throwaway prototype explicitly described as such), do a fast, compressed version: a quick mental research check and a one-line list of the 1-2 gotchas that actually matter, rather than the full plan document. Use judgment — but default to the full process when in doubt, since the cost of skipping it is exactly the "worked until production" failure mode this skill exists to prevent.