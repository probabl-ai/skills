# Cross-validation taxonomy

When to pick which sklearn splitter. Symbols and exact signatures
live in `sklearn-api` — this file is the methodology, not the API
reference.

## Decision tree

1. **Time ordering matters** (forecasting, leakage from future to
   past)? → **Ask the user two questions before picking a splitter**:

   a. Is `sklearn.model_selection.TimeSeriesSplit` sufficient, or do
      they want a custom splitter that uses the time column directly
      (purged windows, custom embargo, calendar-aware blocks,
      walk-forward with retraining)? See `custom-splitter.md` if
      they pick custom.
   b. Should the time column stay as a covariate, or be dropped from
      the feature matrix? Encoders can extract calendar / cyclic
      patterns from a timestamp; in some problems the absolute time
      is informative, in others it's just a sort key. The user's
      call.

   Stop here once those two answers are in.

2. **Group structure** (multiple rows per subject / session /
   customer / region)? → `GroupKFold`. Don't reach for the
   stratified variant — see "Avoid" below.

3. **Otherwise** (regression, classification — balanced *or*
   imbalanced — no groups, no time) → `KFold`. Use `RepeatedKFold`
   if the dataset is small and the score is noisy across folds.

## Avoid (methodological gotchas)

These splitters are in scikit-learn and they "work", but produce
misleading estimates more often than they help. Don't recommend them
by default.

### Stratified variants — `StratifiedKFold`, `StratifiedGroupKFold`, `StratifiedShuffleSplit`, `RepeatedStratifiedKFold`

Stratification forces each fold to match the overall class
proportions. The cost: it **reduces the across-fold variance of the
score by construction** — folds are deliberately made more similar to
each other than they would be under random sampling. The standard
deviation across folds becomes an under-estimate of the real
estimation uncertainty, which produces over-confident error bars and
over-confident A/B comparisons between models.

If class imbalance is so extreme that some `KFold` folds end up with
zero minority examples, the right fix is more data, fewer splits, or
a different evaluation protocol (e.g. bootstrap with explicit class
weighting) — **not** stratification.

### `LeaveOneOut`, `LeaveOneGroupOut`, `LeavePGroupsOut`

Each test fold is one row (or one group). The per-fold score is
extremely noisy, and aggregating across many such folds doesn't
recover a robust estimate — the variance of the estimator is high
even when the average looks tight. Use `KFold` (or `GroupKFold`)
with a moderate number of splits instead — typically 5 to 10.

If the user truly has only a handful of distinct groups (≤ ~20) and
wants to see per-group generalization, run a few folds of
`GroupKFold` and **report per-group scores** rather than aggregate
over a leave-one-group-out scheme — the aggregate hides the noise.

## Splitter entries

Each entry: when to pick, which `split_kwargs` keys it consumes.

### `KFold`

- **Pick when:** regression / classification (balanced or imbalanced)
  / no group / no time. The default for the boring case.
- **`split_kwargs`:** none.

### `GroupKFold`

- **Pick when:** rows are grouped; each group must stay entirely in
  train or test (e.g., one customer can't appear in both).
- **`split_kwargs`:** `{"groups": <Series of group keys>}`.

### `TimeSeriesSplit`

- **Pick when:** temporal ordering, *and* the user has confirmed
  (decision-tree step 1) that the sklearn implementation is
  sufficient. Use `gap=` to enforce an embargo between train and
  test windows.
- **`split_kwargs`:** none required (data must be ordered by time
  upstream — typically a sort step in the pipeline).
- **Companion question — always ask at this point:** keep the time
  column as a covariate, or drop it? Encoders may still extract
  calendar patterns from a timestamp; the user owns the call.

### `RepeatedKFold`

- **Pick when:** small dataset / noisy fold-to-fold score; multiple
  shuffles reduce variance of the score *estimate* by averaging over
  different partitions of the same data. This is legitimate variance
  reduction (different splits → independent samples of the score) —
  unlike stratification, which makes folds artificially similar.
  Cost scales linearly with repetitions.
- **`split_kwargs`:** none.

### `ShuffleSplit` / `GroupShuffleSplit`

- **Pick when:** very large dataset where exhaustive k-fold is
  wasteful, or a fixed train/test ratio per fold matters more than
  coverage.
- **`split_kwargs`:** none for `ShuffleSplit`; `groups` for
  `GroupShuffleSplit`.

## Common mistakes

- **`KFold` on grouped data.** Same subject ends up in train and
  test → optimistic score, real-world failure. Always check for
  group structure before defaulting to `KFold`.
- **`KFold` on time-ordered data.** Future leaks into past → useless
  forecast estimate. Use `TimeSeriesSplit`, not `KFold` with
  `shuffle=True`.
- **`StratifiedKFold` for imbalanced classification.** Hides
  variance — see "Avoid". Use `KFold` and accept that fold-to-fold
  variance reflects real estimation uncertainty.
- **`LeaveOneOut` for "more thorough" evaluation.** It's not more
  thorough; it's higher-variance. Use `KFold` with 5–10 splits.
- **Forgetting the time-column question.** When you pick
  `TimeSeriesSplit`, always ask whether to keep the timestamp as a
  feature or drop it.
