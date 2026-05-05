# `sklearn.model_selection`

_Model selection._

## Splitters

### `GroupKFold` <sub>class</sub>

```python
GroupKFold(n_splits=5, *, shuffle=False, random_state=None)
```

K-fold iterator variant with non-overlapping groups.

### `GroupShuffleSplit` <sub>class</sub>

```python
GroupShuffleSplit(n_splits=5, *, test_size=None, train_size=None, random_state=None)
```

Shuffle-Group(s)-Out cross-validation iterator.

### `KFold` <sub>class</sub>

```python
KFold(n_splits=5, *, shuffle=False, random_state=None)
```

K-Fold cross-validator.

### `LeaveOneGroupOut` <sub>class</sub>

```python
LeaveOneGroupOut()
```

Leave One Group Out cross-validator.

### `LeaveOneOut` <sub>class</sub>

```python
LeaveOneOut()
```

Leave-One-Out cross-validator.

### `LeavePGroupsOut` <sub>class</sub>

```python
LeavePGroupsOut(n_groups)
```

Leave P Group(s) Out cross-validator.

### `LeavePOut` <sub>class</sub>

```python
LeavePOut(p)
```

Leave-P-Out cross-validator.

### `PredefinedSplit` <sub>class</sub>

```python
PredefinedSplit(test_fold)
```

Predefined split cross-validator.

### `RepeatedKFold` <sub>class</sub>

```python
RepeatedKFold(*, n_splits=5, n_repeats=10, random_state=None)
```

Repeated K-Fold cross validator.

### `RepeatedStratifiedKFold` <sub>class</sub>

```python
RepeatedStratifiedKFold(*, n_splits=5, n_repeats=10, random_state=None)
```

Repeated class-wise stratified K-Fold cross validator.

### `ShuffleSplit` <sub>class</sub>

```python
ShuffleSplit(n_splits=10, *, test_size=None, train_size=None, random_state=None)
```

Random permutation cross-validator.

### `StratifiedGroupKFold` <sub>class</sub>

```python
StratifiedGroupKFold(n_splits=5, shuffle=False, random_state=None)
```

Class-wise stratified K-Fold iterator variant with non-overlapping groups.

### `StratifiedKFold` <sub>class</sub>

```python
StratifiedKFold(n_splits=5, *, shuffle=False, random_state=None)
```

Class-wise stratified K-Fold cross-validator.

### `StratifiedShuffleSplit` <sub>class</sub>

```python
StratifiedShuffleSplit(n_splits=10, *, test_size=None, train_size=None, random_state=None)
```

Class-wise stratified ShuffleSplit cross-validator.

### `TimeSeriesSplit` <sub>class</sub>

```python
TimeSeriesSplit(n_splits=5, *, max_train_size=None, test_size=None, gap=0)
```

Time Series cross-validator.

### `check_cv` <sub>function</sub>

```python
check_cv(cv=5, y=None, *, classifier=False)
```

Input checker utility for building a cross-validator.

### `train_test_split` <sub>function</sub>

```python
train_test_split(*arrays, test_size=None, train_size=None, random_state=None, shuffle=True,
    stratify=None)
```

Split arrays or matrices into random train and test subsets.

## Hyper-parameter optimizers

### `GridSearchCV` <sub>class</sub>

```python
GridSearchCV(estimator, param_grid, *, scoring=None, n_jobs=None, refit=True, cv=None,
    verbose=0, pre_dispatch='2*n_jobs', error_score=nan, return_train_score=False)
```

Exhaustive search over specified parameter values for an estimator.

### `HalvingGridSearchCV` <sub>class</sub>

```python
HalvingGridSearchCV(estimator, param_grid, *, factor=3, resource='n_samples',
    max_resources='auto', min_resources='exhaust', aggressive_elimination=False, cv=5,
    scoring=None, refit=True, error_score=nan, return_train_score=True, random_state=None,
    n_jobs=None, verbose=0)
```

Search over specified parameter values with successive halving.

### `HalvingRandomSearchCV` <sub>class</sub>

