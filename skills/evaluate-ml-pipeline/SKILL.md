---
name: evaluate-ml-pipeline
description: >
  Evaluate one learner with `skore.evaluate`. The splitter and
  any non-default score are already on the DataOp from
  `build-ml-pipeline`. This skill writes the call without
  `splitter=`, persists the report, and records the locator.
  When the locked split is the training table and test table
  that shipped with the data, fit on the training table, then
  pass `splitter="prefit"` with only the test table.
  When `model-ml-pipeline` dispatched this turn, return the
  locator. A standalone turn also owns the evaluate-stage close.

  TRIGGER when code calls `cross_val_score`, `cross_validate`,
  `classification_report`, `.skb.cross_validate`, or a
  handwritten metric print, or the user asks to score, evaluate,
  or run CV on one learner. Narrative reads of a persisted
  report belong to `audit-ml-pipeline`.

  HOW TO USE: before any evaluation call. Resolve G-SKORE-MODE,
  read the stops, and emit Pre-flight before code. Confirm
  symbols with `python -m skore_skills api get`.
---

# Evaluate ML Pipeline

Score one learner and persist the report. The pipeline, the
splitter, and any non-default score are already declared.
`skore.evaluate` is the entry point. Do not hand-roll
`cross_val_score`, `cross_validate`, `classification_report`,
or metric prints.

A `SkrubLearner` does not implement sklearn's `fit(X, y)`.
`cross_val_score` raises. Call `skore.evaluate(learner, data={...})`
and omit `splitter=`, unless `translation.splitter` is `prefit`.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Experiment markdown and `#` comments describe this evaluation.
Questions and the close use the same data-science language: not
skill ids, `G-*` names, or the wrapper CLI.
`<!-- results-embed: … -->` is a site marker.

## Procedure

1. `python -m skore_skills status`. If `status.setup.pending`
   is non-empty and `status.skills.setup-ml-project` is true,
   load `setup-ml-project` and stop. Do not start this skill.
   When it returns, continue. Do not load it again on this turn.
   If that skill is not installed, name the pending pieces in
   one line and stop. Do not invent `git init`, scaffold, or
   `env init`. If `status.setup.env` or `status.setup.workspace`
   is `declined`, stop in one line. A declined `git` or
   `editable` is not asked again; continue. Then
   `python -m skore_skills frame show` without
   `--revise`. Anything other than `proceed` loads
   `frame-ml-problem` and stops. `translation` null → stop.
   Do not write an evaluation call.
2. History-dependent pipeline (backward shift, lag, rolling
   window, target shift, or a join with side history): if
   `tests/smoke/test_<stem>.py` is missing or pytest is red,
   stop. Route to `build-ml-pipeline`. Do not write
   `skore.evaluate`. Documented n/a only when there is no
   history-dependent step.
3. `python -m skore_skills evaluate consent --stem <stem>`.
   - `ask`, and this turn has not already answered **Evaluate**
     from `build-ml-pipeline`: quote JSON `context` and present
     Evaluate (Recommended) / Modify / Stop. Stop. "Run
     evaluation" is not consent on a first run.
   - The user already answered **Evaluate** this turn, or JSON
     is `proceed` (a real locator already exists): continue.
   - `stop` — smoke file missing. Route to build.
4. G-SKORE-MODE. Read `status.policy.skore_mode`. If it is
   already set, keep it. If unset, ask local (recommended) /
   hub / mlflow, then `python -m skore_skills policy set
   skore_mode <mode>`. **local**: `mkdir reports` (`exist_ok`);
   do not write `reports/README.md`. **hub** or **mlflow**: do
   not create `reports/`. Then load `add-python-package` if
   installed; it runs `env add-skore --mode <mode> --execute`.
   Do not spell `skore[...]` here. Do not run `env add` here.
   Constructors: `references/g_skore_mode.md`. A switch or a
   migration loads `sync-ml-reports` when that skill is
   installed.
5. Emit Pre-flight, then 1–3 sentences: this is local
   full-dataset evaluation with the locked scheme, report
   metrics, and `project.put`. When `translation.splitter` is
   `prefit`, say the model is fitted on the training table and
   scored on the shipped test table. Name the stem, the fold
   count when known, and `experiments/<stem>.py` plus
   `scratch/results/<stem>/`. Timing depends on rows, folds,
   and the learner. Do not invent minutes. If consent is still
   pending, preview and stop.
