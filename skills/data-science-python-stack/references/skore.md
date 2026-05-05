# skore

> **Always install the latest `skore`.** The library ships breaking
> changes in minor versions (e.g. `report.id`, `data=` on `evaluate`,
> `splitter=` on `CrossValidationReport`); older versions silently
> diverge from the examples below and from `skore-api`. Use `skore =
> ">=<latest>"` as a floor; refresh the floor on every install.

Two responsibilities, one library:

1. **Evaluation & reporting** — analyse a fitted (or to-be-fitted)
   scikit-learn estimator and produce a structured report. The report
   is the single artifact you'd hand to a stakeholder or pin in a PR
   description.
2. **Experiment tracking (Project API)** — persist runs, params,
   metrics, fitted estimators, and reports as a structured project on
   disk.

In this stack, `skore` replaces `mlflow` for tracking and replaces
ad-hoc `cross_val_score` + handwritten metric printouts for
evaluation. `mlflow` is kept only for model serving / registry.

Docs: https://docs.skore.probabl.ai/stable/

## Evaluation & reporting

### Main entry point: `skore.evaluate`

`evaluate` is the canonical entry point. Reach for it first; drop down
to the report classes only when you need finer control.

```python
from skore import evaluate

report = evaluate(
    estimator, X, y, splitter=5,  # e.g. 5-fold CV
)
```

`evaluate` is a wrapper that builds and returns the appropriate report
object based on its arguments (e.g. a `CrossValidationReport` when
`splitter` is an integer or a sklearn splitter). The returned object
is what you inspect, plot, persist, or compare.

See: https://docs.skore.probabl.ai/stable/auto_examples/getting_started/plot_getting_started.html

### Underlying report classes (drop down when needed)

`evaluate` returns one of these; you can also construct them directly
when you need control beyond what `evaluate`'s arguments expose:

- **`EstimatorReport(estimator, X_train=..., y_train=..., X_test=..., y_test=...)`**
  (or `train_data={...}` / `test_data={...}` for a `SkrubLearner`) —
  one estimator on a held-out split. Metrics, diagnostic plots, and
  feature-level inspection through one API.
- **`CrossValidationReport(estimator, X, y, splitter=...)`**
  (or `data={"X": X, "y": y}` for a `SkrubLearner`) — one estimator
  under cross-validation; aggregates per-fold metrics into a single
  report object.
- **`ComparisonReport([report_a, report_b, ...])`** — compare multiple
  estimator or CV reports side by side; produces the table and plots
  you'd otherwise build by hand.

**Pick skore evaluation when:**
- You're producing analysis output anyone will consume after the run —
  notebook reader, PR reviewer, stakeholder.
- You're comparing more than one estimator and want the comparison
  organized, not glued together by hand.
- You want a single artifact that bundles metrics + plots + the
  estimator that produced them.

**Pick something else when:**
- You need a single scalar score in a tight inner loop (e.g. a tuning
  search) — `cross_val_score` is fine for that. Promote to skore once
  the result is being analysed or reported.

## Project API (experiment tracking)

```python
project = skore.Project("my_project")
project.put("baseline", report_or_estimator_or_metric)
project.get("baseline")
```

Use the Project API as the durable home for everything you produce:
fitted estimators, reports, params, metrics, plots. The project is a
directory on disk; commits naturally with the code.

**Pick skore Project API when:**
- You want tracking that doesn't require a server, a UI, or any
  network setup — just a folder.
- You want to keep the artifact and its evaluation report in the same
  place, retrievable by key.
- The project is single-user or small-team; the trade-off is no
  multi-user web UI like mlflow's.

**Pick something else when:**
- You need a multi-user remote tracking server with a shared web UI
  across collaborators — that's not skore's target. Surface the gap to
  the user before substituting.

## Pair with

- `scikit-learn` — skore reports take sklearn estimators directly.
  Authoring a report is the *evaluation* counterpart to authoring a
  pipeline.
- `mlflow` — once a tracked model is ready to be served, register and
  serve it via mlflow. **Develop & evaluate in skore, serve in
  mlflow.**
- `matplotlib` / `plotly` — skore plots respect the project's
  visualization choice; pick the backend per the visualization section
  in the index.
