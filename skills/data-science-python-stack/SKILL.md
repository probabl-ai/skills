---
name: data-science-python-stack
description: >
  Opinionated Python stack for data-science / ML work — one library
  per job, organized into tiers (mandatory / user choice / optional /
  transitive). SKILL.md is the index; per-library
  `references/<library>.md` files carry scope, "pick this when" /
  "pick something else when", and pairings.

  TRIGGER when (any of these):
  (1) **a library import fails** in this stack's domain — the answer
  is install, not substitute (see § "Missing dependency");
  (2) **a library choice has to be made** — explicitly (the user asks
  "which library for X?") or implicitly (code is about to introduce a
  new dependency, or the project is being scaffolded and the tabular
  library hasn't been picked yet);
  (3) starting a new Python data-science / ML project;
  (4) the user or current code reaches for a substitute outside the
  stack (xgboost, lightgbm, black, isort, flake8, poetry, hatch), or
  reaches for `mlflow` to log params/metrics, or for `cross_val_score`
  + handwritten reporting — redirect: tracking → `skore` Project API,
  evaluation / reporting → `skore` report classes, `mlflow` stays
  only for model serving / registry.

  SKIP when: the project is non-Python; the work is web / backend /
  infra unrelated to data science; the library is already chosen and
  installed and the task is implementation inside it (bug fix, feature
  work, refactor) with no new dependency in play.

  HOW TO USE: **read this SKILL.md end-to-end before recommending or
  installing anything** — picking from a single index entry hides the
  tier (whether the library is mandatory, a user-choice, optional, or
  already transitively present) and the pairings, and both matter.
  Then read the linked `references/<library>.md` for the chosen
  library's scope and tradeoffs. Don't silently substitute one library
  for another; if no entry fits, surface the gap to the user.
---

# Data Science Python Stack

Opinionated stack — one library per job, organized into four tiers:

1. **Mandatory** — installed at project start, no exceptions.
2. **User choice (tabular library)** — ask the user; one option must
   be picked.
3. **Optional** — install only when the project's task requires it.
4. **Transitive** — already pulled in by the mandatory tier; do not
   install explicitly, but know they're available.

## When to invoke this skill

Two events trigger this skill before any other action:

1. **A library import fails** in the stack's domain. The answer is
   install (see § "Missing dependency" below), never substitute.
2. **A library choice has to be made** — for tabular data at project
   start, or any time code is about to introduce a new dependency
   (deep learning, model serving, notebooks, …).

In both cases, **read the whole SKILL.md before deciding**. The tier
structure below determines whether a library should already be
present, needs a user prompt, or is opt-in — that decision can't be
made from a single index entry.

## Missing dependency — install, do not substitute

When code in this stack needs a library but `import` fails, the answer
is **install it**, not substitute. Specifically:

- Surface the missing dependency to the user with the exact install
  command. **Invoke `python-env-manager` to detect the project's
  environment manager (pixi / uv / poetry / hatch / conda / pip+venv)
  and produce the right install command** — don't infer the manager
  from memory; the project may not use the default. **Stop and wait
  for confirmation before doing anything else.**
- Do **not** rewrite the code to use a non-stack equivalent
  (`sklearn.Pipeline` for `skrub`, `cross_val_score` + handwritten
  metric prints for `skore`. Substitution silently breaks the contract
  that the workflow skills (`build-ml-pipeline`,
  `evaluate-ml-pipeline`, `organize-ml-workspace`) rely on.
- This rule **overrides** "make the code run". If the user prefers a
  substitute, they will say so — until they do, install. Reaching
  for a substitute because the dependency is missing is the most
  common way the stack gets silently undone, so treat the missing
  import as a hard stop.

## How to use this skill

1. Read this whole SKILL.md before picking — the tier structure
   determines whether the library should already be installed, needs
   a user-choice prompt, or is opt-in.
2. Match the task to an entry in the right tier.
3. Read the linked `references/<library>.md` for the chosen library's
   scope and tradeoffs before introducing it.
4. Install via `pixi` by default. If the project already uses a
   different manager (pip+venv, uv, conda), follow that instead.
5. Don't substitute libraries silently. If no entry fits the task,
   surface the tradeoff to the user.

## Tier 1 — Mandatory (install at project start)

These four libraries are always installed in a data-science / ML
project. The first three co-own the modeling workflow:
scikit-learn provides the estimators, skrub provides the
data-cleaning + DataOps layer that sits before them, skore
evaluates the result and persists it as a project on disk. The
fourth, `ruff`, owns lint + format and is non-negotiable: every
project Claude touches should pass `ruff check`. Each is named
explicitly even when transitively present, because the workflow
skills (`build-ml-pipeline`, `evaluate-ml-pipeline`,
`python-code-style`) depend on them directly and should not
silently lose them if upstream packaging changes.

- [`scikit-learn`](references/scikit-learn.md) — tabular ML
  algorithms, preprocessing, model-selection helpers. Use
  `HistGradientBoosting{Classifier,Regressor}` instead of pulling in
  xgboost or lightgbm. **Evaluation, cross-validation reports, and
  model comparison are owned by `skore`** — don't inline
  `cross_val_score` / `classification_report` for analysis output.
- [`skrub`](references/skrub.md) — wrap custom dataframe operations
  in a sklearn-compatible computation graph that replays
  deterministically across train and test splits. Use for the
  data-cleaning + feature-engineering layer that sits before the
  sklearn pipeline.
- [`skore`](references/skore.md) — predictive-model evaluation built
  on top of scikit-learn (`evaluate`, `EstimatorReport`,
  `CrossValidationReport`, `ComparisonReport`) **and** experiment
  tracking via the Project API (`skore.Project(...)`,
  `project.put(...)`, `project.get(...)`). Replaces ad-hoc
  `cross_val_score` + handwritten metric printouts; replaces
  `mlflow` for tracking. Brings `numpy`, `pandas`, `matplotlib`,
  `seaborn`, `plotly`, `joblib`, and others transitively (see
  Tier 4) — so static *and* interactive plotting are available
  without any extra install.
- [`ruff`](references/ruff.md) — single-tool lint + format,
  replaces `black` / `isort` / `flake8` / `pydocstyle`. Install in
  the **same feature/env as the rest of the Tier 1 stack** so
  `pixi run ruff` works without extra activation. The
  configuration (rule selection, numpydoc convention, per-file
  ignores) and the rule "Claude runs ruff after generating code"
  are owned by the `python-code-style` skill, which also ships the
  canonical `ruff.toml` template.

## Tier 2 — User choice: tabular library

For tabular data the user picks the library their own code targets.
**Ask at project start; don't pick silently — but don't ship the
project without one of these.**

- **`pandas` (+ `pyarrow`)** — established tabular library; pyarrow
  is the recommended Parquet engine + Arrow-backed dtype backend.
  `pandas` is already pulled in by `skore` (Tier 4), so picking this
  option only requires explicitly adding `pyarrow` if Parquet IO is
  in scope. See [`pandas`](references/pandas.md) /
  [`pyarrow`](references/pyarrow.md). Pick this if the user has
  existing pandas code or no preference.
- **`polars`** — Arrow-native tabular library; faster on large
  frames, stricter type system. Requires an explicit install (it is
  not pulled in by anything in Tier 1). See
  [`polars`](references/polars.md). Pick this if the user wants the
  performance / typing properties or already uses polars elsewhere.

## Tier 3 — Optional (install on demand)

Add these only when the task calls for them. Do not pre-install.

### Deep learning

For NLP, computer vision, or any task where deep learning is the
right tool. None of these are mandatory; reach for them only when
the project's modeling task requires DL.

- [`pytorch`](references/pytorch.md) — tensor library with GPU /
  MPS support and autograd. Default deep-learning framework. Also
  the GPU alternative to numpy for raw numerical work.
- [`keras`](references/keras.md) — high-level, layer-oriented deep
  learning API. Multi-backend (runs on pytorch, TensorFlow, or
  JAX).
- [`skorch`](references/skorch.md) — wraps a PyTorch `nn.Module`
  so it behaves like a sklearn estimator (`fit` / `predict`,
  GridSearchCV, pipelines). Bridge between deep models and the
  sklearn API.

### Model serving

- [`mlflow`](references/mlflow.md) — model packaging, registry,
  and REST serving (`mlflow.pyfunc`, `mlflow models serve`). Use
  **only** for serving and registry concerns; tracking belongs to
  `skore`.

### Notebooks

For notebook-based work, prefer Python files with `# %%` cell
markers (jupytext percent format) over `.ipynb` files. Python
files are diffable and version-control friendly; jupytext handles
the conversion to/from notebook format when needed.

- [`jupyterlab`](references/jupyterlab.md) — browser-based
  notebook IDE; edits and runs notebooks (or jupytext-paired
  `.py` files). Brings `ipykernel` transitively.
- [`jupytext`](references/jupytext.md) — sync `.ipynb` ↔ `.py`
  (`# %%` markers) so the notebook source-of-truth stays
  version-control friendly.

### Testing

- [`pytest`](references/pytest.md) — testing.

## Tier 4 — Transitive (already pulled in; do not install explicitly)

These land in the env as runtime dependencies of the mandatory tier
(or of the chosen tabular library). Documented here so you don't
add a redundant explicit dependency, and so you know what's
available without an extra install.

- [`numpy`](references/numpy.md) — N-d arrays, numerical
  primitives. Pulled in by `scikit-learn` and `skore`.
- [`scipy`](references/scipy.md) — scientific computing on top of
  numpy (stats, optimize, sparse, signal). Supports the array API.
  Pulled in by `scikit-learn`.
- [`matplotlib`](references/matplotlib.md) — static plotting
  foundation. Pulled in by `skore` (via `seaborn`).
- [`seaborn`](references/seaborn.md) — static statistical plots
  (distributions, regression, faceting). Pulled in by `skore`.
- [`plotly`](references/plotly.md) — interactive plots (hover,
  zoom, pan); browser-based, suited for dashboards and exploratory
  notebooks. Pulled in by `skore` — **interactive viz is free, no
  extra install needed**.
- [`ipykernel`](references/ipykernel.md) — Python kernel for
  Jupyter. Pulled in by `jupyterlab` when the notebooks tier is
  installed.

## Conventions

- **Environment manager:** detection + install commands are owned by
  the `python-env-manager` skill — invoke it for any add / remove /
  upgrade. Default *recommendation* is `pixi`; if the project
  already uses a different manager (uv / poetry / hatch / conda /
  pip+venv), `python-env-manager`'s detection table picks it up
  and never substitutes one manager for another.
- **Versions:** don't pin unless the user asks or there's a known
  incompatibility. **Exception — `skore` and `skrub` must always be
  the latest available release.**
- **One tool per job:** don't introduce a second library for a task
  already covered without explicit user request. (One library *can*
  own multiple jobs — `skore` covers both evaluation and tracking.
  The rule forbids piling a second tool onto a covered job, not a
  single tool covering multiple jobs.)
- **Line width:** wrap text at 88 chars where natural. Don't compress
  content to fit; long inline links and code spans are fine to leave
  on longer lines.
