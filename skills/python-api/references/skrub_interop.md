# SkrubLearner + skore.evaluate — the interop pattern

*Workflow pattern (durable across library versions). For per-version
signatures of `skore.evaluate`, `Project`, the report classes, or
the `SkrubLearner` fit shape, see the workspace's
`scratch/api/<lib>/<version>/` cache populated by `python-api`
Shape 0/1/2/3.*

`skore.evaluate(...)` is a dispatcher: depending on the
`estimator`/`splitter` combination it returns an `EstimatorReport`,
a `CrossValidationReport`, or a `ComparisonReport`. Feeding it a
`SkrubLearner` (the learner returned by `make_learner()` on a skrub
DataOps graph) requires the **env-dict-style** fit shape, not the
sklearn-style `(X, y)`.

This doc spells out both shapes, when each applies, and how the
workspace's `experiments/01_baseline.py` uses the env-dict path.

## Two fit shapes — pick by estimator type

### Sklearn-style — `(X, y)` positional

For any estimator that fits via `estimator.fit(X, y)`:

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
import skore

X, y = make_classification(random_state=42)
report = skore.evaluate(LogisticRegression(), X, y, splitter=0.2)
```

`X` and `y` are passed positionally (or by keyword). `splitter` is
either a numeric `test_size`, a scikit-learn cross-validator, or
left at the default.

### Env-dict-style — `data={"<var>": ...}`

For a `SkrubLearner` (the only common case in this workspace), the
learner's `fit` method takes a **single mapping** keyed by the names
of the `skrub.var(name=...)` declarations in the DataOps graph:

```python
import skore
from load_forecast.pipeline import build_learner
from load_forecast.evaluate import splitter

learner = build_learner()  # binds skrub.var("data_dir")
report = skore.evaluate(
    learner,
    data={"data_dir": "/abs/path/to/data"},
    splitter=splitter,
)
```

`X` / `y` and `data` are **mutually exclusive** — pick the form that
matches your estimator. `SkrubLearner` only accepts `data`; calling
`skore.evaluate(skrub_learner, X, y)` raises.

## Why env-dict for SkrubLearner

The DataOps graph carries *named* source variables — `data_dir`,
`history_source`, `predict_grid`, `weather_source` — that get bound
at fit time. A sklearn-style `(X, y)` call only binds two unnamed
slots; it can't express "here's the path to the data directory, the
graph derives X and y from there". The env-dict is the natural
shape for source-bound variables.

The keys in `data={...}` must exactly match the `skrub.var(name)`
declarations in the graph. Common shapes:

| Graph root | env-dict |
|---|---|
| `skrub.var("data_dir")` | `data={"data_dir": "/path/to/data"}` |
| `skrub.var("X")`, `skrub.var("y")` | `data={"X": X_array, "y": y_array}` |
| `skrub.var("predict_grid")`, `skrub.var("history_source")` | `data={"predict_grid": grid, "history_source": "/path"}` |

For source-bound vars (paths), pass an absolute path — the same path
used for `learner.skb.preview()` if you set that up. See
`build-ml-pipeline/references/source-binding.md` for the source-vs-
materialized binding decision.

## What `evaluate` returns

The return type depends on `splitter`:

| `splitter` | Report type |
|---|---|
| `float` (e.g. `0.2`) or `None` | `EstimatorReport` — single train/test split |
| A scikit-learn cross-validator (`KFold`, `TimeSeriesSplit`, custom) | `CrossValidationReport` — multi-fold |
| Multi-key comparison | `ComparisonReport` |

Confirm the exact dispatch rules via `python-api`
(`inspect.signature(skore.evaluate)` + the docstring) against the
installed skore version — the dispatch table can evolve.

## Persisting to the Project store

Every report goes under a **stable key** in the workspace's
`skore.Project` so future runs can read it back (the
`audit-ml-pipeline` skill renders each report to a markdown
digest, and `iterate-from-skore` mines that digest for Backlog
candidates).

The Project init form depends on the workspace's `skore mode:`
decision (recorded in `JOURNAL.md` Status `Workspace decisions`;
gate owned by `organize-ml-workspace` § "G-SKORE-MODE"). Three
forms; pick the one matching the workspace:

```python
# local mode
project = skore.Project(
    name="load-forecast",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project.put("01_baseline", report)
```

```python
# hub mode
from skore import login
login(mode="hub")  # interactive on first run; cached after
project = skore.Project("<hub-workspace>/load-forecast", mode="hub")
project.put("01_baseline", report)
```

```python
# mlflow mode  (no login — auth is the MLflow server's concern)
project = skore.Project(
    name="load-forecast",            # MLflow experiment name
    mode="mlflow",
    tracking_uri="http://127.0.0.1:5000",  # recorded at G-SKORE-MODE
)
project.put("01_baseline", report)   # key = MLflow run name
```

- **Key convention**: file stem of the experiment script. Re-using
  the key in a later run overwrites the previous report — fork into
  a new experiment file if you want both. (In mlflow mode the key
  is the run name under the experiment.)
- **Local-mode `workspace=str(PROJECT_ROOT / "reports")`** — the
  on-disk directory where the Project store lives. Created on
  first `put`. **Not** a valid kwarg in hub or mlflow mode.
- **mlflow-mode `tracking_uri=`** — the MLflow tracking server URI
  (HTTP(S) server, `sqlite:///…`, or `file:./mlruns` backend).
  mlflow-only kwarg; no `login()`. `skore[mlflow]` extra required.
  Note: `project.delete(...)` is not implemented for mlflow-mode
  projects.
- **`name=`** — short, stable, per-workspace name. Local mode uses
  it directly; hub mode uses it after `<hub-workspace>/` as in
  `"<hub-workspace>/load-forecast"`; mlflow mode uses it as the
  experiment name. Set once at project bootstrap inside each
  experiment script's `skore.Project(...)` call (the agent reads
  the value from `experiments/01_baseline.py` when needed; there is
  no auto-discovery script).

