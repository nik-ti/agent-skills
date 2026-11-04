# Treg skills

This folder holds all seven Treg skills and their local setup notes. The upstream files live in `upstream/skills/`; `upstream/` is a Git submodule, so this shared repository records a specific Treg revision while Treg keeps its own history.

Both `~/.agents/skills` and `~/.claude/skills` point to the shared skills folder, so these files have one shared source.

Installed skills: `treg`, `rea-growth`, `web-access`, `lead-signals`, `make-ugc`, `recruit`, and `jev-memory`. Installing these files does not activate the optional Claude Code memory extension or run any paid workflows.

Source: https://github.com/superdesigndev/treg/tree/main/skills

### Update all Treg skills

From the `agent-skills` repository root, run:

```sh
git submodule update --remote -- skills/treg/upstream
```

This fetches Treg's latest `main` revision. The local checkout only includes the upstream `skills/` directory, keeping the server application out of the working folder. Existing skills update together, and new upstream skill folders appear on the next update.

To save the new revision in this shared repository:

```sh
git add skills/treg/upstream
git commit -m "Update Treg skills from upstream"
git push
```

Use this Git update command for these files rather than `treg skill bootstrap`, which installs standalone copies. Keep local notes and customizations beside `upstream/`, outside the submodule, so updates stay straightforward.

### Set up an existing clone

```sh
git submodule update --init -- skills/treg/upstream
git -C skills/treg/upstream sparse-checkout set --no-cone /skills/
```

Codex was verified to discover all seven nested skills through the shared user skills directory. Skills should be available on the next turn; restart the agent if its list has not refreshed. Claude Code shares these files, but its discovery was not checked during this installation.

Treg API credentials remain in local Treg configuration and project environment files; they do not belong in this repository.
