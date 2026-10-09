# export-ml-notebook eval

---

## CASE_01 — Fill EDA percent file

**User prompt:**
> Give me an executed notebook of the EDA.

**Assumed workspace state:**
- `data_analysis/data_analysis.py` exists.
- `policy.notebooks` is true.
- `jupytext` and `nbformat` are installed.

**Must do:**
- Run `python -m skore_skills notebook fill data_analysis/data_analysis.py`.
- Leave code-cell outputs empty. Do not start EDA from this skill.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Rewrite `data_analysis/data_analysis.py` from a `.ipynb`.
- Run `git commit`.
- Run `notebook convert` or `cells run` on
  `data_analysis/data_analysis.py`.
- Pass `--html` unless the user asked for HTML or a site viewer.

---

## CASE_02 — Null flag defaults on then installs

**User prompt:**
> Make an ipynb from data_analysis/data_analysis.py.

**Assumed workspace state:**
- `policy.notebooks` is null.
- `add-python-package` is installed.

**Must do:**
- Persist `notebooks true`. Do not AskUserQuestion.
- Load `add-python-package` for `jupytext` and `nbformat`, then
  fill.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Fill while the flag is still null or false.
- Run `pixi add` / `uv add` from this skill.

---

## CASE_03 — Fill without HTML does not rebuild site

**User prompt:**
> Convert data_analysis/data_analysis.py to a notebook.

**Assumed workspace state:**
- `policy.notebooks` is true.
- `policy.site` is true.
- `export-ml-site` is installed.

**Must do:**
- Fill `data_analysis/data_analysis.py` without `--html`. Leave
  code-cell outputs empty.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `python -m skore_skills site build`.
- Run `git end-turn`.

---

## CASE_04 — Notebook page on the site on explicit request

**User prompt:**
> Put the executed EDA notebook on the site.

**Assumed workspace state:**
- `data_analysis/data_analysis.py` exists.
- `policy.notebooks` is true.
- `jupytext` and `nbformat` are installed.
- `add-python-package` is installed.
- `policy.site` is true.
- `export-ml-site` is installed.

**Must do:**
- Load `add-python-package` for `nbconvert`.
- Run `python -m skore_skills notebook fill data_analysis/data_analysis.py --html`.
- Leave code-cell outputs empty.
- Run `python -m skore_skills site build --if-stale`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `notebook convert` or `cells run` on
  `data_analysis/data_analysis.py`.
- Run `git end-turn`.

---

## CASE_05 — Gate off

**User prompt:**
> Convert data_analysis/data_analysis.py to a notebook.

**Assumed workspace state:**
- `policy.notebooks` is false.

**Must do:**
- Say notebooks are off and offer to turn them on.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `notebook fill` or `notebook convert` while the flag is false.

---

## CASE_06 — Audit notebook is filled without a kernel

**User prompt:**
> Run the audit and make its notebook available.

**Assumed workspace state:**
- `policy.notebooks` is true and `policy.site` is true.
- `audit/01_baseline.py` exists.

**Must do:**
- Run `notebook fill audit/01_baseline.py --html`.
- Leave code-cell outputs empty. The digest is
  `scratch/audit/01_baseline/audit.md` from `materialize.py`,
  not from this fill.

**Must NOT do:**
- `notebook convert` or `cells run` `audit/01_baseline.py`.
- Execute the audit script to fill the notebook.
- Write the digest to `audit/01_baseline.digest.md`.
- Change either recorded policy.
