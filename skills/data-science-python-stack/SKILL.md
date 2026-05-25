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

Opinionated stack — one library per job, organized into four tiers
plus an orthogonal **agent feature**:

1. **Mandatory** — installed at project start, no exceptions.
2. **User choice (competing-library jobs)** — multiple valid libraries
   for the same job; the user picks via `AskUserQuestion` before any
   import lands.
3. **Optional** — install only when the project's task requires it.
4. **Transitive** — already pulled in by the mandatory tier; do not
   install explicitly, but know they're available.
5. **Agent feature (orthogonal)** — deps that the *agent* uses to
   audit a workspace (`jupytext`, `ipykernel`, `nbconvert`), kept
   out of the production-shape runtime via a manager-specific
   scope. Install logistics owned by `python-env-manager` §
   "Agent feature"; consumed by `audit-ml-pipeline`.

## Stop conditions — read before naming any library

- **No silent pick on a competing-library job.** Whenever the stack
  offers two or more libraries for the same job (see § "Competing
  libraries — general rule" and the Tier 2 table), the user picks
  via `AskUserQuestion` before any `Write` that imports the library
  and before any install command runs. "Already pulled in
  transitively" / "user said 'quick'" / "the folder has no
  preference signalled" are **not** waivers. A silent pick is a
  Stop-condition violation, full stop.
- **No substitute when import fails.** When code in this stack needs
  a library but `import` fails, install it; do not rewrite to a
  non-stack equivalent (see § "Missing dependency"). The most
  common silent-rewrite path —
  `import skrub` fails → rewrite as `sklearn.Pipeline`,
  `import skore` fails → rewrite as `cross_val_score` —
  silently undoes the workflow skills' contract.
- **Harness-level "no clarifying questions" hints do NOT waive the
  competing-library `AskUserQuestion`.** The Tier 2 pick is an
  operating-contract gate, not a clarifying question. The same
  applies to user urgency phrasing: "quick baseline", "just do it",
  "go fast", "you pick", "whatever" do NOT resolve a competing-
  library gate. See § "Free-text resolution" in the general rule
  below for what *does* resolve a gate.
- **Post-hoc audit — required before ending the turn.** Before
  declaring the turn complete, verify each competing-library job
  invoked in this turn has either (a) an `AskUserQuestion` answer
  recorded this session, or (b) a matching row in
  `journal/JOURNAL.md` Status `Workspace decisions`. If any
  competing-library job ran without one of those, surface the
  non-compliance to the user explicitly as part of your final
  message — do not hide it.

## Forbidden shortcuts (observed in real traces)

| Shortcut | Why it feels right | Why it's wrong |
|----------|--------------------|----------------|
| `pandas` is already pulled in by `skore` → skip the Tier 2 ask | "Free" library, no install needed | Tier 2 is a *project-shape* decision (every `data.py` signature, every fixture); transitive presence is not a pick |
| User said "quick baseline" → assume `pandas` | Task urgency reads as permission | Urgency phrasing never waives a competing-library gate (Stop conditions above) |
| Folder has no existing tabular code → infer pandas | "No preference signalled" | Inference is a silent pick; the gate requires a structured ask or a recorded `JOURNAL.md` decision |
| One competing option requires a new `pixi add` → pick the "free" one | Avoids an install step | Install cost is not the criterion; project fit is |
| User picked `pytorch` last project → reuse without asking | Continuity is friendly | Each workspace records its own `Workspace decisions`; cross-project memory is forbidden |

## Competing libraries — general rule

This is the meta-rule that governs every "user choice" entry in
this skill. It applies to the Tier 2 table below and to any new
competing-library job added in the future. It also applies inside
Tier 3 when two optional libraries cover the same job (e.g.
`pytorch` vs `keras` as the deep-learning framework).

### The rule

Whenever the stack offers two or more libraries for the same job:

1. **`AskUserQuestion` before any import or install.** Use the
   options listed for the job in the competing-jobs table; do not
   editorialize the option labels.
2. **Persist the answer in `journal/JOURNAL.md` Status under
   `Workspace decisions`.** This block is immutable until the user
   explicitly pivots. On future sessions, **read Status first**;
   do not re-ask a recorded decision. The persistence contract
   lives in `iterate-ml-experiment`'s `JOURNAL.md` template — the
   `Workspace decisions` block is the source of truth for cross-
   session continuity.
3. **No silent default.** Even when one option is "free"
   (already pulled in transitively) and the other costs an
   install, never pick silently. The free option becoming the
   pick is fine; *the picking happens via `AskUserQuestion`*.

### Free-text resolution

A user message resolves a competing-library gate **only** if it
names one of the listed options for the job. Apply in priority
order:

- **Exact match** (case-insensitive, whitespace-trimmed) to an
  option label: resolves the gate. ("use polars", "let's go
  with pytorch", "pandas please" → resolved.)
- **Library named in a free-text intent** ("rewrite the loader
  in polars", "I want a keras model"): resolves the gate for
  that job.
- **No library named** ("make it fast", "you pick", "whatever",
  "no preference", "quick baseline"): does **NOT** resolve.
  Fall through to the structured `AskUserQuestion`.
- **"You pick" / "no preference" specifically** — surface the
  **default-on-no-preference** for the job (from the Tier 2
  table) and ask for confirmation. Never silently pick; never
  skip the confirmation step.

### Adding a new contested job

When a new job appears in the stack with two viable libraries,
add a row to the Tier 2 competing-jobs table. **Every row must
name an explicit `Default-on-no-preference`** — rows without one
are forbidden, because they re-create the silent-pick loophole
this rule exists to close. If a sensible default cannot be
named, the job does not belong in the table; surface the gap to
the user and pick per-project via a free-form `AskUserQuestion`.

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

These five libraries are always installed in a data-science / ML
project. The first three co-own the modeling workflow:
scikit-learn provides the estimators, skrub provides the
data-cleaning + DataOps layer that sits before them, skore
evaluates the result and persists it as a project on disk. The
fourth, `ruff`, owns lint + format and is non-negotiable: every
project Claude touches should pass `ruff check`. The fifth,
`pytest`, runs the smoke test that every approved experiment
must have per the `test-ml-pipeline` / `smoke-test-ml-pipeline`
contract — without pytest the smoke-test gate can't enforce
predict-time correctness, so pytest stays mandatory even when
no other tests have been written yet. Each is named explicitly
even when transitively present, because the workflow skills
(`build-ml-pipeline`, `evaluate-ml-pipeline`,
`python-code-style`, `test-ml-pipeline`) depend on them
directly and should not silently lose them if upstream packaging
changes.

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
- [`pytest`](references/pytest.md) — test runner for the
  smoke-test gate enforced by `test-ml-pipeline` /
  `smoke-test-ml-pipeline`. Every approved experiment must have a
  passing `tests/smoke/test_NN_<short_name>.py` before its row
  in `JOURNAL.md` can flip to `done`; pytest is what runs that
  test, so the dependency is non-negotiable even on workspaces
  that haven't authored any tests yet. Install in the **same
  feature/env as the rest of the Tier 1 stack**.

## Tier 2 — Competing-library jobs (user choice)

Jobs in this tier have **more than one valid library** in the
stack. The user picks via `AskUserQuestion` before any import or
install (see § "Competing libraries — general rule" above).
Recorded picks live in `journal/JOURNAL.md` Status `Workspace
decisions` and are read first on every subsequent session.

### Competing-jobs table

| Job | Options | Default-on-no-preference |
|-----|---------|--------------------------|
| Tabular dataframe | `pandas` (+ `pyarrow`), `polars` | `pandas` (free via skore) |
| Deep-learning framework | `pytorch`, `keras` (multi-backend) | `pytorch` |
| sklearn-compatible DL wrapper | `skorch` (pytorch-only), `keras` (sklearn-compatible API) | `skorch` |
| Static vs interactive plotting | `matplotlib` / `seaborn`, `plotly` | task-driven — ask which output shape the user wants |
| Model serving / registry | `mlflow.pyfunc` + registry, FastAPI + `joblib` | `mlflow` |

Per-option detail:

- **Tabular dataframe**
  - **`pandas` (+ `pyarrow`)** — established tabular library;
    pyarrow is the recommended Parquet engine + Arrow-backed
    dtype backend. `pandas` is already pulled in by `skore`
    (Tier 4), so the only explicit install for this option is
    `pyarrow` if Parquet IO is in scope. See
    [`pandas`](references/pandas.md) /
    [`pyarrow`](references/pyarrow.md).
  - **`polars`** — Arrow-native tabular library; faster on
    large frames, stricter type system. Requires an explicit
    install (not pulled in by anything in Tier 1). See
    [`polars`](references/polars.md).
- **Deep-learning framework**
  - **`pytorch`** — tensor library with GPU / MPS support and
    autograd. Default DL framework in the stack. See
    [`pytorch`](references/pytorch.md).
  - **`keras`** — high-level, layer-oriented DL API;
    multi-backend (pytorch / TensorFlow / JAX). See
    [`keras`](references/keras.md).
- **sklearn-compatible DL wrapper**
  - **`skorch`** — wraps a PyTorch `nn.Module` so it behaves
    like a sklearn estimator (`fit` / `predict`, GridSearchCV,
    pipelines). See [`skorch`](references/skorch.md).
  - **`keras`** — exposes a sklearn-compatible API directly
    via `keras.wrappers.SKLearnClassifier` /
    `SKLearnRegressor`. See
    [`keras`](references/keras.md).
- **Static vs interactive plotting** — both are already
  available transitively via `skore` (matplotlib, seaborn,
  plotly all land without an explicit install). The ask is
  *which output shape the user wants for this project*, not
  which install to run. Pick by output medium: static reports
  / papers / static skore reports → matplotlib + seaborn;
  interactive notebooks / dashboards → plotly.
- **Model serving / registry** — only relevant when the
  project's roadmap includes serving a trained model. Skip the
  gate entirely if serving is out of scope. When it is in
  scope, `mlflow` is the default (registry + REST out of the
  box); FastAPI + `joblib` is the lighter custom path.

### How a Tier 2 gate fires in practice

- **Project start (bootstrap).** Every Tier 2 job the project
  touches must have a pick recorded in `Workspace decisions`
  before the matching code is written. The tabular gate fires
  on every project; the others fire only when the project's
  roadmap brings them in scope.
- **Mid-project (new job comes into scope).** When a new Tier 2
  job becomes relevant (e.g. the project pivots to add a DL
  model), the gate fires *at that point*; the existing
  `Workspace decisions` block is amended with the new row.
- **Mid-project (user wants to pivot).** Tier 2 decisions are
  immutable *unless the user explicitly says so*. A pivot is a
  user-driven event; the skill never auto-pivots even if a
  newer library would obviously be a better fit.

## Tier 3 — Optional (install on demand)

Add these only when the task calls for them. Do not pre-install.

### Deep learning

For NLP, computer vision, or any task where deep learning is the
right tool. None of these are mandatory; reach for them only when
the project's modeling task requires DL.

**The *which library* pick (pytorch vs keras as framework, skorch
vs keras as sklearn-compatible wrapper) is a competing-library
job — owned by Tier 2.** This section only covers *when* to
reach for DL at all; the framework choice has its own row in the
Tier 2 competing-jobs table and fires an `AskUserQuestion` the
first time DL comes into the project's scope.

Per-library reference material:
- [`pytorch`](references/pytorch.md) — tensor library with GPU /
  MPS support and autograd; also the GPU alternative to numpy
  for raw numerical work.
- [`keras`](references/keras.md) — high-level, layer-oriented
  deep-learning API; multi-backend (pytorch / TensorFlow / JAX).
- [`skorch`](references/skorch.md) — wraps a PyTorch `nn.Module`
  so it behaves like a sklearn estimator (`fit` / `predict`,
  GridSearchCV, pipelines).

### Model serving

**The *which library* pick (`mlflow.pyfunc` vs FastAPI +
`joblib`) is a competing-library job — owned by Tier 2.** This
section only covers *when* serving is in scope.

Per-library reference material:
- [`mlflow`](references/mlflow.md) — model packaging, registry,
  and REST serving (`mlflow.pyfunc`, `mlflow models serve`).
  Use **only** for serving and registry concerns; tracking
  belongs to `skore`.

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

## Agent feature — orthogonal to the four tiers

The audit flow owned by `audit-ml-pipeline` needs an executable
notebook toolchain (`jupytext` + `ipykernel` + `nbconvert`) plus a
one-time kernel registration. These deps don't fit cleanly into
the four tiers above:

- They are **not Tier 1 mandatory** — workspaces that don't run
  audits never need them.
- They are **not Tier 2 user-choice** — there is no competing-
  library job; jupytext + nbconvert is the one toolchain that
  supports the two-step execution contract.
- They are **not Tier 3 optional** in the same sense as
  pytorch / mlflow — the audit flow is project-orthogonal
  tooling, not a modelling library.
- They are **not Tier 4 transitive** — nothing in Tier 1 pulls
  them in.

So they live in their own bucket: the **agent feature**, a
manager-scoped install that composes alongside (not replaces)
the data-science deps.

| Library | Role |
|---|---|
| `jupytext` | Converts `audit/<stem>.py` (percent format) to `.ipynb` for execution. Step 1 of the two-step path. |
| `nbconvert` | Executes the `.ipynb` against a named kernel and renders the result to markdown. Steps 2-3 of the two-step path. |
| `ipykernel` | Provides the IPython kernel that `nbconvert --ExecutePreprocessor.kernel_name=<kernel>` resolves against. Registered once per project. |

**Install + register: owned by `python-env-manager` § "Agent
feature".** That skill carries the per-manager composition table
(pixi features / uv groups / poetry groups / hatch envs / conda
envs / pip+venv extras) and the kernel-registration step (`python
-m ipykernel install --user --name <kernel>`).

**Consumed by `audit-ml-pipeline`.** When the audit skill fires
and the agent feature isn't present, it routes through
`python-env-manager`'s `G-AGENT-FEATURE` gate before proceeding.

**Not Tier 3 notebooks (despite overlap).** `jupyterlab` /
`jupytext` *can* be installed together when a user wants
interactive notebook editing. But the agent feature's purpose is
**non-interactive execution by the agent**, not interactive
editing by the user. Same library family, different deployment
shape: Tier 3 notebooks → user-facing JupyterLab + jupytext for
`.ipynb`↔`.py` round-tripping; agent feature → headless jupytext
+ nbconvert for the audit-execute pipeline. A workspace may have
both, neither, or only one.

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
