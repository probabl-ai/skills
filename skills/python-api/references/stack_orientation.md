# Stack orientation — sklearn / skrub / skore

Per-library surface map. Stable across versions; per-version detail
goes in `scratch/api/<lib>/<version>/`. Load this when the inline
orientation in `SKILL.md` doesn't name what you need.

## scikit-learn

- `sklearn.metrics` — scoring functions, both functional
  (`accuracy_score`, `roc_auc_score`, `mean_absolute_error`) and
  callable-via-`make_scorer`.
- `sklearn.preprocessing` — stateful scalers, encoders, imputers
  (`StandardScaler`, `OneHotEncoder`, `KBinsDiscretizer`).
- `sklearn.pipeline` / `sklearn.compose` — `Pipeline`,
  `make_pipeline`, `ColumnTransformer`, `FeatureUnion`.
- `sklearn.model_selection` — splitters (`KFold`, `GroupKFold`,
  `TimeSeriesSplit`, `train_test_split`) and search (`GridSearchCV`,
  `RandomizedSearchCV`).
- `sklearn.linear_model` / `sklearn.ensemble` / `sklearn.neighbors`
  / etc. — the estimators themselves.

When in doubt, Shape 2 on `sklearn` (top level is mostly submodule
re-exports) followed by `pkgutil.iter_modules(sklearn.__path__)`
finds the right submodule.

## skrub

- **Top-level helpers**: `tabular_pipeline`, `TableVectorizer`,
  `DatetimeEncoder`, `TextEncoder`, `StringEncoder`. Use these for
  tabular learners that pick reasonable defaults per column type.
- **DataOps**: the lazy-pipeline DSL lives in the `.skb` namespace
  on every node (`X.skb.apply`, `X.skb.apply_func`, `X.skb.mark_as_X`,
  `X.skb.mark_as_y`, `X.skb.make_learner`, `.skb.preview`,
  `.skb.full_report`). Sources / variables are `skrub.var(name, value=...)`
  and `skrub.as_data_op({...})`.
- **Selectors** for column-routing within `apply`:
  `skrub.selectors.{numeric, categorical, string, ...}`.

`dir(skrub)` for top-level; `dir(X.skb)` for the DataOp node API.

## skore

- **Evaluation entry point**: `skore.evaluate(estimator, X=None,
  y=None, data=None, *, splitter=..., ...)` — dispatcher, returns
  the right report type based on `splitter`. `X` / `y` for
  sklearn-style fits; `data={"<var>": value}` for env-dict-style
  (`SkrubLearner`).
- **Report types**: `EstimatorReport` (single train/test split),
  `CrossValidationReport` (CV), `ComparisonReport` (multi-key). All
  expose `.metrics` (with `.summarize().frame()` for the task-
  appropriate headline metrics), `.checks` (with
  `.summarize().frame()` for the automated `passed` / `issue` /
  `tip` walk — the surface `audit-ml-pipeline` renders and
  `iterate-from-skore` mines via the digest), and `.inspection`
  (for feature importance / coefficients where the estimator
  supports it).
- **Project**: `skore.Project(name, *, mode='local', **kwargs)`.
  `name=` is the bare project name in **all** modes; what changes is
  the companion kwarg:
  - **local** (default): `skore.Project(name="<project>",
    mode="local", workspace=str(PROJECT_ROOT / "reports"))`.
    `workspace=` points to the on-disk directory (`Path`/`str`);
    defaults to the OS **data** dir if omitted (e.g. macOS
    `~/Library/Application Support/skore`, Linux
    `~/.local/share/skore`). Reports persist locally; no account /
    login.
  - **hub**: `skore.login(mode="hub")` (interactive, first run only)
    then `skore.Project(name="<project>", mode="hub",
    workspace="<hub-workspace>")`. Here `workspace=` carries the
    **Skore Hub org/team identifier** (a `str`, not a directory —
    skore overloads the term across modes). Requires
    `pip install "skore[hub]"` and an account on
    https://skore.probabl.ai with access to the workspace.
  - **mlflow**: `skore.Project(name="<experiment>", mode="mlflow",
    tracking_uri="<uri>")`. `name=` is the MLflow experiment name;
    `workspace=` is not accepted. Requires
    `pip install "skore[mlflow]" "mlflow>=3"` (the explicit
    `mlflow>=3` pin is required — `skore[mlflow]` alone can resolve an
    unsupported mlflow 2.x).

  Read-only attributes: `name`, `mode`, `workspace` (`Path` for
  local, `str` for hub, `None` for mlflow), `tracking_uri` (`str`
  for mlflow, `None` otherwise).

  Methods (same surface across modes): `put(key, report)`,
  `get(id)` (**by id, not by `key`** — get the id from
  `summarize()`), `summarize()` (returns a pandas DataFrame indexed
  by id with columns including `key`, `learner`, `ml_task`,
  `report_type`, mean metrics, … — rows ordered ascending by
  `date`), and the static `Project.delete(name, *, mode, **kwargs)`
  (same per-mode kwargs as the constructor; implemented for all
  three modes incl. mlflow).

  Source: https://docs.skore.probabl.ai/stable/reference/api/skore.Project.html
  (skore 0.18.0). The mode choice for this stack's workspaces is
  owned by `organize-ml-workspace` § "G-SKORE-MODE"; the install
  variant per mode is owned by `python-env-manager` § "Tier 1
  install: skore variant per mode".

`dir(skore)` for top-level; `dir(report)` and
`dir(report.metrics)` for the report accessor surface.
