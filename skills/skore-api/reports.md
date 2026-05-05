# Report API

Three report types, one shared shape. `evaluate` picks the right one for you, but you can also instantiate them directly.

## The three report types

| Report | Returned when… | Source |
| --- | --- | --- |
| `EstimatorReport` | single estimator + single split (or `splitter="prefit"`) | `skore/src/skore/_sklearn/_estimator/report.py` |
| `CrossValidationReport` | single estimator + CV splitter or integer fold count | `skore/src/skore/_sklearn/_cross_validation/report.py` |
| `ComparisonReport` | list/dict of estimators, or built manually from several reports | `skore/src/skore/_sklearn/_comparison/report.py` |

All three are top-level imports: `from skore import EstimatorReport, CrossValidationReport, ComparisonReport`.

## Direct construction

You usually go through `evaluate`, but the constructors are useful when you already have data splits or fitted models.

```python
from skore import EstimatorReport, CrossValidationReport, ComparisonReport

# explicit train/test split
report = EstimatorReport(
    estimator,
    X_train=X_tr, y_train=y_tr,
    X_test=X_te, y_test=y_te,
    pos_label=None,                 # optional, for binary classification
)

# prefit case
report = EstimatorReport(fitted_estimator, X_test=X_te, y_test=y_te)

# cross-validation, sklearn-style
report = CrossValidationReport(estimator, X, y, splitter=5, n_jobs=-1)

# cross-validation, env-dict style (skrub SkrubLearner)
report = CrossValidationReport(
    skrub_learner, data={"X": X, "y": y}, splitter=5, n_jobs=-1,
)

# EstimatorReport with env-dict splits
report = EstimatorReport(
    skrub_learner,
    train_data={"X": X_tr, "y": y_tr},
    test_data={"X": X_te, "y": y_te},
)

# build a comparison from existing reports
cmp = ComparisonReport({"a": report_a, "b": report_b})
```

## Shared API surface

Properties (read-only):
`estimator`, `estimator_` (the fitted one), `estimator_name_`, `ml_task`, `pos_label`,
`X_train`, `y_train`, `X_test`, `y_test`, `train_data`, `test_data` (estimator report),
`X`, `y`, `input_data`, `splitter`, `split_indices`, `estimator_reports_` (CV report),
`reports_` (comparison report).

Methods on every report:
- `report.metrics` — metrics accessor (see [diagnostics.md](diagnostics.md))
- `report.inspection` — model inspection accessor
- `report.data` — dataset analysis (estimator + CV reports)
- `report.cache_predictions(...)` — precompute and cache predictions / probabilities
- `report.get_predictions(...)` — retrieve cached predictions
- `report.clear_cache()` — drop the prediction cache
- `report.get_state()` / `Report.from_state(state)` — round-trip serialization (this is what the `Project` uses internally)

In a Jupyter cell, evaluating the report renders an interactive HTML help panel listing every callable on the report and its accessors.

## Predictions cache

skore caches predictions (`predict`, `predict_proba`, `decision_function`) the first time a metric or display needs them. This makes a report very cheap to interrogate: computing `accuracy`, then `roc_auc`, then a ROC curve only triggers one round of predictions per data source.

```python
report.cache_predictions(response_methods=["predict", "predict_proba"], n_jobs=-1)
report.get_predictions(data_source="test", response_method="predict")
```

For a `CrossValidationReport`, predictions are cached per fold; for a `ComparisonReport`, per sub-report.

## Choosing between reports

- **Quick scoring on a held-out split** → `EstimatorReport` via `evaluate(..., splitter=0.2)` (default).
- **Robust estimate / variance across folds** → `CrossValidationReport` via `evaluate(..., splitter=5)` or pass any sklearn splitter.
- **Compare candidates** → pass a `dict` of estimators to `evaluate`, or wrap existing reports in `ComparisonReport`. Comparison reports forward the metric/inspection API to each sub-report and aggregate the result.

## skrub interop

`evaluate`, `CrossValidationReport`, and `EstimatorReport` all accept skrub `DataOp` and `SkrubLearner` objects in place of an sklearn estimator. `SkrubLearner.fit` does **not** take `(X, y)` positionally — it takes a single environment dict mapping `skrub.var(name=...)` names to values — so the report APIs accept that env-dict via dedicated arguments rather than the standard `X` / `y`:

| Report constructor / `evaluate` | sklearn-style argument | env-dict argument (skrub) |
| --- | --- | --- |
| `evaluate(...)` | `X=`, `y=` | `data=` |
| `CrossValidationReport(...)` | `X=`, `y=` | `data=` |
| `EstimatorReport(...)` | `X_train=`/`y_train=`, `X_test=`/`y_test=` | `train_data=`, `test_data=` |

The two forms are mutually exclusive on a given call. Typical usage:

```python
report = evaluate(
    skrub_learner, data={"X": df, "y": ser}, splitter=KFold(5),
)
```

Source-bound `SkrubLearner` graphs (the recommended `build-ml-pipeline` pattern, where the root variable is e.g. `skrub.var("path", ...)` and the loader runs inside the graph) extend naturally:

```python
report = evaluate(
    skrub_learner, data={"path": "data/train.parquet"}, splitter=KFold(5),
)
```

In that case the env-dict can omit `X` / `y` entirely — they are recomputed from the source binding inside the graph.
