# `sklearn.preprocessing`

_Preprocessing and normalization._

### `Binarizer` <sub>class</sub>

```python
Binarizer(*, threshold=0.0, copy=True)
```

Binarize data (set feature values to 0 or 1) according to a threshold.

### `FunctionTransformer` <sub>class</sub>

```python
FunctionTransformer(func=None, inverse_func=None, *, validate=False, accept_sparse=False,
    check_inverse=True, feature_names_out=None, kw_args=None, inv_kw_args=None)
```

Constructs a transformer from an arbitrary callable.

### `KBinsDiscretizer` <sub>class</sub>

```python
KBinsDiscretizer(n_bins=5, *, encode='onehot', strategy='quantile', quantile_method='warn',
    dtype=None, subsample=200000, random_state=None)
```

Bin continuous data into intervals.

### `KernelCenterer` <sub>class</sub>

```python
KernelCenterer()
```

Center an arbitrary kernel matrix :math:`K`.

### `LabelBinarizer` <sub>class</sub>

```python
LabelBinarizer(*, neg_label=0, pos_label=1, sparse_output=False)
```

Binarize labels in a one-vs-all fashion.

### `LabelEncoder` <sub>class</sub>

```python
LabelEncoder()
```

Encode target labels with value between 0 and n_classes-1.

### `MaxAbsScaler` <sub>class</sub>

```python
MaxAbsScaler(*, copy=True, clip=False)
```

Scale each feature by its maximum absolute value.

### `MinMaxScaler` <sub>class</sub>

```python
MinMaxScaler(feature_range=(0, 1), *, copy=True, clip=False)
```

Transform features by scaling each feature to a given range.

### `MultiLabelBinarizer` <sub>class</sub>

```python
MultiLabelBinarizer(*, classes=None, sparse_output=False)
```

Transform between iterable of iterables and a multilabel format.

### `Normalizer` <sub>class</sub>

```python
Normalizer(norm='l2', *, copy=True)
```

Normalize samples individually to unit norm.

### `OneHotEncoder` <sub>class</sub>

```python
OneHotEncoder(*, categories='auto', drop=None, sparse_output=True, dtype=<class
    'numpy.float64'>, handle_unknown='error', min_frequency=None, max_categories=None,
    feature_name_combiner='concat')
```

Encode categorical features as a one-hot numeric array.

### `OrdinalEncoder` <sub>class</sub>

```python
OrdinalEncoder(*, categories='auto', dtype=<class 'numpy.float64'>, handle_unknown='error',
    unknown_value=None, encoded_missing_value=nan, min_frequency=None, max_categories=None)
```

Encode categorical features as an integer array.

### `PolynomialFeatures` <sub>class</sub>

```python
PolynomialFeatures(degree=2, *, interaction_only=False, include_bias=True, order='C')
```

Generate polynomial and interaction features.

### `PowerTransformer` <sub>class</sub>

```python
PowerTransformer(method='yeo-johnson', *, standardize=True, copy=True)
```

Apply a power transform featurewise to make data more Gaussian-like.

### `QuantileTransformer` <sub>class</sub>

```python
QuantileTransformer(*, n_quantiles=1000, output_distribution='uniform',
    ignore_implicit_zeros=False, subsample=10000, random_state=None, copy=True)
```

Transform features using quantiles information.

### `RobustScaler` <sub>class</sub>

```python
RobustScaler(*, with_centering=True, with_scaling=True, quantile_range=(25.0, 75.0), copy=True,
    unit_variance=False)
```

Scale features using statistics that are robust to outliers.

### `SplineTransformer` <sub>class</sub>

```python
SplineTransformer(n_knots=5, degree=3, *, knots='uniform', extrapolation='constant',
    include_bias=True, order='C', handle_missing='error', sparse_output=False)
```

Generate univariate B-spline bases for features.

### `StandardScaler` <sub>class</sub>

```python
StandardScaler(*, copy=True, with_mean=True, with_std=True)
```

Standardize features by removing the mean and scaling to unit variance.

### `TargetEncoder` <sub>class</sub>

```python
TargetEncoder(categories='auto', target_type='auto', smooth='auto', cv=5, shuffle=True,
    random_state=None)
```

Target Encoder for regression and classification targets.

### `add_dummy_feature` <sub>function</sub>

```python
add_dummy_feature(X, value=1.0)
```

Augment dataset with an additional dummy feature.

### `binarize` <sub>function</sub>

```python
binarize(X, *, threshold=0.0, copy=True)
```

Boolean thresholding of array-like or scipy.sparse matrix.

### `label_binarize` <sub>function</sub>

```python
label_binarize(y, *, classes, neg_label=0, pos_label=1, sparse_output=False)
```

Binarize labels in a one-vs-all fashion.

### `maxabs_scale` <sub>function</sub>

```python
maxabs_scale(X, *, axis=0, copy=True)
```

Scale each feature to the [-1, 1] range without breaking the sparsity.

### `minmax_scale` <sub>function</sub>

```python
minmax_scale(X, feature_range=(0, 1), *, axis=0, copy=True)
```

Transform features by scaling each feature to a given range.

### `normalize` <sub>function</sub>

```python
normalize(X, norm='l2', *, axis=1, copy=True, return_norm=False)
```

Scale input vectors individually to unit norm (vector length).

### `power_transform` <sub>function</sub>

```python
power_transform(X, method='yeo-johnson', *, standardize=True, copy=True)
```

Parametric, monotonic transformation to make data more Gaussian-like.

### `quantile_transform` <sub>function</sub>

```python
quantile_transform(X, *, axis=0, n_quantiles=1000, output_distribution='uniform',
    ignore_implicit_zeros=False, subsample=100000, random_state=None, copy=True)
```

Transform features using quantiles information.

### `robust_scale` <sub>function</sub>

```python
robust_scale(X, *, axis=0, with_centering=True, with_scaling=True, quantile_range=(25.0, 75.0),
    copy=True, unit_variance=False)
```

Standardize a dataset along any axis.

### `scale` <sub>function</sub>

```python
scale(X, *, axis=0, with_mean=True, with_std=True, copy=True)
```

Standardize a dataset along any axis.
