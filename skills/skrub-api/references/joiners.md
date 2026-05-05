# Joiners

Estimators (and one eager function) that augment a *main* dataframe with information from one or more *auxiliary* dataframes. All sklearn-compatible joiners take the auxiliary table at construction time and learn how to attach it to whatever main table is passed at `fit` / `transform`.

## Fuzzy / approximate matching

### class `Joiner`
```python
from skrub import Joiner
```
**Signature:** `Joiner(aux_table, *, key=None, main_key=None, aux_key=None, suffix='', max_dist=inf, ref_dist='random_pairs', string_encoder=<HashingVectorizer pipeline>, add_match_info=True)`

Approximate (fuzzy) join estimator wrapping `fuzzy_join`.

### function `fuzzy_join`
```python
from skrub import fuzzy_join
```
**Signature:** `fuzzy_join(left, right, left_on=None, right_on=None, on=None, suffix='', max_dist=inf, ref_dist='random_pairs', string_encoder=<HashingVectorizer pipeline>, drop_unmatched=False, add_match_info=True)`

Eager fuzzy-join two dataframes: each row of `left` is joined to its nearest neighbor in `right`.

## Predictive (interpolation) join

### class `InterpolationJoiner`
```python
from skrub import InterpolationJoiner
```
**Signature:** `InterpolationJoiner(aux_table, *, key=None, main_key=None, aux_key=None, suffix='', regressor=HistGradientBoostingRegressor(), classifier=HistGradientBoostingClassifier(), vectorizer=TableVectorizer(high_cardinality=MinHashEncoder()), n_jobs=None, on_estimator_failure='warn')`

Join with a table augmented by machine-learning predictions.

## Aggregation joins

### class `AggJoiner`
```python
from skrub import AggJoiner
```
**Signature:** `AggJoiner(aux_table, operations, *, key=None, main_key=None, aux_key=None, cols=None, suffix='')`

Aggregate an auxiliary dataframe before joining it on a base dataframe.

### class `MultiAggJoiner`
```python
from skrub import MultiAggJoiner
```
**Signature:** `MultiAggJoiner(aux_tables, operations, *, keys=None, main_keys=None, aux_keys=None, cols=None, suffixes=None)`

Extension of `AggJoiner` to multiple auxiliary tables.

### class `AggTarget`
```python
from skrub import AggTarget
```
**Signature:** `AggTarget(main_key, operations, *, suffix='_target')`

Aggregate a target `y` before joining its aggregation on a base dataframe.

## Key-argument convention

All joiners accept either:
- `key=...` for a single column name shared by both tables, **or**
- `main_key=...` and `aux_key=...` for distinct names on each side.

The two forms are mutually exclusive.
