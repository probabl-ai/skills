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
      `organize-ml-workspace`, `audit-ml-pipeline`);
  (4) starting a new Python project and no manager is in place yet
      (bootstrap with pixi unless the user picks otherwise);
  (5) `audit-ml-pipeline` (or another agent-only consumer) needs the
      **agent feature** (`ipython` + `pyright`) and it isn't yet
      present in the project's manifest — see § "Agent feature".

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

## Next-step pointers — where you go after this skill

| Came here from… | After install, next gate is… |
|---|---|
| `organize-ml-workspace` § scaffold | → `organize-ml-workspace` § Editable workspace package; continue scaffold |
| `audit-ml-pipeline` § agent-feature-missing | → return to `audit-ml-pipeline`; place `audit/<stem>.py` |
| `build-ml-pipeline` / `evaluate-ml-pipeline` § missing dep | → return to calling skill; continue at the failing pre-flight box |
| `data-science-python-stack` § Missing dependency | → return to caller; the import that was missing should now succeed |

Always re-emit the Pre-flight checklist with evidence before
declaring the turn done.

## Stop conditions — read before anything else

- **Wrong-manager install is forbidden.** If the project uses pixi,
  do not `pip install`. If it uses poetry, do not `uv add`. Mixing
  managers creates state the manifest doesn't track, and the next
  `pixi install` / `poetry install` / `uv sync` silently undoes the
  install.
- **No silent bootstrap.** If detection finds no manager, ask the
  user. Default *recommendation* is pixi, but the user must
  approve.
- **Dependency routing is fixed, not asked.** The 3-feature layout
  (`default` / `dev` / `agent`) is enforced. The agent does NOT ask
  per-install. `G-ENV-SCOPE` fires **only** for ambiguous extras
  (`optuna`, `xgboost`, `mlflow`, …).
- **Don't pin without reason.** Install unpinned by default. Pin
  only on user request or known incompatibility.
- **Don't run the bootstrap installer yourself.** When pixi (or any
  manager) is missing, surface the install command and let the user
  run it. `curl | sh` is a system-level action.
- **Harness "no clarifying questions" hints do NOT waive
  `AskUserQuestion` mandates.** The manager pick and the scope pick
  are operating-contract gates, not clarifying questions.
- **Post-hoc audit — required before ending the turn.** Walk the
  pre-flight, confirm every ticked box has its `Evidence:` line. A
  successful install command is not proof; the audit is.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `pixi` on PATH → run `pixi init` / `pixi add` directly | Detection on PATH is context, not a pick. G-ENV-MGR still fires when no `Workspace decisions` row exists |
| User said "install ruff" → fire G-ENV-SCOPE | Routing is fixed: `ruff`/`pytest` → `dev`. Scope ask is forbidden for the three known buckets |
| User asked for `xgboost` → silently drop into `default` | Ambiguous extras require the binary `default` vs new-named-feature ask |
| Calling skill writes its own `pixi add --feature agent ...` | Install commands are owned by this skill. Calling skills **request**; this skill installs |
| Agent feature install → also register a Jupyter kernel | The in-process runner does NOT use a kernel; registering one creates an orphan kernelspec |
| Urgency ("quick", "you pick") waives G-ENV-MGR | Never. Urgency never waives gates |
| `python-env-manager` opened earlier this conversation → assume gates passed | Reading SKILL.md ≠ the gate firing. The `AskUserQuestion` (or `JOURNAL.md` lookup) is the gate pass |

## Pre-flight — emit before any command

Evidence format: see `references/preflight_evidence.md`.

