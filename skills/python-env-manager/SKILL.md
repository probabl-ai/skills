---
name: python-env-manager
description: >
  Single source of truth for "which Python environment manager does
  this project use, and how do I install a package with it?". Owns
  the detection table (pixi / uv / poetry / hatch / conda+mamba /
  pip+venv), the install / remove / upgrade commands per manager,
  and the bootstrap path when no manager is in place (default
  recommendation: pixi). Stops at "the install command was issued
  with the right manager and the package is importable".

  TRIGGER when (any of these):
  (1) **about to install / add / pin / upgrade / remove a Python
      package** — `pip install`, `pixi add`, `uv add`, `poetry add`,
      `conda install`, etc. — under any framing;
  (2) `data-science-python-stack` § "Missing dependency" surfaced a
      missing import and an install is the next step;
  (3) a workflow skill's Stop condition fired on a missing
      dependency (`build-ml-pipeline`, `evaluate-ml-pipeline`,
      `organize-ml-workspace`);
  (4) starting a new Python project and no manager is in place yet
      (bootstrap with pixi unless the user picks otherwise).

  SKIP when: the project is non-Python; the install/add command is
  for a non-Python tool (npm, brew, apt, cargo, gem); the dependency
  is already installed and importable; the work is purely editing
  existing source code with no new dependency in play.

  HOW TO USE: **detect first, then install**. Run the § "Detection"
  table at the project root before issuing any install command. If
  no manager is detected, ask the user before bootstrapping. Never
  install with a different manager than the one the project uses
  (e.g., never `pip install` into a pixi-managed project) — that
  creates env state divergence the manifest won't track. **Read
  the "Stop conditions" block and emit the Pre-flight checklist as
  visible text in your response — both are mandatory before issuing
  any command.**
---

# Python Env Manager

Detect the env manager, install with the right command. Single
authority for `data-science-python-stack` and the workflow skills
when they need a dependency added.

## Stop conditions — read before anything else

- **Wrong-manager install is forbidden.** If the project uses pixi,
  do not `pip install`. If it uses poetry, do not `uv add`. If it
  uses uv, do not `poetry add`. Mixing managers creates environment
  state the project's manifest doesn't track, and the next
  `pixi install` / `poetry install` / `uv sync` will silently undo
  the install. Detection (below) is mandatory before any command.
- **No silent bootstrap.** If detection finds no manager, do not
  pick one and start installing. Ask the user; the default
  *recommendation* is pixi, but the user must approve before
  `pixi init` runs.
- **Environment / feature / group choice is asked, not assumed.**
  Before issuing **any** install command, ask the user where the
  package belongs — the default feature/env, an existing
  feature/env, or a new one — **unless the user has already told
  you in this conversation** (e.g. "add it to the `tracing`
  feature", "put this in dev"). Silently dumping new deps into the
  default environment is a frequent source of bloat and confusion
  (e.g., adding ML packages to a project where `default` was kept
  minimal because heavy deps live in a specialized feature). This
  rule applies to **every** manager — pixi features, uv groups,
  poetry groups, hatch envs, conda envs, pip venvs. See § "Where
  does the package belong?" for the per-manager question.
- **Don't pin without reason.** Install commands here add packages
  unpinned by default (matching `data-science-python-stack` §
  "Conventions"). Pin only when the user asks or there's a known
  incompatibility.
- **Don't run the bootstrap installer yourself.** When pixi (or any
  manager) is missing, surface the install command and let the
  user run it. `curl | sh` is a system-level action that needs the
  user's hands on it, not Claude's.

## Pre-flight — emit this checklist as visible text before any command

Before running an install / add / remove / upgrade command, output
this block verbatim. Each box must be backed by a real detection
step or an explicit decision documented in the response.

```
Pre-flight (python-env-manager):
- [ ] Detection done; manager identified: <pixi | uv | poetry | hatch
      | conda | pip+venv | none>
- [ ] If "none": user asked which manager to bootstrap (default
      recommendation: pixi)
- [ ] Existing environments / features / groups enumerated from the
      manifest (so the user has a real list to pick from)
- [ ] User asked WHERE the package belongs: default | <existing
      feature/env/group> | <new feature/env/group> — and answered.
      Skip ONLY if the user already told you in this conversation;
      record the source ("user said in turn N: ...").
- [ ] Install command syntax confirmed for that manager (see § "Install
      commands")
- [ ] Package list ready: <pkg-1, pkg-2, ...>
```

