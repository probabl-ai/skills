# `sklearn.cluster`

_Clustering._

### `AffinityPropagation` <sub>class</sub>

```python
AffinityPropagation(*, damping=0.5, max_iter=200, convergence_iter=15, copy=True,
    preference=None, affinity='euclidean', verbose=False, random_state=None)
```

Perform Affinity Propagation Clustering of data.

### `AgglomerativeClustering` <sub>class</sub>

```python
AgglomerativeClustering(n_clusters=2, *, metric='euclidean', memory=None, connectivity=None,
    compute_full_tree='auto', linkage='ward', distance_threshold=None, compute_distances=False)
```

Agglomerative Clustering.

### `Birch` <sub>class</sub>

```python
Birch(*, threshold=0.5, branching_factor=50, n_clusters=3, compute_labels=True)
```

Implements the BIRCH clustering algorithm.

### `BisectingKMeans` <sub>class</sub>

```python
BisectingKMeans(n_clusters=8, *, init='random', n_init=1, random_state=None, max_iter=300,
    verbose=0, tol=0.0001, copy_x=True, algorithm='lloyd', bisecting_strategy='biggest_inertia')
```

Bisecting K-Means clustering.

### `DBSCAN` <sub>class</sub>

```python
DBSCAN(eps=0.5, *, min_samples=5, metric='euclidean', metric_params=None, algorithm='auto',
    leaf_size=30, p=None, n_jobs=None)
```

Perform DBSCAN clustering from vector array or distance matrix.

### `FeatureAgglomeration` <sub>class</sub>

```python
FeatureAgglomeration(n_clusters=2, *, metric='euclidean', memory=None, connectivity=None,
    compute_full_tree='auto', linkage='ward', pooling_func=<function mean at 0x103c99b70>,
    distance_threshold=None, compute_distances=False)
```

Agglomerate features.

### `HDBSCAN` <sub>class</sub>

```python
HDBSCAN(min_cluster_size=5, min_samples=None, cluster_selection_epsilon=0.0,
    max_cluster_size=None, metric='euclidean', metric_params=None, alpha=1.0, algorithm='auto',
    leaf_size=40, n_jobs=None, cluster_selection_method='eom', allow_single_cluster=False,
    store_centers=None, copy='warn')
```

Cluster data using hierarchical density-based clustering.

### `KMeans` <sub>class</sub>

```python
KMeans(n_clusters=8, *, init='k-means++', n_init='auto', max_iter=300, tol=0.0001, verbose=0,
    random_state=None, copy_x=True, algorithm='lloyd')
```

K-Means clustering.

### `MeanShift` <sub>class</sub>

```python
MeanShift(*, bandwidth=None, seeds=None, bin_seeding=False, min_bin_freq=1, cluster_all=True,
    n_jobs=None, max_iter=300)
```

Mean shift clustering using a flat kernel.

### `MiniBatchKMeans` <sub>class</sub>

```python
MiniBatchKMeans(n_clusters=8, *, init='k-means++', max_iter=100, batch_size=1024, verbose=0,
    compute_labels=True, random_state=None, tol=0.0, max_no_improvement=10, init_size=None,
    n_init='auto', reassignment_ratio=0.01)
```

Mini-Batch K-Means clustering.

### `OPTICS` <sub>class</sub>

```python
OPTICS(*, min_samples=5, max_eps=inf, metric='minkowski', p=2, metric_params=None,
    cluster_method='xi', eps=None, xi=0.05, predecessor_correction=True, min_cluster_size=None,
    algorithm='auto', leaf_size=30, memory=None, n_jobs=None)
```

Estimate clustering structure from vector array.

### `SpectralBiclustering` <sub>class</sub>

```python
SpectralBiclustering(n_clusters=3, *, method='bistochastic', n_components=6, n_best=3,
    svd_method='randomized', n_svd_vecs=None, mini_batch=False, init='k-means++', n_init=10,
    random_state=None)
```

Spectral biclustering (Kluger, 2003) [1]_.

### `SpectralClustering` <sub>class</sub>

```python
SpectralClustering(n_clusters=8, *, eigen_solver=None, n_components=None, random_state=None,
    n_init=10, gamma=1.0, affinity='rbf', n_neighbors=10, eigen_tol='auto',
    assign_labels='kmeans', degree=3, coef0=1, kernel_params=None, n_jobs=None, verbose=False)
```

Apply clustering to a projection of the normalized Laplacian.

### `SpectralCoclustering` <sub>class</sub>

```python
SpectralCoclustering(n_clusters=3, *, svd_method='randomized', n_svd_vecs=None,
    mini_batch=False, init='k-means++', n_init=10, random_state=None)
```

Spectral Co-Clustering algorithm (Dhillon, 2001) [1]_.

### `affinity_propagation` <sub>function</sub>

```python
affinity_propagation(S, *, preference=None, convergence_iter=15, max_iter=200, damping=0.5,
    copy=True, verbose=False, return_n_iter=False, random_state=None)
```

Perform Affinity Propagation Clustering of data.

### `cluster_optics_dbscan` <sub>function</sub>

```python
cluster_optics_dbscan(*, reachability, core_distances, ordering, eps)
```

Perform DBSCAN extraction for an arbitrary epsilon.

### `cluster_optics_xi` <sub>function</sub>

```python
cluster_optics_xi(*, reachability, predecessor, ordering, min_samples, min_cluster_size=None,
    xi=0.05, predecessor_correction=True)
```

Automatically extract clusters according to the Xi-steep method.

### `compute_optics_graph` <sub>function</sub>

```python
compute_optics_graph(X, *, min_samples, max_eps, metric, p, metric_params, algorithm, leaf_size,
    n_jobs)
```

Compute the OPTICS reachability graph.

### `dbscan` <sub>function</sub>

```python
dbscan(X, eps=0.5, *, min_samples=5, metric='minkowski', metric_params=None, algorithm='auto',
    leaf_size=30, p=2, sample_weight=None, n_jobs=None)
```

Perform DBSCAN clustering from vector array or distance matrix.

### `estimate_bandwidth` <sub>function</sub>

```python
estimate_bandwidth(X, *, quantile=0.3, n_samples=None, random_state=0, n_jobs=None)
```

Estimate the bandwidth to use with the mean-shift algorithm.

### `k_means` <sub>function</sub>

```python
k_means(X, n_clusters, *, sample_weight=None, init='k-means++', n_init='auto', max_iter=300,
    verbose=False, tol=0.0001, random_state=None, copy_x=True, algorithm='lloyd',
    return_n_iter=False)
```

Perform K-means clustering algorithm.

### `kmeans_plusplus` <sub>function</sub>

```python
kmeans_plusplus(X, n_clusters, *, sample_weight=None, x_squared_norms=None, random_state=None,
    n_local_trials=None)
```

Init n_clusters seeds according to k-means++.

### `mean_shift` <sub>function</sub>

```python
mean_shift(X, *, bandwidth=None, seeds=None, bin_seeding=False, min_bin_freq=1,
    cluster_all=True, max_iter=300, n_jobs=None)
```

Perform mean shift clustering of data using a flat kernel.

### `spectral_clustering` <sub>function</sub>

```python
spectral_clustering(affinity, *, n_clusters=8, n_components=None, eigen_solver=None,
    random_state=None, n_init=10, eigen_tol='auto', assign_labels='kmeans', verbose=False)
```

Apply clustering to a projection of the normalized Laplacian.

### `ward_tree` <sub>function</sub>

```python
ward_tree(X, *, connectivity=None, n_clusters=None, return_distance=False)
```

Ward clustering based on a Feature matrix.
