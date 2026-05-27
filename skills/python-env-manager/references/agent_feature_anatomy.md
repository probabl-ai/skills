# Python Env Manager — Agent feature anatomy

Full anatomy of what the bundled `install_agent_feature_<manager>.sh`
scripts do, how the resulting envs are wired, and how to invoke the
audit runner afterwards. Load on first agent-feature install, or
when debugging a failed install.

## What the agent feature is

A project-scoped install of two agent-only tools plus a config:

- **`ipython`** — powers the in-process cell runner at
  `audit-ml-pipeline/scripts/run_audit.py` via
  `InteractiveShell.run_cell`. No kernel registration, no
  notebook conversion.
- **`pyright`** — powers the opencode LSP integration for Python
  files. Surfaces import / type / undefined-symbol diagnostics in
  the editor. Configured via the bundled `pyrightconfig.json`
  template (this skill ships it at
  `templates/pyrightconfig.json`; the install step copies it to
  the project root).
- **`pyrightconfig.json`** at the project root, with
  `<PYTHON_PATH>` substituted for the lsp env's interpreter.

The deps themselves are catalogued in `data-science-python-stack`
under the "agent feature" category — separate from Tier 1
mandatory because not every workspace uses the audit flow or the
LSP integration. This skill owns *where they get installed*.

## Composition model — fixed by the 4-env layout

Every workspace gets four composed envs: `default` / `dev` /
`agent` / `lsp`. See SKILL.md § "Where does the package belong?"
for the full layout.

- **`agent`** = `default + agent` — used by the audit runner and
  by the agent invoking `pyright` as a CLI tool.
- **`lsp`** = `default + dev + agent` (plus all optional features)
  — used by the opencode LSP integration so pyright resolves every
  import the user could plausibly write, regardless of which
  feature it lives in.

Why they're separate: see `references/composition_model.md`.

## Per-manager invocations — what the scripts do

Three actions per script, in order:

1. Install `ipython` + `pyright` into the agent feature.
2. Compose / create the `lsp` env (manager-specific).
3. Substitute `<PYTHON_PATH>` in the bundled `pyrightconfig.json`
   template and copy to project root.

### Per-manager step mapping

| Manager | Agent install | LSP env creation | Pyright `<PYTHON_PATH>` |
|---|---|---|---|
| **pixi** | `pixi add --feature agent ipython pyright` | Edit `pixi.toml` `[environments]` to add `lsp = { features = ["default", "dev", "agent"], solve-group = "default" }`; then `pixi install -e lsp` | `.pixi/envs/lsp/bin/python` |
| **uv** | `uv add --group agent ipython pyright` | `uv sync --all-groups` (installs every group into the single `.venv`) | `.venv/bin/python` |
| **poetry** | `poetry add --group agent ipython pyright` | `poetry install --with dev,agent` (plus any optional groups); set `poetry config virtualenvs.in-project true` first if not already | `.venv/bin/python` (in-project) — or `$(poetry env info --path)/bin/python` (cached) |
| **hatch** | Edit `pyproject.toml` `[tool.hatch.envs.agent]` listing all runtime deps + `ipython` + `pyright` | Edit `[tool.hatch.envs.lsp]` listing all runtime + dev + agent + optional-feature deps; `hatch env create lsp` | `$(hatch env find lsp)/bin/python` (absolute, machine-local) |
| **conda / mamba** | `conda install -n <project>-agent -c conda-forge ipython pyright` | `conda create -n <project>-lsp -c conda-forge <all runtime + dev + agent + optional deps>` | `$(conda info --base)/envs/<project>-lsp/bin/python` (absolute, machine-local) |
| **pip + venv** | Activate `.venv-agent`, `pip install ipython pyright` | `python -m venv .venv-lsp && source .venv-lsp/bin/activate && pip install <all deps>` | `.venv-lsp/bin/python` |

**Why `pythonPath`, not `venvPath` + `venv`.** Pyright accepts
either form, but pixi / conda envs are not Python venv-style
(no `pyvenv.cfg`); `venvPath` + `venv` resolution can fail
silently on them. `pythonPath` points directly at the interpreter
and works uniformly. Sticking to a single form keeps the
substitution table simple.

## Why "run the script, don't retype"

Each script encodes per-manager footguns (poetry's
`virtualenvs.in-project`, hatch's no-composition, conda's
machine-local paths) that were learned the hard way. Re-typing the
commands by hand — especially for smaller / less-careful models —
is the named forbidden shortcut: each footgun missed produces a
silent failure mode the script catches.

Per-manager footgun catalogue: `references/per_manager_footguns.md`.

## Post-install: how to invoke the audit runner

```bash
# pixi
pixi run -e agent python \
  .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
  audit/<stem>.py

# uv
uv run --group agent python \
  .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
  audit/<stem>.py

# poetry
poetry run python \
  .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
  audit/<stem>.py

# hatch
hatch run agent:python \
  .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
  audit/<stem>.py

# conda
conda run -n <project>-agent python \
  .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
  audit/<stem>.py

# pip + venv
.venv-agent/bin/python \
  .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
  audit/<stem>.py
```

The runner now streams the digest to stdout by default. Pass a
second arg `<dst.md>` to also write to a file.

## `pyrightconfig.json` — bundled template

Lives at
`.agents/skills/python-env-manager/templates/pyrightconfig.json`.
One placeholder the install step substitutes:

- `<PYTHON_PATH>` — interpreter of the lsp env (manager-specific).

Other settings are fixed at the template:

- `include`: `src` / `tests` / `experiments` / `audit`
- `exclude`: `__pycache__` / `.pixi` / `scratch` / `reports`
- `typeCheckingMode`: `basic`
- `reportMissingImports`: `warning`
- `pythonVersion`: `3.11`

**Do NOT author from memory** — read the template, run the
per-manager substitution (the `sed` form shown in each subsection
works on Linux/macOS), copy to project root.

## Why pyright targets the `lsp` env, not the runtime env

The LSP must resolve EVERY import the user could write across
`src/` / `tests/` / `experiments/` / `audit/`. That set spans
runtime deps (in `default`), test deps (in `dev`), agent deps (in
`agent`), and every optional-feature dep. The `lsp` env is the
only env that composes all of them. Pointing pyright at any
narrower env produces false "unresolved import" warnings on
legitimate code.

## Cleanup — when the agent feature is removed

If the user wants to drop the audit / LSP flow:

```bash
# Remove the deps (manager-specific; example for pixi)
pixi remove --feature agent ipython pyright

# Remove the bundled config
rm ./pyrightconfig.json
```

Update `JOURNAL.md` Status to flip
`agent feature: installed → skipped — recorded: <date>`. Note in
the History or Status block that the audit + LSP flow was disabled.

## Verification — what must be true after install

Before handing back to the calling skill:

```bash
<activation> ipython -c "print(0)"
<activation> pyright --version
ls pyrightconfig.json
```

All three must succeed. If any fails, surface the failure to the
user verbatim — do not paper over with a partial install.
