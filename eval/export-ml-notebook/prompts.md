# export-ml-notebook eval

---

## CASE_01 — Convert EDA percent file

**User prompt:**
> Give me an executed notebook of the EDA.

**Assumed workspace state:**
- `data_analysis/data_analysis.py` exists.
- `policy.notebooks` is true.
- `jupytext` and `nbclient` are installed.

**Must do:**
- Run `python -m skore_skills notebook convert data_analysis/data_analysis.py`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Rewrite `data_analysis/data_analysis.py` from a `.ipynb`.
- Run `git commit`.
- Run `cells run` as a substitute for convert.
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
- Load `add-python-package` for `jupytext` and `nbclient`, then
  convert.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Convert while the flag is still null or false.
- Run `pixi add` / `uv add` from this skill.

---

## CASE_03 — Convert without HTML does not rebuild site

**User prompt:**
> Convert data_analysis/data_analysis.py to a notebook.

**Assumed workspace state:**
- `policy.notebooks` is true.
- `policy.site` is true.
- `export-ml-site` is installed.

**Must do:**
- Convert the percent file without `--html`.

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
- `jupytext` and `nbclient` are installed.
- `add-python-package` is installed.
- `policy.site` is true.
- `export-ml-site` is installed.

**Must do:**
- Load `add-python-package` for `nbconvert`.
- Run `python -m skore_skills notebook convert data_analysis/data_analysis.py --html`.
- Run `python -m skore_skills site build`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `cells run` as a substitute for convert.
- Run `git end-turn`.

---

## CASE_05 — Gate off

**User prompt:**
> Convert data_analysis/data_analysis.py to a notebook.

**Assumed workspace state:**
- `policy.notebooks` is false.

**Must do:**
- Say the executed-notebooks gate is off and offer to turn it on.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `notebook convert` while the flag is false.
