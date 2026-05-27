# Python Env Manager — Editable workspace package

Per-manager wiring for installing `src/<pkg>/` in editable mode.
Cross-referenced from SKILL.md § "Install commands — by manager"
and from `organize-ml-workspace` § Editable workspace package.

When the project ships a local Python package under `src/<pkg>/`
(declared by a `pyproject.toml` at the project root), it must be
installed in **editable** mode so that `from <pkg>.X import Y`
works from any CWD without `PYTHONPATH=src` hacks **and** so that
edits to the source tree are picked up immediately.
`organize-ml-workspace` hands off here after dropping
`pyproject.toml`.

The wiring differs per manager. Use the matching command — never
fall back to `pip install -e .` inside a managed env (that produces
the same out-of-manifest drift as any other wrong-manager install).

## Per-manager wiring

| Manager | Wiring | Notes |
|---|---|---|
| **pixi** | Two-step: `pixi add --pypi "<pkg> @ ."` then edit `pixi.toml` `[pypi-dependencies]` to add `editable = true` (resulting line: `<pkg> = { path = ".", editable = true }`), then `pixi install` | Verified against pixi 0.69. The bare `pixi add --pypi --editable .` form documented in earlier releases is rejected with `× URL requirement must be preceded by a package name` — the name-prefixed `<pkg> @ .` syntax is the working shape. Pass `--feature <name>` on `pixi add` to scope (e.g. `default` for the Tier 1 feature). On next `pixi install`, the package is editable in every env that includes that feature. |
| **uv** | nothing extra — `uv sync` installs the `[project]` package editable by default | If the workspace has multiple packages, add `[tool.uv.sources]` entries; for the single-package case the default `uv sync` is enough. |
| **poetry** | nothing extra — `poetry install` is editable by default | Make sure `pyproject.toml` carries `[tool.poetry] packages = [{include = "<pkg>", from = "src"}]` (or that the build backend's package discovery picks up `src/<pkg>/`). |
| **hatch** | nothing extra — `hatch run` envs install editable by default | Make sure `[tool.hatch.build.targets.wheel] packages = ["src/<pkg>"]` is declared in `pyproject.toml`. |
| **conda / mamba** | after the env is in place: `pip install -e .` (run inside the conda env) | conda has no native concept of editable installs from a local `pyproject.toml`; pip is the right tool here. `pip install -e .` here is **inside a conda-managed env** — that's the supported hybrid, not a wrong-manager install. |
| **pip + venv** | activate the venv, then `pip install -e .` | The standalone case. There is no manifest entry — surface this and offer migration. |

## Drift cleanup

If you find a stale `<pkg>.egg-info/` at the project root or under
`src/` (typically a relic of an out-of-band `pip install -e .`)
**and** the manager's manifest does not carry the editable entry,
that is drift. Clean up the egg-info **after** wiring the install
correctly through the manager — never before (the cleanup can
break a working but unmanaged setup).
