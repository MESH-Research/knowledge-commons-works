# AGENTS.md

## Build/Lint/Test Commands
- Build: `make build` or `npm run build`
- Lint Python: `ruff .` (via ruff.xml)
- Lint JS: `npm run lint`
- Run all tests: `npm test`
- Run single test: `npm test -- <test-file>`, e.g., `npm test -- test_utils.js`

## Code Style Guidelines
- **Python**: PEP8, type hints required. Imports sorted: stdlib → third-party → local.
- **JS/TS**: ES2020, camelCase vars, PascalCase components. Alphabetized imports.
- **Types**: TypeScript interfaces for public API shapes; Python `mypy`-compatible.
- **Error Handling**: `try/catch` blocks, context-rich logs, never log secrets.
- **Copilot/Cursor**: Check `.github/copilot-instructions.md` and `.cursor/rules/` for team rules.

