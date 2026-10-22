# Editor container (pluggable nvim-sandbox)

KCWorks attaches a **pluggable editor container** to the project network and
volumes via `./kcworks-project.sh`. By default that image is **nvim-sandbox**
(local path `~/Development/nvim-sandbox`; override with
`KCWORKS_EDITOR_CONTEXT` / `KCWORKS_EDITOR_IMAGE`).

SSH/GPG agent forwarding: [agents-macos.md](agents-macos.md).

## Three projects

| Project | Role |
|---------|------|
| **nvim-sandbox** | Generic editor image: Dockerfile, entrypoint, seed, default manifest |
| **kcworks-next** | Wiring only: compose overlays, `kcworks-project.sh`, project volumes/network |
| **nvim-sandbox-addon** (optional) | Personal seed repo (Notes, etc.), cloned **into** the editor home by seed |

## Bring-up

```bash
# One-time: editor image sources
#   ~/Development/nvim-sandbox

./kcworks-startup.sh          # app network + volumes
./kcworks-project.sh          # build/use nvim-sandbox + agents + tmux attach
./kcworks-project.sh --up-only
./kcworks-project.sh --build  # rebuild from KCWORKS_EDITOR_CONTEXT
```

## Configuration

| Variable | Default | Effect |
|----------|---------|--------|
| `KCWORKS_EDITOR_IMAGE` | `nvim-sandbox:latest` | Image tag |
| `KCWORKS_EDITOR_CONTEXT` | `~/Development/nvim-sandbox` | Docker build context |
| `EDITOR_CONFIG_PULL=1` | off | ff-only pull manifest configs **and** addon |
| `EDITOR_TOOLS_UPDATE=1` | off | reinstall mutable CLIs + refresh `~/editor-tools` |
| `EDITOR_MANIFEST` | (see nvim-sandbox) | Override default manifest path |
| `EDITOR_ADDON_REPO` | unset | Opt-in: git remote for personal addon (cloned by seed) |
| `EDITOR_ADDON_DIR` | `~/.local/share/nvim-sandbox/addon` | Clone destination on the home volume |
| `EDITOR_ADDON_SCRIPT` | `seed-addon.sh` | Script path relative to the clone |
| `EDITOR_ADDON_REF` | unset | Optional git ref/tag/SHA after clone |

Pass addon env via host `.env` / shell (compose forwards them into the editor
service). KCWorks does **not** include a personal addon compose overlay.

Example (host `.env` or export before `./kcworks-project.sh`):

```bash
EDITOR_ADDON_REPO=git@github.com:monotasker/nvim-sandbox-addon.git
```

## What KCWorks mounts

| Mount | Target |
|-------|--------|
| `${project}-src_data` | `/opt/invenio/src` (compose `working_dir`) |
| `${project}-instance_data` | `/opt/invenio/var/instance` |
| `${project}-editor-home` | `/home/dev` |

Do not set compose `user:` (entrypoint must start as root for the SSH proxy,
then `runuser` to uid 1000).

## Ready contract

`kcworks-project.sh` waits for:

`/home/dev/.local/share/editor-tools/ready.stamp`

## Manifest + personal addon

Implemented **inside nvim-sandbox** seed (as uid **1000 / `dev` only** — never
root):

1. Clone config repos from the manifest (default: monotasker nvconfig/tmux/zsh)
2. If `EDITOR_ADDON_REPO` or `manifest.addon` is enabled, clone the addon onto
   the home volume and run its seed script as `dev`

Edit/commit the addon **inside the container** (full clone under
`~/.local/share/nvim-sandbox/addon`) and push with the forwarded SSH agent.
Host checkout of the addon repo is for development outside the container if
you want it; the running editor uses the in-volume clone.

Details: nvim-sandbox `README.md`.

## Related files (this repo)

- `docker/editor/docker-compose.editor.yml` — project attach overlay
- `docker/editor/docker-compose.editor.agents.yml` — SSH/GPG sockets
- `docker/editor/README.md` — pointer to nvim-sandbox
- `kcworks-project.sh` — launcher / ready wait
