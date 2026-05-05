# `sklearn.utils`

_Utilities._

### `Bunch` <sub>class</sub>

```python
Bunch(**kwargs)
```

Container object exposing keys as attributes.

### `_safe_indexing` <sub>function</sub>

```python
_safe_indexing(X, indices, *, axis=0)
```

Return rows, items or columns of X using indices.

### `as_float_array` <sub>function</sub>

```python
as_float_array(X, *, copy=True, ensure_all_finite=True)
```

Convert an array-like to an array of floats.

### `assert_all_finite` <sub>function</sub>

```python
assert_all_finite(X, *, allow_nan=False, estimator_name=None, input_name='')
```

Throw a ValueError if X contains NaN or infinity.

### `deprecated` <sub>class</sub>

```python
deprecated(extra='')
```

Decorator to mark a function or class as deprecated.

### `estimator_html_repr` <sub>function</sub>

```python
estimator_html_repr(estimator)
```

Build a HTML representation of an estimator.

### `gen_batches` <sub>function</sub>

```python
gen_batches(n, batch_size, *, min_batch_size=0)
```

Generator to create slices containing `batch_size` elements from 0 to `n`.

### `gen_even_slices` <sub>function</sub>

```python
gen_even_slices(n, n_packs, *, n_samples=None)
```

Generator to create `n_packs` evenly spaced slices going up to `n`.

### `indexable` <sub>function</sub>

```python
indexable(*iterables)
```

Make arrays indexable for cross-validation.

### `murmurhash3_32` <sub>object</sub>

```python
murmurhash3_32(key, seed=0, positive=False)
```

Compute the 32bit murmurhash3 of key at seed.

### `resample` <sub>function</sub>

```python
resample(*arrays, replace=True, n_samples=None, random_state=None, stratify=None,
    sample_weight=None)
```

Resample arrays or sparse matrices in a consistent way.

### `safe_mask` <sub>function</sub>

```python
safe_mask(X, mask)
```

Return a mask which is safe to use on X.

### `safe_sqr` <sub>function</sub>

```python
safe_sqr(X, *, copy=True)
```

Element wise squaring of array-likes and sparse matrices.

### `shuffle` <sub>function</sub>

```python
shuffle(*arrays, random_state=None, n_samples=None)
```

Shuffle arrays or sparse matrices in a consistent way.

### `Tags` <sub>class</sub>

```python
Tags(estimator_type: 'str | None', target_tags: 'TargetTags', transformer_tags: 'TransformerTags
    | None' = None, classifier_tags: 'ClassifierTags | None' = None, regressor_tags:
    'RegressorTags | None' = None, array_api_support: 'bool' = False, no_validation: 'bool' =
    False, non_deterministic: 'bool' = False, requires_fit: 'bool' = True, _skip_test: 'bool' =
    False, input_tags: 'InputTags' = <factory>) -> None
```

Tags for the estimator.

### `InputTags` <sub>class</sub>

```python
InputTags(one_d_array: 'bool' = False, two_d_array: 'bool' = True, three_d_array: 'bool' =
    False, sparse: 'bool' = False, categorical: 'bool' = False, string: 'bool' = False, dict:
    'bool' = False, positive_only: 'bool' = False, allow_nan: 'bool' = False, pairwise: 'bool' =
    False) -> None
```

Tags for the input data.

### `TargetTags` <sub>class</sub>

```python
TargetTags(required: 'bool', one_d_labels: 'bool' = False, two_d_labels: 'bool' = False,
    positive_only: 'bool' = False, multi_output: 'bool' = False, single_output: 'bool' = True)
    -> None
```

Tags for the target data.

### `ClassifierTags` <sub>class</sub>

```python
ClassifierTags(poor_score: 'bool' = False, multi_class: 'bool' = True, multi_label: 'bool' =
    False) -> None
```

Tags for the classifier.

### `RegressorTags` <sub>class</sub>

```python
RegressorTags(poor_score: 'bool' = False) -> None
```

Tags for the regressor.

### `TransformerTags` <sub>class</sub>

```python
TransformerTags(preserves_dtype: 'list[str]' = <factory>) -> None
```

Tags for the transformer.

### `get_tags` <sub>function</sub>

```python
get_tags(estimator) -> 'Tags'
```

Get estimator tags.

## Input and parameter validation

### `check_X_y` <sub>function</sub>

```python
check_X_y(X, y, accept_sparse=False, *, accept_large_sparse=True, dtype='numeric', order=None,
    copy=False, force_writeable=False, ensure_all_finite=True, ensure_2d=True, allow_nd=False,
    multi_output=False, ensure_min_samples=1, ensure_min_features=1, y_numeric=False,
    estimator=None)
```

Input validation for standard estimators.

### `check_array` <sub>function</sub>

```python
check_array(array, accept_sparse=False, *, accept_large_sparse=True, dtype='numeric',
    order=None, copy=False, force_writeable=False, ensure_all_finite=True,
    ensure_non_negative=False, ensure_2d=True, allow_nd=False, ensure_min_samples=1,
    ensure_min_features=1, estimator=None, input_name='')
```

