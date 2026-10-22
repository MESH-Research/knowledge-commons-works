# KCWorks editor wiring

The editor **image** lives in a separate project
(`~/Development/nvim-sandbox` by default; override with
`KCWORKS_EDITOR_CONTEXT`).

This directory only holds KCWorks-specific Compose overlays:

| File | Role |
|------|------|
| `docker-compose.editor.yml` | Attach nvim-sandbox image to project network + src/instance/home volumes |
| `docker-compose.editor.agents.yml` | SSH/GPG agent socket forwards |

Launcher: `./kcworks-project.sh` from the repository root.

Docs: `docs/source/developing/editor.md`.
