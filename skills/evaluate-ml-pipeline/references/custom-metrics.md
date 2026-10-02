# Custom metric

A metric skore already reports for the task needs no scorer. The
list is in `build-ml-pipeline`. Any other metric attaches to the
prediction DataOp with `.skb.with_scoring(...)` before
`.skb.make_learner()`. Confirm every signature with
`python -m skore_skills api get`.

Do not call `report.metrics.add`. Do not pass `scoring=` to
`skore.evaluate`; that argument does not exist. CV metadata is
separate: `split_kwargs` belongs on `mark_as_X`. Metric kwargs
belong on `with_scoring`.

## The scorer

Pass a scikit-learn metric name `with_scoring` accepts, or a
`make_scorer` around a `(y_true, y_pred)` function. Static
configuration such as `beta` belongs on `make_scorer`. Use a
named module-level function, not a lambda: `project.put` pickles
the learner that holds the scorer.

```python
from sklearn.metrics import fbeta_score, make_scorer

f2 = make_scorer(fbeta_score, beta=2, pos_label=1)
predictions = X.skb.apply(classifier, y=y).skb.with_scoring(
    f2,
    name="f2",
)
learner = predictions.skb.make_learner()
```

A metric that is not a scikit-learn function is the same wrapper.
Define it at module level:

```python
def business_cost(y_true, y_pred, *, false_positive_cost):
    false_positives = ((y_pred == 1) & (y_true == 0)).sum()
    return false_positive_cost * false_positives


cost = make_scorer(
    business_cost,
    greater_is_better=False,
    false_positive_cost=10,
)
predictions = predictions.skb.with_scoring(cost, name="business_cost")
learner = predictions.skb.make_learner()
```

Row-aligned inputs such as `sample_weight` are DataOps derived
from the marked X rows, passed as `kwargs`. They are not
`split_kwargs`.

```python
from sklearn.metrics import make_scorer, mean_absolute_error

weighted_mae = make_scorer(
    mean_absolute_error,
    greater_is_better=False,
)

X_source = data.drop(columns=[TARGET]).skb.mark_as_X()
sample_weight = X_source["sample_weight"]
X = X_source.drop(columns=["sample_weight"])
y = data[TARGET].skb.mark_as_y()

predictions = X.skb.apply(regressor, y=y).skb.with_scoring(
    weighted_mae,
    kwargs={"sample_weight": sample_weight},
    name="weighted_mae",
)
learner = predictions.skb.make_learner()
```

`sample_weight` must be derived from the same marked/aligned X
rows. Using the unsplit raw table can pass all rows to a fold
scorer and raise an inconsistent-length error.

Use one call for one scorer. A list or dictionary can share one
kwargs mapping. When metrics need different kwargs, chain
`with_scoring` calls adjacently at the end of the graph:

```python
predictions = (
    predictions.skb.with_scoring("accuracy")
    .skb.with_scoring(
        weighted_accuracy,
        kwargs={"sample_weight": sample_weight},
        name="weighted_accuracy",
    )
)
```

Do not insert another DataOp between chained scoring calls.

After `skore.evaluate`, the attached name is a row in
`report.metrics.summarize().frame()`:

```python
report = skore.evaluate(learner, data={"data": frame})
report.metrics.summarize().frame()
project.put(STEM, report)
```

The locked `cv` is on `mark_as_X`. Omit `splitter=` so skore
reuses it. See `references/metadata-routing.md`.
