# `sklearn.feature_selection`

_Feature selection._

### `GenericUnivariateSelect` <sub>class</sub>

```python
GenericUnivariateSelect(score_func=<function f_classif at 0x165069260>, *, mode='percentile',
    param=1e-05)
```

Univariate feature selector with configurable strategy.

### `RFE` <sub>class</sub>

```python
RFE(estimator, *, n_features_to_select=None, step=1, verbose=0, importance_getter='auto')
```

Feature ranking with recursive feature elimination.

### `RFECV` <sub>class</sub>

```python
RFECV(estimator, *, step=1, min_features_to_select=1, cv=None, scoring=None, verbose=0,
    n_jobs=None, importance_getter='auto')
```

Recursive feature elimination with cross-validation to select features.

### `SelectFdr` <sub>class</sub>

```python
SelectFdr(score_func=<function f_classif at 0x165069260>, *, alpha=0.05)
```

Filter: Select the p-values for an estimated false discovery rate.

### `SelectFpr` <sub>class</sub>

```python
SelectFpr(score_func=<function f_classif at 0x165069260>, *, alpha=0.05)
```

Filter: Select the pvalues below alpha based on a FPR test.

### `SelectFromModel` <sub>class</sub>

```python
SelectFromModel(estimator, *, threshold=None, prefit=False, norm_order=1, max_features=None,
    importance_getter='auto')
```

Meta-transformer for selecting features based on importance weights.

### `SelectFwe` <sub>class</sub>

```python
SelectFwe(score_func=<function f_classif at 0x165069260>, *, alpha=0.05)
```

Filter: Select the p-values corresponding to Family-wise error rate.

### `SelectKBest` <sub>class</sub>

```python
SelectKBest(score_func=<function f_classif at 0x165069260>, *, k=10)
```

Select features according to the k highest scores.

### `SelectPercentile` <sub>class</sub>

```python
SelectPercentile(score_func=<function f_classif at 0x165069260>, *, percentile=10)
```

Select features according to a percentile of the highest scores.

### `SelectorMixin` <sub>class</sub>

```python
SelectorMixin()
```

Transformer mixin that performs feature selection given a support mask

### `SequentialFeatureSelector` <sub>class</sub>

```python
SequentialFeatureSelector(estimator, *, n_features_to_select='auto', tol=None,
    direction='forward', scoring=None, cv=5, n_jobs=None)
```

Transformer that performs Sequential Feature Selection.

### `VarianceThreshold` <sub>class</sub>

```python
VarianceThreshold(threshold=0.0)
```

Feature selector that removes all low-variance features.

### `chi2` <sub>function</sub>

```python
chi2(X, y)
```

Compute chi-squared stats between each non-negative feature and class.

### `f_classif` <sub>function</sub>

```python
f_classif(X, y)
```

Compute the ANOVA F-value for the provided sample.

### `f_regression` <sub>function</sub>

```python
f_regression(X, y, *, center=True, force_finite=True)
```

Univariate linear regression tests returning F-statistic and p-values.

### `mutual_info_classif` <sub>function</sub>

```python
mutual_info_classif(X, y, *, discrete_features='auto', n_neighbors=3, copy=True,
    random_state=None, n_jobs=None)
```

Estimate mutual information for a discrete target variable.

### `mutual_info_regression` <sub>function</sub>

```python
mutual_info_regression(X, y, *, discrete_features='auto', n_neighbors=3, copy=True,
    random_state=None, n_jobs=None)
```

Estimate mutual information for a continuous target variable.

### `r_regression` <sub>function</sub>

```python
r_regression(X, y, *, center=True, force_finite=True)
```

Compute Pearson's r for each features and the target.