6. Write the call in `experiments/NN_*.py` only. See the call
   shapes below. `python -m skore_skills style` after the edit.
   The experiment ends at `project.put` and a bare `report`.
7. After `put` has stored the report, copy `templates/snapshot.py`
   to `scratch/results/<stem>/snapshot.py` and run it. Then End
   of turn. Do not add snapshot writes to the experiment file.

Every Python probe goes to `scratch/<ts>_<short>.py` and runs
with the composed-dev Python from `env verify`. No inline
`python -c`. No `warnings.filterwarnings` unless the user asks.
An unconfirmed signature stays unwritten. End that probe with
`BLOCKED: <class> signature needs an API lookup that cannot run
this turn (<why>).` A cache hit is a satisfied lookup.

## The call

`skore.evaluate` in `experiments/NN_*.py`. Omit `splitter=` so
skore reuses the DataOp `cv` and `split_kwargs`, unless
`translation.splitter` is `prefit`. Passing any other
`splitter=` drops `split_kwargs`. Omitted `splitter=` with no
DataOp `cv` is an 80/20 holdout, correct only when
`translation.report` is `EstimatorReport` and
`translation.splitter` is null. Wiring:
`references/metadata-routing.md`.

When `translation.splitter` is `prefit`, fit on the training
table only, then score the test table. Confirm `fit` and
`evaluate` with `api get`. Do not pass the training table into
`evaluate`. Omitting `splitter=` here draws a new 80/20 split
of the test table. Do not concatenate the two tables.

```python
learner = build_learner()
fitted = learner.fit({"table": train_df})
report = skore.evaluate(
    fitted,
    data={"table": test_df},
    splitter="prefit",
)
```

An estimator whose `fit` is `(X, y)` uses the same rule:

```python
fitted_model = LogisticRegression().fit(X_train, y_train)
report = skore.evaluate(
    fitted_model, X_test, y_test, splitter="prefit"
)
```

`X` / `y` and `data` stay mutually exclusive.

- `SkrubLearner` — `skore.evaluate(learner, data={...})`. Keys
  are the `skrub.var` names. Interop:
  `references/skrub_interop.md`.
- An estimator whose `fit` is `(X, y)` —
  `skore.evaluate(estimator, X, y)`. Still omit `splitter=`
  when the locked `cv` is already the evaluation scheme. The
  prefit call above is the exception: the estimator is already
  fitted, and `X` and `y` are the test table.

The `cv` on `mark_as_X` is `KFold`, `GroupKFold`, or the
date-based class from build. If `translation` names a `cv` and
the marker has none, return to `build-ml-pipeline`. Do not
wire `split_kwargs` here. Empty `split_kwargs` plus a possible
group column → return to `build-ml-pipeline`. Do not default
to `KFold`. `translation.splitter` `prefit` is not a `cv` on
the marker.

No `Stratified*` for class imbalance. It compresses across-fold
variance.

The headline is `translation.metric`. A name on the skore
default list in `build-ml-pipeline` needs no scorer. Any other
name must already be `.skb.with_scoring(...)` on the prediction
DataOp. If it is not, return to `build-ml-pipeline` before
`skore.evaluate`. Do not call `report.metrics.add`. When the
scorer is attached, that name is a row in
`report.metrics.summarize().frame()`. `skore.evaluate` has no
`scoring=` argument (`references/custom-metrics.md`). If the
name is attached and still missing from that frame, the
predictor class is wrong: it must be the mixin, then
`BaseEstimator` (`RegressorMixin` or `ClassifierMixin` first).
Return to `build-ml-pipeline`. `BaseEstimator` alone, and
`BaseEstimator` before the mixin, both fail.

An extra check the user asks for after the lock:
`references/custom-checks.md`. Subclass `skore.Check` at module
level in `experiments/NN_*.py`, then `report.checks.add(...)`
after `evaluate` and before `project.put`. `add` extends SKD
checks. Do not invent a check. Do not register one from
`audit/`. Confirm `Check` and `checks.add` with `api get`.

