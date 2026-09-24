---
description: List currently loaded context files
---

## Loaded Context Files

Use the `/list-context-files` command to see which AGENTS.md and other context files are currently loaded.

## To reload context files after making changes:

1. Type `/reload` in the editor
2. Or restart pi with `pi --session <id>` if you're continuing a session

Context files from parent directories and the current directory walk up toward root:
- Current directory: `AGENTS.md`
- Parent directories (walking up)
- Global: `~/.pi/agent/AGENTS.md`

If a directory contains `AGENTS.override.md`, it replaces `AGENTS.md` for that directory.
