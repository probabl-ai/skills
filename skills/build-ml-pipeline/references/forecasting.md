# Forecasting pipelines

Read when `translation.scheme` is `date_time`. The splitter is in
`custom-splitter.md`; the three layers are in `layer_examples.md`.
This file is what is specific to a forecast. Add lags and outside
features only when Method names them.

Snippets use polars and hourly steps. Write the step in
`translation.horizon_unit`. They show shape, not a dataset.

## Prediction grid, X, and y

`X` is the grid of prediction times, one row per forecast issued.
`y` has one column per horizon, `"<h>h"`: the value at
`prediction_time + h`. The row of `X` holds the prediction time
and nothing from the future.

Put the history on a regular grid before any shift. A row shift
on an irregular series misaligns silently. Missing steps become
explicit null rows. Extend the grid past the last observation by
at least the largest horizon, with empty rows, so that joins at
the end of the data still find a row. See "Boundary forecast".

```python
def regular_history(raw, step="1h", buffer=dt.timedelta(hours=48)):
    hourly = raw.group_by(pl.col("time").dt.truncate(step)).agg(
        pl.col("value").mean()
    )
    grid = pl.datetime_range(
        hourly["time"].min(), hourly["time"].max() + buffer,
        interval=step, time_zone="UTC", eager=True,
    ).alias("time")
    return grid.to_frame().join(hourly, on="time", how="left", maintain_order="left")
```

Keep the grid in UTC. Compute calendar features from the local
zone (`convert_time_zone`) so daylight-saving changes do not shift
the hour of day.

A row with a missing label is dropped when fitting and kept when
predicting. This is the `AlignXy` shape from `layer_examples.md`
with one label column per horizon. `fit_transform` inner-joins the
grid to the observed values, so a missing label removes its row
without a `drop_nulls` on pipeline output. `transform` returns the
whole grid.

```python
class AlignXy(BaseEstimator):
    def __init__(self, horizons=(1, 24)):
        self.horizons = horizons

    def fit(self, data, y=None):
        return self

    def fit_transform(self, data, y=None):
        observed = data["history"].filter(pl.col("value").is_not_null())
        X = data["prediction_time"]
        for h in self.horizons:
            ahead = observed.select(
                (pl.col("time") - pl.duration(hours=h)).alias("prediction_time"),
                pl.col("value").alias(f"{h}h"),
            )
            X = X.join(ahead, on="prediction_time", how="inner", maintain_order="left")
        return {
            "X": X.select("prediction_time"),
            "y": X.drop("prediction_time"),
        }

    def transform(self, data):
        return {"X": data["prediction_time"], "y": None}
```

## Features

Build the features of one horizon from `X`, the history, and `h`.
Call the function once per horizon. Add a `target_time` column
(`prediction_time + h`) first. Lags, rolling windows, calendar
and outside features are all keyed by it.

- A value at time `t` is usable only if it is known by the
  prediction time. A lag from the target time must be at least
  `h`, plus the publication delay of the value when there is one.
  Ask for that delay if neither the data nor the gap says.
- Calendar and holiday features come from the target time. They
  are known in advance.
- Outside features follow `translation.covariate_vintage`:
  `known_future` is the calendar only; `forecast_vintage` joins
  the forecast issued at the prediction time for the target time;
  `actuals_only` joins the observed value at the target time.
  Write that caveat in the experiment and the design note.
- Drop `prediction_time` and `target_time` before the predictor
  unless `time_role` is `covariate`.

Guard each lag or rolling function against future values. Mask the
history after the last value known at the prediction time, keeping
the grid, and compare the features of a few sampled rows. A
difference means the function reads the future. Run it while
developing and in the smoke test; it can be switched off for
speed.

```python
def check_no_future_leak(
    add_features, grid, history, horizon, n=5, delay=dt.timedelta(0), seed=0
):
    sample = grid.sample(min(n, grid.height), seed=seed)
    for t in sample["prediction_time"]:
        row = sample.filter(pl.col("prediction_time") == t)
        known = history.with_columns(
            pl.when(pl.col("time") <= t - delay).then(pl.col("value")).alias("value")
        )
        full = add_features(row, history=history, horizon=horizon)
        if not full.equals(add_features(row, history=known, horizon=horizon)):
            raise AssertionError(f"{add_features.__name__} reads past {t - delay}")
```

## Predictor

One predictor per horizon, fit on `y["<h>h"]`. State the number of
predictors to the user when there are many horizons.

A final step joins the predictions into one frame, columns
`"<h>h"`. It reads `skrub.eval_mode()`. In `fit` its inputs are the
fitted predictors, so it returns them unchanged. In `predict` and
`score` they are the predictions. `preview` runs on real values.
Confirm the mode names with
`python -m skore_skills api get skrub.eval_mode`.

```python
def concat_horizons(parts, mode=skrub.eval_mode()):
    if mode == "fit":
        return parts
    return pl.DataFrame({f"{h}h": p for h, p in parts.items()})
```

Two defaults that mislead on a series:

- Trees do not extrapolate a trend. When the level drifts, predict
  the difference from a value known at prediction time (the
  baseline's value) and add it back.
- `HistGradientBoostingRegressor` early stopping uses a random
  validation split, so neighbouring steps sit on both sides. Fix
  `max_iter` and set `early_stopping=False`.

## Several series

One frame with a series id column. Build lags and rolling windows
per series (`.over("series_id")`) and join on the id and the time.
The split is by time and the same dates apply to every series.
Pick one model with the id as a feature, or one model per series,
and say which. If the forecast must also serve a series that was
not in the fit, say that the lock is a single deployment and this
file does not cover it.

## Boundary forecast

Before smoke and evaluate, fit on all the data and forecast from
the first prediction time whose target time is past the last
observation. No label exists for it. Check:

- the call returns one row, with one value per horizon;
- for each feature column, the share of nulls on that row is not
  above the share on the training rows;
- the values look plausible when plotted over the recent history
  (`evaluate-ml-pipeline/references/forecasting.md`).

A missing buffer shows up here: the shifted values land past the
end of the history, and the features are null.
