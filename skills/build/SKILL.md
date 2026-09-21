---
name: build
description: >
  The default workflow before building anything. Use this BEFORE writing any code whenever the user asks to build, create, make, set up, or ship an app, website, landing page, script, CLI tool, automation, scraper, bot (Telegram/Discord/Slack), AI agent, LLM feature, SaaS, or a significant new feature on an existing project — even when phrased casually ("make me a thing that...", "I want a bot for...", "can you set up..."). Do NOT skip this because the request sounds simple: the user is non-technical and relies on this skill to interview them, pin down concrete success/failure criteria, research existing libraries so nothing is rebuilt from scratch, write SPEC.md, and write tests before the code. Also use it when a project folder already contains a SPEC.md — read it and resume. Skip only if the user literally says to skip planning and just write code.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, Agent, WebSearch, WebFetch, AskUserQuestion
---

# Build

The user is not a developer. They can't tell you upfront about rate limits, empty states, race conditions, or that a library already does 80% of the job — they've never hit those things. So the burden is on you, before writing a line of code, to interview them like a product manager, research like someone who already spent an hour on GitHub, and think like the full-stack engineer they don't have.

Four failure modes this skill exists to prevent:

- **Success undefined** → the agent over-engineers, or declares the first thing that runs "done".
- **Failure undefined** → the agent silently cuts corners it would never cut if the corner were named.
- **Tests written after the code** → they get shaped to pass against the code that exists, not against what the user needs.
- **Rebuilding what exists** → most features already exist as free, maintained libraries and repos. New ones are published daily. Search first.

Everything discovered here lives in one file, `SPEC.md`, at the project root. It's the memory of the project: a fresh agent in a new session should read it once and be able to continue without re-interviewing anyone.

## Step 0: Is there already a SPEC.md?

Look for `SPEC.md` in the project root before anything else. If it exists, read it, then read its **Status** section twice. That's where you are. Skip the interview, skip the initial research, and pick up the build sequence from where Status says it stopped. If Status is stale or contradicts the code, fix Status first — a wrong map is worse than no map.

If there's no SPEC.md, continue.

## Step 1: Interview the user

Goal: leave this step able to write **GOAL** and **FAILURE** lines that are concrete enough to test. Not "it should work well" — that's a wish, not a criterion.

Use `AskUserQuestion` if it's available (batches of up to 4 questions, offer sensible options); otherwise ask in chat. Plain language, no jargon. Cover, in roughly this order:

1. **What it does, who uses it, where it runs.** One or two sentences you could repeat back. Local script, website, web app, phone, Telegram bot, background job, AI agent with tool access?
2. **What "done" looks like as observable behavior.** Ask for the moment they'd sit back and say "yes, this is it". Push until it's something you could watch happen: "a stranger fills the form on their phone and I get an email within a minute" — not "the form works".
3. **What would make them call it a failure even if it technically works.** This is the most important question and the one people skip. Slow? Ugly? Spams them with notifications? Misses items? Costs money per run? Needs babysitting? Get 3+ concrete lines.
4. **Non-negotiables.** Stack or tools they already pay for or know, accounts they already own, budget (especially for metered APIs), deadline, anything that must stay the same.
5. **What's explicitly out of scope.** Naming what you're *not* building prevents the plan from ballooning.

When an answer is vague, don't accept it — offer two or three concrete interpretations and let them pick. Two rounds of questions is usually enough; after that, state your assumptions explicitly and let them correct you rather than interrogating further.

If the user already hands you a contract or a detailed spec, don't re-interview — validate it (Step 4's checks) and ask only about gaps.

## Step 2: Research prior art — in parallel, and for the whole build

Start this right after the interview and let it run while you do Step 3. If you can spawn a subagent (`Task`/`Agent`), give the research to one so it doesn't block you; otherwise do it inline before planning.

The premise: for almost any feature you're about to write, someone already published a free library, framework, template, model, or full project that does it. Finding it turns "invent from zero" into "assemble and adapt", and avoids building on something abandoned or outdated. Search in this order:

1. **Purpose-built libraries / SDKs** for the core task (official API clients, parsers, auth libraries, scheduling libs).
2. **Frameworks or boilerplates** for this category of project (SaaS starter, bot framework, agent framework, CLI template, site generator).
3. **Full open-source projects** doing something close to the whole thing. Even an imperfect match shows what the hard parts turned out to be.
4. **Known gotchas for the specific APIs and services involved** — search "[service] API rate limit", "[library] common issues", "[service] webhook reliability". This is where the not-in-the-docs problems live.