```
Pre-flight (python-env-manager):
- [ ] Sibling SKILL.md files opened this turn:
      data-science-python-stack, iterate-ml-experiment,
      organize-ml-workspace
      Evidence: Read .agents/skills/<each>/SKILL.md (this turn)
- [ ] `journal/JOURNAL.md` Status `Workspace decisions` block read
      this turn for `env manager:` and `agent feature:` rows.
      Evidence: lists each row's value or "not recorded yet" |
                "n/a — JOURNAL.md does not exist yet"
- [ ] Detection done; manager identified: <pixi | uv | poetry | hatch
      | conda | pip+venv | none>
      Evidence: ls / Glob on project root + matched signal from § "Detection"
- [ ] G-ENV-MGR resolved: <pixi | uv | poetry | hatch | conda | pip+venv>
      Evidence: AskUserQuestion id=<id> | JOURNAL.md Status (recorded YYYY-MM-DD) |
                "detection returned a single manager; manifest commits the project"
- [ ] Dep category determined for each package:
      runtime → default | dev → dev | agent → agent |
      ambiguous → G-ENV-SCOPE binary ask
      Evidence: explicit categorization in this turn's response
- [ ] G-ENV-SCOPE resolved ONLY for ambiguous extras
      Evidence: AskUserQuestion id=<id> | user quote turn N |
                "n/a — package routes automatically"
- [ ] (Agent-feature installs only) G-AGENT-FEATURE resolved: install | skipped
      Evidence: AskUserQuestion id=<id> | JOURNAL.md Status (recorded YYYY-MM-DD) |
                "n/a — not an agent-feature install"
- [ ] Install command syntax confirmed for that manager (see § "Install commands")
      Evidence: cite the matching subsection
- [ ] Package list ready: <pkg-1, pkg-2, ...>
      Evidence: explicit list in this turn's response
- [ ] (Agent-feature installs only) `pyrightconfig.json` drop step queued
      Evidence: Read templates/pyrightconfig.json (this turn) + Write to project root
                | "n/a — not an agent-feature install"
                | "n/a — pyrightconfig.json already at project root"
- [ ] (Agent-feature installs only) Verification commands queued
      Evidence: commands quoted in this turn's response | "n/a"
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this same checklist appears in the end-of-turn summary.
```

## Detection — first signal wins

| Signal at project root | Manager | Notes |
|---|---|---|
| `pixi.toml` or `pixi.lock` | **pixi** | Default for this stack |
| `uv.lock`, or `pyproject.toml` `[tool.uv]` | **uv** | Fast Rust-based |
| `poetry.lock`, or `pyproject.toml` `[tool.poetry]` | **poetry** | Common in older projects |
| `hatch.toml`, or `pyproject.toml` `[tool.hatch]` | **hatch** | Declarative; flow varies — ask |
| `environment.yml` + `conda`/`mamba` on PATH | **conda / mamba** | Scientific stacks |
| `requirements.txt` + `.venv/` or `venv/` | **pip + venv** | Least integrated |
| None of the above | **(nothing detected)** | Ask the user; default *suggestion*: pixi |

Notes:
- `pyproject.toml` with only `[build-system]` / `[project]` and no
  `[tool.X]` is ambiguous — ask, don't infer.
- Multiple signals (e.g. `pixi.toml` + `[tool.poetry]`): surface the
  ambiguity before picking.

For ambient-manager edge cases (2+ managers on PATH, existing conda
envs that could be reused): → `references/ambient_detection.md`.

→ next: G-ENV-MGR (below).

## Gates this skill owns

### `G-ENV-MGR` — which manager

**Fires when**: detection returned `(nothing detected)` AND project is
fresh; OR detection returned a single manager but no
`Workspace decisions` row for `env manager` exists yet.

**AskUserQuestion**: single pick — the manager. Options from the
detection table. Default *recommendation* on nothing-detected:
`pixi`. Free-text resolves only when it names a listed manager.

**Persists**: `env manager: <pick> — recorded: <date>` in
`journal/JOURNAL.md` Status `Workspace decisions`.

→ next: § "Install commands — by manager".

### `G-ENV-SCOPE` — only for ambiguous extras

**Fires when**: a requested dep doesn't match the § "Auto-routing
table" below (e.g. `optuna`, `xgboost`, `mlflow`).

**AskUserQuestion (binary)**:
1. **`default`** — fold into runtime deps. Pick when the dep IS a
   runtime concern.
2. **New named feature `<X>`** — propose a name from the user's
   wording (`tracing` for `mlflow`, `tuning` for `optuna`, `dl` for
   `torch`). Pick when the dep is a tier-shift to feature-flag.

