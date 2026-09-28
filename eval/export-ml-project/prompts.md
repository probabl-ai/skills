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
- AskUserQuestion `allow_multiple`: notebooks **not** preselected,
  site preselected.
- Load `export-ml-site` if site stays checked.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git end-turn`.
- Invent `mkdocs` steps instead of loading the child.

---

## CASE_02 — Missing child skips

**User prompt:**
> Export notebooks and the site.

**Assumed workspace state:**
- User checks both boxes.
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

## CASE_03 — Null flags preselect both boxes

**User prompt:**
> Export the project.

**Assumed workspace state:**
- `policy.notebooks` is null.
- `policy.site` is null.
- `export-ml-notebook` and `export-ml-site` are installed.

**Must do:**
- Run `python -m skore_skills status`.
- AskUserQuestion `allow_multiple`: notebooks preselected, site
  preselected (`null` treated as on).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave either flag `null` after persist.
- Run `git end-turn`.
