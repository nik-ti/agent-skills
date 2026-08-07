---
name: langchain-skills
description: "INVOKE FIRST for any task building, debugging, or extending a LangChain, LangGraph, or Deep Agents project (Python or TypeScript) — including agents that call an OpenRouter-served or other non-Anthropic/OpenAI model through LangChain. Covers framework selection, quickstarts, create_agent/@tool patterns, custom graphs, persistence, human-in-the-loop, RAG, evals, and LangSmith."
---

This is a bundle of reference files, one directory deeper than skills normally sit, so the individual files inside don't register as their own invocable skills — read them directly with the Read tool instead of trying to invoke them by name.

1. **Read `AGENTS.md` in this same directory first.** It routes to the right file(s) for the task — framework choice (LangChain vs LangGraph vs Deep Agents), which quickstart to use for a new project, or which topic skill (persistence, human-in-the-loop, RAG, middleware, evals, LangSmith, etc.) applies.
2. **Read the specific `<name>/SKILL.md` file(s) it points to before writing any agent code.** They carry the current APIs and patterns — treat them as overriding anything from training data, since this ecosystem moves fast.
