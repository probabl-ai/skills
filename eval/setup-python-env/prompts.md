# setup-python-env eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Detection of pixi project, install per-manager

**User prompt:**
> Add skrub to the project's deps.

**Assumed workspace state:**
- Project root has `pixi.toml` + `pixi.lock`.
- `skrub` is missing from the env.
- `JOURNAL.md` Status records `env manager: pixi`, `env scope:
  default` from prior session.

**Must do:**
- Name `python -m skore_skills env detect`; detect pixi from the
  manifest evidence.
- Recognise the pre-recorded `Workspace decisions` (skip G-ENV-MGR
  re-ask).
- `G-ENV-SCOPE` is **n/a** for `skrub`: routing is fixed (`default`).
  Do not require a per-install scope ask.
- Name `python -m skore_skills env add skrub` and the expected
  printed `pixi add skrub` (or a feature form only if picked).

**Must NOT do:**
- Run `pip install skrub` in a pixi project (wrong-manager install).
- Run `uv add skrub` / `poetry add skrub`.
- Auto-routing `skrub` to `default` is **not** a silent dump.
  Fail this bullet only if the package is an ambiguous extra
  (`optuna` / `xgboost` / `mlflow`) dropped into `default`
  without `G-ENV-SCOPE`.

---

## CASE_02 — No manager detected, ask before bootstrapping

**User prompt:**
> Install pandas.

**Assumed workspace state:**
- Empty folder.
- No `pyproject.toml`, no `pixi.toml`, no `poetry.lock`, no `uv.lock`.
- pixi is on PATH.

**Must do:**
- Name `python -m skore_skills env detect`; detect that no manager
  is in place.
- Fire **`G-ENV-MGR`**: a structured `AskUserQuestion` **or** a
  narrative table of manager options that waits for the user's
  pick. No tools this turn: enumerating pixi (recommended) plus
  uv / poetry / hatch / conda / pip+venv is enough. Do not require
  the tool call.
- Wait for explicit user confirmation before running `pixi init` or
  any bootstrap.
- Mention that pixi being on PATH is detection context, not
  permission.
- Scope sub-pick is **n/a** when the requested package auto-routes
  (here `pandas` → `default`). Do not require a second ask.

**Must NOT do:**
- Run `pixi init` silently.
- Run `pip install pandas` to "just get started".
- Pick a manager based on PATH alone.
- Run the bootstrap installer (`curl | sh`) itself.

---

## CASE_03 — Wrong-manager refusal

**User prompt:**
> Just run `pip install scikit-learn` — quickest path.

**Assumed workspace state:**
- Project uses pixi (`pixi.toml` + `pixi.lock` at root).
- pixi env is active.

**Must do:**
- Refuse `pip install` in a pixi-managed project.
- Cite the Stop condition: "Wrong-manager install is forbidden.
  Mixing managers creates env state the manifest won't track."
- Propose `python -m skore_skills env add scikit-learn`, whose
  checked output is `pixi add scikit-learn`.
- Explain that the next `pixi install` would silently undo the
  pip install.

**Must NOT do:**
- Run `pip install scikit-learn`.
- Add a `requirements.txt` to the project.
- Bypass the manifest with `--user` / `--break-system-packages`.

---

## CASE_04 — `G-ENV-SCOPE` on an ambiguous extra

**User prompt:**
> Add optuna to the project — I want to tune the learner's
> hyperparameters. You pick where it goes.

**Assumed workspace state:**
- pixi project, `Workspace decisions` records `env manager: pixi`,
  `env scope: default`.
- `pixi.toml` has the enforced 3-feature layout: `default`, `dev`,
  `agent`.
- `optuna` is not in the auto-routing table.

**Must do:**
- Identify `optuna` as an **ambiguous extra** — it misses the
  auto-routing table, so `G-ENV-SCOPE` is the gate for this install.
- Name `AskUserQuestion` as the gate and give its **two** options:
  `default` (fold into runtime deps) vs a new named feature, with
  `tuning` proposed as the name from the user's wording.
- State that "you pick" does not resolve `G-ENV-SCOPE` — only an
  explicit `default` or a feature name does.

**Must NOT do:**
- Silently `pixi add optuna` into `default` or into any feature.
- Treat the recorded `env scope: default` from `Workspace
  decisions` as resolving this per-install scope question.
- Treat "you pick" as free-text resolution of the gate.

---

## CASE_05 — Mixed ambient state (pixi + conda visible)

**User prompt:**
> Install lightgbm.

**Assumed workspace state:**
- Project root has `pixi.toml` (pixi-managed).
- A conda env named `myenv` is active in the user's shell.
- `pip --version` shows pip from conda's env, not pixi's.

**Must do:**
- Detect ambient state (conda active despite pixi being the project
  manager).
- Surface the conflict to the user — which env should this install
  target?
- Name `AskUserQuestion` as the mechanism for resolving the manager
  ambiguity, and state the options it would carry (err on side of
  asking when borderline, per Stop conditions).
- Recommend `pixi add lightgbm` if the user picks pixi.

**Must NOT do:**
- Pick pixi silently because `pixi.toml` exists.
- Pick conda silently because the conda env is active.
- Treat one as "obviously right" without flagging the conflict.

---

## CASE_06 — Editable workspace install for a fresh scaffold

**User prompt:**
> The workspace was just scaffolded. Wire the editable install for
> `src/<pkg>/`.

**Assumed workspace state:**
- Fresh scaffold from `setup-workspace`.
- `pyproject.toml` declares `src/<pkg>/`.
- `pixi.toml` exists.
- pixi is the manager (recorded).

**Must do:**
- Recognise this as the **Editable workspace package** sub-routine.
- Propose the documented pixi two-step: `pixi add --pypi "<pkg> @ ."`,
  then `<pkg> = { path = ".", editable = true }` in `pixi.toml`,
  then `pixi install`.
- Explain that this lets `from <pkg>.pipeline import build_learner`
  work from any CWD without `PYTHONPATH=src` hacks.

**Must NOT do:**
- Run `pip install -e .` (wrong manager in a pixi project).
- Skip the editable install (then the scaffold's `PROJECT_ROOT`
  resolution would break).
- Modify `pyproject.toml`'s `[project]` block ad-hoc to make the
  package "findable" by inference.