Input validation on an array, list, sparse matrix or similar.

### `check_consistent_length` <sub>function</sub>

```python
check_consistent_length(*arrays)
```

Check that all arrays have consistent first dimensions.

### `check_random_state` <sub>function</sub>

```python
check_random_state(seed)
```

Turn seed into an np.random.RandomState instance.

### `check_scalar` <sub>function</sub>

```python
check_scalar(x, name, target_type, *, min_val=None, max_val=None, include_boundaries='both')
```

Validate scalar parameters type and value.

### `validation.check_is_fitted` <sub>function</sub>

```python
validation.check_is_fitted(estimator, attributes=None, *, msg=None, all_or_any=<built-in
    function all>)
```

Perform is_fitted validation for estimator.

### `validation.check_memory` <sub>function</sub>

```python
validation.check_memory(memory)
```

Check that ``memory`` is joblib.Memory-like.

### `validation.check_symmetric` <sub>function</sub>

```python
validation.check_symmetric(array, *, tol=1e-10, raise_warning=True, raise_exception=False)
```

Make sure that array is 2D, square and symmetric.

### `validation.column_or_1d` <sub>function</sub>

```python
validation.column_or_1d(y, *, dtype=None, input_name='y', warn=False, device=None)
```

Ravel column or 1d numpy array, else raises an error.

### `validation.has_fit_parameter` <sub>function</sub>

```python
validation.has_fit_parameter(estimator, parameter)
```

Check whether the estimator's fit method supports the given parameter.

### `validation.validate_data` <sub>function</sub>

```python
validation.validate_data(_estimator, /, X='no_validation', y='no_validation', reset=True,
    validate_separately=False, skip_check_array=False, **check_params)
```

Validate input data and set or check feature names and counts of the input.

## Meta-estimators

### `metaestimators.available_if` <sub>function</sub>

```python
metaestimators.available_if(check)
```

An attribute that is available only if check returns a truthy value.

## Weight handling based on class labels

### `class_weight.compute_class_weight` <sub>function</sub>

```python
class_weight.compute_class_weight(class_weight, *, classes, y, sample_weight=None)
```

Estimate class weights for unbalanced datasets.

### `class_weight.compute_sample_weight` <sub>function</sub>

```python
class_weight.compute_sample_weight(class_weight, y, *, indices=None)
```

Estimate sample weights by class for unbalanced datasets.

## Dealing with multiclass target in classifiers

### `multiclass.is_multilabel` <sub>function</sub>

```python
multiclass.is_multilabel(y)
```

Check if ``y`` is in a multilabel format.

### `multiclass.type_of_target` <sub>function</sub>

```python
multiclass.type_of_target(y, input_name='', raise_unknown=False)
```

Determine the type of data indicated by the target.

### `multiclass.unique_labels` <sub>function</sub>

```python
multiclass.unique_labels(*ys)
```

Extract an ordered array of unique labels.

## Optimal mathematical operations

### `extmath.density` <sub>function</sub>

```python
extmath.density(w)
```

Compute density of a sparse vector.

### `extmath.fast_logdet` <sub>function</sub>

```python
extmath.fast_logdet(A)
```

Compute logarithm of determinant of a square matrix.

### `extmath.randomized_range_finder` <sub>function</sub>

```python
extmath.randomized_range_finder(A, *, size, n_iter, power_iteration_normalizer='auto',
    random_state=None)
```

Compute an orthonormal matrix whose range approximates the range of A.

### `extmath.randomized_svd` <sub>function</sub>

```python
extmath.randomized_svd(M, n_components, *, n_oversamples=10, n_iter='auto',
    power_iteration_normalizer='auto', transpose='auto', flip_sign=True, random_state=None,
    svd_lapack_driver='gesdd')
```

Compute a truncated randomized SVD.

### `extmath.safe_sparse_dot` <sub>function</sub>

```python
extmath.safe_sparse_dot(a, b, *, dense_output=False)
```

Dot product that handle the sparse matrix case correctly.

### `extmath.weighted_mode` <sub>function</sub>

```python
extmath.weighted_mode(a, w, *, axis=0)
```

Return an array of the weighted modal (most common) value in the passed array.

## Working with sparse matrices and arrays

### `sparsefuncs.incr_mean_variance_axis` <sub>function</sub>

```python
sparsefuncs.incr_mean_variance_axis(X, *, axis, last_mean, last_var, last_n, weights=None)
```

Compute incremental mean and variance along an axis on a CSR or CSC matrix.

### `sparsefuncs.inplace_column_scale` <sub>function</sub>

```python
sparsefuncs.inplace_column_scale(X, scale)
```

Inplace column scaling of a CSC/CSR matrix.

### `sparsefuncs.inplace_csr_column_scale` <sub>function</sub>

```python
sparsefuncs.inplace_csr_column_scale(X, scale)
```

Inplace column scaling of a CSR matrix.

### `sparsefuncs.inplace_row_scale` <sub>function</sub>

```python
sparsefuncs.inplace_row_scale(X, scale)
```

