# mlflow

Open-source platform for managing the ML lifecycle. **In this stack
mlflow is used only for model serving and the model registry** —
tracking is owned by `skore` (Project API), and evaluation /
reporting is owned by `skore` reports.

**Pick mlflow when:**
- You need to package a fitted model behind a stable interface
  (`mlflow.pyfunc`, `mlflow.sklearn`, `mlflow.pytorch`, etc.) so it
  can be loaded and called the same way regardless of the underlying
  framework.
- You need a model registry — versioned, named models with a clear
  promotion path (Staging → Production).
- You need REST serving (`mlflow models serve` or
  `mlflow.deployments`) to expose a model as an HTTP endpoint without
  hand-rolling Flask / FastAPI.

**Pick something else when:**
- The task is **tracking** (params, metrics, artifacts, run
  comparison) → use `skore`'s Project API. Don't reach for
  `mlflow.log_param` / `mlflow.log_metric` / `mlflow.start_run`.
- You only need to evaluate a model and produce a report → use
  `skore`'s `EstimatorReport` / `CrossValidationReport` /
  `ComparisonReport`.
- The model is consumed in-process and never served over the wire —
  `joblib.dump` is enough.

**Operational notes:**
- mlflow has two halves: a **server** (registry + serving) and the
  **client library** that packages and pushes models. They can be the
  same process for local use, or split with a remote server URI for
  shared use.
- The user's project may have mlflow in a separate environment —
  check before assuming it's installed alongside the modelling code.

**Pair with:**
- `skore` Project API — store the fitted estimator and its evaluation
  in skore during development; promote the *registered* version into
  mlflow once it's ready to be served.
- `joblib` (transitively via sklearn) — `mlflow.sklearn.log_model`
  uses joblib under the hood for sklearn estimators.
