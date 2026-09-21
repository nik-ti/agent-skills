# Gotchas: AI agents and LLM-powered features

Pull the 3-6 per section that matter. Also read the file for whatever the agent is wrapped in (bot, web app, script). Write each into SPEC.md as "we handle X by doing Y".

## Cost and limits
- Cost per call × expected volume, estimated in dollars per day. Metered model APIs surprise people at scale; a loop that retries can multiply it.
- Rate limits and latency of the model provider; a retry/backoff plan and ideally a fallback model.
- Context window limits: what happens when input (a long document, a big inbox) exceeds it? Chunk, summarize, or truncate — decide.
- Cap the number of steps or tool calls an agent can take in one run so a confused agent can't loop forever and burn money.

## Correctness
- Hallucination on anything factual: ground answers in retrieved data, quote sources, or flag uncertainty. Never present a guess as a fact silently.
- Non-determinism: the same input can give different output. Anything downstream that assumes stability (dedupe, exact-match parsing) will break. Ask for structured output (JSON schema / tool calls) rather than parsing free text.
- Validate model output before acting on it — missing fields, wrong types, empty results.
- Evaluate on a handful of real examples before shipping, and keep those examples as a regression test.

## Safety of actions
- Prompt injection: if the agent reads untrusted content (web pages, emails, uploaded files, chat messages) before taking actions, that content can contain instructions. Treat it as data, separate it from instructions, and limit what tools it can trigger.
- Confirm before irreversible actions: sending, deleting, paying, posting publicly. A dry-run mode is cheap insurance.
- Least privilege: give the agent only the tools and scopes it needs (read-only where possible).
- Log every tool call with its inputs so the user can audit what the agent did.

## Model and framework choices
- Use the current model generation; check the provider's docs for model IDs rather than relying on memory — they change. Pick the cheapest model that passes the eval, not the biggest.
- Don't hand-roll an agent loop if a maintained framework fits (see the langchain-skills or claude-api skill if available). Do hand-roll if the framework is heavier than the problem.
- Prompt caching for repeated large contexts; batch APIs for bulk offline jobs — both cut cost significantly.
- Keep prompts in their own files, not buried in code, so they can be read and edited without touching logic.

## User experience
- Streaming or progress feedback for anything that takes more than a couple of seconds.
- A clear "I don't know / couldn't do it" path rather than a confident wrong answer.
- Show what the agent did (sources used, actions taken), not just the final answer.
