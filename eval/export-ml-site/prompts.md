# export-ml-site eval

---

## CASE_01 — Init then build

**User prompt:**
> Build the documentation website.

**Assumed workspace state:**
- `policy.site` is true.
- `mkdocs-material` is installed.
- The workspace is scaffolded.

**Must do:**
- Run `python -m skore_skills site init`.
- Run `python -m skore_skills site build`.
- Name `report.html` at the workspace root as the file to open.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `notebook convert`.
- Run `git commit`.
- Load `add-python-package` for `jupytext` or `nbclient`.

---

## CASE_02 — Later turns only build

**User prompt:**
> Rebuild the site.

**Assumed workspace state:**
- `policy.site` is true.
- `site init` already ran.

**Must do:**
- Run `python -m skore_skills site build`.
- Do not run `site init` again.
- Name `report.html` at the workspace root as the file to open.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- AskUserQuestion for the site gate again.
- Run `notebook convert`.
- Run `git end-turn`.

---

## CASE_03 — Gate off

**User prompt:**
> Build the MkDocs site.

**Assumed workspace state:**
- `policy.site` is false.

**Must do:**
- Say the documentation-site gate is off and offer to turn it on.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `site init` or `site build` while the flag is false.

---

## CASE_04 — Null flag installs mkdocs only

**User prompt:**
> Build the documentation website.

**Assumed workspace state:**
- `policy.site` is null.
- `add-python-package` is installed.

**Must do:**
- Persist `site true`. Do not AskUserQuestion.
- Load `add-python-package` for `mkdocs-material`, then init and
  build.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Install `jupytext`, `nbclient`, or `nbconvert` for the site flag.
- Convert while only turning the site on.
