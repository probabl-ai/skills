# `sklearn.inspection`

_Inspection._

### `partial_dependence` <sub>function</sub>

```python
partial_dependence(estimator, X, features, *, sample_weight=None, categorical_features=None,
    feature_names=None, response_method='auto', percentiles=(0.05, 0.95), grid_resolution=100,
    custom_values=None, method='auto', kind='average')
```

Partial dependence of ``features``.

### `permutation_importance` <sub>function</sub>

```python
permutation_importance(estimator, X, y, *, scoring=None, n_repeats=5, n_jobs=None,
    random_state=None, sample_weight=None, max_samples=1.0)
```

Permutation importance for feature evaluation [BRE]_.

## Plotting

### `DecisionBoundaryDisplay` <sub>class</sub>

```python
DecisionBoundaryDisplay(*, xx0, xx1, response, multiclass_colors=None, xlabel=None, ylabel=None)
```

Decisions boundary visualization.

### `PartialDependenceDisplay` <sub>class</sub>

```python
PartialDependenceDisplay(pd_results, *, features, feature_names, target_idx, deciles,
    kind='average', subsample=1000, random_state=None, is_categorical=None)
```

Partial Dependence Plot (PDP) and Individual Conditional Expectation (ICE).
