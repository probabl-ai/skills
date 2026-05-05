# `sklearn.ensemble`

_Ensemble methods._

### `AdaBoostClassifier` <sub>class</sub>

```python
AdaBoostClassifier(estimator=None, *, n_estimators=50, learning_rate=1.0, random_state=None)
```

An AdaBoost classifier.

### `AdaBoostRegressor` <sub>class</sub>

```python
AdaBoostRegressor(estimator=None, *, n_estimators=50, learning_rate=1.0, loss='linear',
    random_state=None)
```

An AdaBoost regressor.

### `BaggingClassifier` <sub>class</sub>

```python
BaggingClassifier(estimator=None, n_estimators=10, *, max_samples=None, max_features=1.0,
    bootstrap=True, bootstrap_features=False, oob_score=False, warm_start=False, n_jobs=None,
    random_state=None, verbose=0)
```

A Bagging classifier.

### `BaggingRegressor` <sub>class</sub>

```python
BaggingRegressor(estimator=None, n_estimators=10, *, max_samples=None, max_features=1.0,
    bootstrap=True, bootstrap_features=False, oob_score=False, warm_start=False, n_jobs=None,
    random_state=None, verbose=0)
```

A Bagging regressor.

### `ExtraTreesClassifier` <sub>class</sub>

```python
ExtraTreesClassifier(n_estimators=100, *, criterion='gini', max_depth=None, min_samples_split=2,
    min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='sqrt', max_leaf_nodes=None,
    min_impurity_decrease=0.0, bootstrap=False, oob_score=False, n_jobs=None, random_state=None,
    verbose=0, warm_start=False, class_weight=None, ccp_alpha=0.0, max_samples=None,
    monotonic_cst=None)
```

An extra-trees classifier.

### `ExtraTreesRegressor` <sub>class</sub>

```python
ExtraTreesRegressor(n_estimators=100, *, criterion='squared_error', max_depth=None,
    min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=1.0,
    max_leaf_nodes=None, min_impurity_decrease=0.0, bootstrap=False, oob_score=False,
    n_jobs=None, random_state=None, verbose=0, warm_start=False, ccp_alpha=0.0,
    max_samples=None, monotonic_cst=None)
```

An extra-trees regressor.

### `GradientBoostingClassifier` <sub>class</sub>

```python
GradientBoostingClassifier(*, loss='log_loss', learning_rate=0.1, n_estimators=100,
    subsample=1.0, criterion='friedman_mse', min_samples_split=2, min_samples_leaf=1,
    min_weight_fraction_leaf=0.0, max_depth=3, min_impurity_decrease=0.0, init=None,
    random_state=None, max_features=None, verbose=0, max_leaf_nodes=None, warm_start=False,
    validation_fraction=0.1, n_iter_no_change=None, tol=0.0001, ccp_alpha=0.0)
```

Gradient Boosting for classification.

### `GradientBoostingRegressor` <sub>class</sub>

```python
GradientBoostingRegressor(*, loss='squared_error', learning_rate=0.1, n_estimators=100,
    subsample=1.0, criterion='friedman_mse', min_samples_split=2, min_samples_leaf=1,
    min_weight_fraction_leaf=0.0, max_depth=3, min_impurity_decrease=0.0, init=None,
    random_state=None, max_features=None, alpha=0.9, verbose=0, max_leaf_nodes=None,
    warm_start=False, validation_fraction=0.1, n_iter_no_change=None, tol=0.0001, ccp_alpha=0.0)
```

Gradient Boosting for regression.

### `HistGradientBoostingClassifier` <sub>class</sub>

```python
HistGradientBoostingClassifier(loss='log_loss', *, learning_rate=0.1, max_iter=100,
    max_leaf_nodes=31, max_depth=None, min_samples_leaf=20, l2_regularization=0.0,
    max_features=1.0, max_bins=255, categorical_features='from_dtype', monotonic_cst=None,
    interaction_cst=None, warm_start=False, early_stopping='auto', scoring='loss',
    validation_fraction=0.1, n_iter_no_change=10, tol=1e-07, verbose=0, random_state=None,
    class_weight=None)
```

Histogram-based Gradient Boosting Classification Tree.

### `HistGradientBoostingRegressor` <sub>class</sub>

```python
HistGradientBoostingRegressor(loss='squared_error', *, quantile=None, learning_rate=0.1,
    max_iter=100, max_leaf_nodes=31, max_depth=None, min_samples_leaf=20, l2_regularization=0.0,
    max_features=1.0, max_bins=255, categorical_features='from_dtype', monotonic_cst=None,
    interaction_cst=None, warm_start=False, early_stopping='auto', scoring='loss',
    validation_fraction=0.1, n_iter_no_change=10, tol=1e-07, verbose=0, random_state=None)
```

Histogram-based Gradient Boosting Regression Tree.

### `IsolationForest` <sub>class</sub>

```python
IsolationForest(*, n_estimators=100, max_samples='auto', contamination='auto', max_features=1.0,
    bootstrap=False, n_jobs=None, random_state=None, verbose=0, warm_start=False)
```

Isolation Forest Algorithm.

### `RandomForestClassifier` <sub>class</sub>

```python
RandomForestClassifier(n_estimators=100, *, criterion='gini', max_depth=None,
    min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features='sqrt',
    max_leaf_nodes=None, min_impurity_decrease=0.0, bootstrap=True, oob_score=False,
    n_jobs=None, random_state=None, verbose=0, warm_start=False, class_weight=None,
    ccp_alpha=0.0, max_samples=None, monotonic_cst=None)
```

A random forest classifier.

### `RandomForestRegressor` <sub>class</sub>

```python
RandomForestRegressor(n_estimators=100, *, criterion='squared_error', max_depth=None,
    min_samples_split=2, min_samples_leaf=1, min_weight_fraction_leaf=0.0, max_features=1.0,
    max_leaf_nodes=None, min_impurity_decrease=0.0, bootstrap=True, oob_score=False,
    n_jobs=None, random_state=None, verbose=0, warm_start=False, ccp_alpha=0.0,
    max_samples=None, monotonic_cst=None)
```

A random forest regressor.

### `RandomTreesEmbedding` <sub>class</sub>

```python
RandomTreesEmbedding(n_estimators=100, *, max_depth=5, min_samples_split=2, min_samples_leaf=1,
    min_weight_fraction_leaf=0.0, max_leaf_nodes=None, min_impurity_decrease=0.0,
    sparse_output=True, n_jobs=None, random_state=None, verbose=0, warm_start=False)
```

An ensemble of totally random trees.

### `StackingClassifier` <sub>class</sub>

```python
StackingClassifier(estimators, final_estimator=None, *, cv=None, stack_method='auto',
    n_jobs=None, passthrough=False, verbose=0)
```

Stack of estimators with a final classifier.

### `StackingRegressor` <sub>class</sub>

```python
StackingRegressor(estimators, final_estimator=None, *, cv=None, n_jobs=None, passthrough=False,
    verbose=0)
```

Stack of estimators with a final regressor.

### `VotingClassifier` <sub>class</sub>

```python
VotingClassifier(estimators, *, voting='hard', weights=None, n_jobs=None,
    flatten_transform=True, verbose=False)
```

Soft Voting/Majority Rule classifier for unfitted estimators.

### `VotingRegressor` <sub>class</sub>

```python
VotingRegressor(estimators, *, weights=None, n_jobs=None, verbose=False)
```

Prediction voting regressor for unfitted estimators.
