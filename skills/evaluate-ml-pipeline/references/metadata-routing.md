# Metadata routing: `mark_as_X` → splitter

`.skb.mark_as_X(split_kwargs={...})` (set during pipeline declaration)
attaches per-row metadata that travels with X through fold splits.
The keys in `split_kwargs` map directly to the keyword arguments of
the splitter's `split(X, y, **split_kwargs)` call.

skrub reference for the build-time API:
https://skrub-data.org/stable/reference/generated/skrub.DataOp.skb.mark_as_X.html

## Build-time contract

In `build-ml-pipeline`, the user attaches metadata at the X marker:

```python
X = data.drop([...]).skb.mark_as_X(
    split_kwargs={"groups": data["customer_id"]},
)
y = data["target"].skb.mark_as_y()
```

The DataOp `data["customer_id"]` is split alongside X at fold time —
fold `i` gets the slice of `groups` that matches the slice of X.

Multiple keys are fine if the splitter consumes more than one
metadata column (rare). Most splitters take at most one.

## Eval-time contract

When you build a splitter at evaluation time, its `split()` signature
must accept the keys you put in `split_kwargs`:

Some splitters are listed for completeness but are discouraged on
methodological grounds — see `cross-validation.md` § "Avoid" before
picking (stratified variants and `LeaveOne*Out` family).

| Splitter                              | Required `split_kwargs` keys |
|---------------------------------------|------------------------------|
| `KFold`                               | none                         |
| `GroupKFold`                          | `groups`                     |
| `TimeSeriesSplit`                     | none (data must be ordered)  |
| `RepeatedKFold`                       | none                         |
| `ShuffleSplit`                        | none                         |
| `GroupShuffleSplit`                   | `groups`                     |
| `StratifiedKFold` *(avoid)*           | none                         |
| `StratifiedGroupKFold` *(avoid)*      | `groups`                     |
| `LeaveOneGroupOut` *(avoid)*          | `groups`                     |
| `LeavePGroupsOut` *(avoid)*           | `groups`                     |
| Custom splitter                       | whatever you declared        |

Pass the splitter via `cv=...` to `skore.evaluate` /
`CrossValidationReport`. The framework forwards the metadata
automatically — you don't pass `groups=` yourself at evaluation time.

## Mismatch errors

If the splitter expects `groups` but the X marker doesn't carry one,
sklearn raises `ValueError: The 'groups' parameter should not be
None.` at fold time. Resolution:

1. Return to `build-ml-pipeline` and add
   `split_kwargs={"groups": data[col]}` at the X marker.
2. If no group column exists in the data, switch to a splitter that
   doesn't require groups (the user may have over-specified the
   structure).

## When `split_kwargs` is missing entirely

The X marker can be created without `split_kwargs` (the default is
no metadata). At evaluation time:

- If you can confirm with the user that the data has no group
  structure and no temporal ordering, default to `KFold` /
  `StratifiedKFold`.
- If you cannot confirm, return to `build-ml-pipeline` and ask the
  user before picking a splitter. Do not silently default — it
  produces optimistic scores when group structure exists.
