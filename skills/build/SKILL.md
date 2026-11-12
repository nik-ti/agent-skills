---
name: build
description: >
  Start here before any build, change, fix, refactor, or improvement, including websites and landing pages. Apply references/principles.md throughout every iteration and maintain a concise project-root changelog.md for all work. Websites and frontend do not require SPEC.md; route them to one appropriate design skill. For backend and other non-frontend work, ask thoughtful gap-driven questions, research existing solutions, define a product agreement in SPEC.md with specific success and failure criteria, then test and build in phases. For mixed projects, apply that protocol only to the non-frontend portion. Keep plans and progress outside SPEC.md. If the user asks to skip planning, still apply the shared principles, changelog, and scope routing.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task, Agent, WebSearch, WebFetch, AskUserQuestion
---

# Build

This skill establishes the engineering foundation for every change, then routes the work by scope. Its detailed build protocol applies only to backend and other non-frontend work.

## First: Read and apply the principles — every time

Before planning or making any change, read [references/principles.md](references/principles.md). These are the foundation for every build, fix, improvement, and refactor, including frontend work, websites, and landing pages. Do not skip them because the task is small or the project already exists.

Keep these principles active throughout the work: revisit them before each iteration or phase, when changing approach, and before delivery. Apply the relevant principles within the task's scope and authorization; do not treat them as a one-time preflight checklist. Reading them does not require a SPEC.md for frontend work.

## Use simple, clear names — all work, including frontend

Always use simple, clear, descriptive names for files, folders, functions, parameters, and variables. Nikita should be able to understand their purpose by reading their names. Prefer familiar business words over cryptic abbreviations, vague labels, or clever shorthand: for example, `calculateTotal`, `customerName`, and `isPaid`. Follow the language's naming conventions and preserve required framework/API names. Apply this throughout every iteration, including inside files, and check naming clarity before delivery.

## Keep documents separate — all work, including frontend

- **`SPEC.md` is only the product agreement:** intended users, scope, required behavior, business rules, hard constraints, and observable success/failure criteria. Unresolved product decisions must be clearly marked as unapproved. Do not put architecture research, build sequences, setup commands, progress, test results, or session history in it. Only change an agreed requirement when the user authorizes that change; never rewrite it to match an implementation defect.
- **`README.md` explains the project:** where things live, setup/run/test commands, and current technical choices. Update it after significant changes if it exists. Put detailed design or research in an existing appropriate document when needed; do not create paperwork for its own sake. Keep implementation tasks in the session plan or existing task tracker.
- **`changelog.md` is required at the project root for every project changed**, including websites, landing pages, frontend-only fixes, and backend work. Use this exact lowercase filename. Create it if missing and keep it current as meaningful work is completed, including partial work at handoff. Read the latest relevant entry when resuming.

Keep each changelog entry concise: date and scope, what changed and why, verification actually performed (command/environment or browser evidence), and any material limitation or next action. Distinguish implemented, verified, deployed, and enabled for customers; claim only what was checked. Use a few bullets per meaningful change, newest first. Do not log every tool call, repeat the whole spec, include transcripts, or expose secrets/customer data. If checks were not run, say so. Existing history in another changelog stays intact; avoid duplicating it when introducing `changelog.md`.

Example entry:

```markdown
## YYYY-MM-DD — Short change description
- Changed: <observable change and why>.
- Verified: <checks actually run, environment, result/evidence>.
- Remaining: <material limitation or next action, only if needed>.
```

## Next: Route frontend and non-frontend work

**The numbered build protocol below is only for backend and other non-frontend work.** Frontend work follows the shared principles, documentation/changelog requirements above, and one frontend design skill.

For frontend work, choose **one** skill for the task and follow its workflow. Honor the user's named skill first; otherwise select by scope:

| Frontend task | Skill |
|---|---|
| New website, landing page, or new page needing a complete design direction | [hallmark](../hallmark/SKILL.md) |
| UI/UX design system, palette and typography selection, or UX guidance across platforms and frameworks | [ui-ux-pro-max](../ui-ux-pro-max/README.md) |
| Changes to an existing design, general UI work, or a focused visual improvement | [frontend-design](../frontend-design/SKILL.md) |

Do not combine these design skills or stack their visual rules; they contain conflicting requirements. Use Hallmark on an existing design only when the user explicitly requests it. Preserve the project's established design system when making focused changes.

**Frontend-only work stops here after applying the shared requirements.** Do not create or require `SPEC.md`, run the backend interview, or impose the backend tests-first protocol on a website, landing page, or UI-only change. Use the selected frontend skill's planning and validation, verify the result in a real browser with desktop and mobile screenshots, inspect those screenshots, and record the change and verification in `changelog.md`. The shared principles still apply on every iteration.

