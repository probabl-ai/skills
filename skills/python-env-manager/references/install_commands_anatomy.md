# Python Env Manager — Install commands anatomy

Per-manager extended prose for the commands in SKILL.md § "Install
commands — by manager". Load when picking between command variants
within one manager, or when a command in the SKILL.md table needs
context.

## pixi

Default for this stack. Organizes deps per **feature** — the
enforced layout is `default` / `dev` / `agent` (plus any optional
features for ambiguous extras). Routing is automatic per § "Where
does the package belong?"; no per-install ask unless the dep is an
ambiguous extra (G-ENV-SCOPE fires).

A real-world example: when the user asks for `mlflow`, the routing
is ambiguous (it's neither plain runtime nor a known agent / dev
tool). G-ENV-SCOPE fires; if the user picks "new feature called
`tracing`", the install becomes `pixi add --feature tracing mlflow`.

## uv

Organizes deps via the `[dependency-groups]` table in
`pyproject.toml`. The mapping:

- `default` → top-level `[project] dependencies`
- `dev` → `--group dev`
- `agent` → `--group agent`
- optional features → named groups via `--group <name>`

No per-install ask unless G-ENV-SCOPE fires. The single env is
`.venv` at the project root; composition happens via sync flags.
`uv sync --all-groups` is the canonical re-sync after any add.

## poetry

Uses `[tool.poetry.group.X]` for scoped deps. The mapping:

- `default` → `[tool.poetry.dependencies]`
- `dev` → `--group dev`
- `agent` → `--group agent`
- optional features → `--group <name>`

`poetry install` is editable by default for the project package.
Cache-dir env location is the default; set
`poetry config virtualenvs.in-project true` to anchor `.venv` at
the project root (see `references/per_manager_footguns.md`).

## hatch

Declarative — no universal `hatch add`. Map the 3 fixed buckets to
hatch envs:

- `default` → `[project] dependencies`
- `dev` → `[tool.hatch.envs.dev.dependencies]`
- `agent` → `[tool.hatch.envs.agent.dependencies]`
- optional → additional `[tool.hatch.envs.<name>.dependencies]`

**Caveat**: hatch envs are isolated — they do not compose with each
other. Each non-default env must duplicate runtime deps it needs at
import time. Flag this duplication cost to the user before
recommending hatch for a fresh workspace.

Standard flow:

1. Edit `pyproject.toml`:
   - Project-level dep → add to `[project] dependencies`.
   - Env-specific dep → add to
     `[tool.hatch.envs.<env>.dependencies]`.
2. Re-sync the env: `hatch env prune` (optional, removes stale
   envs), then any `hatch run -e <env> <command>` re-creates it.

## conda / mamba

`mamba` is a faster drop-in replacement for `conda`. Prefer it if
both are on PATH.

conda doesn't have a native "feature" concept; map buckets to named
envs:

- `default` → project name
- `dev` → `<project>-dev`
- `agent` → `<project>-agent`
- optional features → additional envs

Duplicate the runtime deps across `-dev` / `-agent` / optional envs
(conda's isolation model) — same caveat as hatch. No per-install
ask unless G-ENV-SCOPE fires.

If `environment.yml` is the source of truth for the project, edit
it and run `conda env update -f environment.yml --prune` rather
than installing one-off; this keeps the manifest in sync.

## pip + venv

The least-integrated path. There is no manifest update — `pip
install` mutates the live env without tracking.

pip+venv has no native bucket concept; the 3-feature layout maps to
**separate venvs**: `.venv-default/`, `.venv-dev/`, `.venv-agent/`.
Surface to the user that pip+venv loses the manifest integrity the
other managers provide — the right migration is to a managed
alternative (pixi by default).

Steps:

1. Activate the venv: `source .venv/bin/activate` (Linux/macOS) or
   `.venv\Scripts\activate` (Windows).
2. Install: `pip install <pkg>`.
3. If `requirements.txt` is the project's manifest, regenerate or
   edit it — `pip freeze > requirements.txt` is one option, but it
   captures all transitive pins; for a tighter diff, edit the file
   by hand to add the new top-level dep.

`pip install` alone leaves no audit trail. If the project is fresh,
offer migration to a managed alternative.
