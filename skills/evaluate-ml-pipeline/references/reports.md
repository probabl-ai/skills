# Report escalation

`skore.evaluate(...)` is the default entry point. It returns the
report for this one learner. Escalate to an explicit report class
only when you need something the dispatcher doesn't expose.

| Need                                          | Use                       | Why                                   |
|-----------------------------------------------|---------------------------|---------------------------------------|
| One score / one report, default metrics       | `evaluate(learner, data={...})` | One call, no boilerplate. Omit `splitter=`. |
| Per-fold predictions / per-fold artifacts     | `CrossValidationReport(...)` | Holds fold-level objects              |
| Single fit on a held-out set (no CV)          | `EstimatorReport(...)`    | Skips the fold loop                   |

For exact signatures and what each report exposes (metrics,
inspection accessors, diagnostic plots), see `python -m skore_skills api get`.

## When NOT to escalate

- Don't use `EstimatorReport` to "speed up" CV — it scores one fit,
  which is a high-variance estimate. Use `evaluate` /
  `CrossValidationReport` for a robust score.
- Don't manually loop folds and aggregate scores — that's what
  `CrossValidationReport` does, with the right per-fold accounting.
