# Forecast evaluation

Read when the lock is a time deployment (`translation.scheme` is
`date_time`). The score, the report, and the persistence are
unchanged. This file adds what a forecast needs beside them.

## Score against the baseline

The Baseline cell is `seasonal_naive` and its note names the
variant. Score that naive forecast on the same test rows with the
same metric, from values known at each prediction time. Report the
metric for the model and the baseline, overall and per horizon.
A model that does not beat the baseline at some horizon is a
result. Say so; do not hide it in an average.

## Plot the series

Scores alone hide where a forecast fails. Draw, with
`plot-ml-figure`, the observed and predicted values over the test
folds:

- The x-axis is the target time (`prediction_time + h`), not the
  prediction time. One line per horizon, at most a few.
- Vertical dashed lines at the start of each test fold. When the
  folds are many, draw the last ones and say so. Shade the gap
  and horizon embargo when it is wide enough to see.
- Predictions come from the report: `X_test`, `y_test`, and
  `get_predictions(data_source="test")` on a report (on each
  entry of `reports_` for a cross-validation report). Confirm
  them with `api get`.

When the prediction goal is `intervals`, draw the median as a line
and the interval between the lowest and the highest quantile as a
shaded band. Call it a prediction interval, not a confidence
interval. Report its coverage next to its nominal level (the
share of observed values inside it, per horizon). Check that the
quantiles do not cross; if they do, sort them and say so. With
`point_predictions`, draw no band.

## Boundary forecast

Always show the user the forecast issued at the last observation
(`build-ml-pipeline` `references/forecasting.md`). Plot the recent
history, then the forecast at its target times. It has no truth to
score, so this plot is the check that it is plausible.

## Covariate vintage

When `translation.covariate_vintage` is `actuals_only`, put one
line on every forecast plot and one line in the close: the scores
are optimistic because the features used observed values where
deployment will have forecasts.
