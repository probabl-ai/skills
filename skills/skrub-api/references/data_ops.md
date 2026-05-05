# DataOps — lazy plan-building API

The DataOps framework lets you describe a multi-step pipeline (including joins, multiple inputs, and hyperparameter choices) by chaining operations on `DataOp` objects, then materialize the result as a `SkrubLearner`. See `references/learners.md` for `SkrubLearner` / `ParamSearch` / `cross_validate`.

## Variables

### function `var`
```python
from skrub import var
```
**Signature:** `var(name, value=NULL)`

Create a skrub variable representing an input to the plan. Pass `value=...` to bind a preview value (used at design time).

### function `X`
```python
from skrub import X
```
**Signature:** `X(value=NULL)`

Shortcut for `var("X", value).skb.mark_as_X()`.

### function `y`
```python
from skrub import y
```
**Signature:** `y(value=NULL)`

Shortcut for `var("y", value).skb.mark_as_y()`.

## DataOp class & helpers

### class `DataOp`
```python
from skrub import DataOp
```
**Signature:** `DataOp` (constructed indirectly via `var`, `X`, `y`, `as_data_op`)

Representation of a computation that can be used to build DataOps plans and learners.

The `.skb` namespace exposes the DataOps-specific methods (without it, attribute access is forwarded to the underlying value):

```
applied_estimator       apply                   apply_func
clone                   concat                  cross_validate
describe_defaults       describe_param_grid     describe_steps
description             draw_graph              drop
eval                    freeze_after_fit        full_report
get_data                get_vars                if_else
is_X                    is_y                    iter_cv_splits
iter_learners_grid      iter_learners_randomized
make_grid_search        make_learner            make_randomized_search
mark_as_X               mark_as_y               match
name                    preview                 select
set_description         set_name                subsample
train_test_split
```

Most user-facing entry points are `.skb.apply(...)`, `.skb.eval()`, `.skb.preview()`, `.skb.make_learner()`, `.skb.cross_validate(...)`, `.skb.mark_as_X()` / `.skb.mark_as_y()`.

### function `as_data_op`
```python
from skrub import as_data_op
```
**Signature:** `as_data_op(value)`

Wrap a concrete value as a `DataOp` that evaluates to it.

### function `deferred`
```python
from skrub import deferred
```
**Signature:** `deferred(func)`

Decorator/wrapper that turns a regular Python callable into one that returns a `DataOp` when applied to `DataOp` arguments.

> **Prefer `.skb.apply_func` for unary stateless steps.** `deferred` and `apply_func` are equivalent when the wrapped function takes a single `DataOp`; standardize on `apply_func` so the chain has one canonical attach syntax. Reserve `deferred` for callables that must combine **multiple `DataOp`s** at once (e.g. a custom multi-table merge), and check first whether a skrub joiner (`Joiner`, `AggJoiner`, `MultiAggJoiner`) already covers the case. The `build-ml-pipeline` skill owns the policy.

### function `eval_mode`
```python
from skrub import eval_mode
```
**Signature:** `eval_mode()`

Return the mode in which the DataOp is currently being evaluated (e.g. `"preview"`, `"fit"`, `"transform"`, `"predict"`). Useful inside `deferred` functions that need to behave differently at fit vs. transform time.
