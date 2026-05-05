# `sklearn.base`

_Base classes and utility functions._

### `BaseEstimator` <sub>class</sub>

```python
BaseEstimator()
```

Base class for all estimators in scikit-learn.

### `BiclusterMixin` <sub>class</sub>

```python
BiclusterMixin()
```

Mixin class for all bicluster estimators in scikit-learn.

### `ClassNamePrefixFeaturesOutMixin` <sub>class</sub>

```python
ClassNamePrefixFeaturesOutMixin()
```

Mixin class for transformers that generate their own names by prefixing.

### `ClassifierMixin` <sub>class</sub>

```python
ClassifierMixin()
```

Mixin class for all classifiers in scikit-learn.

### `ClusterMixin` <sub>class</sub>

```python
ClusterMixin()
```

Mixin class for all cluster estimators in scikit-learn.

### `DensityMixin` <sub>class</sub>

```python
DensityMixin()
```

Mixin class for all density estimators in scikit-learn.

### `MetaEstimatorMixin` <sub>class</sub>

```python
MetaEstimatorMixin()
```

Mixin class for all meta estimators in scikit-learn.

### `OneToOneFeatureMixin` <sub>class</sub>

```python
OneToOneFeatureMixin()
```

Provides `get_feature_names_out` for simple transformers.

### `OutlierMixin` <sub>class</sub>

```python
OutlierMixin()
```

Mixin class for all outlier detection estimators in scikit-learn.

### `RegressorMixin` <sub>class</sub>

```python
RegressorMixin()
```

Mixin class for all regression estimators in scikit-learn.

### `TransformerMixin` <sub>class</sub>

```python
TransformerMixin()
```

Mixin class for all transformers in scikit-learn.

### `clone` <sub>function</sub>

```python
clone(estimator, *, safe=True)
```

Construct a new unfitted estimator with the same parameters.

### `is_classifier` <sub>function</sub>

```python
is_classifier(estimator)
```

Return True if the given estimator is (probably) a classifier.

### `is_clusterer` <sub>function</sub>

```python
is_clusterer(estimator)
```

Return True if the given estimator is (probably) a clusterer.

### `is_regressor` <sub>function</sub>

```python
is_regressor(estimator)
```

Return True if the given estimator is (probably) a regressor.

### `is_outlier_detector` <sub>function</sub>

```python
is_outlier_detector(estimator)
```

Return True if the given estimator is (probably) an outlier detector.
