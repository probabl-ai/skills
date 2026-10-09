# frame-ml-problem eval

---

## CASE_01 — A blank journal asks every missing decision

**User prompt:**
> Which comparison metric should we lock before building?

**Assumed workspace state:**
- `status.setup.pending` is empty.
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
- Ask for one baseline token for the Baseline cell.

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
- `status.setup.pending` is empty.
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
- `status.setup.pending` is empty.
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
- `status.setup.pending` is empty.
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
- Ask lock, modify, or stop.

---

## CASE_03 — A complete draft is recorded

**User prompt:**
> The table is filled. Lock it.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Every required cell is valid and Status is `draft`.
- `frame show` returns `ask` / `set` with no choices, and
  `context.metric` `MAE`.
- After Status is written `locked`, `frame show` returns
  `proceed` with a non-null `translation`. This turn was not
  dispatched by `model-ml-pipeline`.
- No experiment script exists. History has no running, done, or
  abandoned model row. `status.skills.model-ml-pipeline` is true.

**Must do:**
- Write Status `locked`.
- Say these choices are reused for the rest of the experiment so
  models stay comparable, and that any one of them can be changed
  by naming it. Quote MAE in those lines.
- Run `frame show` again.
- Load `model-ml-pipeline` and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write Python or a class constructor.
- Write a design note.
- AskUserQuestion.
- Treat "Lock it" as a menu choice.
- Say "lock" in the reuse and change lines.
- Load `build-ml-pipeline`.
- Run `python -m skore_skills git end-turn --stage implement`.

---

## CASE_04 — A named goal is replaced in the same turn

**User prompt:**
> The constraint changed: we now need intervals, not point predictions.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Status is `locked`.
- Prediction goal is `point_predictions`, metric role is
  `point_error`, metric is `MAE`, deployment is `iid`, and
  folds is `5`.
- `intervals` is a prediction-goal candidate.

**Must do:**
- Run `frame clear --cell prediction_goal`. Prediction goal,
  metric role, and metric are the ones to fill again, and Status
  is `draft`. `frame clear` stamps Revised on. Do not type the
  date.
- Write `intervals`, because the message already states it.
- Ask the metric role and metric, which are no longer filled.
- Leave deployment and folds filled.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `frame show --revise` or ask Modify / Keep / Stop.
- Say "cell", "blank", "clear", or "reopen".
- Leave Status `locked`.
- Reopen deployment or folds.
- Write a model or a splitter.
- Invent a calendar date for Revised on.

---

## CASE_09 — A named metric asks for its replacement

**User prompt:**
> Change the comparison metric. Keep the rest of the framing.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Status is `locked`.
- Metric is `MAE`. Metric role is `point_error`. Prediction goal
  is `point_predictions`. Folds is `5`.
- `experiments/01_baseline.py` exists.
- After `frame clear --cell metric`, `frame show` asks for the
  metric. The message does not state the new value.

**Must do:**
- Run `frame clear --cell metric`. Leave metric role, prediction
  goal, and folds filled.
- Ask which comparison metric replaces `MAE`.
- Say `experiments/01_baseline.py` still uses the previous metric
  and is not run. The next build or evaluate rewrites it after
  the table is locked again.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `frame show --revise` or ask Modify / Keep / Stop.
- Say "cell", "blank", "clear", or "reopen".
- Reopen metric role, prediction goal, or folds.
- Write the replacement metric in this turn.
- Rewrite an experiment file or a report.
- Run `experiments/01_baseline.py`.

---

## CASE_10 — Draft table blanks the named metric

**User prompt:**
> Change the comparison metric. The table is not locked yet.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Status is `draft`.
- Metric is `MAE`. Metric role is `point_error`. The other
  required cells are valid.
- `frame show` returns `ask` / `set`, not `revise`.

**Must do:**
- Run `frame clear --cell metric` and stop.
- Do not write the replacement metric.
- Do not name metric role as cleared.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Set Status to `locked`.
- Treat `set` as accepting the table.

---

## CASE_11 — Unnamed change asks which decision

**User prompt:**
> A problem constraint changed.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Status is `locked`.
- Metric is `MAE` and folds is `5`. The user did not name
  a cell.

**Must do:**
- AskUserQuestion one pick among the filled decisions. Do not
  run `frame clear`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask Modify / Keep / Stop.
- Set Status to `draft` or reopen a decision on this turn.
- Leave every cell filled and ask to lock again as if the change
  were done.

---

## CASE_07 — Dispatched lock returns to modeling

**User prompt:**
> Lock the table.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- `model-ml-pipeline` dispatched this turn.
- `frame show` returns `proceed` with a non-null `translation`.

**Must do:**
- Return to `model-ml-pipeline` and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `build-ml-pipeline` or write a design note.
- Run `python -m skore_skills git end-turn --stage implement`.

---

## CASE_08 — A first standalone lock loads modeling