For a project with both frontend and backend work, route the UI to one frontend skill and apply the protocol below only to the backend portion. A backend `SPEC.md` may document the interfaces the UI depends on; it does not turn UI work into a backend workflow. A page that only uses an existing API remains frontend work unless backend changes are also needed.

## Backend and non-frontend build protocol

The user is not a developer. They can't tell you upfront about rate limits, race conditions, or that a library already does 80% of the job — they've never hit those things. So the burden is on you, before writing a line of backend code, to interview them like a product manager, research like someone who already spent an hour on GitHub, and think like the engineer they don't have.

Four failure modes this skill exists to prevent:

- **Success undefined** → the agent over-engineers, or declares the first thing that runs "done".
- **Failure undefined** → the agent silently cuts corners it would never cut if the corner were named.
- **Tests written after the code** → they get shaped to pass against the code that exists, not against what the user needs.
- **Rebuilding what exists** → most features already exist as free, maintained libraries and repos. New ones are published daily. Search first.

The agreed product behavior lives in `SPEC.md` at the project root. A fresh agent uses it to understand the agreement, the README to run/check the project, and `changelog.md` plus the current code to understand progress. Keep these responsibilities separate.

## Step 0: Is there already a SPEC.md?

After reading the principles and routing the work, look for `SPEC.md` in the project root. If it exists, read the agreement, README, latest relevant `changelog.md` entries, and the code/tests for the requested work. Reuse answered questions and valid research; ask only about new scope, missing decisions, ambiguity, or changed constraints. Do not assume the existence of a spec means every new requirement is settled.

If the implementation contradicts an approved requirement, report the mismatch and fix the implementation within scope; do not silently change the agreement. If an older spec mixes requirements with progress/design notes, preserve its product rules and move the relevant non-product material to the appropriate documents when working on that area. Do not restructure unrelated projects.

If there's no SPEC.md, continue.

## Step 1: Interview the user

Goal: understand the important workflows well enough to write multiple specific **SUCCESS** and **FAILURE** criteria. One broad GOAL and a few generic failure bullets are not enough for a substantial feature.

Before asking anything, read the request, relevant conversation, existing agreement, README, and available code/examples. Separate what is already known from what needs the user's judgment. Every question must resolve a meaningful gap that could change behavior, scope, cost, permissions, or acceptance. Do not ask obvious questions, repeat answered ones, ask the user to discover technical facts you can inspect, or invent questions to fill a quota. Make routine implementation decisions yourself and explain material tradeoffs.

Use an available question tool in small focused batches, respecting its limits; otherwise ask in chat. Use plain language, concrete examples, and sensible options with consequences. For a substantial build, explore the relevant areas below as deeply as needed to settle the important decisions:

1. **Users and the real workflow.** Who does each step, what triggers it, what must happen next, and when is the work complete?
2. **Inputs and outputs.** Concrete sample inputs, required fields, formats, destinations, and the exact result the user expects.
3. **Business rules and boundaries.** Thresholds, calculations, exceptions, conflicting inputs, and what happens at the boundary or when a value is unknown.
4. **Success examples.** Walk through normal and important alternative scenarios; agree on the expected result for each.
5. **Unacceptable outcomes.** Ask what would make each workflow fail even if the code runs: wrong result, missing data, duplicate action, silent failure, or excessive manual work.
6. **Failure and recovery.** Invalid/empty input, unavailable dependencies, interrupted runs, retries, and what the user sees or can do next.
7. **Access and external actions.** Who may see/change what; which actions need review; what must never be sent, deleted, charged, or exposed automatically.
8. **Timing, volume, and cost.** Realistic usage, deadlines for results, tolerable delays, operating limits, and budgets when relevant.
9. **Compatibility and non-negotiables.** Existing workflows/data that must keep working, accounts/tools already chosen, and hard constraints.
10. **Scope and unresolved choices.** What is included now, excluded, or still requires a product decision.

Treat this as a thinking guide, not a questionnaire to recite. Ask more useful questions when uncertainty remains; stop when the important scenarios and decisions are clear, regardless of the number of rounds. For vague answers, offer concrete interpretations and examples. Record low-impact assumptions explicitly; do not present an unconfirmed business rule, permission, destructive action, or spending limit as agreed. Continue independent work while awaiting decisions that block only part of the task.

If the user provides a detailed contract, validate it using Step 4 and ask only about meaningful gaps. Existing answers should reduce the interview, not prevent follow-up on missing cases.

## Step 2: Research prior art — in parallel, and for the whole build

