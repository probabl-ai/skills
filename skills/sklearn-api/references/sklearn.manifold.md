# `sklearn.manifold`

_Manifold learning._

### `ClassicalMDS` <sub>class</sub>

```python
ClassicalMDS(n_components=2, *, metric='euclidean', metric_params=None)
```

Classical multidimensional scaling (MDS).

### `Isomap` <sub>class</sub>

```python
Isomap(*, n_neighbors=5, radius=None, n_components=2, eigen_solver='auto', tol=0, max_iter=None,
    path_method='auto', neighbors_algorithm='auto', n_jobs=None, metric='minkowski', p=2,
    metric_params=None)
```

Isomap Embedding.

### `LocallyLinearEmbedding` <sub>class</sub>

```python
LocallyLinearEmbedding(*, n_neighbors=5, n_components=2, reg=0.001, eigen_solver='auto',
    tol=1e-06, max_iter=100, method='standard', hessian_tol=0.0001, modified_tol=1e-12,
    neighbors_algorithm='auto', random_state=None, n_jobs=None)
```

Locally Linear Embedding.

### `MDS` <sub>class</sub>

```python
MDS(n_components=2, *, metric_mds=True, n_init='warn', init='warn', max_iter=300, verbose=0,
    eps=1e-06, n_jobs=None, random_state=None, dissimilarity='deprecated', metric='euclidean',
    metric_params=None, normalized_stress='auto')
```

Multidimensional scaling.

### `SpectralEmbedding` <sub>class</sub>

```python
SpectralEmbedding(n_components=2, *, affinity='nearest_neighbors', gamma=None,
    random_state=None, eigen_solver=None, eigen_tol='auto', n_neighbors=None, n_jobs=None)
```

Spectral embedding for non-linear dimensionality reduction.

### `TSNE` <sub>class</sub>

```python
TSNE(n_components=2, *, perplexity=30.0, early_exaggeration=12.0, learning_rate='auto',
    max_iter=1000, n_iter_without_progress=300, min_grad_norm=1e-07, metric='euclidean',
    metric_params=None, init='pca', verbose=0, random_state=None, method='barnes_hut',
    angle=0.5, n_jobs=None)
```

T-distributed Stochastic Neighbor Embedding.

### `locally_linear_embedding` <sub>function</sub>

```python
locally_linear_embedding(X, *, n_neighbors, n_components, reg=0.001, eigen_solver='auto',
    tol=1e-06, max_iter=100, method='standard', hessian_tol=0.0001, modified_tol=1e-12,
    random_state=None, n_jobs=None)
```

Perform a Locally Linear Embedding analysis on the data.

### `smacof` <sub>function</sub>

```python
smacof(dissimilarities, *, metric=True, n_components=2, init=None, n_init='warn', n_jobs=None,
    max_iter=300, verbose=0, eps=1e-06, random_state=None, return_n_iter=False,
    normalized_stress='auto')
```

Compute multidimensional scaling using the SMACOF algorithm.

### `spectral_embedding` <sub>function</sub>

```python
spectral_embedding(adjacency, *, n_components=8, eigen_solver=None, random_state=None,
    eigen_tol='auto', norm_laplacian=True, drop_first=True)
```

Project the sample on the first eigenvectors of the graph Laplacian.

### `trustworthiness` <sub>function</sub>

```python
trustworthiness(X, X_embedded, *, n_neighbors=5, metric='euclidean')
```

Indicate to what extent the local structure is retained.
