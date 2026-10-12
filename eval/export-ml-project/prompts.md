# export-ml-project eval

---

## CASE_01 — Ask then load children

**User prompt:**
> Export the project.

**Assumed workspace state:**
- `policy.notebooks` is false.
- `policy.site` is true.
- `export-ml-notebook` and `export-ml-site` are installed.

**Must do:**
- Run `python -m skore_skills status`.
- AskUserQuestion `allow_multiple`. The preamble states
  notebooks are off and the site is on. The question's last line is exactly: Select each one you want.
- Load `export-ml-site` if the user selects the site.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git end-turn`.
- Invent `mkdocs` steps instead of loading the child.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.

---

## CASE_02 — Missing child skips

**User prompt:**
> Export notebooks and the site.

**Assumed workspace state:**
- User selects both.
- `status.skills.export-ml-notebook` is `false`.
- `status.skills.export-ml-site` is `true`.

**Must do:**
- Skip notebooks in one line because `export-ml-notebook` is not
  installed.
- Load `export-ml-site`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent `notebook convert` from memory.
- Treat the missing skill as an error that aborts export.

---

## CASE_03 — Null flags do not select either box

**User prompt:**
> Export the project.

**Assumed workspace state:**
- `policy.notebooks` is null.
- `policy.site` is null.
- `export-ml-notebook` and `export-ml-site` are installed.

**Must do:**
- AskUserQuestion `allow_multiple`. The preamble states that
  neither notebooks nor the site is recorded yet. The
  question's last line is exactly: Select each one you want.
  Do not treat `null` as on. This turn stops at the question.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `policy set`, or write `notebooks` or `site` policy values,
  before the user answers. Describing the two choices and saying
  they are not recorded yet is not persistence.
- Run `git end-turn`.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.
