---
name: setup-python-env
description: >
  Bootstrap a Python environment manager and three named envs
  (default runtime, agent tools, composed dev). Detect with
  `python -m skore_skills env detect`, persist manager and
  `env.managed`, then `env init --manager`, `env sync --execute`,
  install Skore for a recorded `hub` or `mlflow` destination
  (plain Skore when that destination is unset or `local`), and
  `env verify --execute`. Does not add other stage ML libraries.

  TRIGGER when the user asks for the env manager, pixi, uv, or a
  Python environment, or when no environment manager is recorded
  yet.

  SKIP adding later packages — load add-python-package.
  SKIP scaffolding src/ — that is setup-workspace.

  HOW TO USE: detect, ask managed vs user-managed, ask the
  manager when needed, then env init, env sync, add Skore for
  the recorded hub or mlflow destination (plain Skore when that
  is unset or local), and env verify.
---

# Set Up Python Environment

Bootstrap only. Direct packages this turn: `ruff`, `ipython`,
`ipykernel`, and plain `skore`. Skore supplies `skore-skills` as a
mandatory dependency. Other stage libraries go through
`add-python-package`.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Ask which manager to use and whether we manage the env in
plain language. Do not name `G-ENV-MGR`, skill ids, or the
wrapper CLI to the user. Do not mention `skore-skills`.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] env detect + status
- [ ] G-ENV-MGR: ask if none / ambiguous / mismatch; else keep recorded
- [ ] env.managed: ask (default true) and persist
- [ ] unmanaged → stop | managed → env init, env sync, add-skore (no --mode), env verify
```

## Not this skill

A request to add a package outside `ruff`, `ipython`, `ipykernel`,
and plain `skore` is not bootstrap. Do not `env init` and do not
`pixi add`. Hand that package to the package-install step and
stop. The close names the package and that step in plain language.
Do not write the catalog id.

## Sequence

1. `python -m skore_skills env detect` and `status`.
2. **G-ENV-MGR.** Read the JSON fields, not sentinel strings:
   ask when `env_manager` is `"none"`, `ambiguous` is true, or
   `mismatch` is true. Use `recommended` as the ask order. PATH is
   not permission. Do not `curl | sh`.
3. Ask whether **we** manage the env (default yes). Persist
   `python -m skore_skills policy set env.managed true` or `false`.
4. Unmanaged: stop. Name ruff / ipython / ipykernel / skore; do
   not init. Do not mention `skore-skills` to the user.
5. Managed: `policy set env_manager <manager>`, then

   ```bash
   python -m skore_skills env init --manager <manager>
   python -m skore_skills env sync --execute
   python -m skore_skills env add-skore --execute
   python -m skore_skills env verify --execute
   ```

   Do not pass `--mode`. Omitting it installs for a recorded
   `hub` or `mlflow` destination, and plain Skore otherwise.

   If the selected manager is pixi and `pixi.toml` already exists,
   skip `env init`; preserve that manifest and continue with
   `env sync --execute`. Never replace it or try to add
   `[tool.pixi]` to `pyproject.toml`.

   Do not hand-edit TOML. Do not run `pixi init`. Do not create
   `src/`. Do not ask where reports go. Plain Skore is the early
   install when no destination is recorded; `add-python-package`
   upgrades it for Hub or MLflow after that choice is recorded.
   Do not pass `--mode local`.
   If verify reports missing `skore` or `skore_skills`, rerun
   `env add-skore --execute` the same way; never add `skore-skills`
   directly. If verify reports missing agent tools, load
   `add-python-package` for ruff / ipython / ipykernel (agent feature)
   when that skill is installed, not a second `env init`.
   If `add-python-package` is not installed, name ruff / ipython /
   ipykernel and stop.

## Return and close

When dispatched by `setup-ml-project`, return to that caller after
verification. Standalone, run
`python -m skore_skills git end-turn --stage setup`. If JSON
`action` is `invoke`, load `persist-ml-git` only if
`status.skills.persist-ml-git` is true and stop; that skill
returns to triage. If persist is missing, name the pending
`staged` paths and stop. Otherwise load `triage-ml-task` only if
`status.skills.triage-ml-task` is true; else stop.

## Three environments

Agent context only; do not narrate `skore-skills` to the user.

- **default** — project runtime; bootstrap installs plain `skore`,
  which supplies `skore-skills`, when the report destination is
  unset or `local`. A recorded `hub` or `mlflow` destination uses
  that install instead.
- **agent** — ruff, ipython, ipykernel.
- **dev** — default + agent. Every later `python -m skore_skills`
  command uses this composed environment; `env verify --execute`
  must pass before other skills run.
