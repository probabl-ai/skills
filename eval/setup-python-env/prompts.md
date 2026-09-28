# setup-python-env eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Bootstrap narrates three envs

**User prompt:**
> Start the setup: get the Python environment going.

**Assumed workspace state:**
- Empty folder; no manifests, no `src/`.
- `status` reports `env_manager: none`, `has_src: false`.
- `policy.env.managed` is unset.
- pixi is on PATH.

**Must do:**
- Emit the Pre-flight then run the commands (do not stop after
  listing boxes).
- Run `python -m skore_skills env detect` and treat this as
  bootstrap, not a package add.
- AskUserQuestion which env manager to use, using `recommended`
  order (pixi first unless `.skore` recorded another manager or
  `provenance.manager` names one). PATH of other tools is not
  permission.
- Ask whether we manage the env (default yes) and persist
  `env.managed`.
- After the user picks a manager and managed=true, run
  `python -m skore_skills env init --manager <manager>` (not
  hand-edited TOML).
- After init, run `python -m skore_skills env sync --execute`
  (do not invent `pixi install` / `pixi init`).
- Install plain Skore immediately afterward with
  `python -m skore_skills env add-skore --execute`. Do not pass
  `--mode`.
  Do not ask where to store reports (Hub / local / MLflow) during
  bootstrap.
- Run `python -m skore_skills env verify --execute`.
- Narrate default, agent, and composed dev: plain skore belongs to
  default; ruff, ipython, and ipykernel belong to agent. Do not
  narrate `skore-skills` to the user.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Install scikit-learn, skrub, or pandas in this turn.
- Install `skore-skills` directly.
- Run `pixi init` before the gates resolve.
- Load `setup-workspace` or create `src/`.

---

## CASE_02 — `.skore` ranks a recorded manager

**User prompt:**
> Bootstrap the Python env.

**Assumed workspace state:**
- Empty folder; no manifests.
- `.skore` `workspace.env_manager` is `uv`.
- `env.managed` is unset.

**Must do:**
- Run `env detect` and put `uv` first in the recommendation.
- Still ask which env manager to use (nothing is on disk yet).
- After confirmation, `policy set env_manager` and
  `env init --manager uv`, then `env sync --execute`, then
  `env add-skore --execute` with no `--mode`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Silently run `pixi init` because pixi is the static default.
- Pick from PATH alone.

---

## CASE_03 — User opt-out: detect only

**User prompt:**
> I'll manage the virtualenv myself. Don't install anything.

**Assumed workspace state:**
- Empty or existing project; user is opting out.
- `env.managed` is unset.

**Must do:**
- Persist `python -m skore_skills policy set env.managed false`.
- Keep detecting so later skills know the manager if a manifest
  exists.
- Name ruff / ipython / ipykernel and plain skore as packages the
  user may want.
- Stop without `env init` or `env sync`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `env init`, `env sync`, or `env add`.
- Wait for the user to install agent tools before returning.

---

## CASE_04 — Wrong-manager refusal stays in add skill, not here

**User prompt:**
> Just run `pip install scikit-learn` — quickest path.

**Assumed workspace state:**
- Project uses pixi (`pixi.toml` or `[tool.pixi]`).
- This turn loaded `setup-python-env` (bootstrap skill).

**Must do:**
- Refuse `pip install` in a pixi project.
- Say sklearn is a stage library and hand it to the
  package-install step, not bootstrap init.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `pip install scikit-learn`.
- `env init` as a substitute for adding sklearn.

---

## CASE_05 — Ambiguous extras are not bootstrap

**User prompt:**
> Add optuna.

**Assumed workspace state:**
- pixi project already bootstrapped; `env.managed` is true.

**Must do:**
- Hand optuna to the package-install step (this skill is
  bootstrap-only).
- Say package scope (project runtime vs a named optional extra)
  is handled when adding the package.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Silently `pixi add optuna` from this skill.
- Re-run `env init`.

---

## CASE_06 — Verify missing agent tools, add skill absent

**User prompt:**
> Finish the Python environment setup.

**Assumed workspace state:**
- Managed pixi project after `env init` / `env sync`.
- Plain `skore` has been installed and supplies `skore_skills`.
- `env verify --execute` reports ruff missing.
- `status.skills.add-python-package` is `false`.

**Must do:**
- Run `python -m skore_skills env verify --execute`.
- Name ruff / ipython / ipykernel and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent `env add` for sklearn.
- Invent the `add-python-package` procedure from memory.

---

## CASE_07 — Recorded Hub destination is not downgraded

**User prompt:**
> We should manage the environment. Finish that setup.

**Assumed workspace state:**
- Managed pixi project. `pixi.toml` already exists.
- `policy.env_manager` is `pixi`.
- `policy.env.managed` is unset. The user answers yes.
- `policy.skore_mode` is `hub`.

**Must do:**
- Ask whether we manage the env and persist `env.managed`.
- Skip `env init` because `pixi.toml` exists, then
  `env sync --execute`.
- Install Skore with
  `python -m skore_skills env add-skore --execute` and no `--mode`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `env add-skore --mode local`.
- Ask where to store reports (Hub / local / MLflow).
