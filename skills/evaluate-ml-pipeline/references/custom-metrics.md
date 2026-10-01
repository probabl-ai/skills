# Custom metric routing

Custom metrics have two supported routes. Pick by estimator.
Extra keyword arguments travel with that route; they do not
choose it. Confirm every signature with
`python -m skore_skills api get`.

| Need | Route | Read the result with |
|---|---|---|
| sklearn-style report, or an extra metric asked for on that report | `report.metrics.add(...)` | `report.metrics.summarize(...)` |
| `SkrubLearner`, including the locked comparison metric | prediction DataOp `.skb.with_scoring(...)` before `make_learner` | `report.metrics.score()` |

Neither route is a `scoring=` argument to `skore.evaluate`; that
argument does not exist. CV metadata is separate:
`split_kwargs` belongs on `mark_as_X`, while metric kwargs belong
to `metrics.add` or `with_scoring`. On a `SkrubLearner`, the
locked comparison metric uses `with_scoring` whether or not it
needs those kwargs.

## Report registry — add before `Project.put`

Use this route for sklearn-style reports and metrics that can be
computed from the report's estimator, X, and y.

For `(y_true, y_pred, **kwargs) -> score`, build a sklearn scorer.
Static configuration such as `beta` belongs on `make_scorer`:

```python
from sklearn.metrics import fbeta_score, make_scorer

report = skore.evaluate(estimator, X, y, splitter=splitter)
f2 = make_scorer(fbeta_score, beta=2, pos_label=1)
report.metrics.add(f2, name="f2")
report.metrics.summarize(metric="f2").frame()
project.put(STEM, report)
```

For a plain `(estimator, X, y, **kwargs) -> score` callable,
static kwargs can be supplied to `add`:

```python
def business_cost(estimator, X, y, *, false_positive_cost):
    predictions = estimator.predict(X)
    false_positives = ((predictions == 1) & (y == 0)).sum()
    return false_positive_cost * false_positives


report = skore.evaluate(estimator, X, y, splitter=splitter)
report.metrics.add(
    business_cost,
    false_positive_cost=10,
    greater_is_better=False,
)
report.metrics.summarize(metric="business_cost").frame()
project.put(STEM, report)
```

`CrossValidationReport.metrics.add` registers the metric on every
split report. Use named module-level functions, not lambdas:
Project storage pickles the metric registry, and top-level names are
the supported portable contract across reloads.

The ordering is mandatory:

```python
report = skore.evaluate(...)
report.metrics.add(...)
report.metrics.summarize(...)
project.put(STEM, report)
```

`Project.put` stores a point-in-time snapshot. Adding a metric
after `put` changes only the in-memory report until another `put`.

## DataOp scoring — attach before `make_learner`

A `SkrubLearner` consumes an environment dictionary, so a regular
sklearn scorer registered post-hoc cannot in general call it as
`estimator.predict(X)`. Attach scoring to the prediction DataOp:

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

`sample_weight` must be derived from the same marked/aligned X rows.
Using the unsplit raw table can pass all rows to a fold scorer and
raise an inconsistent-length error.

Use one call for one scorer. A list or dictionary can share one
kwargs mapping. When metrics need different kwargs, chain
`with_scoring` calls **adjacently** at the end of the graph:

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

After evaluation, inspect DataOp scoring with `metrics.score`;
these names do not become custom rows in `metrics.summarize`:

```python
report = skore.evaluate(learner, data={"data": frame})
report.metrics.score()
project.put(STEM, report)
```

The locked `cv` is on `mark_as_X`. Omit `splitter=` so skore
reuses it. See `references/metadata-routing.md`.
