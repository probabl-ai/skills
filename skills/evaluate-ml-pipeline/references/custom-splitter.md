# Custom cross-validator

Author a new splitter only when:

1. No sklearn built-in fits the structure of the problem (purged-and-
   embargoed time-series, blocked spatial, custom leave-out
   schemes), **and**
2. The user has confirmed they want a custom one.

Otherwise, prefer the sklearn built-in.

## Minimal contract

A scikit-learn-compatible splitter implements two methods:

```python
class MySplitter:
    def split(self, X, y=None, groups=None):
        # Yield (train_idx, test_idx) pairs as integer numpy arrays.
        # Indices are POSITIONS into X (0-based), not labels.
        ...

    def get_n_splits(self, X=None, y=None, groups=None):
        # Return the number of splits as an int — must match the
        # number of pairs `split` will yield.
        ...
```

Contract details:

- `split` is a generator (uses `yield`).
- The yielded arrays are integer positions, not boolean masks or
  labels.
- The two arrays in each pair must be disjoint; their union doesn't
  need to cover X (e.g. `LeavePOut` skips some rows).
- `get_n_splits(...)` is allowed to ignore its arguments if the
  count is fixed at construction time.

## Subclassing `BaseCrossValidator`

Optional but encouraged: subclass
`sklearn.model_selection.BaseCrossValidator` to inherit a sensible
`__repr__`, parameter validation, and the standard iteration
protocol. Implement `_iter_test_indices(self, X, y, groups)` and
`get_n_splits(...)`; the base class fills in `split`.

Look up the exact base class signature in `sklearn-api`.

## Wiring with `split_kwargs`

The splitter receives `split_kwargs` keys as kwargs to `split`. So if
the pipeline carries `split_kwargs={"groups": ...}`, the custom
splitter's `split(self, X, y, groups)` is called with that `groups`
value at fold time.

Add only the kwargs you need. Extra kwargs not declared in your
splitter's `split` signature will surface as a `TypeError` —
investigate which side has the mismatch (the X marker or the
splitter signature).

## When to deviate from `BaseCrossValidator`

If the splitter is fundamentally different from k-fold semantics
(probabilistic / overlapping folds, bootstraps), inheritance may not
help. Just satisfy the two-method contract directly.
