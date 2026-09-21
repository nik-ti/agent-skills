# SPEC.md template

Copy the skeleton below into `SPEC.md` at the project root and fill it in. This file is the project's memory: a fresh agent in a new session reads it once and continues without re-interviewing anyone. That only works if it stays short.

## Rules for keeping it useful

- **Concise over complete.** Aim for under ~150 lines total. If it grows past that, compress — merge bullets, delete anything the code now explains on its own.
- **Status is "where we are", not a changelog.** Don't log every step. Record what's built, what changed from the plan and why, and what the next session needs to know. Replace stale lines instead of appending to them.
- **Every FAILURE line must be checkable.** If you can't say how you'd verify it, rewrite it or mark it `UNVERIFIABLE` with a manual check the user can do.
- **Record the exact commands** to run the project and the tests. A new agent shouldn't have to rediscover them.
- **Plain language.** The user reads this too. Name the real-world consequence of a tradeoff, not just its technical name.
- **Never put secrets in it.** Reference `.env` variable names, not values.

## Skeleton

```markdown
# <Project name>

## What we're building
<1-2 sentences: what it does, who uses it, where it runs.>

## Contract

GOAL: <Success as an observable outcome, with a number where possible.>

CONSTRAINTS:
- <Hard limit — stack, budget, scope, compatibility>
- <...>

FORMAT:
- <Exact output shape — files, structure, where it runs, what's included>
- <...>

FAILURE (any of these = not done):
- <Concrete, checkable condition>
- <...>

## Built on top of
- <library / framework / repo> — <what it saves us from building; maintenance status; license>
- <...>

## Gotchas we're handling
- <We handle X by doing Y.>
- <...>

## Build sequence
1. <Phase 1 — something runnable/testable early>
2. <Phase 2>
3. <...>

## How to run and test
- Run: `<command>`
- Tests: `<command>`
- Setup notes: <env vars needed (names only), accounts, one-time steps>

## Status
_Updated: <YYYY-MM-DD>_
- Built: <what works right now>
- Changed from plan: <decision + why>, or "nothing yet"
- Next: <the next phase or open item>
- Watch out for: <anything surprising a new session must know>
```