## Detection — figure out the manager first

Run these checks at the project root in order. **The first signal
that matches wins.** If multiple signals are present (a real
possibility — e.g. `pyproject.toml` + `pixi.toml`), surface the
ambiguity to the user before installing.

| Signal at project root | Manager | Notes |
|---|---|---|
| `pixi.toml` or `pixi.lock` | **pixi** | Default for this stack. Likely multi-feature. |
| `uv.lock`, or `pyproject.toml` with `[tool.uv]` | **uv** | Fast Rust-based manager. |
| `poetry.lock`, or `pyproject.toml` with `[tool.poetry]` | **poetry** | Common in older Python projects. |
| `hatch.toml`, or `pyproject.toml` with `[tool.hatch]` | **hatch** | Declarative; install flow varies — ask the user. |
| `environment.yml` (and `conda` / `mamba` on PATH) | **conda / mamba** | Heavy but common in scientific stacks. |
| `requirements.txt` + `.venv/` or `venv/` | **pip + venv** | Plain Python; least integrated. |
| None of the above | **(nothing detected)** | Ask the user. Default *suggestion*: pixi. |

Notes:
- A `pyproject.toml` with **only** `[build-system]` / `[project]` and
  no `[tool.X]` table for any manager is ambiguous. Don't infer a
  manager from `pyproject.toml` alone — ask.
