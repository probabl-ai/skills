# `sklearn.random_projection`

_Random projection._

### `GaussianRandomProjection` <sub>class</sub>

```python
GaussianRandomProjection(n_components='auto', *, eps=0.1, compute_inverse_components=False,
    random_state=None)
```

Reduce dimensionality through Gaussian random projection.

### `SparseRandomProjection` <sub>class</sub>

```python
SparseRandomProjection(n_components='auto', *, density='auto', eps=0.1, dense_output=False,
    compute_inverse_components=False, random_state=None)
```

Reduce dimensionality through sparse random projection.

### `johnson_lindenstrauss_min_dim` <sub>function</sub>

```python
johnson_lindenstrauss_min_dim(n_samples, *, eps=0.1)
```

Find a 'safe' number of components to randomly project to.
