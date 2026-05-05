# `sklearn.svm`

_Support vector machines._

### `LinearSVC` <sub>class</sub>

```python
LinearSVC(penalty='l2', loss='squared_hinge', *, dual='auto', tol=0.0001, C=1.0,
    multi_class='ovr', fit_intercept=True, intercept_scaling=1, class_weight=None, verbose=0,
    random_state=None, max_iter=1000)
```

Linear Support Vector Classification.

### `LinearSVR` <sub>class</sub>

```python
LinearSVR(*, epsilon=0.0, tol=0.0001, C=1.0, loss='epsilon_insensitive', fit_intercept=True,
    intercept_scaling=1.0, dual='auto', verbose=0, random_state=None, max_iter=1000)
```

Linear Support Vector Regression.

### `NuSVC` <sub>class</sub>

```python
NuSVC(*, nu=0.5, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True,
    probability=False, tol=0.001, cache_size=200, class_weight=None, verbose=False, max_iter=-1,
    decision_function_shape='ovr', break_ties=False, random_state=None)
```

Nu-Support Vector Classification.

### `NuSVR` <sub>class</sub>

```python
NuSVR(*, nu=0.5, C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True,
    tol=0.001, cache_size=200, verbose=False, max_iter=-1)
```

Nu Support Vector Regression.

### `OneClassSVM` <sub>class</sub>

```python
OneClassSVM(*, kernel='rbf', degree=3, gamma='scale', coef0=0.0, tol=0.001, nu=0.5,
    shrinking=True, cache_size=200, verbose=False, max_iter=-1)
```

Unsupervised Outlier Detection.

### `SVC` <sub>class</sub>

```python
SVC(*, C=1.0, kernel='rbf', degree=3, gamma='scale', coef0=0.0, shrinking=True,
    probability=False, tol=0.001, cache_size=200, class_weight=None, verbose=False, max_iter=-1,
    decision_function_shape='ovr', break_ties=False, random_state=None)
```

C-Support Vector Classification.

### `SVR` <sub>class</sub>

```python
SVR(*, kernel='rbf', degree=3, gamma='scale', coef0=0.0, tol=0.001, C=1.0, epsilon=0.1,
    shrinking=True, cache_size=200, verbose=False, max_iter=-1)
```

Epsilon-Support Vector Regression.

### `l1_min_c` <sub>function</sub>

```python
l1_min_c(X, y, *, loss='squared_hinge', fit_intercept=True, intercept_scaling=1.0)
```

Return the lowest bound for `C`.
