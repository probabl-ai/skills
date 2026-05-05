# `sklearn.neighbors`

_Nearest neighbors._

### `BallTree` <sub>class</sub>


BallTree for fast generalized N-point problems

### `KDTree` <sub>class</sub>


KDTree for fast generalized N-point problems

### `KNeighborsClassifier` <sub>class</sub>

```python
KNeighborsClassifier(n_neighbors=5, *, weights='uniform', algorithm='auto', leaf_size=30, p=2,
    metric='minkowski', metric_params=None, n_jobs=None)
```

Classifier implementing the k-nearest neighbors vote.

### `KNeighborsRegressor` <sub>class</sub>

```python
KNeighborsRegressor(n_neighbors=5, *, weights='uniform', algorithm='auto', leaf_size=30, p=2,
    metric='minkowski', metric_params=None, n_jobs=None)
```

Regression based on k-nearest neighbors.

### `KNeighborsTransformer` <sub>class</sub>

```python
KNeighborsTransformer(*, mode='distance', n_neighbors=5, algorithm='auto', leaf_size=30,
    metric='minkowski', p=2, metric_params=None, n_jobs=None)
```

Transform X into a (weighted) graph of k nearest neighbors.

### `KernelDensity` <sub>class</sub>

```python
KernelDensity(*, bandwidth=1.0, algorithm='auto', kernel='gaussian', metric='euclidean', atol=0,
    rtol=0, breadth_first=True, leaf_size=40, metric_params=None)
```

Kernel Density Estimation.

### `LocalOutlierFactor` <sub>class</sub>

```python
LocalOutlierFactor(n_neighbors=20, *, algorithm='auto', leaf_size=30, metric='minkowski', p=2,
    metric_params=None, contamination='auto', novelty=False, n_jobs=None)
```

Unsupervised Outlier Detection using the Local Outlier Factor (LOF).

### `NearestCentroid` <sub>class</sub>

```python
NearestCentroid(metric='euclidean', *, shrink_threshold=None, priors='uniform')
```

Nearest centroid classifier.

### `NearestNeighbors` <sub>class</sub>

```python
NearestNeighbors(*, n_neighbors=5, radius=1.0, algorithm='auto', leaf_size=30,
    metric='minkowski', p=2, metric_params=None, n_jobs=None)
```

Unsupervised learner for implementing neighbor searches.

### `NeighborhoodComponentsAnalysis` <sub>class</sub>

```python
NeighborhoodComponentsAnalysis(n_components=None, *, init='auto', warm_start=False, max_iter=50,
    tol=1e-05, callback=None, verbose=0, random_state=None)
```

Neighborhood Components Analysis.

### `RadiusNeighborsClassifier` <sub>class</sub>

```python
RadiusNeighborsClassifier(radius=1.0, *, weights='uniform', algorithm='auto', leaf_size=30, p=2,
    metric='minkowski', outlier_label=None, metric_params=None, n_jobs=None)
```

Classifier implementing a vote among neighbors within a given radius.

### `RadiusNeighborsRegressor` <sub>class</sub>

```python
RadiusNeighborsRegressor(radius=1.0, *, weights='uniform', algorithm='auto', leaf_size=30, p=2,
    metric='minkowski', metric_params=None, n_jobs=None)
```

Regression based on neighbors within a fixed radius.

### `RadiusNeighborsTransformer` <sub>class</sub>

```python
RadiusNeighborsTransformer(*, mode='distance', radius=1.0, algorithm='auto', leaf_size=30,
    metric='minkowski', p=2, metric_params=None, n_jobs=None)
```

Transform X into a (weighted) graph of neighbors nearer than a radius.

### `kneighbors_graph` <sub>function</sub>

```python
kneighbors_graph(X, n_neighbors, *, mode='connectivity', metric='minkowski', p=2,
    metric_params=None, include_self=False, n_jobs=None)
```

Compute the (weighted) graph of k-Neighbors for points in X.

### `radius_neighbors_graph` <sub>function</sub>

```python
radius_neighbors_graph(X, radius, *, mode='connectivity', metric='minkowski', p=2,
    metric_params=None, include_self=False, n_jobs=None)
```

Compute the (weighted) graph of Neighbors for points in X.

### `sort_graph_by_row_values` <sub>function</sub>

```python
sort_graph_by_row_values(graph, copy=False, warn_when_not_sorted=True)
```

Sort a sparse graph such that each row is stored with increasing values.
