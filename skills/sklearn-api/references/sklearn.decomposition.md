# `sklearn.decomposition`

_Matrix decomposition._

### `DictionaryLearning` <sub>class</sub>

```python
DictionaryLearning(n_components=None, *, alpha=1, max_iter=1000, tol=1e-08,
    fit_algorithm='lars', transform_algorithm='omp', transform_n_nonzero_coefs=None,
    transform_alpha=None, n_jobs=None, code_init=None, dict_init=None, callback=None,
    verbose=False, split_sign=False, random_state=None, positive_code=False,
    positive_dict=False, transform_max_iter=1000)
```

Dictionary learning.

### `FactorAnalysis` <sub>class</sub>

```python
FactorAnalysis(n_components=None, *, tol=0.01, copy=True, max_iter=1000,
    noise_variance_init=None, svd_method='randomized', iterated_power=3, rotation=None,
    random_state=0)
```

Factor Analysis (FA).

### `FastICA` <sub>class</sub>

```python
FastICA(n_components=None, *, algorithm='parallel', whiten='unit-variance', fun='logcosh',
    fun_args=None, max_iter=200, tol=0.0001, w_init=None, whiten_solver='svd',
    random_state=None)
```

FastICA: a fast algorithm for Independent Component Analysis.

### `IncrementalPCA` <sub>class</sub>

```python
IncrementalPCA(n_components=None, *, whiten=False, copy=True, batch_size=None)
```

Incremental principal components analysis (IPCA).

### `KernelPCA` <sub>class</sub>

```python
KernelPCA(n_components=None, *, kernel='linear', gamma=None, degree=3, coef0=1,
    kernel_params=None, alpha=1.0, fit_inverse_transform=False, eigen_solver='auto', tol=0,
    max_iter=None, iterated_power='auto', remove_zero_eig=False, random_state=None, copy_X=True,
    n_jobs=None)
```

Kernel Principal component analysis (KPCA).

### `LatentDirichletAllocation` <sub>class</sub>

```python
LatentDirichletAllocation(n_components=10, *, doc_topic_prior=None, topic_word_prior=None,
    learning_method='batch', learning_decay=0.7, learning_offset=10.0, max_iter=10,
    batch_size=128, evaluate_every=-1, total_samples=1000000.0, perp_tol=0.1,
    mean_change_tol=0.001, max_doc_update_iter=100, n_jobs=None, verbose=0, random_state=None)
```

Latent Dirichlet Allocation with online variational Bayes algorithm.

### `MiniBatchDictionaryLearning` <sub>class</sub>

```python
MiniBatchDictionaryLearning(n_components=None, *, alpha=1, max_iter=1000, fit_algorithm='lars',
    n_jobs=None, batch_size=256, shuffle=True, dict_init=None, transform_algorithm='omp',
    transform_n_nonzero_coefs=None, transform_alpha=None, verbose=False, split_sign=False,
    random_state=None, positive_code=False, positive_dict=False, transform_max_iter=1000,
    callback=None, tol=0.001, max_no_improvement=10)
```

Mini-batch dictionary learning.

### `MiniBatchNMF` <sub>class</sub>

```python
MiniBatchNMF(n_components='auto', *, init=None, batch_size=1024, beta_loss='frobenius',
    tol=0.0001, max_no_improvement=10, max_iter=200, alpha_W=0.0, alpha_H='same', l1_ratio=0.0,
    forget_factor=0.7, fresh_restarts=False, fresh_restarts_max_iter=30,
    transform_max_iter=None, random_state=None, verbose=0)
```

Mini-Batch Non-Negative Matrix Factorization (NMF).

### `MiniBatchSparsePCA` <sub>class</sub>

```python
MiniBatchSparsePCA(n_components=None, *, alpha=1, ridge_alpha=0.01, max_iter=1000,
    callback=None, batch_size=3, verbose=False, shuffle=True, n_jobs=None, method='lars',
    random_state=None, tol=0.001, max_no_improvement=10)
```

Mini-batch Sparse Principal Components Analysis.

### `NMF` <sub>class</sub>

```python
NMF(n_components='auto', *, init=None, solver='cd', beta_loss='frobenius', tol=0.0001,
    max_iter=200, random_state=None, alpha_W=0.0, alpha_H='same', l1_ratio=0.0, verbose=0,
    shuffle=False)
```

Non-Negative Matrix Factorization (NMF).

### `PCA` <sub>class</sub>

```python
PCA(n_components=None, *, copy=True, whiten=False, svd_solver='auto', tol=0.0,
    iterated_power='auto', n_oversamples=10, power_iteration_normalizer='auto',
    random_state=None)
```

Principal component analysis (PCA).

### `SparseCoder` <sub>class</sub>

```python
SparseCoder(dictionary, *, transform_algorithm='omp', transform_n_nonzero_coefs=None,
    transform_alpha=None, split_sign=False, n_jobs=None, positive_code=False,
    transform_max_iter=1000)
```

Sparse coding.

### `SparsePCA` <sub>class</sub>

```python
SparsePCA(n_components=None, *, alpha=1, ridge_alpha=0.01, max_iter=1000, tol=1e-08,
    method='lars', n_jobs=None, U_init=None, V_init=None, verbose=False, random_state=None)
```

Sparse Principal Components Analysis (SparsePCA).

### `TruncatedSVD` <sub>class</sub>

```python
TruncatedSVD(n_components=2, *, algorithm='randomized', n_iter=5, n_oversamples=10,
    power_iteration_normalizer='auto', random_state=None, tol=0.0)
```

Dimensionality reduction using truncated SVD (aka LSA).

### `dict_learning` <sub>function</sub>

```python
dict_learning(X, n_components, *, alpha, max_iter=100, tol=1e-08, method='lars', n_jobs=None,
    dict_init=None, code_init=None, callback=None, verbose=False, random_state=None,
    return_n_iter=False, positive_dict=False, positive_code=False, method_max_iter=1000)
```

Solve a dictionary learning matrix factorization problem.

### `dict_learning_online` <sub>function</sub>

```python
dict_learning_online(X, n_components=2, *, alpha=1, max_iter=100, return_code=True,
    dict_init=None, callback=None, batch_size=256, verbose=False, shuffle=True, n_jobs=None,
    method='lars', random_state=None, positive_dict=False, positive_code=False,
    method_max_iter=1000, tol=0.001, max_no_improvement=10)
```

Solve a dictionary learning matrix factorization problem online.

### `fastica` <sub>function</sub>

```python
fastica(X, n_components=None, *, algorithm='parallel', whiten='unit-variance', fun='logcosh',
    fun_args=None, max_iter=200, tol=0.0001, w_init=None, whiten_solver='svd',
    random_state=None, return_X_mean=False, compute_sources=True, return_n_iter=False)
```

Perform Fast Independent Component Analysis.

### `non_negative_factorization` <sub>function</sub>

```python
non_negative_factorization(X, W=None, H=None, n_components='auto', *, init=None, update_H=True,
    solver='cd', beta_loss='frobenius', tol=0.0001, max_iter=200, alpha_W=0.0, alpha_H='same',
    l1_ratio=0.0, random_state=None, verbose=0, shuffle=False)
```

Compute Non-negative Matrix Factorization (NMF).

### `sparse_encode` <sub>function</sub>

```python
sparse_encode(X, dictionary, *, gram=None, cov=None, algorithm='lasso_lars',
    n_nonzero_coefs=None, alpha=None, copy_cov=True, init=None, max_iter=1000, n_jobs=None,
    check_input=True, verbose=0, positive=False)
```

Sparse coding.
