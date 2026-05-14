---
name: smoke-test-ml-pipeline
description: >
  Owns the smoke test contract for an ML experiment: a small,
  diagnostic-by-construction pytest that fits the experiment's
  learner on a portion of the real `data/` source and predicts
  on a *disjoint* portion that deliberately carries **no
  pre-history buffer**. The assertion is structural — the number
  of predictions must equal the number of rows in the predict
  grid. A pipeline that loads-then-features-then-splits will
  silently drop the cold-start rows of the predict slice and the
  test will fail with a row-count mismatch; a pipeline that marks
  X early and references upstream history nodes from feature
  steps will pass trivially. The smoke test is the executable
  proof of the X-marker placement rule from `build-ml-pipeline`.

  TRIGGER when: `test-ml-pipeline` has dispatched here to write
  the smoke test for an approved experiment; `pytest tests/smoke/`
  is failing on row count; the user asks "why is the smoke test
  failing?"; a pipeline edit in `build-ml-pipeline` needs an
  executable proof; an experiment script changes the pipeline
  shape and the matching smoke test needs revisiting.

  SKIP when: the experiment plan does not exist or is not yet
  approved (route to `iterate-ml-experiment`); the user is asking
  about a regression test or schema invariant (route to
  `regression-test-ml-pipeline` /
  `distribution-test-ml-pipeline` once those exist); the question
  is the *interpretation* of CV metrics, not predict-time
  correctness (route to `evaluate-ml-pipeline`).

  HOW TO USE: read the matching experiment's `plan/NN_*.md` and
  `experiments/NN_*.py` first to understand the pipeline's source
  binding (what env-dict keys does `build_learner` expect?). Then
  construct two env-dicts from the **real `data/` source** — a
  train env and a predict env — such that the predict env carries
  *only the rows we want predictions for* and *no pre-history
  buffer*. The hard assertion is that the prediction count
  matches the predict-env row count exactly. The soft assertion
  is that the smoke set's MAE is within `3 × CV_mean` (or the
  task-appropriate analogue). **Do not write the experiment plan
  or run CV — that's other skills' job.**
---

# Smoke Test ML Pipeline

The minimal pytest that catches the "load → featurize → split"
anti-pattern at iteration time, before it reaches production.

## Stop conditions — read before anything else

- **No smoke test without an approved plan + script.** The pairing
  rule from `test-ml-pipeline` is hard:
  `tests/smoke/test_NN_<short_name>.py` exists only when
  `plan/NN_<short_name>.md` is at least `approved` *and*
  `experiments/NN_<short_name>.py` exists with the matching stem.
- **Symbol from memory is forbidden.** Any skrub /
  scikit-learn name you write in the smoke test must come from a
  `Skill(python-api)` / `Skill(python-api)` call **in this
  turn**. The smoke test is a small file but it imports the
  predicting-package API surface; the same memory-forbidden rule
  applies.
- **Don't shrink the assertion.** The hard assertion is exact
  row-count equality. Not "approximately equal", not "at least 80%
  of expected rows". A row-count mismatch *is* the failure mode the
  smoke test exists to catch. Loosening the assertion silently
  reintroduces the bug.
- **Don't synthesize the fixture.** The smoke test reads the real
  `data/` source. Synthetic fixtures look fine but skip the
  loaders that actually break in production.
- **No wrappers, no NaN-handling, no `eval_mode` hacks.** If the
  smoke test only passes after wrapping the predictor or
  conditioning on `eval_mode`, the pipeline is wrong. Route back
  to `build-ml-pipeline` and fix the X-marker placement.
  Wrappers paper over the failure mode; they don't solve it.
- **The smoke test uses *only* the predicting package's API.**
  For a `SkrubLearner` produced by `build-ml-pipeline` that means
  skrub's `fit` / `predict` / (optionally `score`) plus
  `sklearn.metrics` for any metric the soft assertion uses.
  **Do not import `skore`** (or any other tracking / reporting
  library) in the test file. The smoke test must be runnable in
  any environment that can `import skrub` + `import sklearn` —
  the skore Project is a side artifact, not a test dependency.
  Soft-assertion baselines (CV-mean MAE, etc.) are **hardcoded
  from the plan's Status.headline** with a comment pointing to
  the plan; update by hand when the experiment's headline number
  changes.

## Pre-flight — emit this checklist as visible text before any test code

