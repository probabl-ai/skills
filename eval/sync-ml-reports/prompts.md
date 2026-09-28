# sync-ml-reports eval

---

## CASE_01 — Switch local to Hub

**User prompt:**
> Switch the default destination to Hub workspace acme-corp for
> project load-forecast. Transfer now, not a dry run.

**Assumed workspace state:**
- `policy.skore_mode` is `local`.
- `experiments/01_baseline.py` has `skore.Project(name="load-forecast",
  mode="local", workspace=str(PROJECT_ROOT / "reports"))`.
- `add-python-package` is installed.
- `SKORE_HUB_API_KEY` is set.
- `skore` is on PATH.
- `persist-ml-git` and `triage-ml-task` are installed.

**Must do:**
- Run `python -m skore_skills status`.
- Load `add-python-package` for Skore at Hub mode.
- Name `skore sync load-forecast --from=local --to=hub` with
  `--from-workspace` on `reports/` and `--to-workspace=acme-corp`.
- Persist `python -m skore_skills policy set skore_mode hub`.
- Rewrite the Project init to Hub form (`login` + `workspace="acme-corp"`).
- Run `python -m skore_skills git end-turn --stage evaluate`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Call `Project.sync` in Python.
- Run `git commit` in this skill.
- Ask a first-time local / Hub / MLflow destination pick.
- Pass `--from-workspace` / `--to-workspace` as an MLflow flag.

---

## CASE_02 — Copy only, keep local mode

**User prompt:**
> Copy our local reports to Hub workspace acme-corp for project
> load-forecast. Keep evaluating locally. Transfer now, not a dry
> run.

**Assumed workspace state:**
- `policy.skore_mode` is `local`.
- Project name is `load-forecast`.
- `add-python-package` is installed.
- `SKORE_HUB_API_KEY` is set.
- `skore` is on PATH.

**Must do:**
- Run `python -m skore_skills status`.
- Name `skore sync` from `local` to `hub` with Hub
  `--to-workspace=acme-corp`.
- Run `python -m skore_skills git end-turn --stage evaluate`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Persist `policy set skore_mode`.
- Rewrite Project init blocks.
- Call `Project.sync` in Python.
- Run `git commit` in this skill.

---

## CASE_03 — Unset mode does not steal G-SKORE-MODE

**User prompt:**
> Upload the reports to Hub.

**Assumed workspace state:**
- `policy.skore_mode` is unset.
- `evaluate-ml-pipeline` is installed.

**Must do:**
- Run `python -m skore_skills status`.
- Stop because report destination must be chosen in the evaluate
  workflow first.
- The close is only that stop: the destination is not chosen yet
  and is picked when a report is stored. Do not list local, Hub,
  or MLflow, a workspace name, or a tracking URI.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `skore sync`.
- Persist `policy set skore_mode`.
- Ask local / Hub / MLflow as this skill's first destination
  pick.

---

## CASE_04 — Missing Hub API key

**User prompt:**
> Switch the default destination to Hub workspace acme-corp.
> Transfer now, not a dry run.

**Assumed workspace state:**
- `policy.skore_mode` is `local`.
- Project name is `load-forecast`.
- `add-python-package` is installed.
- `SKORE_HUB_API_KEY` is unset / missing.

**Must do:**
- Run `python -m skore_skills status`.
- Name `SKORE_HUB_API_KEY` and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Open a browser login.
- Run `skore sync`.
- Call `Project.sync` in Python.
- Read `.skore` for the key.
