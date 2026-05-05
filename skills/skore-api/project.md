# Project management

`skore.Project` persists reports across runs and lets you browse them as a dataframe. Three storage backends — `local` (default), `hub`, `mlflow` — selected via the `mode` argument and configured by separate plugin packages (`skore-local-project`, `skore-hub-project`, `skore-mlflow-project`).

## Lifecycle

```python
from skore import Project, evaluate

project = Project("my-xp")                       # local mode by default
project.put("baseline-v1", report_a)             # report_a is an Estimator/CV report
project.put("baseline-v2", report_b)             # same key updates with history kept

summary = project.summarize()                    # Summary (DataFrame subclass)
report = project.get(some_id)                    # fetch a specific report by id
Project.delete("my-xp")                          # static method; not for mlflow mode
```

Constraint: a project is bound to a **single ML task**. The first `put` sets `project.ml_task`; subsequent reports must match.

`project.put` accepts both `EstimatorReport` and `CrossValidationReport`. Re-using a key keeps the previous version in history (the latest one is what `summarize` surfaces).

## The three modes

### Local (default)

```python
project = Project("my-xp", mode="local")           # implicit
project = Project("my-xp", workspace=Path("/tmp/wksp"))   # custom location
```

Persistence: a directory under the user cache dir (`~/Library/Caches/skore` on macOS, `~/.cache/skore` on Linux, `%LOCALAPPDATA%\skore` on Windows) — overridable via the `workspace` kwarg or `SKORE_WORKSPACE` env var. The same workspace can host multiple projects.

### Hub (skore hub)

```python
from skore import login, Project

login(mode="hub")                                # opens browser; or use API key
project = Project("acme/my-xp", mode="hub")      # name must be "<workspace>/<name>"
```

`login` configures in-memory credentials only (not persisted). Get an API key at https://skore.probabl.ai/account.

### MLflow

```python
project = Project("my-experiment", mode="mlflow",
                  tracking_uri="http://localhost:5000")
```

Reports are persisted as MLflow artifacts in runs under the experiment name. `login` is a no-op for this backend.

## Summary — filter and retrieve

`project.summarize()` returns a `Summary`, which is a `pandas.DataFrame` subclass with a few extras:

```python
summary = project.summarize()
summary.columns          # metadata + every metric: learner, ml_task, rmse, accuracy, …
summary.index            # MultiIndex of (position, id)

# Standard pandas filtering works:
top = summary.query("rmse < 67 and learner == 'LinearRegression'")

# Convert filtered rows back to reports:
reports = top.reports()                          # list of reports (default)
cmp     = top.reports(return_as="comparison")    # ComparisonReport
```

In Jupyter, the default rendering shows an interactive parallel-coordinates plot; the path you trace selects a query that `reports()` then materializes (`filter=True`, the default).

`reports()` is a thin layer over `project.get(id)` for every id in the index, so it's lazy in the sense that you only pay deserialization cost for reports you actually want.

## Typical workflow

```python
from skore import Project, evaluate

project = Project("titanic-baseline")

for name, model in candidate_models.items():
    report = evaluate(model, X, y, splitter=5)
    project.put(name, report)

# Later — or in a separate notebook:
summary = Project("titanic-baseline").summarize()
top3   = summary.nsmallest(3, "log_loss")
cmp    = top3.reports(return_as="comparison")
cmp.metrics.summarize().frame
cmp.metrics.roc().plot()
```

## Deleting a project

```python
Project.delete("my-xp")                          # local
Project.delete("acme/my-xp", mode="hub")         # hub
# Not implemented for mlflow.
```

## Files of interest

- `skore/src/skore/_project/project.py` — `Project` class.
- `skore/src/skore/_project/_summary.py` — `Summary` class.
- `skore/src/skore/_project/login.py` — `login` function.
- `skore-local-project/`, `skore-hub-project/`, `skore-mlflow-project/` — backend plugins.
