# `sklearn.multioutput`

_Multioutput regression and classification._

### `ClassifierChain` <sub>class</sub>

```python
ClassifierChain(estimator=None, *, order=None, cv=None, chain_method='predict',
    random_state=None, verbose=False, base_estimator='deprecated')
```

A multi-label model that arranges binary classifiers into a chain.

### `MultiOutputClassifier` <sub>class</sub>

```python
MultiOutputClassifier(estimator, *, n_jobs=None)
```

Multi target classification.

### `MultiOutputRegressor` <sub>class</sub>

```python
MultiOutputRegressor(estimator, *, n_jobs=None)
```

Multi target regression.

### `RegressorChain` <sub>class</sub>

```python
RegressorChain(estimator=None, *, order=None, cv=None, random_state=None, verbose=False,
    base_estimator='deprecated')
```

A multi-label model that arranges regressions into a chain.
