# SSH + GPG agent forwarding on macOS (Docker Desktop)

Compose overlays bind-mount host agent **sockets** into workspace/editor
containers. Private keys stay on the YubiKey; the container only requests
sign/auth (YubiKey touch / PIN via host pinentry).

**Default for local bring-up:** `kcworks-startup.sh` (dev) and
`kcworks-project.sh` (repository root) always include the agents overlays and
set the host sockets for you:

- **SSH:** a **dedicated** `ssh-agent` started (or reused) by
  `scripts/dev-host/kcworks-ssh-agent.sh`, holding only the key(s) meant for containers.
  Your login agent (`SSH_AUTH_SOCK`) is never mounted.
- **GPG:** gpg-agent's **extra socket** (`gpgconf --list-dirs agent-extra-socket`),
  which runs in restricted mode: signing and decryption work, key management and
  smartcard (`SCD`) commands are refused.

Overlays:

- Workspace: `docker-compose.dev.agents.yml`
- Editor: `docker/editor/docker-compose.editor.agents.yml`

## Host variables

| Host env | Default | Used by |
|----------|---------|---------|
| `KCWORKS_SSH_AUTH_SOCK` | output of `scripts/dev-host/kcworks-ssh-agent.sh` | overlay bind → `/ssh-agent` |
| `KCWORKS_GPG_AGENT_SOCK` | `gpgconf --list-dirs agent-extra-socket` | overlay bind → `$GNUPGHOME/S.gpg-agent` |
| `KCWORKS_SSH_AGENT_SOCK` | `$HOME/.kcworks/ssh-agent.sock` | where the dedicated agent listens |
| `KCWORKS_SSH_KEY` | (unset) | key / FIDO2 key-handle file loaded when the agent is empty |
| `KCWORKS_SSH_KEY_HOSTS` | (unset) | comma-separated hosts passed to `ssh-add -h` (e.g. `github.com`) |
| `KCWORKS_OPENSSH_BIN` | Homebrew `bin`, else `PATH` | directory with `ssh-agent` / `ssh-add` |

Set `KCWORKS_SSH_KEY` / `KCWORKS_SSH_KEY_HOSTS` in your shell profile (they are
paths and hostnames, not secrets). Setting `KCWORKS_SSH_AUTH_SOCK` or
`KCWORKS_GPG_AGENT_SOCK` yourself skips the defaults.

The dedicated agent keeps running after the scripts exit, at a stable path, so
containers survive host sleep / login-agent restarts. Stop it with
`pkill -f "ssh-agent -a $HOME/.kcworks/ssh-agent.sock"` (or log out).

## One-time: a container-only SSH key on the YubiKey

Use **Homebrew OpenSSH** (`brew install openssh`); Apple's bundled OpenSSH does
not load FIDO2 (`-sk`) keys into an agent without extra setup.

1. Create a separate resident FIDO2 credential (touch required by default):

   ```bash
   /opt/homebrew/bin/ssh-keygen -t ed25519-sk -O resident \
     -O application=ssh:kcworks-containers \
     -C "kcworks containers" \
     -f ~/.ssh/id_ed25519_sk_kcworks
   ```

   The files written are a key **handle** and public key; they are useless
   without the YubiKey. Avoid `-O verify-required` for this key unless you also
   configure an `SSH_ASKPASS` program — the agent has no terminal to prompt for
   the PIN.

2. Add `~/.ssh/id_ed25519_sk_kcworks.pub` to GitHub as an **authentication** key
   (Settings → SSH and GPG keys). It is separate from your everyday key, so you
   can revoke it alone if a container is compromised.

3. Make sure `github.com` is in your host `~/.ssh/known_hosts` (connect once
   from the host), then export:

   ```bash
   export KCWORKS_SSH_KEY=~/.ssh/id_ed25519_sk_kcworks
   export KCWORKS_SSH_KEY_HOSTS=github.com
   ```

   `KCWORKS_SSH_KEY_HOSTS` makes the agent refuse to use the key for anything
   except authenticating to the listed hosts (requires the host key in
   `known_hosts`; see `ssh-add(1)` `-h`).

4. In the container, fetch over HTTPS and push over SSH so the key (and a
   touch) is only needed for push:

   ```bash
   git remote set-url origin https://github.com/MESH-Research/<repo>.git
   git remote set-url --push origin git@github.com:MESH-Research/<repo>.git
   ```

## Docker Desktop notes

**Workspace SSH proxy:** Docker Desktop often exposes the bind-mounted agent as
`root:root` mode `660`, which uid 1000 cannot open. The workspace entrypoint
(starts as root) runs `socat` to `/tmp/ssh-agent-proxy` (owned by `invenio`)
and sets `SSH_AUTH_SOCK` to that path. Rebuild the workspace image after pull.
Use `docker exec -u invenio …` for bootstrap/shells.

Images pre-create user-owned `GNUPGHOME` (`/home/dev/.gnupg`,
`/opt/invenio/.gnupg`, mode 700). That directory must exist before Compose
bind-mounts the socket into it — otherwise Docker creates the parent as root.
A fresh `editor-home` volume picks up the image seed on first mount.

**GPG into the Linux VM:** a plain bind of a macOS socket under `~/.gnupg`
may fail inside the Desktop Linux VM. If `gpg` inside the container cannot talk
to the agent, run a host-side bridge (typically `socat`) that exposes the
**extra** socket on a path Docker can mount, and point `KCWORKS_GPG_AGENT_SOCK`
at it. Keep **pinentry on the Mac** (`pinentry-mac` in
`~/.gnupg/gpg-agent.conf`); do not expect PIN UI inside the container.

## Bring-up checklist

1. **Host agents**
   - SSH: `scripts/dev-host/kcworks-ssh-agent.sh` prints the socket path; then
     `SSH_AUTH_SOCK=$HOME/.kcworks/ssh-agent.sock ssh-add -l` lists only the
     container key.
   - GPG: `gpgconf --list-dirs agent-extra-socket` prints a live socket; host
     commit signing / simplesec already work with `pinentry-mac`.

2. **Start stack / editor** (agents included by the host scripts):

   ```bash
   # App stack + workspace (+ agents)
   ./kcworks-startup.sh

   # Editor (after network + volumes exist; agents + tmux attach)
   ./kcworks-project.sh
   ```

3. **Smoke test inside the container** (be present for YubiKey touch / PIN):

   ```bash
   docker exec -u invenio -it kcworks-workspace bash -lc 'ssh-add -l'
   docker exec -u invenio -it kcworks-workspace bash -lc 'ssh -T git@github.com'
   docker exec -u invenio -it kcworks-workspace bash -lc 'echo test | gpg --clearsign'
   ```

   `gpg --card-status` is expected to fail through the extra socket; that is
   the restriction working.

## Image packages

Both images install agent-facing clients (rebuild after pull):

- **Editor** (`docker/editor/Dockerfile`): `openssh-client`, `gnupg`, `openssl`
- **Workspace** (`Dockerfile` `dev-workspace` stage): `openssh-client`, `gnupg`, `openssl`

## Security reminder

Overlays mount sockets **read-only**. Containers may request sign/auth only;
they never receive private keys, cannot reach your login SSH agent, and cannot
administer gpg-agent or the card (touch-per-use, PINs, key admin remain on the
host). Every SSH signature still needs a YubiKey touch — an unexpected blink
means something in a container asked for one.
