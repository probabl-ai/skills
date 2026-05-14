# Pre-mark alignment — the 3-layer skrub DataOps pattern

*Workflow pattern (durable across library versions). For per-version
signatures or method surfaces of skrub / sklearn / skore, see the
workspace's `scratch/api/<lib>/<version>/` cache populated by
`python-api` Shape 0/1/2/3.*

The canonical shape for any pipeline where **features depend on history
that isn't part of the predict-time row itself**: time-series lags,
group-relative encodings, joins onto a slow-changing dimension table.
The pattern guarantees that predict-time featurization sees the full
upstream history, not just the rows of the current CV fold (or the
current predict batch).

## Why this exists — the failure mode it prevents

The naive shape — *load → compute features → split for CV* — silently
drops cold-start rows at every fold boundary. A lag-24h feature
computed inside a test fold has no rows < 24 h before the fold's first
row to look up against, so it's NaN. Either the model NaN-tolerates
(and feeds garbage signal), or the pipeline drops the row (and
`len(predictions) < n_predict_grid_rows`).

The 3-layer pattern fixes this by **marking X early on a `predict_grid`
node** and computing history-dependent features *after* the mark, with
the history DataOp passed as an extra argument so the join sees the
full history regardless of fold membership.

The smoke test in `tests/smoke/test_NN_*.py` is the executable proof
of this pattern (see `smoke-test-ml-pipeline`). A pipeline that
follows the pattern passes structurally; one that doesn't fails with
a row-count mismatch.

## The three layers

```
Layer 1 — sources at the root
   history_source = skrub.var("data_dir")
   history = history_source.skb.apply_func(load_history)

Layer 2 — pre-mark alignment, then mark X / y
   aligned = skrub.as_data_op({"history": history}).skb.apply(AlignXy())
   X = aligned["X"].skb.mark_as_X()
   y = aligned["y"].skb.mark_as_y()

Layer 3 — features AFTER mark_as_X, taking the upstream history DataOp
   X = X.skb.apply_func(add_lag_features, history)
   X = X.skb.apply_func(add_weather_features, history)
```

Three observations matter:

1. **`AlignXy` is a stateful BaseEstimator** with `fit_transform`
   returning `{"X": ..., "y": ...}` and `transform` returning
   `{"X": ..., "y": None}`. The fit-time path derives `y` from
   history (a target shift, a join, a label lookup); the predict-time
   path emits only the grid because there's no observable target.
2. **`X.skb.mark_as_X()` lands on the predict-grid node** — the rows
   the model is asked to predict on. Not on a featurized frame; the
   features come later.
3. **Layer-3 feature functions take `history` as a positional argument**,
   not the subset of history that belongs to the current fold. The
   join in each function reaches into the full upstream history node,
   so cold-start rows resolve to real values.

## Worked example — load forecasting at t+12

This is the actual code from `src/load_forecast/pipeline.py` in this
workspace, adapted minimally for narrative.

### `AlignXy` — Layer 2

```python
from sklearn.base import BaseEstimator
import polars as pl

_HORIZON_H = 12


class AlignXy(BaseEstimator):
    """Derive the t+12 target from the load history.

    fit_transform → {"X": DataFrame[time], "y": Series[load at t+12]}
    transform     → {"X": DataFrame[time], "y": None}
    """

    def fit_transform(self, data, y=None):
        history = data["history"]
        # Shift history timestamps back by the horizon: future.time == t
        # means the target (load at t+12) is history.actual_load_mw
        # where history.time == t + 12h.
        future = history.select(
            (pl.col("time") - pl.duration(hours=_HORIZON_H)).alias("time"),
            pl.col("actual_load_mw").alias("target_load_mw"),
        )
        predict_grid = history.select("time")
        joined = predict_grid.join(
            future.drop_nulls(), on="time", how="inner"
        ).sort("time")
        return {
            "X": joined.drop("target_load_mw"),
            "y": joined["target_load_mw"],
        }

    def transform(self, data):
        # Predict-time: y is unknown, but X (the predict grid) is the
        # full set of timestamps in history. Inner-joining on the
        # target here would drop the last horizon hours — wrong.
        return {"X": data["history"].select("time").sort("time"), "y": None}

    def fit(self, data, y=None):
        return self
```

