# frame-ml-problem eval

---

## CASE_01 — A blank journal asks every missing decision

**User prompt:**
> Which comparison metric should we lock before building?

**Assumed workspace state:**
- `journal/JOURNAL.md` exists. Modeling decisions Status is still
  the empty placeholder.
- `scratch/data_analysis/extras.json` has `"task": "classification"`.
- `python -m skore_skills frame show` returns `ask` /
  `missing_keys`. `missing` lists prediction_goal, deployment,
  horizon, gap, time_role, generalize_to, known_at_predict,
  metric_role, metric, baseline, baseline_note, and folds.
- `questions` names a reference for each of those keys.
  prediction_goal candidates are `probabilities`, `point_labels`,
  and `uncovered`. The horizon and gap questions cite
  `references/horizon-gap.md` and have no candidates. The
  baseline question cites `references/baseline.md`.

**Must do:**
- Run `python -m skore_skills frame show`.
- Read each named reference once, including
  `references/prediction-goal.md`, `references/horizon-gap.md`,
  and `references/baseline.md`.
- Ask every key in `missing` in one message. Prediction-goal
  options are only `probabilities`, `point_labels`, and
  `uncovered`. Say horizon and gap are n/a unless the deployment
  is time, and generalize-to is n/a unless the deployment is
  groups.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write Python, a pipeline, or a splitter constructor.
- Ask only the prediction goal and stop.
- Invent a horizon, a baseline, or a fold count.

---

## CASE_02 — A time deployment asks the remaining cells

**User prompt:**
> New rows arrive later than the fit. Lock that.

**Assumed workspace state:**
- Prediction goal is `point_predictions` and Deployment is `time`.
  Status is `draft`.
- `frame show` returns `missing` with horizon, gap, time_role,
  known_at_predict, metric_role, metric, baseline, baseline_note,
  and folds. The horizon and gap questions cite
  `references/horizon-gap.md` and have no candidates.

**Must do:**
- Read `references/horizon-gap.md` once.
- Ask every still-missing key in one message.
- Explain horizon as the lead from prediction time to the target,
  and gap as the delay from the end of training to when the
  forecast is issued. Ask for the horizons as numbers in one
  unit, and for the gap in that same unit. A gap of 0 is allowed.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask for a generalize-to column.
- Write `TimeSeriesSplit` or `gap=` into the journal.
- Invent a fold count.

---

## CASE_05 — Clustering uses the fallback, not the closed menu

**User prompt:**
> We are clustering customers. What should we lock?

**Assumed workspace state:**
- `scratch/data_analysis/extras.json` has `"task": "clustering"`.
- `frame show` returns `ask` / `uncovered`, `reference`
  `references/fallback.md`, and `context.task` `clustering`.
  There is no `candidates` list.

**Must do:**
- Read `references/fallback.md` and no other file under
  `references/`.
- Say the closed menu does not cover clustering.
- Ask what a better result means and what the baseline is.
- Write Prediction goal `uncovered` plus those two prose cells.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask for `probabilities` or `point_labels`.
- Write a splitter class or Python.

---

## CASE_06 — A missing command uses the same fallback

**User prompt:**
> Lock the comparison metric and the baseline.

**Assumed workspace state:**
- `python -m skore_skills frame show` exits with `No such command
  'frame'`. There is no JSON.

**Must do:**
- Read `references/fallback.md`.
- Record the comparison and the baseline in words, with Prediction
  goal `uncovered`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent `probabilities`, `iid`, or `KFold`.
- Open `references/prediction-goal.md` or
  `references/metric-role.md`.
- Write Python.

---

## CASE_03 — Confirm lock quotes the context

**User prompt:**
> The table is filled. Lock it.

**Assumed workspace state:**
- Every required cell is valid and Status is `draft`.
- `frame show` returns `ask` / `confirm_lock` with choices
  `lock`, `modify`, `stop`, and `context.metric` `MAE`.

