# `sklearn.neural_network`

_Neural network models._

### `BernoulliRBM` <sub>class</sub>

```python
BernoulliRBM(n_components=256, *, learning_rate=0.1, batch_size=10, n_iter=10, verbose=0,
    random_state=None)
```

Bernoulli Restricted Boltzmann Machine (RBM).

### `MLPClassifier` <sub>class</sub>

```python
MLPClassifier(hidden_layer_sizes=(100,), activation='relu', *, solver='adam', alpha=0.0001,
    batch_size='auto', learning_rate='constant', learning_rate_init=0.001, power_t=0.5,
    max_iter=200, shuffle=True, random_state=None, tol=0.0001, verbose=False, warm_start=False,
    momentum=0.9, nesterovs_momentum=True, early_stopping=False, validation_fraction=0.1,
    beta_1=0.9, beta_2=0.999, epsilon=1e-08, n_iter_no_change=10, max_fun=15000)
```

Multi-layer Perceptron classifier.

### `MLPRegressor` <sub>class</sub>

```python
MLPRegressor(loss='squared_error', hidden_layer_sizes=(100,), activation='relu', *,
    solver='adam', alpha=0.0001, batch_size='auto', learning_rate='constant',
    learning_rate_init=0.001, power_t=0.5, max_iter=200, shuffle=True, random_state=None,
    tol=0.0001, verbose=False, warm_start=False, momentum=0.9, nesterovs_momentum=True,
    early_stopping=False, validation_fraction=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-08,
    n_iter_no_change=10, max_fun=15000)
```

Multi-layer Perceptron regressor.
