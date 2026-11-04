# Shared agent skills

This repository holds Nikita's shared agent instructions. Both `~/.agents/skills` and `~/.claude/skills` point to its `skills/` folder, so changes have one shared source.

## Treg skills

All seven upstream Treg skills live in `skills/treg/skills/`, inside the single `skills/treg/` folder. That folder is a Git submodule: this repository records a specific Treg revision, while Treg keeps its own Git history and upstream remote.

Installed skills: `treg`, `rea-growth`, `web-access`, `lead-signals`, `make-ugc`, `recruit`, and `jev-memory`. Installing these files does not activate the optional Claude Code memory extension or run any paid workflows.

Source: https://github.com/superdesigndev/treg/tree/main/skills

### Update all Treg skills

From this repository, run:

```sh
git submodule update --remote -- skills/treg
```

This fetches Treg's latest `main` revision. The local checkout only includes the upstream `skills/` directory, keeping the server application out of the working folder. Existing skills update together, and new upstream skill folders appear on the next update.

To save the new revision in this shared repository:

```sh
git add skills/treg
git commit -m "Update Treg skills from upstream"
git push
```

Use this Git update command for these files rather than `treg skill bootstrap`, which installs standalone copies. Keep local customizations outside the upstream submodule so updates stay straightforward.

### Set up an existing clone

```sh
git submodule update --init -- skills/treg
git -C skills/treg sparse-checkout set --no-cone /skills/
```

Codex was verified to discover all seven nested skills through the shared user skills directory. Skills should be available on the next turn; restart the agent if its list has not refreshed. Claude Code shares these files, but its discovery was not checked during this installation.

Treg API credentials remain in local Treg configuration and project environment files; they do not belong in this repository.