Free-text resolution: explicit `default` or a feature name resolves;
"you pick" / "doesn't matter" does NOT.

#### When `default` is picked

One step: `pixi add <pkg>` (no `--feature` flag → lands in
`default`).

→ next: return to caller skill.

#### When a new named feature `<X>` is picked — 6 steps, all required

**This is the load-bearing procedure smaller models forget.** Step
3 specifically is the one that silently breaks LSP integration.

1. **Install into the new feature**: `pixi add --feature <X> <pkg>`
   (manager-equivalents: `uv add --group <X> <pkg>`,
   `poetry add --group <X> <pkg>`).
2. **Confirm the feature block exists** in the manifest.
3. **APPEND `<X>` to the `lsp` env's features list** —
   per-manager:
   - **pixi**: edit `pixi.toml` `[environments]`,
     `lsp = { features = [..., "<X>"], ... }`.
   - **uv / poetry**: nothing extra (`--all-groups` / `--with` covers).
   - **hatch / conda / pip+venv**: re-author the lsp env's dep list.
4. **Re-sync the lsp env**: pixi → `pixi install -e lsp`; uv →
   `uv sync --all-groups`; poetry → `poetry install --with <X>`;
   others → re-create.
5. **Update `JOURNAL.md`**: append `<X>` to the
   `optional features:` row.
6. **Verify**: `bash .agents/skills/python-env-manager/scripts/verify_layout.sh`.
   Exit 0 = consistent. Exit 1 = drift, with remediation lines.

Skipping step 3 or 4 → the package installs into `<X>` but pyright
doesn't index it because `lsp` doesn't compose `<X>`. User sees
"unresolved import" on legitimate code.

→ next: return to caller skill.

### `G-AGENT-FEATURE` — install ipython + pyright

**Fires when**: an agent-only consumer (currently `audit-ml-pipeline`)
needs `ipython` / `pyright` and the manifest doesn't expose them.

**AskUserQuestion (binary)**: `install` | `skip`.
- `install` → run the bundled per-manager script (see § "Agent
  feature install"). Recommended default for any workspace using
  the audit flow.
- `skip` → block the calling skill; surface "audit step unavailable
  until the agent feature is installed". No silent degradation.

**Persists**: `agent feature: <installed | skipped> — recorded: <date>`.

There is no kernel registration. The audit runner is in-process.
The `agent kernel:` row in `Workspace decisions` is no longer
collected for new workspaces; legacy rows are informational.

→ next: § "Agent feature install" if `install`.

### Persistence lookup — read JOURNAL.md before any gate fires

Read `Workspace decisions` first:

- `env manager: <pixi | uv | poetry | hatch | conda | pip+venv> — recorded: <date>`
- `agent feature: <installed | skipped> — recorded: <date>`
- `optional features: <name1, name2, ... | none> — recorded: <date>`

If a row is recorded, **do not re-ask** — cite
`JOURNAL.md Status (Workspace decisions, recorded YYYY-MM-DD)` as
the evidence for that row in the pre-flight.

If `journal/JOURNAL.md` doesn't exist yet (truly fresh project
before `organize-ml-workspace`), the gates fire fresh and answers
land in `Workspace decisions` once `iterate-ml-experiment` writes
the JOURNAL.

## Where does the package belong? — 3-feature layout

### The fixed buckets

| Bucket | Contents | Composes with | Purpose |
|---|---|---|---|
| `default` | `scikit-learn`, `skrub`, `skore`, tabular lib, editable `<pkg>` | (itself) | runtime |
| `dev` | `ruff`, `pytest` | `default + dev` | lint / test |
| `agent` | `ipython`, `pyright` | `default + agent` | audit runner + pyright CLI |
| `lsp` | (no own deps) | `default + dev + agent + <all optional>` | LSP integration |

Pixi composed-envs declaration:
```toml
[environments]
default = { features = ["default"], solve-group = "default" }
dev     = { features = ["default", "dev"],          solve-group = "default" }
agent   = { features = ["default", "agent"],        solve-group = "default" }
lsp     = { features = ["default", "dev", "agent"], solve-group = "default" }
```

