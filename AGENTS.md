# AGENTS.md

## Python environment
- **Package management**: This project uses [uv](https://github.com/astral-sh/uv) for Python package and virtualenv management. The root `.venv` is managed by uv.
- **Installed packages**: Find installed Python packages in the root project's `.venv` (e.g. `./.venv/bin/pip list`, or `uv pip list` with the project venv, or inspect `.venv/lib/python*/site-packages/`). Use the project venv for running Python, linting, and tests.

## Build/Lint/Test Commands
- **Build**: Python/build artifacts are produced during `uv install` of the local package (do not use `make` for building). For frontend: `npm run build`.
- **Lint Python**: Run ruff via uv: `uv run ruff check` (or `uv run ruff check .` to target the current directory). Config in pyproject.toml.
- Lint JS: `npm run lint`
- **Python tests**: Run using `./run-tests.sh`. Before running Python tests, always ask the user whether they want to run them (do not run automatically).
- **JS tests**: Run using `./run-js-tests.sh`.
- Run single JS test: `npm test -- <test-file>`, e.g., `npm test -- test_utils.js`

## Code Style Guidelines
- **Python**: PEP8, type hints required. Put all imports at the top of the file unless that would cause major unnecessary overhead or circular dependencies. Imports sorted: stdlib → third-party → local.
- **JS/TS**: ES2020, camelCase vars, PascalCase components. Alphabetized imports.
- **Types**: TypeScript interfaces for public API shapes; Python type checking via [ty](https://github.com/astral-sh/ty) (not mypy).
- **Error Handling**: `try/catch` blocks, context-rich logs, never log secrets.
- **Copilot/Cursor**: Check `.github/copilot-instructions.md` and `.cursor/rules/` for team rules.