```
Pre-flight (smoke-test-ml-pipeline):
- [ ] Tier 1 mandatory libs importable: pytest + sklearn + skrub
      (per `data-science-python-stack` § "Tier 1"). **Not skore** —
      see the Stop conditions; the smoke test is intentionally
      portable to any skrub-capable environment
- [ ] `plan/NN_<short_name>.md` read this turn (frozen sections:
      Question, Method) so the test asserts what the experiment claims
- [ ] `experiments/NN_<short_name>.py` skimmed this turn for the env-dict
      keys `build_learner` consumes (`data_dir` / `start` + `end` /
      `raw_frame` / etc.)
- [ ] `src/<pkg>/data.py` skimmed this turn for the loader signature
      (so the predict-env construction matches the loader's expectations)
- [ ] Test category & stem decided: `tests/smoke/test_NN_<short_name>.py`
- [ ] Predict-grid size decided: smallest window that still triggers
      the failure mode (default: a single horizon-length slice; for
      time series, the most recent N steps such that the target is
      *just* observable for assertion)
- [ ] Hard assertion wired: `len(predictions) == n_predict_grid_rows`
- [ ] Soft assertion wired (or explicitly skipped): smoke MAE within
      `3 × CV_MEAN_HARDCODED_FROM_PLAN` (or task-appropriate
      analogue). Value is a literal pulled from the matching
      `plan/NN_<short_name>.md` § Status.headline; the test does
      not import `skore` / read the project store at runtime.
```

## What the smoke test asserts

Two assertions, two severities:

### Hard — the row-count check

```python
assert len(predictions) == n_predict_grid_rows
```