### Auto-routing table — no ask

| Package | Routes to |
|---|---|
| `scikit-learn`, `skrub`, `skore` (or `skore[hub]`) | `default` |
| `pandas` + `pyarrow` OR `polars` | `default` |
| `ruff`, `pytest` | `dev` |
| `ipython`, `pyright` | `agent` |
| The editable workspace package (`<pkg> @ .`) | `default` |

Ambiguous → `G-ENV-SCOPE` fires.

Rationale (why `lsp` is separate, optional-feature growth model):
→ `references/composition_model.md`.

## Install commands — by manager

Once detected, use ONLY the matching commands. Per-manager
extended prose (the "why" + caveats per row) lives in
`references/install_commands_anatomy.md`.

### pixi

| Action | Command |
|---|---|
| Add to default | `pixi add <pkg>` |
| Add to a feature | `pixi add --feature <feature> <pkg>` |
| Add to an env | `pixi add -e <env> <pkg>` |
| Remove | `pixi remove <pkg>` (or `--feature <feature>`) |
| Upgrade | `pixi upgrade <pkg>` |
| Run inside env | `pixi run -e <env> <command>` |
| Sync from manifest | `pixi install` |

### uv

`default` → `[project] dependencies`; `dev` → `--group dev`;
`agent` → `--group agent`; optional features → `--group <name>`.

| Action | Command |
|---|---|
| Add runtime | `uv add <pkg>` |
| Add dev | `uv add --dev <pkg>` |
| Add to group | `uv add --optional <group> <pkg>` |
| Remove | `uv remove <pkg>` |
| Upgrade | `uv lock --upgrade-package <pkg>` |
| Run inside env | `uv run <command>` |
| Sync | `uv sync` (use `--all-groups` to cover dev+agent+optional) |

### poetry

`default` → `[tool.poetry.dependencies]`; `dev` → `--group dev`;
`agent` → `--group agent`; optional → `--group <name>`.

| Action | Command |
|---|---|
| Add runtime | `poetry add <pkg>` |
| Add dev | `poetry add --group dev <pkg>` |
| Add to group | `poetry add --group <name> <pkg>` |
| Remove | `poetry remove <pkg>` |
| Upgrade | `poetry update <pkg>` |
| Run | `poetry run <command>` |
| Sync | `poetry install` |

### hatch

Declarative — no universal `hatch add`. Edit
`pyproject.toml`:`[project] dependencies` or
`[tool.hatch.envs.<env>.dependencies]`, then any
`hatch run -e <env> <command>` re-creates the env. Caveat: hatch
envs do not compose; each non-default env duplicates runtime deps.

### conda / mamba

No native feature concept; map buckets to named envs
(`<project>`, `<project>-dev`, `<project>-agent`).

| Action | Command |
|---|---|
| Add (conda-forge) | `conda install -n <env> -c conda-forge <pkg>` |
| With mamba | `mamba install -n <env> -c conda-forge <pkg>` |
| Remove | `conda remove -n <env> <pkg>` |
| Sync from yml | `conda env update -f environment.yml --prune` |

### pip + venv

Least-integrated. No manifest update — `pip install` mutates the
live env without tracking. Recommend migration to a managed
alternative.

Editable workspace install (`src/<pkg>/`) per manager:
→ `references/editable_workspace.md`.

## Agent feature install

