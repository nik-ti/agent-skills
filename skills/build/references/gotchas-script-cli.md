# Gotchas: local scripts, CLI tools, one-off data transforms

Pull the 3-6 that matter. Write each into SPEC.md as "we handle X by doing Y".

## Input
- The input will not be what you planned for: wrong encoding, extra columns, empty file, header row missing, dates in three formats, trailing whitespace, a 2GB file when you expected 2MB. Validate early and fail with a message that names the problem and the row/line.
- Paths: spaces, non-ASCII characters, relative vs. absolute, `~` not expanding. Use the language's path library.
- Don't require arguments the user has to remember — give defaults and a `--help` that explains them in plain words.

## Output and safety
- Never overwrite the user's input file. Write to a new file (or a new folder) and say where it went.
- Destructive operations (delete, move, bulk rename) get a `--dry-run` that prints what would happen, and a confirmation before doing it.
- Partial failure: if it processes 900 of 1000 items and dies, does the user know which 100 failed, and can they re-run just those?
- Print a short summary at the end: what was read, what was written, what was skipped and why.

## Running it
- One command to run, documented at the top of the file and in SPEC.md. Dependencies pinned in `requirements.txt` / `package.json`; a virtualenv or equivalent so it doesn't fight with other projects.
- Progress feedback for anything over a few seconds (a counter or progress bar), so it doesn't look hung.
- Secrets (if any) from `.env`, never hardcoded, and `.env` ignored by git.
- If it's meant to run repeatedly on a schedule, it's an automation — read `gotchas-automation.md` too.

## Don't overbuild
- A script the user runs by hand doesn't need a config system, a plugin architecture, or a web UI. Keep it to a couple of clearly named files.
- Use the standard library or one well-known package for parsing (CSV, JSON, dates) rather than hand-written parsing.
