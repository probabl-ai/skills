# research-ml-practice eval

---

## CASE_01 — Intake when concern is missing

**User prompt:**
> Research this for me.

**Assumed workspace state:**
- Caller did not supply a concern or the canned extra-analysis
  survey.
- No JOURNAL and no EDA report.

**Must do:**
- AskUserQuestion for a named concern.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Start a depth web search with an empty concern.
- Drop a column or rewrite raw data.

---

## CASE_02 — Skip intake when concern is supplied

**User prompt:**
> Research whether a 0.97 Pearson with the target is leakage on
> this regression table. Domain is real estate.

**Assumed workspace state:**
- Concern and domain are in the prompt.

**Must do:**
- Skip intake (concern and domain are already in the prompt).
- Abstract the problem class; do not query a dataset proper
  name.
- Return an intended `scratch/research/<slug>.md` path and a
  one- or two-sentence finding.
- Name that candidates are laned (`measure` / `declare` /
  `evaluate` / `confirm`) without dumping the note.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Re-ask domain and concern.
- Run the canned extra-analysis survey first.
- Drop the correlated column.
- Run `pixi add` / `uv add`.
- Write `data_analysis.md` or the design note.
- Paste the full scratch note into chat.

---

## CASE_03 — Boundaries

**User prompt:**
> Research whether I should drop customer_id.

**Assumed workspace state:**
- Concern is dropping an identifier column.

**Must do:**
- Rank dropping as a *candidate* for the pipeline skill, not an
  action on `data/`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Modify raw data files.
- Pick the final learner.
- `git end-turn` or `git commit`.
- Write `data_analysis.md`.

---

## CASE_04 — Extra-analysis survey abstracts the toy table

**User prompt:**
> Given the kind of problem in JOURNAL and the kinds of
> structure already seen in EDA, what extra measurements on a
> raw table like this are still worth doing?

**Assumed workspace state:**
- Caller passed the canned extra-analysis survey.
- JOURNAL names California housing and target MedHouseVal.
- `data_analysis/data_analysis.md` records a top-coded target
  and lat/lon columns.

**Must do:**
- Rewrite the problem class (e.g. continuous housing-value
  regression, top-coded target, rounded lat/lon) before
  searching.
- Return an intended `scratch/research/survey-<slug>.md` path
  and a one- or two-sentence finding.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Query `california_housing`, `sklearn.datasets`, or a
  sklearn fetcher.
- Return sklearn `Pipeline` / estimator / `GridSearch` steps
  as EDA extras.
- Write a ranked pipeline action table in that note.
- Copy unsourced Open questions as the extras list.
- Write `data_analysis.md` or the design note.
- Paste the full scratch note into chat.
