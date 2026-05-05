# `sklearn.compose`

_Composite estimators._

### `ColumnTransformer` <sub>class</sub>

```python
ColumnTransformer(transformers, *, remainder='drop', sparse_threshold=0.3, n_jobs=None,
    transformer_weights=None, verbose=False, verbose_feature_names_out=True,
    force_int_remainder_cols='deprecated')
```

Applies transformers to columns of an array or pandas DataFrame.

### `TransformedTargetRegressor` <sub>class</sub>

```python
TransformedTargetRegressor(regressor=None, *, transformer=None, func=None, inverse_func=None,
    check_inverse=True)
```

Meta-estimator to regress on a transformed target.

### `make_column_selector` <sub>class</sub>

```python
make_column_selector(pattern=None, *, dtype_include=None, dtype_exclude=None)
```

Create a callable to select columns to be used with :class:`ColumnTransformer`.

### `make_column_transformer` <sub>function</sub>

```python
make_column_transformer(*transformers, remainder='drop', sparse_threshold=0.3, n_jobs=None,
    verbose=False, verbose_feature_names_out=True, force_int_remainder_cols='deprecated')
```

Construct a ColumnTransformer from the given transformers.
