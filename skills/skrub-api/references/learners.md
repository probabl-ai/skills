# Learners & hyperparameter tuning

Materialize a DataOps plan into something that can be `fit` / `predict` / `score`'d, and search over hyperparameter choices declared with `choose_*`. See `references/data_ops.md` for the underlying `DataOp` API.

## Learners

### class `SkrubLearner`
```python
from skrub import SkrubLearner
```
**Signature:** `SkrubLearner(data_op)`

Learner that evaluates a skrub `DataOp`. Built from a plan via `data_op.skb.make_learner()` or directly. Implements the sklearn estimator interface (`fit`, `predict`, `score`, `transform` where applicable).

### class `ParamSearch`
```python
from skrub import ParamSearch
```
**Signature:** `ParamSearch(data_op, search)`

Wraps a `DataOp` together with a sklearn search object (e.g. `GridSearchCV`, `RandomizedSearchCV`) to tune hyperparameters declared with `choose_*` inside the plan.

### class `OptunaParamSearch`
```python
from skrub import OptunaParamSearch
```
**Signature:** `OptunaParamSearch(data_op, n_iter=10, scoring=None, n_jobs=None, refit=True, cv=None, verbose=0, pre_dispatch='2*n_jobs', random_state=None, error_score=nan, return_train_score=False, storage=None, study_name=None, sampler=None, timeout=None)`

Hyperparameter search over a `DataOp` plan using Optuna (TPE/CMA-ES samplers etc.).

## Cross-validation

### function `cross_validate`
```python
from skrub import cross_validate
```
**Signature:** `cross_validate(learner, environment, *, keep_subsampling=False, cv=None, **kwargs)`

Cross-validate a learner built from a `DataOp`. `environment` is a dict mapping variable names (as declared via `var(...)`) to actual values. Extra `**kwargs` are forwarded to `sklearn.model_selection.cross_validate`.

## Hyperparameter primitives (used inside plans)

These build placeholder values that `ParamSearch` / `OptunaParamSearch` will iterate over.

### function `choose_from`
```python
from skrub import choose_from
```
**Signature:** `choose_from(outcomes, *, name=None)`

A choice among several possible outcomes. `outcomes` may be a list (positional) or a dict (named).

### function `choose_bool`
```python
from skrub import choose_bool
```
**Signature:** `choose_bool(*, name=None, default=True)`

A choice between `True` and `False`.

### function `choose_int`
```python
from skrub import choose_int
```
**Signature:** `choose_int(low, high, *, log=False, n_steps=None, name=None, default=None)`

A choice of integers from `[low, high]`. Set `log=True` for log-uniform sampling, `n_steps` to discretize.

### function `choose_float`
```python
from skrub import choose_float
```
**Signature:** `choose_float(low, high, *, log=False, n_steps=None, name=None, default=None)`

A choice of floating-point numbers from `[low, high]`.

### function `optional`
```python
from skrub import optional
```
**Signature:** `optional(value, *, name=None, default=value)`

A choice between `value` and `None`. Useful for "include this step or not" toggles.