- `hatch` is declarative: dependencies live in `[project]
  dependencies` or `[tool.hatch.envs.<env>.dependencies]` in
  `pyproject.toml`, and `hatch` re-syncs on next `hatch run`. If
  detected, ask the user how they prefer to add deps (edit
  `pyproject.toml` vs. another flow) — there's no universal `hatch
  add` command.
- If both `pixi.toml` and a `pyproject.toml` with another manager's
  `[tool.X]` are present, the project may be transitioning. Ask
  before picking.

## Where does the package belong? — ask before installing

Every manager in this skill supports **scoped** dependencies — pixi
features, uv groups, poetry groups, hatch envs, conda envs, pip
venvs. Picking the wrong scope is a real cost: ML deps dropped into
a `default` feature that the project deliberately kept slim, dev
tools polluting the runtime env, a heavy library installed into the
wrong conda env. **The user owns this decision.**

**Default rule:** before any install command, enumerate the
existing scopes from the manifest and ask the user where the
package(s) belong. Offer three branches: an existing scope, a new
scope (and ask for a name), or the default. **Skip the question
only when the user has already specified a scope in this
conversation** (e.g. "add it to the `tracing` feature", "put this
under dev"). When skipping, record the source in the Pre-flight
checklist ("user said in turn N: ...").

The exact question to ask, per manager:

| Manager | Existing scopes to enumerate | Question template |
|---|---|---|
| **pixi** | features in `pixi.toml` `[feature.X]` and environments in `[environments]` | "I see features `<list>`. Should `<pkg>` go into the default feature, an existing one (`<list>`), or a new feature (and what should it be named)?" |
| **uv** | groups in `[dependency-groups]` / `[tool.uv]` | "Should `<pkg>` be a runtime dep, a dev dep (`--dev`), or live in an optional group (existing: `<list>`, or a new one)?" |
| **poetry** | groups in `[tool.poetry.group.X]` | "Should `<pkg>` be a runtime dep, in `--group dev`, or in another group (existing: `<list>`, or a new one)?" |
| **hatch** | envs in `[tool.hatch.envs.X]` | "Should `<pkg>` go into the project's `[project] dependencies`, or into a hatch env (existing: `<list>`, or a new one)?" |
| **conda / mamba** | envs from `conda env list` (or those declared in `environment.yml`) | "Which conda env should `<pkg>` go into — the active one (`<name>`), another existing env (`<list>`), or a new env (and what should it be named)?" |
| **pip + venv** | venvs visible at the project root (`.venv/`, `venv/`, etc.) | "Should `<pkg>` go into the existing venv (`<path>`), or into a new venv (and where)?" |

If the manifest lists no scopes (a fresh `pixi.toml` with only
`[dependencies]`, a `pyproject.toml` with no groups), you can offer
"default" + "create a new <feature/group/env>" and skip
enumeration.

**Why this matters.** The manifest is the project's contract. Every
new dep nudges the contract; doing it without the user makes the
contract drift in ways the user has to discover later. Asking is
cheap; reverting is not (especially with `pixi remove --feature`,
`poetry remove --group`, or undoing a conda env mutation).

## Install commands — by manager

Once detected, use *only* the matching commands. Do not mix.

### pixi

Default for this stack. Pixi organizes deps per **feature**
(e.g. `default`, `dev`, `tracing`). **Before running any
`pixi add`, ask the user which feature the package belongs in** —
see § "Where does the package belong?" for the question template.
Enumerate the existing features from `pixi.toml` first so the user
has a concrete list.

| Action | Command |
|---|---|
| Add to default feature | `pixi add <pkg>` |
| Add to a specific feature | `pixi add --feature <feature> <pkg>` |
| Add to a specific environment | `pixi add -e <env> <pkg>` |
| Remove | `pixi remove <pkg>` (or `--feature <feature>`) |
| Upgrade | `pixi upgrade <pkg>` |
| Run inside an env | `pixi run -e <env> <command>` |
| Sync env from manifest | `pixi install` |

A real-world example: in some projects `mlflow` lives in a
`tracing` feature, not `default` — silently dropping it into
`default` would have been wrong. Always ask.

### uv

**Before running any `uv add`, ask the user whether the package is
a runtime dep, a dev dep (`--dev`), or belongs to an optional
group** — see § "Where does the package belong?". Enumerate
existing groups from `pyproject.toml` (`[dependency-groups]` or
`[project.optional-dependencies]`) so the user has a real list.

| Action | Command |
|---|---|
| Add a runtime dep | `uv add <pkg>` |
| Add a dev dep | `uv add --dev <pkg>` |
| Add to an optional group | `uv add --optional <group> <pkg>` |
| Remove | `uv remove <pkg>` |
| Upgrade a single pkg | `uv lock --upgrade-package <pkg>` |
| Run inside the env | `uv run <command>` |
| Sync env from manifest | `uv sync` |

### poetry

**Before running any `poetry add`, ask the user whether the package
is a runtime dep, in `--group dev`, or in another group** — see §
"Where does the package belong?". Enumerate existing groups from
`pyproject.toml` (`[tool.poetry.group.X]`) so the user has a real
list.

| Action | Command |
|---|---|
| Add a runtime dep | `poetry add <pkg>` |
| Add a dev dep | `poetry add --group dev <pkg>` |
| Add to a named group | `poetry add --group <name> <pkg>` |
| Remove | `poetry remove <pkg>` |
| Upgrade | `poetry update <pkg>` |
| Run inside the env | `poetry run <command>` |
| Sync env from manifest | `poetry install` |

### hatch

Hatch is declarative. There is no universal `hatch add`. **Before
editing `pyproject.toml`, ask the user whether the package should
go into project-level deps or an env-specific section** — see §
"Where does the package belong?". Enumerate existing envs from
`[tool.hatch.envs.X]` so the user has a real list.

Standard flow:

1. Edit `pyproject.toml`:
   - Project-level dep → add to `[project] dependencies`.
   - Env-specific dep → add to
     `[tool.hatch.envs.<env>.dependencies]`.
2. Re-sync the env: `hatch env prune` (optional, removes stale
   envs), then any `hatch run -e <env> <command>` re-creates it.

### conda / mamba

`mamba` is a faster drop-in replacement for `conda`. Prefer it if
both are on PATH.

**Before running any `conda install` / `mamba install`, ask the
user which env the package belongs in** — see § "Where does the
package belong?". Enumerate envs with `conda env list` (or read
the `name:` field from `environment.yml`) so the user has a real
list. Defaulting to the active env without asking can pollute a
shared base environment.

| Action | Command |
|---|---|
| Add a dep (conda-forge channel) | `conda install -n <env> -c conda-forge <pkg>` |
| Same with mamba | `mamba install -n <env> -c conda-forge <pkg>` |
| Remove | `conda remove -n <env> <pkg>` |
| Sync from `environment.yml` | `conda env update -f environment.yml --prune` |

If `environment.yml` is the source of truth for the project, edit
it and run the `env update` rather than installing one-off; this
keeps the manifest in sync.

### pip + venv

The least-integrated path. There is no manifest update — `pip
install` mutates the live env without tracking.

**Before running any `pip install`, ask the user whether the
package goes into the existing venv or a new one** — see § "Where
does the package belong?". List visible venvs at the project root
(`.venv/`, `venv/`, etc.) so the user can pick. Don't activate and
install silently — even with pip, the choice of which venv to
mutate is the user's.

Steps:

1. Activate the venv: `source .venv/bin/activate` (Linux/macOS) or
   `.venv\Scripts\activate` (Windows).
2. Install: `pip install <pkg>`.
3. If `requirements.txt` is the project's manifest, regenerate or
   edit it — `pip freeze > requirements.txt` is one option, but
   it captures all transitive pins; for a tighter diff, edit the
   file by hand to add the new top-level dep.

Surface to the user that `pip install` alone leaves no audit trail.
If the project is fresh, offer migration to a managed alternative
(pixi by default).

## Bootstrap — when no manager is detected

If detection found nothing **and the user agrees to use pixi**:

1. Check whether pixi is on PATH: `command -v pixi`.
2. If pixi is not installed, surface the install command and **ask
   the user to run it** (do not run `curl | sh` yourself):
   - Linux/macOS: `curl -fsSL https://pixi.sh/install.sh | sh`
   - Windows: `iwr -useb https://pixi.sh/install.ps1 | iex`
