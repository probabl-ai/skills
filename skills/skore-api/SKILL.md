---
name: skore-api
description: API reference for using skore as an evaluation library for scikit-learn-compatible models. Covers `evaluate` as a dispatcher returning a report, the report API (metrics / inspection / data accessors and their diagnostics), and project management to persist and compare reports across runs (local, hub, mlflow). Trigger when the user mentions skore reports, `EstimatorReport`, `CrossValidationReport`, `ComparisonReport`, `evaluate`, `Project`, `summarize`, or asks how to evaluate / inspect / persist a model with skore.
---

# Using skore as an evaluation library

skore turns the "fit a model + score a metric" loop into a richer object — a **report** — that exposes metrics, inspection tools, and dataset diagnostics through a uniform API. Reports can then be persisted in a **project** so several runs can be browsed, filtered and compared.

There are two pieces:

1. **Evaluation** — call `skore.evaluate(...)` once; get back the right report type for your evaluation strategy. From there you read diagnostics off the report.
2. **Project management** — drop reports into a `skore.Project`, get a `Summary` dataframe with all metadata + metrics, filter it, retrieve reports.

## Quick map

| You want to… | Look at |
| --- | --- |
| Pick the right evaluation strategy and get a report | This file, *Evaluate* below |
| Understand the three report types and their accessors | [reports.md](reports.md) |
| List of available diagnostics (metrics, inspection, data) | [diagnostics.md](diagnostics.md) |
| Persist, summarize, filter, retrieve, compare reports | [project.md](project.md) |

## Evaluate — the single entry point

`skore.evaluate(estimator, X=None, y=None, data=None, *, splitter=0.2, pos_label=None, n_jobs=None)` is a dispatcher: the type of report it returns depends on `estimator` and `splitter`.

You feed the data in **one** of two ways:

- **sklearn-style** — pass `X` and `y` positionally / by keyword. Use this for any sklearn-compatible estimator that fits via `estimator.fit(X, y)`.
- **env-dict-style** — pass `data={"<var-name>": value, ...}`. Use this for estimators whose `fit` takes a single mapping rather than `(X, y)` — most importantly **skrub `SkrubLearner`**, which is the recommended pipeline shape per `build-ml-pipeline`. The keys in `data` are the `skrub.var(name=...)` names declared in the DataOps graph (typically `"X"` and `"y"`, plus any extra source-bound vars like `"path"`).

`X`/`y` and `data` are mutually exclusive — pick the form that matches your estimator.

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from skore import evaluate

X, y = make_classification(random_state=42)
```

Single estimator, single train/test split (default 80/20, shuffled, `random_state=0`):

```python
report = evaluate(LogisticRegression(), X, y)              # -> EstimatorReport
report = evaluate(LogisticRegression(), X, y, splitter=0.3) # custom test_size
```

Single estimator, cross-validation:

```python
report = evaluate(LogisticRegression(), X, y, splitter=5)  # -> CrossValidationReport
# or pass any sklearn CV splitter, e.g. KFold(n_splits=10)
```

Skrub `SkrubLearner` (env-dict form):

```python
import skrub
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold

X_dataop = skrub.var("X").skb.mark_as_X()
y_dataop = skrub.var("y").skb.mark_as_y()
predictions = X_dataop.skb.apply(Ridge(), y=y_dataop)
learner = predictions.skb.make_learner()

report = evaluate(learner, data={"X": X, "y": y}, splitter=KFold(5))
# -> CrossValidationReport
```

Already-fitted estimator (`X`, `y` are the test set):

```python
fitted = LogisticRegression().fit(X_train, y_train)
report = evaluate(fitted, X_test, y_test, splitter="prefit")  # -> EstimatorReport
```

Multiple estimators (compare them):

```python
report = evaluate(
    {"baseline": LogisticRegression(), "tuned": LogisticRegression(C=2.0)},
    X, y, splitter=0.2,
)                                                          # -> ComparisonReport
list(report.reports_)  # -> ['baseline', 'tuned']
```

Pass a list of estimators (positional comparison) or align different feature matrices per estimator with a list/dict of `X`. See `evaluate`'s docstring at `skore/src/skore/_sklearn/evaluate.py` for the full matrix of `(estimator, X)` shapes.

The same `data=` parameter is accepted by `CrossValidationReport(estimator, data=..., splitter=...)`. `EstimatorReport` exposes `train_data=` / `test_data=` for the same purpose at the prefit-or-single-split level. See [reports.md](reports.md).

## What you get back

Whatever `evaluate` returns, the **API is uniform**: each report exposes three accessors.

```python
report.metrics       # -> scores + metric displays (ROC, PR, confusion matrix, …)
report.inspection    # -> coefficients, permutation / impurity importance
report.data          # -> dataset analysis (EstimatorReport / CrossValidationReport)
```

Plus convenience methods such as `report.cache_predictions()`, `report.clear_cache()`, `report.get_predictions(...)`, `report.help()` (try `report` in a Jupyter cell — it has a rich HTML representation listing every available method).

For details and signatures see [reports.md](reports.md) and [diagnostics.md](diagnostics.md).

## Persisting and comparing — projects

A `skore.Project` is a keyed store of reports. Use it across runs to keep history, filter, and reload reports.

```python
from skore import Project, evaluate

project = Project("my-xp")                       # local mode (default)
project.put("baseline", evaluate(model_a, X, y))
project.put("tuned",    evaluate(model_b, X, y))

summary = project.summarize()                    # pandas DataFrame (subclass)
best = summary.query("rmse < 67").reports()      # filter, then materialize
```

Three modes are available — `local` (cache dir on the user machine), `hub` (skore hub, requires `skore.login()`), `mlflow` (reports stored as MLflow artifacts). See [project.md](project.md).

## Common pitfalls

- `splitter=0.2` is a *single* train/test split, not CV. Pass an `int` or a CV object for cross-validation.
- For prefit estimators you **must** pass `splitter="prefit"`; otherwise skore will refit.
- A `Project` is constrained to a single ML task — you can't mix classification and regression reports in the same project.
- `Summary` is a subclass of `pandas.DataFrame`; standard `.query`, `.loc`, etc. all work, but call `.reports()` at the end to turn the filtered rows back into report objects.
- `X` / `y` and `data` are mutually exclusive on `evaluate` and `CrossValidationReport`. Mixing them raises. Pick env-dict for `SkrubLearner` and sklearn-style for everything else.
