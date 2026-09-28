# review-ml-choices eval

---

## CASE_01 — Package name stays read-only

**User prompt:**
> Show what we decided. Rename the Python package to forecasts.

**Assumed workspace state:**
- `policy.package` is `load_forecast`.
- `src/load_forecast/` exists.
- `review-ml-choices` is the skill for this turn.

**Must do:**
- Use the `review choices` JSON. Do not rebuild which rows are
  offered.
- Show the package name and say an existing tree is not renamed.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `setup-workspace` to rename `src/`.
- Run `policy set package`.
- Scaffold a new package.

---

## CASE_02 — Unset report destination is not a switch

**User prompt:**
> What did we decide? Change where reports go.

**Assumed workspace state:**
- `policy.skore_mode` is unset.
- `status.skills.sync-ml-reports` is `true`.
- `status.skills.evaluate-ml-pipeline` is `true`.

**Must do:**
- Use the `review choices` JSON. Do not rebuild which rows are
  offered.
- Show that where reports go is not chosen yet.
- Say the first choice happens when a report is stored.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `sync-ml-reports`.
- Run `policy set skore_mode`.

---

## CASE_03 — Recorded report destination loads sync

**User prompt:**
> Show our choices. I want to change where reports go.

**Assumed workspace state:**
- `policy.skore_mode` is `local`.
- `status.skills.sync-ml-reports` is `true`.
- The user picks the report-destination change.

**Must do:**
- Use the `review choices` JSON. Do not rebuild which rows are
  offered.
- Show the current destination as local.
- Hand off to changing where reports go, and stop, without a
  catalog id.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `policy set skore_mode`.
- Rewrite `skore.Project` init blocks in this skill.

---

## CASE_04 — Notebooks and site load export

**User prompt:**
> What did we decide about notebooks and the site? I want to change that.

**Assumed workspace state:**
- `policy.notebooks` is true.
- `policy.site` is false.
- `status.skills.export-ml-project` is `true`.
- The user picks that change.

**Must do:**
- Use the `review choices` JSON. Do not rebuild which rows are
  offered.
- Show both current values.
- Hand off to changing notebooks and the site, and stop, without
  a catalog id.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `policy set notebooks` or `policy set site`.
- Invent `notebook convert` or `mkdocs` steps.

---

## CASE_05 — Present data analysis is not marked skipped

**User prompt:**
> Change our choices. Skip the data analysis; we already wrote it.

**Assumed workspace state:**
- `status.data_analysis` is `present`.
- `data_analysis/data_analysis.md` exists.
- `status.skills.explore-ml-data` is `true`.

**Must do:**
- Use the `review choices` JSON. Do not rebuild which rows are
  offered.
- Say the written analysis stays and that the change is to run
  it again.
- Hand off to running it again, without a catalog id.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write a JOURNAL Data understanding Status of `skipped`.
- Overwrite `data_analysis/data_analysis.md` from this skill.

---

## CASE_06 — One framing cell loads frame

**User prompt:**
> Show our choices. I want to change the comparison metric.

**Assumed workspace state:**
- `status.modeling_decisions` is `locked`.
- `status.skills.frame-ml-problem` is `true`.
- `frame show` returns `action` `proceed` and `decisions.metric`
  `MAE`, `decisions.validation` `cv`, `decisions.folds` `5`.
- The user picks the metric.

**Must do:**
- Use the `review choices` JSON. Do not rebuild which rows are
  offered.
- Offer the metric (MAE) as its own choice, not one
  “modeling decisions” row.
- Hand off to re-asking that metric, and stop, without a
  catalog id.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Edit the journal, including blanking the metric, from this
  skill.
- Run `frame show --revise` from this skill.
- Run `policy set`.

---

## CASE_07 — Hub mode is not replayed as local

**User prompt:**
> Show our choices. Change who manages the environment.

**Assumed workspace state:**
- `policy.env.managed` is true.
- `policy.skore_mode` is `hub`.
- `status.skills.setup-python-env` is `true`.
- The user picks that change.

**Must do:**
- Use the `review choices` JSON. Do not rebuild which rows are
  offered.
- Hand off to re-deciding who manages the environment, and stop,
  without a catalog id.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `env add-skore --mode local`.
- Run `policy set env.managed` from this skill.