This is the *structural-correctness* assertion. It is a binary
pass/fail and it is the **whole point** of the smoke test. A
correctly built pipeline (per `build-ml-pipeline`'s X-marker rule)
satisfies this trivially. A pipeline that loads-then-features-
then-splits will fail it because predict-time featurization on the
predict env runs with no pre-history buffer and silently drops
cold-start rows.

`n_predict_grid_rows` is the count of rows the predict env
*claims* to want predictions for — typically the number of
target-time rows in the predict-time grid. If the pipeline's
source binding is a directory of raw files, it's the row count of
the supervised frame derived from the predict env at predict time
(usable via `build_supervised_frame(predict_dir)`).

### Soft — the metric-vs-CV gap

```python
smoke_mae = mean_absolute_error(y_true, predictions)
assert smoke_mae < 3 * cv_mae_mean, (
    f"smoke MAE {smoke_mae:.0f} is more than 3× the CV mean "
    f"({cv_mae_mean:.0f}); predictions may be NaN-poisoned even "
    f"though the count matches."
)
```

The metric gap catches the second-order failure mode: the
prediction count is right, but the values are garbage because some
features are NaN at predict time (e.g. an encoder hasn't seen a
new category, a lag is null because the upstream history reference
wasn't wired correctly). The `3×` bound is a starting heuristic;
adjust per task. The smoke window is a single seasonal slice, so
the bound has to be loose enough that a *legitimate* hard-season
window doesn't trip it.

The soft assertion is **opt-out, not opt-in**: skip it only if the
task has no obvious metric-vs-CV comparator (e.g. the smoke fixture
deliberately has no ground truth). If you skip it, leave a comment
on *why* in the test file.

## The diagnostic-by-construction property

The fixture is built specifically to **fail on the buggy shape and
pass on the correct one**. This is the single most important
property of the smoke test; if you take the fixture construction
shortcut and it doesn't have this property, the test is worthless.

Concretely, the predict-time env-dict carries **only the rows we
want predictions for, with no pre-history buffer beyond what
predict-time-known features absolutely require**. Two consequences:

- **Late-`mark_as_X` pipeline**: features are computed inside the
  graph from the predict env's data alone. Backward lags / rolling
  windows / target shifts have NaN at the cold-start rows. The
  pre-marker `drop_nulls` (or the model's NaN intolerance) drops
  those rows. `len(predictions) < n_predict_grid_rows`. **Test
  fails.**
- **Early-`mark_as_X` pipeline**: the marker lands on the
  predict-grid node (Layer 2 of `build-ml-pipeline`'s rule 2);
  history-dependent features take the upstream history DataOp as
  an additional `apply_func` argument. At predict time, the
  history node resolves to the full available history (bound
  from the same source the train env uses), and the join in each
  feature step produces real values for every row in the predict
  grid. `len(predictions) == n_predict_grid_rows`. **Test
  passes.**

The two outcomes are deterministic. The smoke test cannot be
"flaky" — if the row count is off by one, the pipeline is wrong.

For the predict-grid size: **smallest is best**. Use the smallest
predict window that is still an honest predict-time grid. A
single horizon-length slice (e.g. one day for a t+24 model) is
enough to expose the failure; anything larger only hides it
behind volume.

## Fixture construction — `data/` is the source

The fixture **reads from the real `data/` source**, not from a
synthetic generator and not from a checked-in fixture file. The
loaders the experiment uses are the loaders the smoke test must
exercise. Synthetic fixtures defeat the purpose.

Construction depends on the experiment's source binding (read
`experiments/NN_*.py` to find out which env-dict keys
`build_learner` consumes), but the shape is always the same:

1. Identify the predict-grid time bounds (`predict_start`,
   `predict_end`). For time series, the most recent
   horizon-equivalent window of the data.
2. Identify the train env. The cleanest choice is *all data
   strictly before `predict_start - HORIZON`* (embargo equal to
   the forecast horizon). For tabular IID, just exclude the rows
   in the predict grid.
3. Build two env-dicts:
   - `train_env`: whatever shape the experiment uses for its
     fit binding, restricted to data before the embargo.
   - `predict_env`: the predict-grid description, with **no
     additional history padding** (this is the diagnostic
     property; if you pad, the test passes spuriously).
4. Compute `n_predict_grid_rows` independently of the prediction —
   the count comes from the supervised representation of the
   predict env (not from the prediction itself).
5. Compute `y_true` from the supervised representation of the
   predict env (the soft assertion's ground truth).

The fixture **must not write derived files to `data/holdout/`,
`data/train/`, etc.** Those are workspace-level artifacts owned
by the project's setup script(s); the smoke test fixture is
ephemeral. Use `tmp_path` (the pytest-built-in temporary
directory fixture) when the experiment's source binding requires
on-disk inputs.

Three common source-binding shapes — the smoke fixture has to
match whichever the experiment uses:

| Binding shape | Predict env construction | `n_predict_grid_rows` |
|---|---|---|
| **Directory of raw files** — `build_learner` binds a `data_dir`-style var; the loader globs / reads files from it. | Write a tiny temp dir with the time-sliced raw files inside the test (use the `tmp_path` pytest built-in). Bind it as `data_dir`. | The row count of the supervised representation of the predict env (e.g. `len(build_supervised_frame(predict_dir))` in load-forecasting), known a priori from the slice. |
| **Predict-grid + raw-history sources** — the early-mark shape from `build-ml-pipeline` rule 2: `predict_grid` plus `history_source` / `weather_source` / etc. as separate vars. | Build the in-memory `predict_grid` value (a list of timestamps, a panel-key grid, …) and the source identifiers. No file write needed. | `len(predict_grid)`. |
| **Materialized `(X, y)` IID** — `build_learner` binds `X` and `y` directly (or a single `data` env-dict mapping to `{"X": ..., "y": ...}`). | Hold out a small subset of rows from the materialized `X` (and the matching `y`) before fit; `train_env` gets the rest, `predict_env` gets the held-out subset. | `len(predict_subset)`. |

For the second shape (predict-grid + raw-history sources), the
three layers — sources → predict-grid + alignment + `mark_as_X`
→ features after (with history as an upstream reference) — are
described in `build-ml-pipeline` § "Common patterns" rule 2,
with a full worked example (drawn from this workspace's
01_baseline pipeline) in
`python-api/references/pre_mark_alignment.md`. Read that
reference before constructing the predict env for an early-mark
pipeline.

### IID flat-table problems — what the smoke test still buys you

For pipelines with **no cross-row dependencies** (per-row math,
stateful encoders that learn at fit and apply per-row at
predict, no lags / rolling / joins-with-history), the smoke
test reduces to "fit on the train subset, predict on the
held-out subset, assert `len(predictions) == len(predict_subset)`".

The **diagnostic-by-construction property does not apply** —
there are no cross-row reaches for the test to break, so the
hard assertion will pass on a correctly-built pipeline *and* on
a buggy one. What the smoke test still catches in the IID case:

- Loader bugs that drop or duplicate rows on a smaller input
  than CV used.
- Shape mismatches between `learner.predict(env)`'s output and
  the predict-env row count (e.g. an estimator that returns
  `(N, 2)` predictions when the test only checks `len(...)`).
- Accidental NaN-poisoning when an encoder has never seen a
  category present in the predict subset (the soft assertion
  on smoke-MAE-vs-CV-mean catches this; keep it on).

Treat the IID smoke test as a **sanity check**, not a
CV-replacement. The CV-replacement role is what the test
plays for cross-row pipelines, where the diagnostic-by-
construction property is the load-bearing guarantee.

## The standard pytest shape

One test function per smoke test file. The function name mirrors
the experiment stem so pytest output is self-explanatory.

```python
"""Smoke test for `experiments/NN_<short_name>.py`."""

# stdlib + numpy first
import pytest

from <pkg> import PROJECT_ROOT
from <pkg>.pipeline import build_learner
# additional imports per the experiment's binding shape

DATA_DIR = PROJECT_ROOT / "data"


@pytest.fixture
def train_predict_envs(tmp_path):
    """Build a (train_env, predict_env, n_predict_grid_rows, y_true) tuple.

    Diagnostic by construction: predict_env carries only the
    rows we want predictions for, with no pre-history padding.
    """
    # ... per-experiment fixture construction ...
    return train_env, predict_env, n_predict_grid_rows, y_true


def test_NN_<short_name>(train_predict_envs):
    """Predict-time replay must produce one prediction per predict-grid row."""
    train_env, predict_env, n_predict_grid_rows, y_true = train_predict_envs

    learner = build_learner()
    learner.fit(train_env)
    predictions = learner.predict(predict_env)

    # HARD: structural correctness.
    assert len(predictions) == n_predict_grid_rows, (
        f"got {len(predictions)} predictions for "
        f"{n_predict_grid_rows} predict-grid rows — pipeline is "
        f"dropping cold-start rows; check `mark_as_X` placement "
        f"and that history-dependent features reference an "
        f"upstream history node, not a per-slice computation."
    )

    # SOFT: predictions are not NaN-poisoned.
    from sklearn.metrics import mean_absolute_error
    smoke_mae = mean_absolute_error(y_true, predictions)
    # CV_MAE_MEAN is hardcoded at the top of the file from
    # `plan/NN_<short_name>.md` § Status.headline. The smoke test
    # uses only the predicting package's API (skrub/sklearn) —
    # no skore import, so it runs anywhere skrub does.
    assert smoke_mae < 3 * CV_MAE_MEAN, (
        f"smoke MAE {smoke_mae:.0f} > 3 × CV mean "
        f"({CV_MAE_MEAN:.0f}) — predictions may be NaN-poisoned."
    )
```

`tmp_path` is the pytest built-in for a per-test temporary
directory; use it whenever the experiment's source binding
requires on-disk inputs.

## Failure semantics

A failing smoke test is a **pipeline-shape problem**, not a
metric problem.

- **Hard-assertion failure** (row count) → the pipeline is broken.
  Re-enter `build-ml-pipeline`, audit the X-marker placement and
  the history-dependent feature steps. Don't tune the model;
  don't loosen the assertion; don't add a wrapper. Fix the shape.
- **Soft-assertion failure** (metric way off) → the predictions
  exist but are garbage on the smoke window. Most common cause:
  an upstream history node isn't being correctly resolved at
  predict time, so a lag column is silently NaN. Inspect
  `learner.skb.full_report()` and look for nodes whose value at
  predict time doesn't match what fit time saw.
- **Failure blocks `done` status.** `iterate-ml-experiment` § 4
  refuses to flip an experiment to `done` until the matching
  smoke test passes. The CV report can land in the skore Project
  before the smoke test passes (CV is independent of predict-time
  binding), but the experiment row in `PLAN.md` stays `approved`
  until smoke passes.

## What this skill does NOT do

- Run pytest. Test execution is the user's call (or CI's).
- Write the experiment plan or the experiment script. Those are
  `iterate-ml-experiment` and `organize-ml-workspace` /
  `build-ml-pipeline`.
- Touch the skore Project. The smoke test does not call
  `project.put` — it's a pre-flight check, not a metric
  artifact. CV metrics come from `evaluate-ml-pipeline`.
- Define what "good metrics" mean. The hard assertion is
  structural; the soft assertion is a sanity bound, not a
  performance target. Performance judgment is the user's, per
  `iterate-ml-experiment`'s rule that the user judges results.

## Companion skills

- **`test-ml-pipeline`** — the router that dispatched here.
  Owns layout and pairing.
- **`build-ml-pipeline`** — owns the X-marker placement rule
  the smoke test asserts. Smoke-test failure typically routes
  back here for a pipeline-shape fix.
- **`iterate-ml-experiment`** — owns the iteration loop. Requires
  the smoke test to pass before an experiment can flip to `done`.
- **`evaluate-ml-pipeline`** — owns CV. The smoke test fills the
  predict-time-binding gap CV doesn't cover. The soft assertion's
  CV-mean baseline is *hardcoded* in the smoke test from the
  matching plan's Status.headline (which `evaluate-ml-pipeline`
  ultimately fills in after the run); the test does not import
  skore at runtime.
- **`python-api`** / **`python-api`** — symbol references for
  the predicting-package APIs the smoke test uses. Consult
  before naming any imported function in the test body.
  `python-api` is **not** a smoke-test dependency — see the
  "no skore import" Stop condition above. **Cache hits first**:
  check `scratch/api/<lib>/<version>/` before WebSearching;
  cache new findings back there (per `python-api` Shape 0/3).
- **`data-science-python-stack`** — declares pytest as a Tier 1
  mandatory dependency for any workspace using this skill.
- **`python-code-style`** — **must be invoked** after writing or
  editing `tests/smoke/test_NN_*.py`. Running `pixi run ruff
  check` directly without invoking this skill silently drops the
  NumPyDoc docstring convention the stack expects: ruff's
  `D`-rules pass on a one-line summary, but only the skill body
  teaches the parameter-shape-in-type-slot and the section
  layout (`Parameters` / `Returns` / `Notes`) the test fixture +
  test function should use.