Escalate past `evaluate` only when the dispatcher is too coarse
(`references/reports.md`): `EstimatorReport` for one held-out
fit, `CrossValidationReport` for per-fold artifacts. Holdout uses
`EstimatorReport`. This loop scores that one learner with one
`skore.evaluate` and one `project.put`.

CV is necessary but not sufficient for any pipeline with
history-dependent features. `skore.evaluate` materializes the
graph once with one env-dict and splits indices. The smoke test
exercises a fresh env-dict at predict time. A passing smoke
test is still required before the caller may flip status to
`done`. Do not edit `JOURNAL.md` History or the design-note
Status to `done` from this skill.

`skore.evaluate(...)` and `project.put(...)` live only in
`experiments/NN_*.py`. A scratch probe, an audit file, or a
notebook that calls them duplicates the report under the same
key. Read a stored report with `project.summarize()` then
`project.get(id)`. `get(key)` raises `KeyError` because `get`
is by id. Do not re-run `evaluate` to paper over that.

Plots that skore does not already draw load `plot-ml-figure`
when that skill is installed.

## After `put`

`Project.put` returns `None`. Read
`project.summarize().frame()`, take the newest row for the key,
and form one locator. Copy `templates/snapshot.py` to
`scratch/results/<stem>/snapshot.py` (gitignored). Substitute
the Project init from `experiments/<stem>.py`, the report id,
and that locator. Run the script with the composed-dev Python
from `env verify`, before `loop locator` and `loop artifacts`.
Do not put these writes in `experiments/<stem>.py`. Run
`python -m skore_skills loop locator --stem <stem>` and paste
JSON `locator` verbatim. Missing locator is
`n/a — backend did not expose a locator`.

- local — `local workspace: [reports/](../reports/) · id: <id>`,
  plus the absolute `reports/` path. Do not link a private file.
- hub — the exact `Consult your report at …` URL:
  `[Open report](<url>) · hub · id: <id>`. If Skore emits no
  URL, link the project landing page as `Open project`.
- mlflow — an exact `View run …` URL when present. If absent
  and `tracking_uri` is HTTP(S), use
  `/#/experiments/<experiment-id>/runs/<run-id>`. For `file:`,
  `sqlite:`, `databricks`, or any other URI without an emitted
  URL: `mlflow · tracking: <uri> · experiment: <id> · run:
  <run-id>`. Do not invent a browser link.

The script writes `report._repr_html_()` to
`scratch/results/<stem>/report.html` and `repr(report)` to
`report.txt`. It regenerates the Method viewer from the stored
learner: `report.estimator_` on `EstimatorReport`,
`report.reports_[0].estimator_` on `CrossValidationReport`.
Confirm `eval` on `DataOp.skb.report` with `api get`.
`learner.report` forwards it. When `eval` is a parameter, call
`learner.report` with `eval=False`, `open=False`,
`overwrite=True`, and `output_dir` set to
`scratch/results/<stem>/pipeline`. No `environment`. That does
not fit. Do not call `full_report`, and do not call `report`
without `eval=False`. If `eval` is absent, or Graphviz still
fails after one `add-python-package` retry for `skrub`, write
`pipeline.html` from `_repr_html_` or
`sklearn.utils.estimator_html_repr`.

## End of turn

When `model-ml-pipeline` dispatched this turn, pass JSON
`locator` up and return. Do not run `loop artifacts`, audit,
record-outcome, convert, site, or `git end-turn`.

Otherwise this skill owns the close. When both `policy.notebooks`
and `policy.site` are true, the turn is unfinished until
record-outcome, `notebook convert --html`, `site build`, and
`git end-turn` have run, in that order, after the locator is in
the close. A stop at an earlier gate still names `notebook convert`
then `site build` in that order. Do not leave them as a conditional
aside, and do not stop after the narrative. Run
`python -m skore_skills loop artifacts --stem <stem>`.
`stop` / `evaluate_incomplete` → name the missing file and do
not audit. `audit` → load `audit-ml-pipeline` when installed.
`record` → skip audit.

