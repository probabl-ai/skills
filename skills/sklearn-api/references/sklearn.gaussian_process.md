# `sklearn.gaussian_process`

_Gaussian processes._

### `GaussianProcessClassifier` <sub>class</sub>

```python
GaussianProcessClassifier(kernel=None, *, optimizer='fmin_l_bfgs_b', n_restarts_optimizer=0,
    max_iter_predict=100, warm_start=False, copy_X_train=True, random_state=None,
    multi_class='one_vs_rest', n_jobs=None)
```

Gaussian process classification (GPC) based on Laplace approximation.

### `GaussianProcessRegressor` <sub>class</sub>

```python
GaussianProcessRegressor(kernel=None, *, alpha=1e-10, optimizer='fmin_l_bfgs_b',
    n_restarts_optimizer=0, normalize_y=False, copy_X_train=True, n_targets=None,
    random_state=None)
```

Gaussian process regression (GPR).

## Kernels

### `kernels.CompoundKernel` <sub>class</sub>

```python
kernels.CompoundKernel(kernels)
```

Kernel which is composed of a set of other kernels.

### `kernels.ConstantKernel` <sub>class</sub>

```python
kernels.ConstantKernel(constant_value=1.0, constant_value_bounds=(1e-05, 100000.0))
```

Constant kernel.

### `kernels.DotProduct` <sub>class</sub>

```python
kernels.DotProduct(sigma_0=1.0, sigma_0_bounds=(1e-05, 100000.0))
```

Dot-Product kernel.

### `kernels.ExpSineSquared` <sub>class</sub>

```python
kernels.ExpSineSquared(length_scale=1.0, periodicity=1.0, length_scale_bounds=(1e-05, 100000.0),
    periodicity_bounds=(1e-05, 100000.0))
```

Exp-Sine-Squared kernel (aka periodic kernel).

### `kernels.Exponentiation` <sub>class</sub>

```python
kernels.Exponentiation(kernel, exponent)
```

The Exponentiation kernel takes one base kernel and a scalar parameter :math:`p` and combines them via

### `kernels.Hyperparameter` <sub>class</sub>

```python
kernels.Hyperparameter(name, value_type, bounds, n_elements=1, fixed=None)
```

A kernel hyperparameter's specification in form of a namedtuple.

### `kernels.Kernel` <sub>class</sub>

```python
kernels.Kernel()
```

Base class for all kernels.

### `kernels.Matern` <sub>class</sub>

```python
kernels.Matern(length_scale=1.0, length_scale_bounds=(1e-05, 100000.0), nu=1.5)
```

Matern kernel.

### `kernels.PairwiseKernel` <sub>class</sub>

```python
kernels.PairwiseKernel(gamma=1.0, gamma_bounds=(1e-05, 100000.0), metric='linear',
    pairwise_kernels_kwargs=None)
```

Wrapper for kernels in sklearn.metrics.pairwise.

### `kernels.Product` <sub>class</sub>

```python
kernels.Product(k1, k2)
```

The `Product` kernel takes two kernels :math:`k_1` and :math:`k_2` and combines them via

### `kernels.RBF` <sub>class</sub>

```python
kernels.RBF(length_scale=1.0, length_scale_bounds=(1e-05, 100000.0))
```

Radial basis function kernel (aka squared-exponential kernel).

### `kernels.RationalQuadratic` <sub>class</sub>

```python
kernels.RationalQuadratic(length_scale=1.0, alpha=1.0, length_scale_bounds=(1e-05, 100000.0),
    alpha_bounds=(1e-05, 100000.0))
```

Rational Quadratic kernel.

### `kernels.Sum` <sub>class</sub>

```python
kernels.Sum(k1, k2)
```

The `Sum` kernel takes two kernels :math:`k_1` and :math:`k_2` and combines them via

### `kernels.WhiteKernel` <sub>class</sub>

```python
kernels.WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-05, 100000.0))
```

White kernel.
