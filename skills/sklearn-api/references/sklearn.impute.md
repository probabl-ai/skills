# `sklearn.impute`

_Imputation._

### `IterativeImputer` <sub>class</sub>

```python
IterativeImputer(estimator=None, *, missing_values=nan, sample_posterior=False, max_iter=10,
    tol=0.001, n_nearest_features=None, initial_strategy='mean', fill_value=None,
    imputation_order='ascending', skip_complete=False, min_value=-inf, max_value=inf, verbose=0,
    random_state=None, add_indicator=False, keep_empty_features=False)
```

Multivariate imputer that estimates each feature from all the others.

### `KNNImputer` <sub>class</sub>

```python
KNNImputer(*, missing_values=nan, n_neighbors=5, weights='uniform', metric='nan_euclidean',
    copy=True, add_indicator=False, keep_empty_features=False)
```

Imputation for completing missing values using k-Nearest Neighbors.

### `MissingIndicator` <sub>class</sub>

```python
MissingIndicator(*, missing_values=nan, features='missing-only', sparse='auto', error_on_new=True)
```

Binary indicators for missing values.

### `SimpleImputer` <sub>class</sub>

```python
SimpleImputer(*, missing_values=nan, strategy='mean', fill_value=None, copy=True,
    add_indicator=False, keep_empty_features=False)
```

Univariate imputer for completing missing values with simple strategies.
