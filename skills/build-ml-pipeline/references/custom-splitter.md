# Custom cross-validator

The split copies the locked deployment: how a new row arrives
when the model is used. That is the Modeling decisions
`deployment` row, plus horizon, gap, and generalize-to when
those cells are set. A scored fit contains only rows that
deployment would already have seen.

`KFold`, `GroupKFold`, and the time series sketch are usual
shapes for that setting. Use one when it scores rows the way
the deployment does. Another deployment gets its own `split`.
Horizon, gap, groups, and timestamps stay in the units and
columns the lock recorded. The constructor follows them.

Attach the class on `mark_as_X` after the learner graph exists
and before `.skb.make_learner()`. For `translation.scheme`
`date_time`, use the time series section.

## Contract

```python
class MySplitter:
    def split(self, X, y=None, groups=None):
        # Yield (train_idx, test_idx) as integer positions into X.
        ...

    def get_n_splits(self, X=None, y=None, groups=None):
        # Return the number of pairs `split` will yield.
        ...
```

- `split` is a generator (`yield`).
- The yielded arrays are integer positions, not boolean masks or
  labels.
- The two arrays in each pair are disjoint. Their union does not
  have to cover `X`.
- `get_n_splits` may ignore its arguments when the count is fixed
  at construction.

`split_kwargs` keys are the keyword arguments of `split`.
`split_kwargs={"groups": groups}` calls `split(..., groups=groups)`.
An extra key that `split` does not declare raises `TypeError`.
skrub requires `cv=` whenever `split_kwargs` is set.

Evaluate omits `splitter=` so skore reuses this `cv`. See
`evaluate-ml-pipeline/references/metadata-routing.md`.

## Subclassing `BaseCrossValidator`

Subclassing inherits `__repr__` and parameter validation. The base
`split` only forwards `groups`. Any other argument, such as
`times` or a block id, means implementing `split` yourself.
`_iter_test_indices` is enough only when `split` needs `X`, `y`,
and `groups`. Confirm the base class with
`python -m skore_skills api get`.

## Time series

A time deployment scores a fit that has only rows available
before the forecast. `split` takes the timestamp array as
`times`, aligned with the rows of `X`. Fold edges are those
timestamps. `n_splits` is the locked retrain count. When that
count is 1 there is no `cv`.

**Gap** is the delay from the last training row to prediction
time, the first moment a forecast can be issued. **Horizon** is
the lead from that prediction time to the target time. For each
horizon `h`, training ends at least `gap + h` before that
target. Both durations come from the lock (`translation.horizons`,
`translation.horizon_unit`, `translation.gap`,
`translation.gap_unit`) and stay in that unit. A gap of 0 means
the forecast is issued as soon as training data ends. Build one
`DateTimeSplit` per horizon. Each one is one predictor.

The sketch below is that deployment as one later test window
per retrain, with the embargo in neither side. A different time
deployment keeps this contract and changes the body of `split`.

The timestamp column is the one the EDA, or the text shipped with
the data, already names. A `sort_key` column is not a feature and
is still the `times` array. A `covariate` column stays in the
features and is the same array.

```python
class DateTimeSplit:
    def __init__(self, n_splits, horizon, gap):
        self.n_splits = n_splits
        self.horizon = horizon
        self.gap = gap

    def split(self, X, y=None, times=None):
        # times: datetime values, one per row of X.
        # Yield (train_idx, test_idx) as integer positions.
        # For each retrain, the test window is the next block of
        # time. Training rows end at least gap + horizon before
        # that window. Rows inside that embargo are in neither side.
        ...

    def get_n_splits(self, X=None, y=None, groups=None):
        return self.n_splits
```

```python
X = frame.skb.mark_as_X(
    cv=DateTimeSplit(n_splits=folds, horizon=horizon, gap=gap),
    split_kwargs={"times": timestamps},
)
```
