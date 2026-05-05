# ruff

A fast, all-in-one Python linter and formatter written in Rust. Replaces
black, isort, flake8, and most pyflakes/pep8 rules with a single tool,
fast enough to run as a save hook or pre-commit step.

**Use ruff for:**
- Formatting (`ruff format`) — drop-in compatible with black.
- Linting (`ruff check`) — implements rules from flake8, pyflakes,
  pyupgrade, pep8-naming, isort, and many more.

**Notes for orchestration:**
- Configuration lives in `pyproject.toml` under `[tool.ruff]`.
- Default rules are intentionally minimal — enable specific rule groups
  (e.g. `E`, `F`, `W`, `I`, `UP`, `B`, `SIM`) as the project matures.
- Don't disable rules to silence formatting weirdness — fix the source
  structure instead.