The critical property: `transform()` returns *all* timestamps, not
just the ones with observable targets. The smoke test in
`tests/smoke/test_01_baseline.py` asserts exactly this — predict on a
24-hour window with no extra buffer, expect 24 predictions.

### Feature functions — Layer 3

```python
import polars as pl

_LOAD_LAGS_H = (12, 24, 168)


def add_lag_features(
    predict_grid: pl.DataFrame,
    history: pl.DataFrame,
    lags: tuple[int, ...] = _LOAD_LAGS_H,
) -> pl.DataFrame:
    """Join lagged load values onto each prediction time.

    For lag k, the value at prediction time t is the actual load at
    t − k hours, looked up from the *full* (non-split) history.
    """
    out = predict_grid
    for lag in lags:
        col = f"lag_{lag}h"
        lagged = history.select(
            (pl.col("time") + pl.duration(hours=lag)).alias("time"),
            pl.col("actual_load_mw").alias(col),
        )
        out = out.join(lagged, on="time", how="left")
    return out
```

Two arguments: the **predict grid** (the rows we're predicting on, the
`X` DataOp) and **history** (the full source DataOp, *not* a CV-fold
subset). The function joins history onto the grid; rows the fold
splitter put in test see real history values from before the fold,
not NaN.

A *pure-timestamp* feature (calendar / holiday / DST-switch) takes
**only** the predict grid — no history argument, because no upstream
reference is needed:

```python
def add_calendar_features(predict_grid: pl.DataFrame) -> pl.DataFrame:
    ...
```

### Assembly — `build_learner`

```python
import skrub
from skrub import tabular_pipeline


def build_learner(
    data_dir_preview=None,
    *,
    include_calendar_features: bool = False,
):
    # --- Layer 1: source root ---
    data_dir = (
        skrub.var("data_dir", value=str(data_dir_preview))
        if data_dir_preview is not None
        else skrub.var("data_dir")
    )
    history = data_dir.skb.apply_func(load_history)

    # --- Layer 2: alignment + mark X / y ---
    aligned = skrub.as_data_op({"history": history}).skb.apply(AlignXy())
    X = aligned["X"].skb.mark_as_X()
    y = aligned["y"].skb.mark_as_y()

    # --- Layer 3: history-dependent features AFTER mark_as_X ---
    X = X.skb.apply_func(add_lag_features, history)
    X = X.skb.apply_func(add_weather_features, history)
    if include_calendar_features:
        X = X.skb.apply_func(add_calendar_features)

    predictor = tabular_pipeline("regressor")
    predictions = X.skb.apply(predictor, y=y)
    return predictions.skb.make_learner()
```

The `data_dir_preview` parameter is an interactive-preview escape
hatch — it makes `learner.skb.preview()` work in a notebook by giving
the var a concrete value to bind against. Production runs pass the
binding via `skore.evaluate(learner, data={"data_dir": ...}, ...)`
(see `python-api/references/skrub_interop.md`).

## When you would NOT use this pattern

- **IID flat-table problems** — per-row math, stateful encoders that
  fit at train and apply per-row at predict, no lags / rolling / joins
  with history. The simpler shape `skore.evaluate(learner, X, y)`
  is fine.
- **No predict-grid concept** — if every row carries its own complete
  feature set at predict time (no upstream reference needed), the
  3-layer overhead is unnecessary.

The smoke-test row-count assertion in `smoke-test-ml-pipeline` still
fires for IID pipelines as a basic sanity check, but the
diagnostic-by-construction property only matters for the cross-row
case described here.

## Companion references

- `python-api/references/skrub_interop.md` — how the
  `SkrubLearner` produced by this pattern integrates with
  `skore.evaluate`.
- `build-ml-pipeline/references/source-binding.md` — why source-bound
  vars (Layer 1) are preferred over materialized `(X, y)` roots.
- `build-ml-pipeline` § "Common patterns" rule 2 — the parent skill's
  short version of this same pattern.
- `smoke-test-ml-pipeline` — the executable proof that a pipeline
  followed the pattern (or didn't).
