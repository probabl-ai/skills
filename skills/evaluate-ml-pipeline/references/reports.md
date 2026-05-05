# Report escalation

`skore.evaluate(...)` is the default entry point. It returns the
right report class based on the inputs (single learner vs. list, CV
vs. no CV). Escalate to an explicit report class only when you need
something the dispatcher doesn't expose.

| Need                                          | Use                       | Why                                   |
|-----------------------------------------------|---------------------------|---------------------------------------|
| One score / one report, default metrics       | `evaluate(learner, X, y, cv=...)` | One call, no boilerplate              |
| Per-fold predictions / per-fold artifacts     | `CrossValidationReport(...)` | Holds fold-level objects              |
| Single fit on a held-out set (no CV)          | `EstimatorReport(...)`    | Skips the fold loop                   |
| Side-by-side of ≥ 2 learners                  | `ComparisonReport([...])` | Aligned metric tables and plots       |

For exact signatures and what each report exposes (metrics,
inspection accessors, diagnostic plots), see `skore-api`.

## When NOT to escalate

- Don't use `EstimatorReport` to "speed up" CV — it scores one fit,
  which is a high-variance estimate. Use `evaluate` /
  `CrossValidationReport` for a robust score.
- Don't manually loop folds and aggregate scores — that's what
  `CrossValidationReport` does, with the right per-fold accounting.
- Don't reach for `ComparisonReport` for a single learner; the
  side-by-side machinery is overhead when there's nothing to
  compare.