**User prompt:**
> Lock the table.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- This turn was not dispatched by `model-ml-pipeline`.
- No experiment script exists. History has no running, done, or
  abandoned model row.
- `status.skills.model-ml-pipeline` is true.
- `frame show` returns `proceed` with a non-null `translation`.

**Must do:**
- Load `model-ml-pipeline` and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `build-ml-pipeline` or write a design note.
- Run `python -m skore_skills git end-turn --stage implement`.

---

## CASE_12 — Pending setup loads project setup

**User prompt:**
> Which comparison metric should we lock before building?

**Assumed workspace state:**
- No `src/` and no `journal/`.
- `status.setup.pending` is `env`, `workspace`, `git`.
- `status.setup.env` and `status.setup.workspace` are `missing`,
  not `declined`.
- `status.skills.setup-ml-project` is true.

**Must do:**
- Load `setup-ml-project` and stop.
- Do not write `journal/JOURNAL.md` or ask the modeling
  decisions.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `python -m skore_skills frame show`.
- Invent a metric, baseline, or fold count.

---

## CASE_13 — A shipped train and test table is a folds choice

**User prompt:**
> How should we split rows for evaluation?

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Status is `draft`. Every modeling-decisions cell except Folds
  is already filled for an iid point-prediction problem.
- `frame show` returns `ask` / `missing_keys`. `missing` is
  `folds`. The question cites `references/validation.md` and has
  no candidates.
- The EDA summary names `data/train.csv` as the training table
  and `data/test.csv` as the test table.

**Must do:**
- Read `references/validation.md`.
- In the folds question, offer using the training table and test
  table the EDA already names, and quote those two files.
- Say that `1` is one split drawn from a single table, and that
  choosing the shipped tables is recorded as `predefined`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write `prefit` or a splitter class in the journal.
- Record `1` as the way to use the shipped tables.
- Tell the user to concatenate the two tables.

---

## CASE_14 — A complete answer set is recorded in the same turn

**User prompt:**
> Prediction goal: point_predictions. Deployment: iid. Horizon,
> gap, generalize-to, known at predict, and time role: n/a.
> Metric role: point_error. Metric: RMSE. Baseline: dummy.
> Baseline note: mean house value. Folds: 2.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Status is still the empty placeholder. No decision cell is
  filled.
- The first `frame show` returns `ask` / `missing_keys` for
  every required key.
- After those cells are written with Status `locked`, a second
  `frame show` returns `proceed` with a non-null `translation`.
  This turn was not dispatched by `model-ml-pipeline`.
- No experiment script exists. History has no running, done, or
  abandoned model row. `status.skills.model-ml-pipeline` is true.

**Must do:**
- Write every decision from the user message. Set Status to
  `locked`.
- Run `frame show` again in this turn.
- Say these choices are reused for the rest of the experiment so
  models stay comparable, and that any one of them can be changed
  by naming it.
- Load `model-ml-pipeline` and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Leave Status `draft`.
- AskUserQuestion with Lock, Modify, and Stop.
- Say "lock" in the reuse and change lines.
- Load `build-ml-pipeline` or write a design note.
- Run `python -m skore_skills git end-turn --stage implement`.

---

## CASE_15 — One answered cell does not fill the rest

**User prompt:**
> Generalize to a column that combines latitude and longitude.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- Status is `draft`. Deployment, horizon, gap, time role, and
  generalize-to are empty. The other required cells are valid.
- `frame show` returns `ask` / `missing_keys`. `missing` lists
  deployment, horizon, gap, time_role, and generalize_to.

**Must do:**
- Write the generalize-to cell from the user message.
- Ask every still-unanswered key in `missing` and stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Invent deployment, horizon, gap, or time role.
- AskUserQuestion with Lock, Modify, and Stop.
- Set Status to `locked`.

---

## CASE_16 — An existing experiment still closes the turn

**User prompt:**
> Lock the table.

**Assumed workspace state:**
- `status.setup.pending` is empty.
- This turn was not dispatched by `model-ml-pipeline`.
- `experiments/01_baseline.py` exists.
- `frame show` returns `proceed` with a non-null `translation`.

**Must do:**
- Run `python -m skore_skills git end-turn --stage implement`.
- If that command returns `invoke`, load `persist-ml-git` when installed.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Load `model-ml-pipeline` or `build-ml-pipeline`.
- Write a design note.

---

## CASE_17 — Journal edit refreshes the live site

**User prompt:**
> Use grouped validation by hospital.

**Assumed workspace state:**
- `frame show` asks for `generalize_to`.
- `policy.site` is true and `export-ml-site` is installed.

**Must do:**
- Write the answered Modeling decisions cell.
- Run `python -m skore_skills site build --if-stale` after the
  Markdown batch and before the next framing question.
- Link `report.html`.

**Must NOT do:**
- Enable notebooks or site policy.
- Build between individual edits in the same Markdown batch.
- Run `notebook convert`.
