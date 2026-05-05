# `sklearn.covariance`

_Covariance estimation._

### `EllipticEnvelope` <sub>class</sub>

```python
EllipticEnvelope(*, store_precision=True, assume_centered=False, support_fraction=None,
    contamination=0.1, random_state=None)
```

An object for detecting outliers in a Gaussian distributed dataset.

### `EmpiricalCovariance` <sub>class</sub>

```python
EmpiricalCovariance(*, store_precision=True, assume_centered=False)
```

Maximum likelihood covariance estimator.

### `GraphicalLasso` <sub>class</sub>

```python
GraphicalLasso(alpha=0.01, *, mode='cd', covariance=None, tol=0.0001, enet_tol=0.0001,
    max_iter=100, verbose=False, eps=np.float64(2.220446049250313e-16), assume_centered=False)
```

Sparse inverse covariance estimation with an l1-penalized estimator.

### `GraphicalLassoCV` <sub>class</sub>

```python
GraphicalLassoCV(*, alphas=4, n_refinements=4, cv=None, tol=0.0001, enet_tol=0.0001,
    max_iter=100, mode='cd', n_jobs=None, verbose=False, eps=np.float64(2.220446049250313e-16),
    assume_centered=False)
```

Sparse inverse covariance w/ cross-validated choice of the l1 penalty.

### `LedoitWolf` <sub>class</sub>

```python
LedoitWolf(*, store_precision=True, assume_centered=False, block_size=1000)
```

LedoitWolf Estimator.

### `MinCovDet` <sub>class</sub>

```python
MinCovDet(*, store_precision=True, assume_centered=False, support_fraction=None, random_state=None)
```

Minimum Covariance Determinant (MCD): robust estimator of covariance.

### `OAS` <sub>class</sub>

```python
OAS(*, store_precision=True, assume_centered=False)
```

Oracle Approximating Shrinkage Estimator.

### `ShrunkCovariance` <sub>class</sub>

```python
ShrunkCovariance(*, store_precision=True, assume_centered=False, shrinkage=0.1)
```

Covariance estimator with shrinkage.

### `empirical_covariance` <sub>function</sub>

```python
empirical_covariance(X, *, assume_centered=False)
```

Compute the Maximum likelihood covariance estimator.

### `graphical_lasso` <sub>function</sub>

```python
graphical_lasso(emp_cov, alpha, *, mode='cd', tol=0.0001, enet_tol=0.0001, max_iter=100,
    verbose=False, return_costs=False, eps=np.float64(2.220446049250313e-16),
    return_n_iter=False)
```

L1-penalized covariance estimator.

### `ledoit_wolf` <sub>function</sub>

```python
ledoit_wolf(X, *, assume_centered=False, block_size=1000)
```

Estimate the shrunk Ledoit-Wolf covariance matrix.

### `ledoit_wolf_shrinkage` <sub>function</sub>

```python
ledoit_wolf_shrinkage(X, assume_centered=False, block_size=1000)
```

Estimate the shrunk Ledoit-Wolf covariance matrix.

### `oas` <sub>function</sub>

```python
oas(X, *, assume_centered=False)
```

Estimate covariance with the Oracle Approximating Shrinkage.

### `shrunk_covariance` <sub>function</sub>

```python
shrunk_covariance(emp_cov, shrinkage=0.1)
```

Calculate covariance matrices shrunk on the diagonal.
