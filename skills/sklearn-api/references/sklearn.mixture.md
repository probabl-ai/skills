# `sklearn.mixture`

_Gaussian mixture models._

### `BayesianGaussianMixture` <sub>class</sub>

```python
BayesianGaussianMixture(*, n_components=1, covariance_type='full', tol=0.001, reg_covar=1e-06,
    max_iter=100, n_init=1, init_params='kmeans',
    weight_concentration_prior_type='dirichlet_process', weight_concentration_prior=None,
    mean_precision_prior=None, mean_prior=None, degrees_of_freedom_prior=None,
    covariance_prior=None, random_state=None, warm_start=False, verbose=0, verbose_interval=10)
```

Variational Bayesian estimation of a Gaussian mixture.

### `GaussianMixture` <sub>class</sub>

```python
GaussianMixture(n_components=1, *, covariance_type='full', tol=0.001, reg_covar=1e-06,
    max_iter=100, n_init=1, init_params='kmeans', weights_init=None, means_init=None,
    precisions_init=None, random_state=None, warm_start=False, verbose=0, verbose_interval=10)
```

Gaussian Mixture.
