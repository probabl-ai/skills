---
name: setup-python-env
description: >
  Detect the Python environment manager and add packages through it.
  Two modes: one-time bootstrap (G-ENV-MGR) and repeatable
  `python -m skore_skills env add`. Persist `env_manager` in
  `.skore` (`workspace` section). Missing layout is a status fact; ask
  triage rather than scaffolding.

  TRIGGER before installing, adding, pinning, upgrading, or removing
  Python packages; when a workflow reports a missing dependency; when
  bootstrapping a Python project; or when IPython/pyright agent support
  is requested.

  SKIP non-Python tools and already-installed dependencies.

  HOW TO USE: run `env detect`, resolve gates, then run `env add`.
  Never use a different manager from the project manifest.
---

# Python Env Manager

Two modes. Do not mix them.

1. **One-time bootstrap.** No manager in the project. Fire
   `G-ENV-MGR`, wait, then bootstrap. Persist with
   `python -m skore_skills policy set env_manager <name>`.
2. **Repeatable add.** A manager is already recorded or detected.
   Skip `G-ENV-MGR`. Run `env add` for the requested packages.

Missing `src/` / scaffold is not this skill's job. Run
`python -m skore_skills status` and ask triage.

## Stop conditions

- **Wrong-manager install is forbidden.** Never `pip install` in a
  pixi project. Mixed state is not tracked and a later install/sync
  can undo it.
- **No silent bootstrap.** If no manager is detected, ask the user.
  Recommend pixi, but do not run `pixi init` before confirmation.
  A manager on PATH is context, not permission.
- **No silent ambiguity resolution.** If multiple project or ambient
  managers are visible, ask which environment is the target.
- **Known packages route automatically.** Runtime packages go to
  default; development tools to dev; IPython/pyright to agent.
  Ask `G-ENV-SCOPE` only for ambiguous extras such as optuna,
  xgboost, or mlflow: default vs a new named feature.
- Urgency and “you pick” do not resolve a gate.
- Install unpinned unless the user asks or compatibility requires a
  pin.
- Do not run system bootstrap installers (`curl | sh`).

## Pre-flight

```
- [ ] Detection: python -m skore_skills env detect
- [ ] Manager: pixi | uv | poetry | hatch | conda | pip-venv | none
- [ ] G-ENV-MGR: resolved | ask | n/a (one manifest manager)
- [ ] Package route: default | dev | agent | G-ENV-SCOPE ask
- [ ] G-AGENT-FEATURE: install | skip | n/a
- [ ] Command: python -m skore_skills env add <packages>
```

## Detect

Run at project root:

```bash
python -m skore_skills env detect
```

The JSON contains `env_manager`, `managers`, `evidence`, and
`ambiguous`. Root manifests are authoritative only when exactly one
manager is visible. Also surface an active ambient environment that
conflicts with the project (for example conda active beside
`pixi.toml`) and ask which target to use.

If detection returns a single project manager, persist it:

```bash
python -m skore_skills policy set env_manager <name>
```

If detection returns `none`, ask:

1. pixi (recommended)
2. uv
3. poetry
4. hatch
5. conda/mamba
6. pip + venv

Wait for the answer before bootstrap. After the manager exists:

```bash
python -m skore_skills policy set env_manager pixi
```

Use the chosen manager name. Persist into the `workspace` section of
`.skore` (merge-write). Do not print hub credentials.

## Add packages

After the gates resolve:

```bash
python -m skore_skills env add <package> [<package> ...]
```

By default the CLI prints the detected manager's command; execute it
only after checking the output. For pixi, a runtime package such as
`skrub`, `pandas`, or `scikit-learn` prints `pixi add <package>`.
Never replace that with pip/uv/poetry.

The three-feature policy is:

- `default`: runtime Python stack
- `dev`: tests, lint, notebooks
- `agent`: IPython and pyright

The current CLI prints the base manager command. If a known non-default
feature is needed, add the manager's feature flag to that printed
command. For an ambiguous extra, ask first: `default` or a new named
feature inferred from the task (for example `tuning` for optuna).

## Agent feature

Ask before installing optional agent-only support. If approved, use
the existing manager-specific script under `scripts/` and copy
`templates/pyrightconfig.json` verbatim. Do not register a Jupyter
kernel. If declined, return to the caller's documented fallback.

## Python code style

Setup also owns the root Ruff configuration. If `ruff.toml` is
missing, copy `templates/ruff.toml` verbatim. After Python edits run:

```bash
python -m skore_skills style <touched paths>
```

Ruff remains manual: no PostToolUse/PreToolUse hook, no black/isort
substitution, and no widening to untouched files. Public functions
use numpydoc `Parameters` / `Returns` sections with array shapes in
the type slot.

## Editable workspace package (pixi)

For a fresh `src/<pkg>/` scaffold:

```bash
pixi add --pypi "<pkg> @ ."
```

Then ensure the pixi manifest contains:

```toml
<pkg> = { path = ".", editable = true }
```

Run `pixi install`. This makes `from <pkg>...` work from any CWD;
do not use `pip install -e .` or `PYTHONPATH=src`.

## Failure handling

- `env detect` ambiguous: ask; do not call `env add`.
- no manager: ask; do not bootstrap.
- hatch: follow the CLI's manifest-edit hint; there is no universal
  add command.
- a forbidden substitute: keep the canonical stack package and
  surface the CLI refusal.

## References (load on demand)

- `references/ambient_detection.md`
- `references/bootstrap.md`
- `references/editable_workspace.md`
- `references/agent_feature_anatomy.md`
- `references/per_manager_footguns.md`
