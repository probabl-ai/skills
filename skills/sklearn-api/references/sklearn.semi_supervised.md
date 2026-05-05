# `sklearn.semi_supervised`

_Semi-supervised learning._

### `LabelPropagation` <sub>class</sub>

```python
LabelPropagation(kernel='rbf', *, gamma=20, n_neighbors=7, max_iter=1000, tol=0.001, n_jobs=None)
```

Label Propagation classifier.

### `LabelSpreading` <sub>class</sub>

```python
LabelSpreading(kernel='rbf', *, gamma=20, n_neighbors=7, alpha=0.2, max_iter=30, tol=0.001,
    n_jobs=None)
```

LabelSpreading model for semi-supervised learning.

### `SelfTrainingClassifier` <sub>class</sub>

```python
SelfTrainingClassifier(estimator=None, threshold=0.75, criterion='threshold', k_best=10,
    max_iter=10, verbose=False)
```

Self-training classifier.