The agent feature = project-scoped install of `ipython` + `pyright`
+ the bundled `pyrightconfig.json` (substituting `<PYTHON_PATH>`
for the lsp env's interpreter).

### Bundled scripts — one per manager

| Manager | Invocation | Args |
|---|---|---|
| **pixi** | `bash .agents/skills/python-env-manager/scripts/install_agent_feature_pixi.sh` | none |
| **uv** | `bash .agents/skills/python-env-manager/scripts/install_agent_feature_uv.sh` | none |
| **poetry** | `bash .agents/skills/python-env-manager/scripts/install_agent_feature_poetry.sh` | none |
| **hatch** | `bash .agents/skills/python-env-manager/scripts/install_agent_feature_hatch.sh` | none (requires user-authored `[tool.hatch.envs.agent]` + `[tool.hatch.envs.lsp]`) |
| **conda** | `bash .agents/skills/python-env-manager/scripts/install_agent_feature_conda.sh <project-name>` | project name |
| **pip+venv** | `bash .agents/skills/python-env-manager/scripts/install_agent_feature_pip_venv.sh <requirements-file>` | requirements file |

**Run the script, don't retype.** Each script encodes per-manager
footguns (poetry's `virtualenvs.in-project`, hatch's no-composition,
conda's machine-local paths). Re-typing by hand is the named
forbidden shortcut.

Per-script anatomy (the 4 actions inside, post-install runner
invocation, cleanup, verification):
→ `references/agent_feature_anatomy.md`.

Per-manager footguns:
→ `references/per_manager_footguns.md`.

→ next: return to caller (typically `audit-ml-pipeline`).

## Tier 1 install: skore variant per mode

Read `skore mode:` from `journal/JOURNAL.md` Status
`Workspace decisions` (set by `organize-ml-workspace` §
G-SKORE-MODE):

| `skore mode:` | Install command |
|---|---|
| `local` | Plain `skore` package (`pixi add skore` / `uv add skore` / `poetry add skore` / …) |
| `hub` | `skore[hub]` extra (`pixi add "skore[hub]"` / `uv add "skore[hub]"` / `poetry add "skore[hub]"` / …) |

If the row is absent (workspace not yet bootstrapped through
`organize-ml-workspace`), route back to that skill's G-SKORE-MODE.
Do not guess.

**Forbidden**: silently picking `skore[hub]` "to be safe". The
`[hub]` extra costs ~20 MB of network deps + auth infra the
local-mode user didn't ask for.

Why the variant matters, mode-switching procedure:
→ `references/skore_variant.md`.

## Bootstrap — when no manager is detected

If detection found nothing AND the user picked `pixi` via G-ENV-MGR:

1. Check `command -v pixi`; surface install URL if missing.
2. `pixi init`.
3. Edit `pixi.toml`: declare 3 features (`default` / `dev` /
   `agent`) + 4 envs (`default` / `dev` / `agent` / `lsp`).
4. Add Tier 1 deps to `default` (per G-SKORE-MODE: plain `skore`
   for local, `"skore[hub]"` for hub).
5. Add tabular lib (per G-TABULAR: `pandas pyarrow` or `polars`).
6. Wire editable workspace package
   (`pixi add --pypi "<pkg> @ ."` then edit to
   `<pkg> = { path = ".", editable = true }`; then `pixi install`).
7. Drop `pyrightconfig.json` via `sed`-substitution of
   `<PYTHON_PATH>` for `.pixi/envs/lsp/bin/python`.
8. Sync all 4 envs: `pixi install` then `pixi install -e dev` /
   `-e agent` / `-e lsp`.

Full step-by-step with exact pixi.toml block, manager-equivalent
flows, pixi-version compatibility notes:
→ `references/bootstrap.md`.

→ next: return to `organize-ml-workspace` § scaffold.

## Companion skills

| Skill | Relationship |
|---|---|
| `data-science-python-stack` | Owns *what* to install; this skill turns it into a command |
| `organize-ml-workspace` | Scaffold hands off here for editable install; G-TABULAR / G-SKORE-MODE feed this skill's bootstrap |
| `audit-ml-pipeline` | G-AGENT-FEATURE fires from there |
| `build-ml-pipeline` / `evaluate-ml-pipeline` | Missing-dep Stop conditions redirect here |
| `iterate-ml-experiment` | Owns the `Workspace decisions` block this skill reads / writes |

## Conventions

- **One install operation per response.** Don't batch unrelated
  packages. Group related (Tier 1 bootstrap, or a single feature's
  deps) and confirm before continuing.
- **No `--no-deps` or version pins by default.** Pin only on
  user request or known incompatibility.
- **Surface, don't bypass.** If an install fails, surface the error
  + command. Don't try alternative managers as a workaround —
  that's a Stop-condition violation.