Then the checkpoint. If audit ran, wait for its close and pass
its digest and G-AUDIT-FINDING into `manage-ml-backlog`
record-outcome when that skill is installed. If audit did not
run, call record-outcome with the user's headline, if any, and
`n/a — audit not run`. Missing backlog skill → one line. Do
not write History here. Never mark `done` while smoke is red.
Record-outcome runs before convert and site build.

If `policy.notebooks` is true and `export-ml-notebook` is
installed, run `python -m skore_skills notebook convert
experiments/<stem>.py`, and the same command on
`audit/<stem>.py` when that file exists, with `--html` when
`policy.site` is also true. The unfitted-snapshot ban (do not
convert when the file already contains `skore.evaluate`) does
not apply to this close. Convert the experiment script even
though this turn wrote `skore.evaluate`. Converting only
`audit/<stem>.py` is not the close. `audit-ml-pipeline` does
not convert on this path. Site build embeds
`audit/<stem>.nb.html` under `## Notebooks`; do not add
`<!-- results-embed: audit -->`.
Convert re-executes the script. If convert fails because
`ipywidgets` is missing, load `add-python-package` for it
(agent) and convert again. Missing jupytext / nbclient /
nbconvert → one line naming `add-python-package`. Then, if
`policy.site` is true and `export-ml-site` is installed, run
`python -m skore_skills site build`. If `site build` errors
with `mkdocs-material is required`, load `add-python-package`
for `mkdocs-material` (agent) and build once more. Do not
`pixi add` / `uv add`. If that skill is missing, or the retry
still fails, name the error in one line. A build error does not
fail the turn.

Run `python -m skore_skills git end-turn --stage evaluate`.
If JSON `action` is `invoke`, load `persist-ml-git` when
installed and stop. Otherwise load `triage-ml-task` when
installed. Do not run `git commit` here.

### Checkpoint

Standalone only. 2–6 sentences of the result, grounded in the
headline or, when audit was skipped, `report.txt`. If audit
ran, ground the story in its Checks and Metrics. Do not invent
a metric.

Links: when site build ran or is about to,
`[report.html](<workspace>/report.html)` and
`html/<stem>.html`. Otherwise
`[journal/<stem>.md](journal/<stem>.md)`.

Tokens after the narrative: JSON `locator` first, then
G-AUDIT-FINDING (`n/a — audit not run` when skipped).

## Stops

- Pending setup (`status.setup.pending` non-empty) → load
  `setup-ml-project`. A declined `git` is not asked again. A
  declined env or workspace stops.
- Smoke missing or red on a history-dependent pipeline → build.
- Empty `split_kwargs` plus a possible group column → return
  to `build-ml-pipeline`. Do not default to `KFold`.
- `import skore` fails → G-SKORE-MODE if unset, then
  `add-python-package`. Do not drop back to `cross_val_score`.
- Hyperparameter search, serving, and multi-run tracking are
  out of scope.
- A missing package loads `add-python-package` when installed.
  Do not run `env add` here.

## Pre-flight — emit before any code

```
Pre-flight (evaluate-ml-pipeline):
- [ ] sklearn, skrub, skore import
- [ ] frame show is proceed; DataOp cv matches translation
      (or holdout / prefit, and the marker has no cv)
- [ ] skore_mode is set (local | hub | mlflow)
- [ ] evaluate consent is proceed, or the user answered Evaluate
- [ ] Call site is experiments/NN_*.py
- [ ] Snapshots are scratch/results/<stem>/snapshot.py
      (not cells in the experiment file)
- [ ] skore.evaluate omits splitter=
      (or splitter="prefit" and only the test table is passed)
- [ ] Smoke: passing | n/a (no history-dependent step) | STOP
```

## References

- `references/metadata-routing.md` — the locked `cv` stays on
  the DataOp; evaluate omits `splitter=`.
- `references/skrub_interop.md` — env-dict versus `(X, y)`.
- `references/g_skore_mode.md` — Project constructors.
- `references/reports.md` — when `evaluate` is too coarse.
- `references/custom-metrics.md` — a non-default metric via
  `with_scoring`.
- `references/custom-checks.md` — a check the user asked for.
- `templates/snapshot.py` — agent-only post-put snapshot. Copy
  to `scratch/results/<stem>/snapshot.py`.
