# Metadata routing

`skore.evaluate` accepts `estimator`, `X`/`y` **or** `data`, and
`splitter`. It does **not** take `groups=` or other `split()`
kwargs. The locked cross-validator lives on the DataOp X marker.
Evaluate omits `splitter=` so skore reuses that `cv` and any
`split_kwargs`.

An omitted `splitter=` is an 80/20 holdout only when the marker
has no `cv`. That is the holdout lock (`translation.report` is
`EstimatorReport`). Confirm signatures with
`python -m skore_skills api get`.

This document routes cross-validation metadata only. Custom metric
kwargs such as `sample_weight` follow
`references/custom-metrics.md`; never put them in `split_kwargs`.

skrub `mark_as_X`:
https://skrub-data.org/stable/reference/generated/skrub.DataOp.skb.mark_as_X.html

## Where the object sits

Build attaches `cv` after the learner graph exists.

| Lock | On `mark_as_X` |
|---|---|
| `KFold` | `cv=KFold(n_splits=...)`, empty `split_kwargs` |
| `GroupKFold` | `cv=GroupKFold(n_splits=...)`, `split_kwargs={"groups": ...}` |
| `scheme` `date_time` | the project-local date splitter, timestamps in `split_kwargs` |
| holdout | no `cv` |

A time series lock is the date-based class in the time series
section of `build-ml-pipeline/references/custom-splitter.md`.

skrub requires `cv=` whenever `split_kwargs` is set. `cv=<int>` is
not a splitter.

```python
report = skore.evaluate(
    build_learner(),
    data={"data_dir": str(DATA_DIR)},
)
```

Passing `splitter=` overrides `cv` and drops `split_kwargs`.

## Traps

- `mark_as_X(split_kwargs=...)` without `cv=` — skrub raises at
  construction.
- `mark_as_X(cv=5, split_kwargs={"groups": ...})` — not a splitter.
- `evaluate(..., splitter=...)` when the cv is on the DataOp —
  the extra kwargs are dropped.
- A locked cv missing from the marker — return to
  `build-ml-pipeline`.
