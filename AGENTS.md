# AGENTS.md

## Python environment
- **Package management**: This project uses [uv](https://github.com/astral-sh/uv) for Python package and virtualenv management. The root `.venv` is managed by uv.
- **Installed packages**: Find installed Python packages in the root project's `.venv` (e.g. `./.venv/bin/pip list`, or `uv pip list` with the project venv, or inspect `.venv/lib/python*/site-packages/`). Use the project venv for running Python, linting, and tests.

## Build/Lint/Test Commands
- **Build**: Python/build artifacts are produced during `uv install` of the local package (do not use `make` for building).
- **Lint Python**: Run ruff via uv: `uv run ruff check` (or `uv run ruff check .` to target the current directory). Config in pyproject.toml.
- **Python tests**: Run using `./run-tests.sh`. Before running Python tests, always ask the user whether they want to run them (do not run automatically).

## JavaScript (root project)
Use **[pnpm](https://pnpm.io/)** for the repository root `package.json` (not `npm install`). The root **`packageManager`** field pins the pnpm version; **`preinstall`** rejects other package managers; **`.npmrc`** sets **`engine-strict=true`**.

**One-time per Node.js install:** enable Corepack (ships with Node 18+) so `pnpm` matches the pinned version:

```bash
corepack enable
```

Then from the repo root:

- **Install deps:** `pnpm install` (CI uses `pnpm install --frozen-lockfile` with `pnpm-lock.yaml`).
- **Build frontend (when applicable):** `pnpm run build`
- **Lint JS:** `pnpm run lint`
- **JS tests:** `./run-js-tests.sh` (runs `pnpm test`), or `pnpm test -- <pattern>`, e.g. `pnpm test -- test_utils.js`

## Code Style Guidelines
- **Python**: PEP8, type hints required. Put all imports at the top of the file unless that would cause major unnecessary overhead or circular dependencies. Imports sorted: stdlib → third-party → local.
- **JS/TS**: ES2020, camelCase vars, PascalCase components. Alphabetized imports.
- **Types**: TypeScript interfaces for public API shapes; Python type checking via [ty](https://github.com/astral-sh/ty) (not mypy).
- **Error Handling**: `try/catch` blocks, context-rich logs, never log secrets.
- **Copilot/Cursor**: Check `.github/copilot-instructions.md` and `.cursor/rules/` for team rules.

## Agent Collaboration Rules
- **Approval before edits**: The agent must explain the suspected root cause and proposed fix before making any code changes, and must get explicit user authorization before editing files.
- **No speculative complexity**: Prefer the smallest validated fix first. If a fix is based on inference rather than reproduction, state that clearly and ask for approval before implementing.
- **Brief options first**: Before edits, provide a short options list (2-4 approaches) with tradeoffs and a recommended path, then wait for user approval.
- **Submodule-aware git history**: When checking git history/status/log for files in a submodule, run git commands from the closest submodule repository root (not the parent repository), unless explicitly asked otherwise.