## Reading back later

The skore Project keys reports by an internal id (a long hash), not by
the user-facing string key. To retrieve, `summarize()` first to get
the id:

```python
import skore

# Project init form follows the workspace's `skore mode:` decision.
# Local-mode form shown here; for hub mode see the previous section.
project = skore.Project(
    name="load-forecast",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
df = project.summarize().reset_index()
id_ = df[df["key"] == "01_baseline"]["id"].iloc[0]
report = project.get(id_)
report.metrics.summarize().frame()  # task-appropriate headline metrics
report.checks.summarize().frame()    # automated checks (passed / issue / tip)
```

`project.summarize()` returns a pandas DataFrame indexed by id with
columns: `key`, `date`, `learner`, `ml_task`, `report_type`,
`dataset` (hash), plus the per-metric `<metric>_mean` columns. The
exact columns evolve with skore; see `python-api` § skore.

## Worked example — `experiments/01_baseline.py`

This is the actual experiment script from the workspace:

```python
# %% [markdown]
# # Experiment 01 — Baseline (t+12 load forecast)

# %%
import skore

from load_forecast import PROJECT_ROOT
from load_forecast.evaluate import splitter
from load_forecast.pipeline import build_learner

# %% [markdown]
# ## Paths

# %%
DATA_DIR = PROJECT_ROOT / "data"

# %% [markdown]
# ## Project

# %%
project = skore.Project(
    name="load-forecast",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)  # local-mode form; see `organize-ml-workspace` § "G-SKORE-MODE" for hub

# %% [markdown]
# ## Learner

# %%
learner = build_learner(data_dir_preview=DATA_DIR)

# %% [markdown]
# ## Evaluate

# %%
report = skore.evaluate(
    learner,
    data={"data_dir": str(DATA_DIR)},
    splitter=splitter,
)
report  # bare line — jupytext-displays inline; no-op as a script

# %% [markdown]
# ## Persist

# %%
project.put("01_baseline", report)
```

Note the clean separation:

- **`data_dir_preview=DATA_DIR`** on `build_learner()` makes
  `learner.skb.preview()` work interactively; it does **not** affect
  what `evaluate` actually fits on.
- **`data={"data_dir": str(DATA_DIR)}`** is what `evaluate` uses to
  bind the source var at fit/CV time.
- **`splitter`** is the project's chosen cross-validator (the
  walk-forward splitter in `src/load_forecast/evaluate.py`).
- **No agent-only `print` calls** — inspection is the agent's
  scratch problem (see `python-api` § "`scratch/` conventions"),
  not the script's. The bare `report` line is jupytext display,
  not a debug print.

## When `evaluate` is too coarse — escalate

If the default `evaluate(...)` dispatch doesn't fit (you need
explicit `train_data=` / `test_data=` on `EstimatorReport`, or a
multi-key `ComparisonReport`), construct the report class directly.
Look up the signatures via `python-api` against the installed skore
version — the kwargs differ between `EstimatorReport` (uses
`train_data` / `test_data`) and `CrossValidationReport` (uses
`splitter`).

## Companion references

- `python-api/references/pre_mark_alignment.md` — the 3-layer
  DataOps pattern that produces the `SkrubLearner` consumed here.
- `build-ml-pipeline/references/source-binding.md` — when to use
  source-bound vars vs materialized `(X, y)` bindings.
- `evaluate-ml-pipeline` — the methodology side: cross-validator
  choice, default metrics, structural metadata (`split_kwargs`).
- `iterate-from-skore` — reads the audit digest at
  `scratch/audit/<stem>/audit.md` (produced by `audit-ml-pipeline`)
  and converts each `issue` / `tip` row from the report's
  `checks.summarize()` into a Backlog candidate, following the
  check's `documentation_url` for the mitigation.
