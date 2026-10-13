# export-ml-site eval

---

## CASE_01 — Init then build

**User prompt:**
> Build the documentation website.

**Assumed workspace state:**
- `policy.site` is true.
- `mkdocs-material` is installed.
- The workspace is scaffolded.
- When `site build` runs, its output ends with `file:///workspace/report.html`.

**Must do:**
- Run `python -m skore_skills site init`.
- Run `python -m skore_skills site build`.
- Say the website has been updated and include
  `file:///workspace/report.html`. Do not say double-click or
  "no server".

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
- When `site build` runs, its output ends with `file:///workspace/report.html`.

**Must do:**
- Run `python -m skore_skills site build`.
- Do not run `site init` again.
- Say the website has been updated and include
  `file:///workspace/report.html`. Do not say double-click or
  "no server".

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

---

## CASE_05 — Missing mkdocs-material retries the build

**User prompt:**
> Build the documentation website.

**Assumed workspace state:**
- `policy.site` is true.
- `site init` already ran.
- `add-python-package` is installed.
- `python -m skore_skills site build` printed
  `mkdocs-material is required; add it with add-python-package`.
- When the retry succeeds, its output ends with `file:///workspace/report.html`.

**Must do:**
- Load `add-python-package` for `mkdocs-material`, then run
  `python -m skore_skills site build` again.
- Say the website has been updated and include
  `file:///workspace/report.html`. Do not say double-click or
  "no server".

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Persist `site true` or run `site init` again.
- Run `pixi add` or `uv add`.
- Run `notebook convert`.
- AskUserQuestion for the site gate.

---

## CASE_06 — Workflow checkpoint skips a current site

**User prompt:**
> Show me the updated report before I choose the next analysis.

**Assumed workspace state:**
- `policy.site` is true.
- The stage finished its Python work and durable Markdown batch.
- `site build --if-stale` may find unchanged inputs.
- When `site build --if-stale` runs, a rebuild and a current site both end with `file:///workspace/report.html`.

**Must do:**
- Run `python -m skore_skills site build --if-stale` once before
  the user decision.
- Say the website has been updated and include
  `file:///workspace/report.html`, whether MkDocs rebuilt or
  reported the site current. Do not say double-click or "no
  server".

**Must NOT do:**
- Rebuild between individual Markdown edits in the same batch.
- Enable notebook policy.
- Treat a current-site no-op as an error.
