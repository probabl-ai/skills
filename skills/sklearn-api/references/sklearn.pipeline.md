# `sklearn.pipeline`

_Pipeline._

### `FeatureUnion` <sub>class</sub>

```python
FeatureUnion(transformer_list, *, n_jobs=None, transformer_weights=None, verbose=False,
    verbose_feature_names_out=True)
```

Concatenates results of multiple transformer objects.

### `Pipeline` <sub>class</sub>

```python
Pipeline(steps, *, transform_input=None, memory=None, verbose=False)
```

A sequence of data transformers with an optional final predictor.

### `make_pipeline` <sub>function</sub>

```python
make_pipeline(*steps, memory=None, transform_input=None, verbose=False)
```

Construct a :class:`Pipeline` from the given estimators.

### `make_union` <sub>function</sub>

```python
make_union(*transformers, n_jobs=None, verbose=False, verbose_feature_names_out=True)
```

Construct a :class:`FeatureUnion` from the given transformers.