```python
HalvingRandomSearchCV(estimator, param_distributions, *, n_candidates='exhaust', factor=3,
    resource='n_samples', max_resources='auto', min_resources='smallest',
    aggressive_elimination=False, cv=5, scoring=None, refit=True, error_score=nan,
    return_train_score=True, random_state=None, n_jobs=None, verbose=0)
```

Randomized search on hyper parameters.

### `ParameterGrid` <sub>class</sub>

```python
ParameterGrid(param_grid)
```

Grid of parameters with a discrete number of values for each.

### `ParameterSampler` <sub>class</sub>

```python
ParameterSampler(param_distributions, n_iter, *, random_state=None)
```

Generator on parameters sampled from given distributions.

### `RandomizedSearchCV` <sub>class</sub>

```python
RandomizedSearchCV(estimator, param_distributions, *, n_iter=10, scoring=None, n_jobs=None,
    refit=True, cv=None, verbose=0, pre_dispatch='2*n_jobs', random_state=None, error_score=nan,
    return_train_score=False)
```

Randomized search on hyper parameters.

## Post-fit model tuning

### `FixedThresholdClassifier` <sub>class</sub>

```python
FixedThresholdClassifier(estimator, *, threshold='auto', pos_label=None, response_method='auto')
```

Binary classifier that manually sets the decision threshold.

### `TunedThresholdClassifierCV` <sub>class</sub>

```python
TunedThresholdClassifierCV(estimator, *, scoring='balanced_accuracy', response_method='auto',
    thresholds=100, cv=None, refit=True, n_jobs=None, random_state=None, store_cv_results=False)
```

Classifier that post-tunes the decision threshold using cross-validation.

## Model validation

### `cross_val_predict` <sub>function</sub>

```python
cross_val_predict(estimator, X, y=None, *, groups=None, cv=None, n_jobs=None, verbose=0,
    params=None, pre_dispatch='2*n_jobs', method='predict')
```

Generate cross-validated estimates for each input data point.

### `cross_val_score` <sub>function</sub>

```python
cross_val_score(estimator, X, y=None, *, groups=None, scoring=None, cv=None, n_jobs=None,
    verbose=0, params=None, pre_dispatch='2*n_jobs', error_score=nan)
```

Evaluate a score by cross-validation.

### `cross_validate` <sub>function</sub>

```python
cross_validate(estimator, X, y=None, *, groups=None, scoring=None, cv=None, n_jobs=None,
    verbose=0, params=None, pre_dispatch='2*n_jobs', return_train_score=False,
    return_estimator=False, return_indices=False, error_score=nan)
```

Evaluate metric(s) by cross-validation and also record fit/score times.

### `learning_curve` <sub>function</sub>

```python
learning_curve(estimator, X, y, *, groups=None, train_sizes=array([0.1  , 0.325, 0.55 , 0.775,
    1.   ]), cv=None, scoring=None, exploit_incremental_learning=False, n_jobs=None,
    pre_dispatch='all', verbose=0, shuffle=False, random_state=None, error_score=nan,
    return_times=False, params=None)
```

Learning curve.

### `permutation_test_score` <sub>function</sub>

```python
permutation_test_score(estimator, X, y, *, groups=None, cv=None, n_permutations=100,
    n_jobs=None, random_state=0, verbose=0, scoring=None, params=None)
```

Evaluate the significance of a cross-validated score with permutations.

### `validation_curve` <sub>function</sub>

```python
validation_curve(estimator, X, y, *, param_name, param_range, groups=None, cv=None,
    scoring=None, n_jobs=None, pre_dispatch='all', verbose=0, error_score=nan, params=None)
```

Validation curve.

## Visualization

### `LearningCurveDisplay` <sub>class</sub>

```python
LearningCurveDisplay(*, train_sizes, train_scores, test_scores, score_name=None)
```

Learning Curve visualization.

### `ValidationCurveDisplay` <sub>class</sub>

```python
ValidationCurveDisplay(*, param_name, param_range, train_scores, test_scores, score_name=None)
```

Validation Curve visualization.
