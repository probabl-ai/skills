# Baseline

The baseline is the comparison point, named in words. It is not an
estimator configuration. Ask for one of the tokens below. A later
comparison is the next experiment.

- `seasonal_naive` — on a time-series forecast, repeat the last
  observed season (for example the last week), not the mean of the
  whole series
- `group_mean` — predict the mean of a column that is known at
  prediction time. Do not use the generalize-to column: those ids
  are unseen, so their mean does not exist
- `logistic` — a simple model that emits probabilities, when that
  is the goal
- `production` — whatever is already used in deployment; name it
  in the note
- `dummy` — a global mean or majority class, when none of the
  above fits

The note is one short phrase: the season, the known column, or the
production system.