Inplace row scaling of a CSR or CSC matrix.

### `sparsefuncs.inplace_swap_column` <sub>function</sub>

```python
sparsefuncs.inplace_swap_column(X, m, n)
```

Swap two columns of a CSC/CSR matrix in-place.

### `sparsefuncs.inplace_swap_row` <sub>function</sub>

```python
sparsefuncs.inplace_swap_row(X, m, n)
```

Swap two rows of a CSC/CSR matrix in-place.

### `sparsefuncs.mean_variance_axis` <sub>function</sub>

```python
sparsefuncs.mean_variance_axis(X, axis, weights=None, return_sum_weights=False)
```

Compute mean and variance along an axis on a CSR or CSC matrix.

### `sparsefuncs_fast.inplace_csr_row_normalize_l1` <sub>object</sub>

```python
sparsefuncs_fast.inplace_csr_row_normalize_l1(X)
```

Normalize inplace the rows of a CSR matrix or array by their L1 norm.

### `sparsefuncs_fast.inplace_csr_row_normalize_l2` <sub>object</sub>

```python
sparsefuncs_fast.inplace_csr_row_normalize_l2(X)
```

Normalize inplace the rows of a CSR matrix or array by their L2 norm.

## Working with graphs

### `graph.single_source_shortest_path_length` <sub>function</sub>

```python
graph.single_source_shortest_path_length(graph, source, *, cutoff=None)
```

Return the length of the shortest path from source to all reachable nodes.

## Random sampling

### `random.sample_without_replacement` <sub>object</sub>

```python
random.sample_without_replacement(n_population, n_samples, method='auto', random_state=None)
```

Sample integers without replacement.

## Auxiliary functions that operate on arrays

### `arrayfuncs.min_pos` <sub>object</sub>

```python
arrayfuncs.min_pos(X)
```

Find the minimum value of an array over positive values.

## Metadata routing

### `metadata_routing.MetadataRequest` <sub>class</sub>

```python
metadata_routing.MetadataRequest(owner)
```

Contains the metadata request info of a consumer.

### `metadata_routing.MetadataRouter` <sub>class</sub>

```python
metadata_routing.MetadataRouter(owner)
```

Coordinates metadata routing for a :term:`router` object.

### `metadata_routing.MethodMapping` <sub>class</sub>

```python
metadata_routing.MethodMapping()
```

Stores the mapping between caller and callee methods for a :term:`router`.

### `metadata_routing.get_routing_for_object` <sub>function</sub>

```python
metadata_routing.get_routing_for_object(obj=None)
```

Get a ``Metadata{Router, Request}`` instance from the given object.

### `metadata_routing.process_routing` <sub>function</sub>

```python
metadata_routing.process_routing(_obj, _method, /, **kwargs)
```

Validate and route metadata.

## Discovering scikit-learn objects

### `discovery.all_displays` <sub>function</sub>

```python
discovery.all_displays()
```

Get a list of all displays from `sklearn`.

### `discovery.all_estimators` <sub>function</sub>

```python
discovery.all_estimators(type_filter=None)
```

Get a list of all estimators from `sklearn`.

### `discovery.all_functions` <sub>function</sub>

```python
discovery.all_functions()
```

Get a list of all functions from `sklearn`.

## API compatibility checkers

### `estimator_checks.check_estimator` <sub>function</sub>

```python
estimator_checks.check_estimator(estimator=None, *, legacy: 'bool' = True,
    expected_failed_checks: 'dict[str, str] | None' = None, on_skip: "Literal['warn'] | None" =
    'warn', on_fail: "Literal['raise', 'warn'] | None" = 'raise', callback: 'Callable | None' =
    None)
```

Check if estimator adheres to scikit-learn conventions.

### `estimator_checks.parametrize_with_checks` <sub>function</sub>

```python
estimator_checks.parametrize_with_checks(estimators, *, legacy: 'bool' = True,
    expected_failed_checks: 'Callable | None' = None, xfail_strict: 'bool | None' = None)
```

Pytest specific decorator for parametrizing estimator checks.

### `estimator_checks.estimator_checks_generator` <sub>function</sub>

```python
estimator_checks.estimator_checks_generator(estimator, *, legacy: 'bool' = True,
    expected_failed_checks: 'dict[str, str] | None' = None, mark: "Literal['xfail', 'skip',
    None]" = None, xfail_strict: 'bool | None' = None)
```

Iteratively yield all check callables for an estimator.

## Parallel computing

### `parallel.Parallel` <sub>class</sub>

```python
parallel.Parallel(n_jobs=default(None), backend=default(None), return_as='list',
    verbose=default(0), timeout=None, pre_dispatch='2 * n_jobs', batch_size='auto',
    temp_folder=default(None), max_nbytes=default('1M'), mmap_mode=default('r'),
    prefer=default(None), require=default(None), **backend_kwargs)
```

Tweak of :class:`joblib.Parallel` that propagates the scikit-learn configuration.

### `parallel.delayed` <sub>function</sub>

```python
parallel.delayed(function)
```

Decorator used to capture the arguments of a function.
