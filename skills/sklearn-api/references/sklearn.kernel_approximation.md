# `sklearn.kernel_approximation`

_Kernel approximation._

### `AdditiveChi2Sampler` <sub>class</sub>

```python
AdditiveChi2Sampler(*, sample_steps=2, sample_interval=None)
```

Approximate feature map for additive chi2 kernel.

### `Nystroem` <sub>class</sub>

```python
Nystroem(kernel='rbf', *, gamma=None, coef0=None, degree=None, kernel_params=None,
    n_components=100, random_state=None, n_jobs=None)
```

Approximate a kernel map using a subset of the training data.

### `PolynomialCountSketch` <sub>class</sub>

```python
PolynomialCountSketch(*, gamma=1.0, degree=2, coef0=0, n_components=100, random_state=None)
```

Polynomial kernel approximation via Tensor Sketch.

### `RBFSampler` <sub>class</sub>

```python
RBFSampler(*, gamma=1.0, n_components=100, random_state=None)
```

Approximate a RBF kernel feature map using random Fourier features.

### `SkewedChi2Sampler` <sub>class</sub>

```python
SkewedChi2Sampler(*, skewedness=1.0, n_components=100, random_state=None)
```

Approximate feature map for "skewed chi-squared" kernel.
