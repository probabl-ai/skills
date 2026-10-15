# Horizon and gap

Record both in the same unit. Horizon may be a comma-separated
list. Gap is one quantity. A gap of `0 <unit>` is allowed.

**Prediction time** is the moment a forecast is issued. **Target
time** is the moment the forecast is about. **Horizon** is the
lead from prediction time to target time. Each entry is one target
and one predictor. Write `<number> <unit>`, for example
`1 hour, 2 hour, 24 hour`. Every entry uses one unit.

**Gap** is the delay from the target time of the last training
row to the first prediction time of the model trained on it. For
each horizon `h`, training ends at least `gap + h` before that
target. A training row is usable only once its true value is
known, so the gap is at least:

- how long after its target time the true value is published (a
  count that is only known four days later adds four days), and
- how long it takes to retrain and deploy a model.

Ask for both when the data or the text shipped with it does not
state them. Do not assume the true value is available at its
target time.

Example. A forecast is issued every day at 12:00 for the next
24 hours (horizon `24 hour`). The Monday 12:00 forecast targets
Tuesday 12:00. If that value is known at once and the model is
redeployed at once, the first forecast that may use it is issued
Tuesday 12:00 and the gap is `0 hour`. If the value is published
four days late, the gap is `4 day`, written in the horizon's
unit (`96 hour`).

Several horizons share one gap. The training end for each is
`gap + h`, so the longest horizon sets the widest embargo.

Do not name a splitter class or a constructor argument.