For each promising find record: what it saves you from building, maintenance status (last commit / release — don't recommend anything abandoned), license, and the use-vs-build tradeoff. Bias hard toward using well-maintained existing tools for anything that isn't the unique point of this project. If research changes the recommended approach, say so plainly — that's often the most valuable output of the whole step.

**This rule stays on for the entire build, not just planning.** Whenever a new sub-problem appears mid-implementation (parsing a format, retry logic, a UI component, a scraping target), spend a minute searching before hand-rolling it. Note anything adopted in SPEC.md under *Built on top of*.

## Step 3: Full-stack gotcha pass

Now think like the senior engineer and product designer the user doesn't have. Read the one or two reference files that match the project — they're short and grouped by type:

| Project type | Read |
|---|---|
| Static site, landing page, marketing site, frontend-only | `references/gotchas-website.md` |
| Web app / SaaS with backend, accounts, database, payments, deployment | `references/gotchas-webapp-saas.md` |
| Automation, scheduled job, scraper, bot, third-party integration | `references/gotchas-automation.md` |
| AI agent, LLM feature, anything calling a model | `references/gotchas-ai-agent.md` |
| Local script, CLI tool, one-off data transform | `references/gotchas-script-cli.md` |

Many projects are two types at once (an AI agent that's also a Telegram bot; a SaaS with an LLM feature). Read both.

From each file, pull the 3-6 items that actually matter for *this* project — not the whole list. Beyond the checklist, always think about:

- **Unhappy paths**: network fails, an API errors, the user types garbage, two things happen at once, rate limits hit, a job overlaps its previous run, a dependency is down.
- **First run and empty states**: before any data exists, on first use, while loading, when a list is empty, when an API key isn't set yet.
- **Boring but critical**: where secrets live and how they stay out of git, what gets logged, what happens on restart or redeploy, what a metered API costs at realistic usage.
- **Hard to change later**: data model, database choice, auth approach, anything with lock-in. Flag these explicitly.

Write each as a decision, not a worry: "we handle X by doing Y". A bare list of risks isn't a plan.

## Step 4: Write SPEC.md and get a go-ahead

Copy the skeleton from `references/spec-template.md` into `SPEC.md` at the project root and fill it in. The heart of it is the contract:

- **GOAL** — what success looks like, with a number or an observable outcome. "Handles 50 leads/day" not "handles leads"; "user can filter by date and status" not "add filtering".
- **CONSTRAINTS** — only hard, non-negotiable limits: stack, budget, scope, compatibility.
- **FORMAT** — the exact shape of the output: files, structure, where it runs, what's included.
- **FAILURE** — the lines that mean "not done" even if it technically works. Missing edge case, silent error swallowing, performance miss, over-engineering, anything from the interview's failure question. Each line should be checkable.

Before presenting it, check the contract is **complete** (all four sections filled), **consistent** (constraints don't contradict the goal), **testable** (every FAILURE line can actually be verified), and **scoped** (the goal is reachable within the constraints). If a FAILURE line can't be verified, mark it `UNVERIFIABLE` and say how the user can check it manually. If a FAILURE line contradicts the GOAL, flag it and ask which wins.

Keep the whole file readable by someone non-technical: name the tradeoff and its real-world consequence ("SQLite means this breaks if several people write at once — fine for a personal tool, a problem if it grows"), not just the technical term.

Present SPEC.md and wait for a go-ahead or corrections before writing code, unless the user has clearly said "just build it". If they push back on a recommendation and you think it'll cause a problem later, say so once, plainly — then follow their call.

## Step 5: Write the tests before the code

Derive tests from the GOAL and FAILURE lines *now*, before any application code exists. This ordering is the point: a model writing tests after the code has the code in front of it and will, without meaning to, write tests that the existing code passes. Tests written first are an honest oracle — they test what the user asked for.

- Cover the important features, not everything. A handful of tests that catch the FAILURE lines beats fifty that check nothing the user cares about.
- Make them runnable with one command, and record that command in SPEC.md under *How to run and test*. If the user can't run them, they don't exist.
- Run them once before building. They should fail. A test that passes against nothing isn't testing anything.
- For UI-heavy projects where automated tests fit poorly, the "test" is a written manual checklist derived from the same FAILURE lines, walked through in a real browser at phone width before calling anything done.

Don't touch application code until the tests are written and failing.

## Step 6: Build in phases, keep SPEC.md current

Follow the build sequence from SPEC.md — something runnable early, then layered on, rather than one big-bang implementation. This surfaces problems while they're cheap.

After each phase: run the tests, then update SPEC.md's **Status** section. Concisely. Status answers "where are we and what changed" for a fresh agent — what's built and working, any decision that changed from the original plan and why, anything surprising the next session needs to know. It's not a changelog; when it grows, compress it. Aim to keep the whole SPEC.md under ~150 lines so it's cheap to inject into a new session.

Keep the Step 2 research rule live throughout.

**Write code the user can navigate.** They're new to coding and will open these files to understand what's going on, so structure and naming matter more than usual:

- Folder structure and file names should say what things are. `nodes/fetch_news.py` and `send_telegram_alert.py`, not `utils2.py` and `handler.py`. Someone should be able to guess what a file does from its name and where it sits before opening it. Keep this intuitive without sacrificing efficiency — don't split things into ten files when three clear ones do the job.
- Every important file starts with a short note — two to four sentences — saying what the file does and how it fits in. Not a paragraph of backstory or design rationale; that belongs in SPEC.md or a README. A codebase that's 40% prose is harder to read, not easier.
- Inside files, comment sparingly: explain the *why* of anything non-obvious, not the *what* of every line.

## Step 7: Verify against the contract, then deliver

Before calling anything done, walk every FAILURE line as a checklist with evidence, confirm the GOAL metric, run the tests, and report it:

```
Contract status: ALL PASS

GOAL: ✓ {evidence}
CONSTRAINTS: ✓
FORMAT: ✓
FAILURE lines: ✓ {n} of {n} verified — none triggered
Tests: ✓ {command} — {n} passing
```

If something failed and couldn't be resolved, say exactly which line, why, and the options — don't quietly relax the contract. "Any of these = not done" means what it says.

Then do a final Status update in SPEC.md.

## Reference files

- `references/spec-template.md` — the SPEC.md skeleton and rules for keeping it short.
- `references/gotchas-*.md` — per-project-type checklists for Step 3 (see table above).