Start this right after the interview and let it run while you do Step 3. If you can spawn a subagent (`Task`/`Agent`), give the research to one so it doesn't block you; otherwise do it inline before planning.

The premise: for almost any feature you're about to write, someone already published a free library, framework, template, model, or full project that does it. Finding it turns "invent from zero" into "assemble and adapt", and avoids building on something abandoned or outdated. Search in this order:

1. **Purpose-built libraries / SDKs** for the core task (official API clients, parsers, auth libraries, scheduling libs).
2. **Frameworks or boilerplates** for this category of project (SaaS starter, bot framework, agent framework, CLI template, site generator).
3. **Full open-source projects** doing something close to the whole thing. Even an imperfect match shows what the hard parts turned out to be.
4. **Known gotchas for the specific APIs and services involved** — search "[service] API rate limit", "[library] common issues", "[service] webhook reliability". This is where the not-in-the-docs problems live.

For each promising find record: what it saves you from building, maintenance status (last commit / release — don't recommend anything abandoned), license, and the use-vs-build tradeoff. Keep technical findings in the README or an appropriate design/research note, outside `SPEC.md`. Bias hard toward using well-maintained existing tools for anything that isn't the unique point of this project. If research changes the recommended approach, say so plainly — that's often the most valuable output of the whole step.

**This rule stays on for the entire backend build, not just planning.** Whenever a new sub-problem appears mid-implementation (parsing a format, retry logic, an API integration, a scraping target), spend a minute searching before hand-rolling it. Record adopted tools in the README or existing technical notes, and summarize material changes in `changelog.md`.

## Step 3: Backend and non-frontend gotcha pass

Now think like the senior engineer and product designer the user doesn't have. Read the one or two reference files that match the project — they're short and grouped by type:

| Project type | Read |
|---|---|
| Web app / SaaS backend, accounts, database, payments, deployment | `references/gotchas-webapp-saas.md` (backend concerns only; UI work follows the selected frontend skill) |
| Automation, scheduled job, scraper, bot, third-party integration | `references/gotchas-automation.md` |
| AI agent, LLM feature, anything calling a model | `references/gotchas-ai-agent.md` |
| Local script, CLI tool, one-off data transform | `references/gotchas-script-cli.md` |

Many projects are two types at once (an AI agent that's also a Telegram bot; a SaaS with an LLM feature). Read both.

From each file, pull the 3-6 items that actually matter for *this* project — not the whole list. Beyond the checklist, always think about:

- **Unhappy paths**: network fails, an API errors, the user types garbage, two things happen at once, rate limits hit, a job overlaps its previous run, a dependency is down.
- **First run and empty states**: before any data exists, on first use, while loading, when a list is empty, when an API key isn't set yet.
- **Boring but critical**: where secrets live and how they stay out of git, what gets logged, what happens on restart or redeploy, what a metered API costs at realistic usage.
- **Hard to change later**: data model, database choice, auth approach, anything with lock-in. Flag these explicitly.

Turn relevant risks into decisions. Put required user-visible behavior and limits in the product agreement; put the technical approach in the README or design notes. For example, "a retry must not create a second invoice" is a product requirement; the database mechanism enforcing it is an implementation choice. Ask about unresolved product tradeoffs instead of treating an agent assumption as approved.

## Step 4: Write SPEC.md and get a go-ahead

Copy the skeleton from `references/spec-template.md` into `SPEC.md` at the project root and fill it in. The heart of it is the contract:

- **GOAL** — what success looks like, with a number or an observable outcome. "Handles 50 leads/day" not "handles leads"; "user can filter by date and status" not "add filtering".
- **CONSTRAINTS** — only hard, non-negotiable limits: stack, budget, scope, compatibility.
- **FORMAT** — the required inputs, outputs, delivery surface, and externally observable structure. Internal folders/architecture belong in technical documentation unless explicitly required by the user.
- **SUCCESS** — multiple identifiable acceptance criteria (`S1`, `S2`, ...), covering each important workflow and its meaningful alternatives. State the actor/trigger, starting conditions or example input, expected result, and agreed threshold where relevant.
- **FAILURE** — identifiable rejection criteria (`F1`, `F2`, ...): concrete conditions that mean the result is unacceptable even if it runs. Cover relevant wrong results, boundary/unknown inputs, denied access, duplicate or partial actions, outages/recovery, and cost/timing limits. Each must describe an observable prohibited outcome and how it can be checked.

Increase coverage by finding distinct meaningful cases, not by restating the same rule. Avoid vague words such as "fast", "accurate", "secure", or "works correctly" without a scenario and observable expectation. Do not invent numerical promises; agree on material thresholds or mark them as unresolved. A useful criterion looks like: "Submitting the same request twice creates one record and returns the existing record on retry." A failure example: "A rejected request still creates a record or sends an email."

Before presenting it, check the agreement is **complete** (scope, GOAL, CONSTRAINTS, FORMAT, SUCCESS, and FAILURE), **consistent**, **testable**, and **scoped**. Every important workflow needs success coverage and relevant failure/edge cases. Each criterion needs a feasible automated or manual acceptance check; unresolved expectations must stay visibly unapproved and block only the affected work. A requirement that cannot yet be checked is not a pass. If criteria conflict, explain the concrete tradeoff and ask which outcome is intended.

Keep the agreement readable by someone non-technical: explain required behavior and the real-world consequence of a constraint. Preserve important rules when shortening it; move detailed product rules to linked feature agreements if needed rather than deleting acceptance coverage to meet an arbitrary line count.

Present SPEC.md and wait for a go-ahead or corrections before writing code, unless the user has clearly said "just build it". If they push back on a recommendation and you think it'll cause a problem later, say so once, plainly — then follow their call.

## Step 5: Write the tests before the code

Derive tests from the agreed SUCCESS and FAILURE criteria *now*, before adding or changing the application behavior. Writing them first helps avoid shaping expectations around the implementation, but tests can still encode a misunderstanding; check their expected answers against the agreed examples. Explain changes to expected business results and the user decision authorizing them.

- Cover the important features, not everything. A handful of tests that catch the FAILURE lines beats fifty that check nothing the user cares about.
- Make them runnable with one command, documented in the README or existing run guide. Refer to criterion IDs in meaningful tests/manual checks so coverage can be traced.
- Run new regression/behavior tests before changing that behavior; see the relevant test fail for the expected reason. Existing tests can already pass. If an honest automated test is impractical, define a concrete manual acceptance check instead of writing a meaningless test.

Do not implement new behavior until its meaningful tests or manual acceptance checks are defined. Passing tests never authorize silently weakening the agreement.

## Step 6: Build in phases, keep SPEC.md current

Keep the build sequence in the session plan or existing task tracker — something runnable early, then layered on, rather than one big-bang implementation. This surfaces problems while they're cheap.

After each meaningful phase: run the relevant checks and update `changelog.md` with the change, why, evidence/environment, and material remaining work. Update the README when setup, commands, or significant technical choices change. Update `SPEC.md` only when an agreed product requirement changes; keep it free of progress/status sections and verification history.

Keep the Step 2 research rule live throughout.

**Write code the user can navigate.** They're new to coding and will open these files to understand what's going on, so structure and naming matter more than usual:

- Folder structure and file names should say what things are. `nodes/fetch_news.py` and `send_telegram_alert.py`, not `utils2.py` and `handler.py`. Someone should be able to guess what a file does from its name and where it sits before opening it. Keep this intuitive without sacrificing efficiency — don't split things into ten files when three clear ones do the job.
- Every important file starts with a short note — two to four sentences — saying what the file does and how it fits in. Not a paragraph of backstory or design rationale; technical rationale belongs in the README or design notes. A codebase that's 40% prose is harder to read, not easier.
- Inside files, comment sparingly: explain the *why* of anything non-obvious, not the *what* of every line.

## Step 7: Verify against the contract, then deliver

Before calling anything done, walk the SUCCESS and FAILURE criteria with evidence, confirm the GOAL and constraints, run the relevant checks, and report it. Use `PASS`, `FAIL`, `NOT CHECKED`, or `BLOCKED` honestly; do not label unrun checks as passing:

```
Contract status: <ALL PASS / INCOMPLETE>

GOAL: {status and evidence}
CONSTRAINTS: {status and evidence}
FORMAT: {status and evidence}
SUCCESS criteria: {criterion IDs and evidence/results}
FAILURE criteria: {criterion IDs and evidence/results}
Checks: {command or manual flow, environment, actual results}
Remaining: {unverified/blocked items, if any}
```

If something failed and couldn't be resolved, say exactly which line, why, and the options — don't quietly relax the contract. "Any of these = not done" means what it says.

Finish the concise `changelog.md` entry. Keep implementation, verification, deployment, and customer enablement distinct. Do not add a Status section or delivery report to `SPEC.md`.

## Reference files

- [references/principles.md](references/principles.md) — mandatory foundation for every change and every iteration, frontend and backend alike.
- `references/spec-template.md` — the product-agreement-only skeleton and acceptance-criteria guidance.
- `references/gotchas-*.md` — backend and non-frontend checklists for Step 3 (see table above). `gotchas-website.md` is not part of this backend protocol.