**Must do:**
- Quote the JSON context, including MAE, in the question.
- Offer only lock, modify, and stop, then stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write Python or a class constructor.
- Treat "Lock it" as the lock choice in this turn.
- Set Status to `locked` in this turn.
- Load `build-ml-pipeline`.

---

## CASE_04 — Revise blanks the named goal and its metric cells

**User prompt:**
> The constraint changed: we now need intervals, not point predictions.

**Assumed workspace state:**
- Status is `locked`.
- Prediction goal is `point_predictions`, metric role is
  `point_error`, metric is `MAE`, deployment is `iid`, and
  folds is `5`.
- `python -m skore_skills frame show --revise` returns `ask` /
  `revise` with choices `modify`, `keep`, `stop`.
- The user chooses `modify`.

**Must do:**
- Name `frame show --revise`.
- On modify, run `frame clear --cell prediction_goal`.
- That blanks prediction goal, metric role, and metric, and sets
  Status to `draft` with Revised on today's date.
- Leave deployment and folds filled.
- Stop for the next `frame show`. Do not write `intervals` in
  this turn.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave Status `locked` after modify.
- Blank deployment or folds.
- Write a model or a splitter.

---

## CASE_09 — Revise blanks only the named metric

**User prompt:**
> Change the comparison metric. Keep the rest of the framing.

**Assumed workspace state:**
- Status is `locked`.
- Metric is `MAE`. Metric role is `point_error`. Prediction goal
  is `point_predictions`. Folds is `5`.
- `experiments/01_baseline.py` exists.
- `python -m skore_skills frame show --revise` returns `ask` /
  `revise` with choices `modify`, `keep`, `stop`.
- The user chooses `modify`.

**Must do:**
- Name `frame show --revise`.
- On modify, run `frame clear --cell metric`. That blanks only
  the metric and leaves metric role, prediction goal, and folds
  filled.
- Stop for the next `frame show`.
- Say `experiments/01_baseline.py` still uses the previous metric
  and is not run. The next build or evaluate rewrites it after
  the table is locked again.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Blank metric role, prediction goal, or folds.
- Write the replacement metric in this turn.
- Rewrite an experiment file or a report.
- Run `experiments/01_baseline.py`.

---

## CASE_10 — Draft table blanks the named metric

**User prompt:**
> Change the comparison metric. The table is not locked yet.

**Assumed workspace state:**
- Status is `draft`.
- Metric is `MAE`. Metric role is `point_error`. The other
  required cells are valid.
- `frame show` returns `ask` / `confirm_lock`, not `revise`.

**Must do:**
- Run `frame clear --cell metric` and stop.
- Do not write the replacement metric.
- Do not name metric role as cleared.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Set Status to `locked`.
- Treat `confirm_lock` as the way to make this change.

---

## CASE_11 — Unnamed change asks which decision

**User prompt:**
> A problem constraint changed.

**Assumed workspace state:**
- Status is `locked`.
- Metric is `MAE` and folds is `5`. The user did not name
  a cell.

**Must do:**
- Ask which filled decision to change. Do not run `frame clear`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Set Status to `draft` or blank a cell on this turn.
- Leave every cell filled and ask to lock again as if the change
  were done.

---

## CASE_07 — Dispatched lock returns to modeling

**User prompt:**
> Lock the table.

**Assumed workspace state:**
- `model-ml-pipeline` dispatched this turn.
- `frame show` returns `proceed` with a non-null `translation`.

**Must do:**
- Return to `model-ml-pipeline` and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `build-ml-pipeline` or write a design note.
- Run `python -m skore_skills git end-turn --stage implement`.

---

## CASE_08 — Standalone lock still closes the turn

**User prompt:**
> Lock the table.

**Assumed workspace state:**
- This turn was not dispatched by `model-ml-pipeline`.
- `frame show` returns `proceed` with a non-null `translation`.

**Must do:**
- Run `python -m skore_skills git end-turn --stage implement`.
- If that command returns `invoke`, load `persist-ml-git` when installed.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `build-ml-pipeline`.
