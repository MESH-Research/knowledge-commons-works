# AGENTS.md

This file is the **canonical** reference for tooling and agent workflows. Cursor loads complementary rules from [`.cursor/rules/`](.cursor/rules/).

## Security & secrets (agents)

- **Do not read, search, or open** credential-bearing paths: `.env`, `.env.*`, `.envrc`, `.invenio.private`, private keys under `docker/nginx_local/`, cloud credential files, Secrets Manager temp env paths, and similar. **Do not** `cat`, `head`, or `tail` those paths.
- **Never** emit real secrets in chat, diffs, comments, or logs; use placeholders in examples. Questions about whether a variable is set: use **names and docs** only—**not** by reading credential files in the agent.
- **Never run** `docker compose … config`, `docker compose config`, `printenv`, unrestricted `env`, or any command whose primary effect is to print or resolve full process environment or fully-resolved Compose. **Never read** that output; capture can exfiltrate secrets before any chat paste. Compose layout: **tracked** YAML and public docs only.
- **Never read or ingest** terminal output, logs, or files expected to contain credentials or full environment dumps.

## Python environment
- **Package management**: This project uses [uv](https://github.com/astral-sh/uv) for Python package and virtualenv management. The root `.venv` is managed by uv.
- **Installed packages**: Find installed Python packages in the root project's `.venv` (e.g. `./.venv/bin/pip list`, or `uv pip list` with the project venv, or inspect `.venv/lib/python*/site-packages/`). Use the project venv for running Python, linting, and tests.

## Build/Lint/Test Commands
- **Build**: Python/build artifacts are produced during `uv install` of the local package (do not use `make` for building).
- **Lint Python**: Run ruff via uv: `uv run ruff check` (or `uv run ruff check .` to target the current directory). Config in pyproject.toml.
- **Python tests**:
  - **Local**: Run using `./run-tests.sh`. This starts docker-services-cli test databases and runs pytest inside the `test-runner` container for security (prevents malicious dependency code from accessing host credentials). CI mode is detected via `$CI`.
  - **CI**: Tests run directly on the Actions runner via the existing workflow; no additional test-runner container (GitHub Actions provides isolation).
  Before running Python tests, always ask the user whether they want to run them (do not run automatically).

## JavaScript (root project)
Use **[pnpm](https://pnpm.io/)** for the repository root `package.json` (not `npm install`). The root **`packageManager`** field pins the pnpm version; **`preinstall`** rejects other package managers; Use *only* the Node/pnpm versions in root **`package.json`** `engines`.

**One-time per Node.js install:** enable Corepack (ships with Node 18+) so `pnpm` matches the pinned version:

```bash
corepack enable
```

Then from the repo root:

- **Install deps:** `pnpm install` (CI uses `pnpm install --frozen-lockfile` with `pnpm-lock.yaml`).
- **Build frontend (when applicable):** `pnpm run build`
- **Lint JS:** `pnpm run lint`
- **JS tests**:
  - **Local**: `./run-tests.sh --js-only` (or `./run-js-tests.sh`, which forwards). Runs each suite in `scripts/run-js-suites.sh` inside the `test-runner` container (root Jest, then package Jest where listed). Pass `-J` with a normal `./run-tests.sh` to run those suites before pytest.
  - **CI**: `./run-js-tests.sh` → `scripts/run-js-suites.sh` on the Actions runner.
  - Add a dependency package to the suite list in `scripts/run-js-suites.sh` once it has its own `jest.config.js` + `package.json` test script. Root Jest ignores `site/kcworks/dependencies/`.
  - Example: `./run-tests.sh --js-only -- test_utils.js` (args forwarded to every suite)

## Code Style Guidelines
- **Python**: PEP8, type hints required. Put all imports at the top of the file unless that would cause major unnecessary overhead or circular dependencies. Imports sorted: stdlib → third-party → local.
- **Python docstrings**: Use **Google-style** docstrings (for example `Args`, `Returns`, `Raises`). Use **Markdown** in docstrings for formatting (lists, `` `inline code` ``, links) where it improves readability.
- **JS/TS**: ES2020, camelCase vars, PascalCase components. Alphabetized imports. Use **JSDoc** where it adds clarity (for example `@param`, `@returns`, `@typedef`, `@template`), especially for exports and plain JavaScript.
- **Types**: TypeScript interfaces for public API shapes; Python type checking via [ty](https://github.com/astral-sh/ty) (not mypy).
- **Error Handling**: `try/catch` blocks, context-rich logs, never log secrets.
- **Cursor**: Project rules live in [`.cursor/rules/`](.cursor/rules/) (especially `project-agents.mdc`); keep them aligned when you change agent or security policy here.

## Agent Collaboration Rules
- **Approval before edits (mandatory)**: Explain the issue and proposed change **before** editing; prefer the smallest validated fix; avoid speculative refactors. **Do not edit** without explicit authorization for **that** change. Silence, venting, or more chat is not authorization. If the request is ambiguous or inference-based, give 2–4 options with tradeoffs (or state the inference gap), then **wait** for a clear yes before implementing.
- **After a mistake**: Stop unapproved edits; acknowledge plainly; offer revert. Do not compensate with more unapproved changes.
- **Submodule-aware git history**: When checking git history/status/log for files in a submodule, run git commands from the closest submodule repository root (not the parent repository).

## Tone and reasoning (agents)

- Be direct and non-patronizing; the maintainer is a peer.
- **Acknowledge what is already correct** in what they said, then **add precision or missing detail**—do not “correct” them when nothing needed fixing.
- **Do not invent** problems, edge cases, or scope stories that aren’t grounded in the codebase, their stated intent, or a concrete risk they asked about.

