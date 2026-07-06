# Publishing admin docs to the knowledge base

KCWorks administrator how-tos in this documentation set can be synced into the
[MESH knowledge-base](https://github.com/MESH-Research/knowledge-base) repository
using **[kc-knowledge-base-sync](https://github.com/MESH-Research/kc-knowledge-base-sync)**
(the `kb-sync` CLI).

The tool lives in its own repository and is included in kcworks-next as a git
submodule at `site/kcworks/dependencies/kc-knowledge-base-sync`, installed as a
dev-only Python dependency.

## Setup

From the kcworks-next repository root:

```bash
git submodule update --init site/kcworks/dependencies/kc-knowledge-base-sync
uv sync --group dev
cp docs/knowledge_base_sync/config.example.yaml docs/knowledge_base_sync/config.yaml
```

Edit `docs/knowledge_base_sync/config.yaml` for your local paths (kcworks-next root,
knowledge-base clone, and optional LM Studio host). That file is gitignored.

You also need a local clone of the
[knowledge-base](https://github.com/MESH-Research/knowledge-base) repository.

## Usage

Run from the kcworks-next root. The default config is
`docs/knowledge_base_sync/config.yaml`, so `--config` is optional:

```bash
uv run kb-sync --dry-run
uv run kb-sync --force
uv run kb-sync --force --commit --pr
```

| Flag | Purpose |
|------|---------|
| `--dry-run` | Show planned output paths without writing files |
| `--force` | Overwrite existing knowledge-base articles |
| `--use-llm` | Format with LM Studio instead of the built-in converter |
| `--commit` | Rebuild indexes and commit in the knowledge-base repo |
| `--pr` | Push and open a GitHub pull request (requires `--commit`) |

See the [package README](https://github.com/MESH-Research/kc-knowledge-base-sync/blob/main/README.md)
for the full flag list and configuration reference.

## Which sections are synced

By default, only headings that match **`How do I …?`** (levels 2–4) are extracted.
That pattern is used throughout the [Administrator's Guide](../admin_guide/index.md).

To include a section with a different heading, place an HTML comment on the line
immediately above it:

```markdown
<!-- kb-sync -->
## Deploy a hotfix without downtime
```

Optional article title override:

```markdown
<!-- kb-sync: Deploy a hotfix -->
## Internal procedure (staging only)
```

Generated knowledge-base filenames use a slug derived from the title. Apostrophes are
**stripped** from slugs (`user's` → `users`), so related articles stay consistently named.

## Configuring sources

`docs/knowledge_base_sync/config.yaml` maps documentation directories to knowledge-base
topic folders. The default example syncs selected files from
`docs/source/admin_guide` into `internal/works-maintenance` in the knowledge-base.

Adjust `sources` when adding new admin-guide pages or targeting a different KB topic.

## Further reading

- [kc-knowledge-base-sync README](https://github.com/MESH-Research/kc-knowledge-base-sync/blob/main/README.md) — installation, extraction rules, LM Studio, and development
- [knowledge-base CONTRIBUTING](https://github.com/MESH-Research/knowledge-base/blob/main/CONTRIBUTING.md) — article format and folder layout