3. Once pixi is available, initialize: `pixi init` (creates
   `pixi.toml` in the current directory).
4. **Ask the user how to organize features** before adding any
   deps: a single `default` feature for everything, or split (e.g.
   `default` for runtime + `dev` for dev tools, or `core` +
   `tracing` if mlflow / observability is in scope). The skill's §
   "Where does the package belong?" rule applies even at bootstrap
   — defaulting to a single feature without asking sets a layout
   the user has to migrate later.
5. Add the relevant Tier 1 deps for an ML project (per
   `data-science-python-stack` § "Tier 1") into the chosen
   feature: `pixi add [--feature <name>] scikit-learn skrub skore
   ruff`. Ruff is mandatory — it's the canonical lint+format tool,
   owned downstream by the `python-code-style` skill — and goes
   into the same feature as the rest of the Tier 1 stack so a
   single `pixi run` activation has everything Claude needs.
6. Ask the user about the tabular-library choice (per
   `organize-ml-workspace` § "Stop conditions" — pandas vs polars)
   and which feature it belongs in. Add accordingly:
   `pixi add [--feature <name>] pandas pyarrow` or
   `pixi add [--feature <name>] polars`.

If the user wants a different manager (uv / poetry / hatch / conda),
mirror the same flow with that manager's init command (`uv init`,
`poetry init`, `conda env create -f environment.yml`, etc.) — and
apply § "Where does the package belong?" at every install step.

## Cross-references

This skill is the install layer for the rest of the stack. Invoke it
whenever those skills surface a missing dependency or a new install:

- **`data-science-python-stack`** — owns *what* to install (Tier 1
  mandatory, Tier 2 user choice, Tier 3 optional). When that skill
  decides a package is needed, this skill turns the decision into
  the right shell command.
- **`organize-ml-workspace`** — its Stop condition "Tabular library
  is asked, not assumed" produces a pandas-vs-polars decision; this
  skill executes the install.
- **`build-ml-pipeline`** / **`evaluate-ml-pipeline`** — their Stop
  conditions on missing `skrub` / `skore` redirect here for the
  install command. Their Pre-flight checklists include "Tier 1
  importable"; if a box fails, this skill is the next step.

## Conventions

- **One install operation per response.** Don't batch unrelated
  packages into one command. Group related packages (Tier 1
  bootstrap, or a single feature's deps) and confirm before
  continuing.
- **No `--no-deps` or version pins by default.** Match
  `data-science-python-stack` § "Conventions". Pin only on user
  request or known incompatibility.
- **Surface, don't bypass.** If an install fails (network, version
  conflict, missing channel), surface the error and the command —
  don't try alternative managers as a workaround. Wrong-manager
  workarounds are a Stop-condition violation.
