# Diagnostics catalog

Every report exposes the same three accessors. They return either scalars / arrays (numerical metrics) or `Display` objects (rich plots that also carry the underlying frames).

```python
report.metrics        # numerical scores + plot displays
report.inspection     # model inspection
report.data           # dataset analysis (EstimatorReport / CrossValidationReport)
```

Calling a `Display` directly returns the object; call `.plot()` for the matplotlib figure or read its `.frame` / underlying attributes for the raw data.

## `report.metrics`

Tabular summary across all registered metrics:

```python
display = report.metrics.summarize(data_source="test")  # "test" | "train" | "both"
display.frame                                           # pandas DataFrame
```

`data_source="both"` returns train and test side-by-side; useful for spotting overfitting.

Per-metric scalars (always available where the ML task allows):

| Method | Task | Notes |
| --- | --- | --- |
| `accuracy(data_source=...)` | classification | |
| `precision(...)` / `recall(...)` | classification | `average=` follows sklearn conventions; binary uses `pos_label` |
| `brier_score(...)` | classification | requires `predict_proba` |
| `roc_auc(...)` | classification | binary or multiclass |
| `log_loss(...)` | classification | requires `predict_proba` |
| `r2(...)` | regression | |
| `rmse(...)` / `mae(...)` / `mape(...)` | regression | |

Timings:

```python
report.metrics.fit_time()           # EstimatorReport only
report.metrics.predict_time(...)    # response_method specific
report.metrics.timings()            # everything as a dict
```

Custom and dynamic metrics:

```python
report.metrics.available()                  # list of registered metrics
report.metrics.add("brier_top1", my_fn)     # any callable f(y_true, y_pred[, **kw])
report.metrics.remove("brier_top1")
```

Plot displays (return `Display` objects with `.plot()`, `.frame`, etc.):

| Method | Task |
| --- | --- |
| `report.metrics.roc(...)` | classification (binary or OvR multiclass) |
| `report.metrics.precision_recall(...)` | classification |
| `report.metrics.confusion_matrix(...)` | classification |
| `report.metrics.prediction_error(...)` | regression |

Each accepts `data_source="train"|"test"|"both"`. Cross-validation versions return one curve per fold; comparison versions overlay one curve per sub-report.

## `report.inspection`

Model-inspection diagnostics — availability depends on the underlying estimator:

| Method | Available when… | Returns |
| --- | --- | --- |
| `coefficients()` | estimator exposes `coef_` (linear models) | `CoefficientsDisplay` |
| `impurity_decrease()` | estimator exposes `feature_importances_` (tree-based) | `ImpurityDecreaseDisplay` |
| `permutation_importance(data_source=..., metric=..., n_repeats=5, max_samples=1.0, n_jobs=None, seed=None)` | always | `PermutationImportanceDisplay` |

`impurity_decrease` reflects training-time importance; `permutation_importance` is held-out (default `data_source="test"`). Reach for permutation importance when impurity is misleading (high-cardinality features, correlated features, etc.).

## `report.data`

Available on `EstimatorReport` and `CrossValidationReport`. Wraps skrub's `TableReport` to give a rich, interactive view of the data the report was built on.

```python
display = report.data.analyze(
    data_source="both",            # "train" | "test" | "both"
    with_y=True,
    subsample=None,                # int to subsample, or None for full data
    subsample_strategy="head",     # "head" | "random"
    seed=None,
)
```

Useful before training (sanity-check distributions, missing values, categoricals) and after (correlate poor metrics with data issues).

## Display objects

Every plotting method returns a `Display` subclass (see `from skore import Display, ConfusionMatrixDisplay, RocCurveDisplay, …`). Each display:

- renders directly in Jupyter (HTML / matplotlib);
- has a `.plot(...)` method with display-specific styling kwargs;
- exposes the underlying numeric data (e.g. `.frame` for tabular displays).

This is what makes reports useful in scripts as well as notebooks: the display is just a thin layer on top of a dataframe you can post-process.
