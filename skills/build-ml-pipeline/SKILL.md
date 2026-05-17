---
name: build-ml-pipeline
description: >
  Opinionated, Pythonic way to **declare** the pipeline that goes from
  a data source to a predictor: data loading, preprocessing, feature
  engineering, estimator selection, and their composition. The pipeline
  is built as a **skrub DataOps graph**; every step is either a
  pure-Python function (stateless) attached via `.skb.apply_func`, or
  a scikit-learn-compatible estimator (stateful) attached via
  `.skb.apply`. Stops at the declared object. Out of scope: `fit`
  invocation, train/test split, hyperparameter tuning, persistence,
  evaluation. Deep-learning declarations are covered via internal
  `references/*.md`; skrub and scikit-learn mechanics live in
  sibling skills.

  TRIGGER when: writing or editing code that declares any link in the
  chain *data source → predictor* — data readers/loaders feeding a
  model (`read_csv`, `read_parquet`, `Dataset` classes), preprocessing
  or feature-engineering steps (transformers, encoders, imputers,
  scalers, text/image featurizers), **pure-Python data-processing
  functions destined for the pipeline path** (a custom `def` that
  cleans/derives/reshapes data, whether wrapped via
  `FunctionTransformer`, skrub `@deferred` / `skrub.var` expressions,
  a sklearn-compatible custom transformer class, or simply called in
  the training path before the estimator), composition objects
  (`Pipeline`, `make_pipeline`, `ColumnTransformer`, `FeatureUnion`,
  skrub `tabular_learner`, `nn.Module` / `LightningModule`
  definitions), or an estimator instantiated as the tail of the chain;
  a step is added, removed, swapped, or reordered inside an existing
  pipeline declaration; a bare `sklearn.Pipeline` / `make_pipeline` is
  being used as the top-level pipeline (fire to redirect the
  declaration into a skrub DataOps graph instead); the user asks to
  build / declare / set up a pipeline / classifier / regressor for X.

  SKIP when: `.fit(...)` calls, training loops, `Trainer.fit`, epoch
  loops; train/test split or cross-validation splitting; hyperparameter
  search (`GridSearchCV`, Optuna, Ray Tune) — separate skill; model
  persistence (`joblib.dump`, `log_model`, checkpointing); evaluation,
  metrics, scoring, error analysis; inference / serving over a
  pre-trained model; pure EDA with no estimator downstream;
  library-choice questions with no concrete declaration in play (defer
  to `data-science-python-stack`).

  HOW TO USE: consult before the first declarative line and on every
  structural edit (added/swapped step, changed input columns, changed
  estimator family). Don't re-consult for cosmetic edits (renames,
  formatting). **First, read the "Stop conditions" block at the top
  of the body and emit the Pre-flight checklist as visible text in
  your response — both are mandatory before any code.** For
  deep-learning declarations specifically, read the relevant
  `references/*.md` inside this skill. For library mechanics, defer to
  the sibling skills rather than inlining detail here — in particular,
  **invoke `python-api` whenever you need to recall a skrub symbol
  (DataOps `.skb` methods, `skrub.var`, joiners, column selectors,
  etc.), and `python-api` whenever you need to pick a scikit-learn
  estimator / transformer / utility, confirm its import path, or check
  a signature**. Don't guess names from memory.
---

# Build ML Pipeline (Declaration)

Declarative shape of a Python ML pipeline from data source to predictor.

## Stop conditions — read before anything else

- **Missing dependency.** If `import skrub` raises in this project's
  env, STOP. **Invoke `python-env-manager`** to detect the
  manager and produce the right install command (the project may
  not use pixi); surface the command to the user and wait for
  confirmation. **Do not substitute with `sklearn.Pipeline` /
  `make_pipeline` / `FunctionTransformer`** — that silently rewrites
  this skill out of the project. See
  `data-science-python-stack` § "Missing dependency".
- **Symbol from memory is forbidden.** Any skrub or scikit-learn name
  you are about to type must come from a `Skill(python-api)` or
  `Skill(python-api)` call **in this turn**. "I remember the
  signature" is not acceptable — names drift between releases.
- **Splitter / cross-validator selection is out of scope here.** Do
  not import `KFold`, `StratifiedKFold`, `train_test_split`, or any
  splitter in pipeline code. That decision belongs to
  `evaluate-ml-pipeline`. The only CV-related thing this skill
  handles is wiring `split_kwargs` at the X marker (see rule 2).
- **Late `mark_as_X` is forbidden when any feature step has a
  cross-row dependency.** Unifying property: an operation is
  cross-row when its output for a row depends on values from
  rows other than that row itself. The common forms — backward
  shift, lag, rolling window, group-by / window aggregation
  spanning rows, target-shift, join with side history,
  filter-by-other-rows — are all the same shape from the
  marker's perspective; lags and rolling windows are self-joins
  with shifted / range keys, so don't be misled by syntax
  (`pl.col("x").shift(k)` is *not* per-row). The list is
  examples, not exhaustive — if a new step doesn't appear here
  but its output for a row reads from another row, the same
  rule applies. When any cross-row step is present,
  `mark_as_X` / `mark_as_y` must come **before** it, and the
  step must reference the relevant cross-row source as an
  additional `apply_func` argument (see rule 2). Otherwise
  predict-time replay on a fresh env-dict silently drops
  cold-start rows. Symptoms: `feature_steps=[]` toggle in the
  public API of `build_learner` to "make predict work for
  cold-start"; a temp-dir gymnastic at predict time to fake
  history; a wrapper estimator whose only job is to filter NaN
  rows the pipeline itself produced. All three are tells that
  `mark_as_X` is too late — fix the *graph topology*, do not
  paper over it. The `smoke-test-ml-pipeline` test is the
  executable proof that the topology is right; if that smoke
  test fails on row count, route back here.
- **Layer 1 doesn't know the question.** The source describes
  *what data exists*; the predict grid describes *which rows
  we want answers for, anchored to which times / keys*. Layer
  1 operates only on the former; anything that requires the
  latter — relating any pair of rows, picking which row is
  the target vs which is history, computing rolling / lag /
  horizon-shifted values, filtering by a condition produced
  from another row — is Layer 2 or downstream. This is the
  deeper principle behind the cross-row rule above: a
  cross-row operation can only be *evaluated* once the
  predict grid has been named, so it cannot live in Layer 1.

  **Constructive test** for any step you're tempted to put
  in the loader: *would an external consumer of the source —
  a SQL view, a feature store, a second model reading the
  same files — derive this same output, without knowing your
  task?* If yes → Layer 1. If the answer requires knowing
  which rows are "the rows we want predictions for" (or any
  horizon / lag / window relative to them), the step is
  Layer 2 or 3, never Layer 1.

  The "downstream graph is IID, smoke passes trivially"
  argument is the rationalization this rule blocks: when the
  question is fused into Layer 1, the smoke test passes by
  construction (no cross-row reaches downstream of the
  marker to break), the CV report looks fine (CV materializes
  the graph once), and the structural debt only surfaces
  when the next experiment tries to compose anything new
  against the raw source and discovers the loader has
  already baked in *this* experiment's framing.
- **Multi-line probes go to `scratch/`, not inline.** Any
  Python investigation longer than 2 lines lands in
  `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` (per the
  workspace's `scratch/README.md`), not in
  `pixi run python -c "..."`. The 2-line cap is contract;
  ignoring it defeats the traceability the scratch folder
  exists for. Common shapes that trigger this rule while
  declaring the pipeline: data-schema inspection, loader
  sanity checks, multi-step `inspect.signature(...)` walks
  across the skrub/sklearn surface. See `python-api`
  § "Scratch traceability" for the file layout.

## Pre-flight — emit this checklist as visible text before any code

Before writing or editing pipeline code, output the following block
verbatim in your response. Each box must be backed by an actual tool
call **in the same turn** — leave it unchecked otherwise, and stop
until you've made the missing call.

```
Pre-flight (build-ml-pipeline):
- [ ] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (per `data-science-python-stack` § "Tier 1")
- [ ] Tabular library identified: pandas | polars
      (informs the loader function and any frame-level ops; if not
       set yet, return to `organize-ml-workspace` and ask the user)
- [ ] Skill(python-api) consulted for: <symbols, or "none">
- [ ] Skill(python-api) consulted for: <symbols, or "none">
- [ ] Source-binding pattern chosen (one or more skrub.var roots —
      identifier(s) for raw history sources, plus identifier(s) for the
      predict-time-grid description if the pipeline has any
      history-dependent feature)
- [ ] X-marker placement decided:
        IID flat-table → directly on the loaded source frame; OR
        panel / time-series / cold-start → on the predict-time-grid
        node *before* any history-dependent featurization (lags,
        rolling windows, target shifts, side-table joins by
        time/group). See rule 2 for the early-mark pattern.
- [ ] Per history-dependent feature step: takes the X DataOp as its
      first argument **and** the upstream history DataOp(s) as
      additional argument(s); the history is referenced, not bound
      to X.
- [ ] Layer 1 audit — for every `apply_func` upstream of `mark_as_X`,
      apply the constructive test: "would an external consumer of
      the source derive this same output, without knowing my task?"
      If no for any step, that step is Layer 2 — push it out of the
      loader into a stateful aligner with `mark_as_X` on its outputs.
- [ ] If a probe is needed in this turn (data shape, loader sanity
      check, symbol discovery beyond a one-liner), the payload goes
      to `scratch/<ts>_<short>.py`, not inline `pixi run python -c
      "..."`. The 2-line cap is the only inline allowance.
- [ ] Preview value handling decided: `build_learner` exposes
      `<source>_preview` as an optional keyword (caller passes an
      absolute path, typically `<pkg>.PROJECT_ROOT / ...`); no
      relative-path literal baked into `pipeline.py`
- [ ] split_kwargs at the X marker decided (groups / time / none)
- [ ] Smoke test wired: `tests/smoke/test_NN_<short_name>.py` exists
      and passes (per `smoke-test-ml-pipeline`); if the pipeline
      has no history-dependent step, the smoke test still exists
      but its assertions are trivial.
```

Filling in `none` for the API skills is only acceptable when no
external symbol is being introduced (e.g., a pure structural edit).
If you find yourself wanting to fill in `none` because you "already
know" the name, that's a Stop-condition violation — go consult.

> **Companion skill (planned): `review-ml-pipeline`** — methodological
> review of an existing declaration (leakage audit, statelessness check,
> step ordering, scope creep). When `review-ml-pipeline` flags a
> problem, return here to fix it: this skill owns the *how* of
> corrections; the review skill owns the *what's wrong*.

## Scope

- **In scope:** how the pipeline *object* is composed in Python — data
  source wiring, preprocessing/feature steps, estimator at the tail, and
  the composition objects that hold them together.
- **Out of scope:** fitting, splitting, tuning, persisting, evaluating —
  those have (or will have) their own skills.

## Core rules

1. **Skrub DataOps is the pipeline entry point.** Declare the pipeline
   as a skrub DataOps graph rooted at one or more `skrub.var(...)`
   calls — not as a bare `sklearn.Pipeline`. See
   https://skrub-data.org/stable/data_ops.html. The `skrub.X(...)` /
   `skrub.y(...)` shortcuts are **not** acceptable roots; see rule 2
   for why. **Consult the `python-api` skill** to confirm the symbol
   you want exists and matches the signature you're about to write —
   don't guess from memory.

2. **Mark X early — on the description of "rows we want
   predictions for". Featurize after.**

   The marker is the **shared-vs-predict-specific boundary** of
   the graph. Everything *upstream* of `mark_as_X` runs
   identically at fit and at predict time on whatever sources
   are bound — raw history, side tables, the predict-grid
   description. Everything *downstream* of it is per-
   prediction-slice work on the X-side. The placement question
   reduces to two questions: **what has to be the same at fit
   and at predict?** (that stays upstream); **what describes
   which rows we want answers for?** (that's where the marker
   lands).

   The deciding test for *where* the marker goes is one
   question: **does any feature step look at rows other than
   the one currently being processed?** Backward lags, rolling
   windows, group-by aggregations that span rows, joins with
   auxiliary history tables, target derivations that pull from
   a row elsewhere — these are all cross-row dependencies, and
   they're all the same shape from the marker's perspective.
   (Lags and rolling windows are self-joins with a shifted /
   range key; a target shift + `drop_nulls` is a self-join with
   `t + horizon` plus an inner-join filter. Don't be fooled by
   syntax — `pl.col("x").shift(k)` and a self-join produce the
   same row-set dependency.)

   - **Yes, there is at least one cross-row step** → the marker
     must come *upstream* of every cross-row step, and each
     such step must reference the relevant cross-row source via
     a node that bypasses the marker. The three-layer model
     below is the canonical way to express this.
   - **No cross-row step at all** (per-row math, type casts,
     stateful encoders that learn at fit and apply per-row at
     predict) → the marker can land anywhere; the IID example
     below is enough.

   The graph has three logical layers:

   - **Sources** (Layer 1) — one `skrub.var(...)` per input
     identifier: raw history file(s) / URL(s) / table name(s),
     side-table source(s), and — for time-series and cold-start
     panels — the *predict-time-grid description* (e.g. a
     `start` / `end` range, or a list of `(group_id, time)`
     tuples). The loader for each source is its first
     `.skb.apply_func`; loaders are pure functions of a single
     source identifier. **Do not load + featurize in one
     `apply_func`** — that fuses Layers 2 and 3 with the loader
     and breaks predict-time replay.
   - **Predict-time grid + alignment** (Layer 2) — a DataOp whose
     rows are exactly the rows we want predictions for. For IID
     flat tables this is the loaded source frame itself; for
     time-series / panel data it is the `target_time` grid (or
     `(group, time)` grid) derived from Layer 1's predict-time
     bounds. **`mark_as_X` and `mark_as_y` go here.** Target
     derivation that requires history (and `drop_nulls` on `y`)
     belongs to a small stateful `BaseEstimator` subclass with
     `fit_transform → {X, y}` / `transform → {X, y=None}`,
     attached at this layer. Putting that derivation in a
     pre-mark `apply_func` is the late-mark anti-pattern flagged
     in the Stop conditions.
   - **Feature engineering** (Layer 3) — `apply_func` chained on
     the X-branch *after* `mark_as_X`. History-dependent steps
     take the X DataOp as their first argument **and** the
     relevant Layer-1 source DataOp(s) as additional arguments;
     the history is *referenced*, not bound to X. The same
     history node materializes the full available history at
     fit time and at predict time, so a backward lag computed
     for a row in the predict-time grid sees real values from
     the train history — no cold-start NaN.

   The `skrub.X(...)` / `skrub.y(...)` shortcuts are still not
   acceptable roots (they bake the marker at the source and
   defeat Layer 1).

   **The preview value is an optional caller-supplied parameter,
   not a literal baked into `pipeline.py`.** `value=` controls what
   `learner.skb.preview()` sees during interactive iteration —
   nothing else. A literal like `value="data/train.parquet"`
   resolves against the **CWD at execution time**, which silently
   breaks every run that isn't started from the project root.
   Expose the preview as an optional keyword on `build_learner` and
   leave it `None` for production fit / cross-validate — the
   env-dict supplies the binding regardless.

   **IID flat-table example.** Layer 2 is the loaded source
   frame; the early-mark rule reduces to "split columns into X
   and y on the source frame, then chain features after". This
   is what the simple example below shows.

   ```python
   def build_learner(data_dir_preview: str | Path | None = None):
       data_dir = (
           skrub.var("data_dir", value=str(data_dir_preview))
           if data_dir_preview is not None
           else skrub.var("data_dir")
       )
       data = data_dir.skb.apply_func(load_parquet)

       X = data.drop(["id", "target"], axis=1).skb.mark_as_X()
       y = data["target"].skb.mark_as_y()

       X = X.skb.apply_func(feature_engineering_step)
       predictions = X.skb.apply(predictor, y=y)
       return predictions.skb.make_learner()
   ```

   **Counter-example — loader-baked target shift (Don't).**
   This is the rationalization the Stop condition "Layer 1
   doesn't know the question" blocks. The target shift in the
   loader assumes the framing *"we want to predict load
   HORIZON hours ahead"*; an external consumer of the source
   would derive the raw hourly series, not this output. The
   horizon belongs to **Layer 2** (the aligner, where the
   predict grid is named), never Layer 1.

   ```python
   # Don't.
   def load_supervised_frame(data_dir):
       raw = read_csvs(data_dir)
       # ↓ target shift — relates rows; requires knowing the horizon
       shifted = raw.with_columns(load.shift(-HORIZON).alias("y"))
       # ↓ drop_nulls on a shifted column — filter by cross-row result
       return shifted.drop_nulls("y")

   data = data_dir.skb.apply_func(load_supervised_frame)
   X = data.drop("y").skb.mark_as_X()   # marker is "early" only on paper
   y = data["y"].skb.mark_as_y()
   ```

   The trap: the smoke test in `tests/smoke/` passes trivially
   (the downstream graph is IID, so there are no cross-row
   reaches downstream of the marker to break), and the CV
   report looks fine — which feels like a green light. But the
   next experiment that adds lagged-load features against the
   raw hourly history cannot compose with this loader, because
   the loader has already collapsed the source into a single
   horizon-specific materialization. Fix it by pushing the
   shift into the Layer-2 aligner shown below.

   **History-dependent example (early-mark with upstream
   reference).** Layer 1 has at least *two* roots — one or more
   raw history sources, plus a `predict_grid` describing the
   rows we want predictions for (a time range, a list of group
   IDs, a `(group, time)` set — whatever shape the problem
   requires). Layer 2 produces an aligned `{X, y}` from those
   roots — for the `y` side, the recipe varies (a join, a target
   shift, a label lookup); the worked example below shows the
   join-based pattern, and
   `python-api/references/pre_mark_alignment.md` carries the full
   3-layer walkthrough drawn from this workspace's 01_baseline.
   Layer 3's history-dependent feature step takes the
   X DataOp *and* the raw history DataOp, and the feature
   function joins real values onto every row in the predict grid.

   ```python
   def build_learner(predict_grid_preview=None, history_source_preview=None):
       predict_grid = (skrub.var("predict_grid", value=predict_grid_preview)
                       if predict_grid_preview is not None
                       else skrub.var("predict_grid"))
       history_source = (skrub.var("history_source", value=history_source_preview)
                         if history_source_preview is not None
                         else skrub.var("history_source"))

       # Layer 1: raw history, no shifts, no drops
       history = history_source.skb.apply_func(load_history)

       # Layer 2: align predict_grid + history into (X, y).
       # `align_xy` is a small stateful BaseEstimator: fit_transform
       # returns {X, y}; transform returns {X, y=None}. The pre-mark
       # alignment pattern is described in the skrub DataOps user
       # guide — WebFetch the docs for the installed skrub version
       # if you need the worked example.
       aligned = skrub.as_data_op(
           {"predict_grid": predict_grid, "history": history}
       ).skb.apply(align_xy)
       X = aligned["X"].skb.mark_as_X()    # rows = the predict grid
       y = aligned["y"].skb.mark_as_y()

       # Layer 3: features AFTER mark_as_X. The feature function
       # takes the X DataOp and the upstream `history` DataOp;
       # the join inside it fills history-dependent values for
       # every row in the predict grid.
       features = X.skb.apply_func(add_history_features, history)
       predictions = features.skb.apply(predictor, y=y)
       return predictions.skb.make_learner()
   ```

   The `align_xy` shape (a small stateful estimator that
   produces `{X, y}` at fit and `{X, y=None}` at predict) is one
   way to encode Layer 2 — straightforward, lets `mark_as_X` /
   `mark_as_y` come immediately after. Other shapes work too
   (e.g. two parallel `apply_func` branches that each produce
   X-aligned rows from `predict_grid` + `history`, marked
   separately); pick whichever expresses the alignment most
   clearly for the data. For the underlying skrub DataOp /
   `mark_as_X` / `mark_as_y` signatures, look them up via
   `python-api` against the installed skrub version; the full
   end-to-end pattern (sources → align → features-after-mark) is
   captured in `python-api/references/pre_mark_alignment.md`,
   with concrete code from this workspace's 01_baseline.

   The experiment script supplies an absolute path, anchored on the
   package's `PROJECT_ROOT` (set up by `organize-ml-workspace` in
   `<pkg>/__init__.py`):

   ```python
   from <pkg> import PROJECT_ROOT
   DATA_DIR = PROJECT_ROOT / "data"

   learner = build_learner(data_dir_preview=DATA_DIR)
   report = skore.evaluate(
       learner, data={"data_dir": str(DATA_DIR)}, splitter=splitter,
   )
   ```

   The env-dict at fit / cross-validate time is one binding per
   source (`data={"data_dir": str(DATA_DIR)}`); swapping the source
   is a one-line change at the call site, with no edit to
   `pipeline.py`.

   **Note on the downstream evaluation contract.** A `SkrubLearner`
   does not implement sklearn's `fit(X, y)` signature — it takes a
   single environment dict. Pair it with
   `skore.evaluate(learner, data={"path": ..., ...}, splitter=...)`
   (or `data={"X": X, "y": y}` for a materialized binding) — never
   with `skore.evaluate(learner, X, y, ...)`, which raises. The
   `data=` argument is the env-dict-style equivalent of `X` / `y` on
   `skore.evaluate`, `CrossValidationReport`, and the
   `train_data=` / `test_data=` pair on `EstimatorReport`. See
   `evaluate-ml-pipeline` for the dispatch story; look up exact
   skore signatures via `python-api`.

   **Cross-validation metadata at the X marker.** If the data has
   group structure (subjects, sessions, customer IDs, repeated
   measures) or temporal ordering, attach the relevant column at
   the X marker via `.skb.mark_as_X(split_kwargs={...})`. The keys
   in `split_kwargs` map directly to the keyword arguments of the
   future cross-validator's `split(X, y, **split_kwargs)` (e.g.
   `groups`). See [`skrub.DataOp.skb.mark_as_X`][markx].

   ```python
   X = data.drop([...]).skb.mark_as_X(
       split_kwargs={"groups": data["customer_id"]},
   )
   ```

   **Ask the user when you can't tell from the data alone** whether
   such structure exists — name the suspect columns (anything ending
   in `_id`, columns called `subject` / `session` / `region`, or
   any `date` / `timestamp` for temporal ordering) and ask whether
   to wire them. Do not silently leave `split_kwargs` empty when
   group structure is plausible — that produces optimistic
   evaluations downstream. Choosing the splitter itself is owned by
   `evaluate-ml-pipeline`; this skill only ensures the metadata is
   wired in.

   [markx]: https://skrub-data.org/stable/reference/generated/skrub.DataOp.skb.mark_as_X.html

   The `skrub.X(...)` / `skrub.y(...)` shortcuts are not acceptable
   roots: they are literally
   `var("X", value).skb.mark_as_X()` and `var("y", value).skb.mark_as_y()`,
   which bakes in the variable name and the marker at the root and
   forces a pre-loaded, pre-split binding.

   When *editing* an existing pipeline that already binds materialized
   data (or uses the shortcuts), do not auto-rewrite. Surface the
   source-bound alternative and ask whether to refactor.

   Full catalogue (encouraged / discouraged / OK-but-offer-an-upgrade):
   `references/source-binding.md`.

3. **Every data modification is either a function or a
   sklearn-compatible estimator. Nothing else.** Two ways to attach it
   to the graph (via the `.skb` accessor):
   - `.skb.apply_func(fn)` — wraps a callable that transforms data.
   - `.skb.apply(estimator)` — wraps any scikit-learn-compatible
     estimator (a transformer in the middle, or the final predictor).

   **Prefer `.skb.apply_func` over `skrub.deferred`.** `deferred` is a
   third skrub primitive (it turns a plain Python callable into one
   that returns a `DataOp` when applied to `DataOp` arguments) and is
   *equivalent* to `.skb.apply_func` for unary stateless steps. Pick
   `.skb.apply_func` so the chain has one canonical attach syntax —
   the chained DataOp is always the function's first argument and the
   step reads top-to-bottom. Use `deferred` **only** when the callable
   must combine **multiple DataOps** at once (e.g. a custom join over
   two tables): `.skb.apply_func` only operates on the single chained
   DataOp and cannot express that. Even there, check first whether a
   skrub joiner (`Joiner` / `AggJoiner` / `MultiAggJoiner`, see Common
   patterns #3) already covers the case before reaching for
   `deferred`.

4. **Stateless → function. Stateful → estimator.** This is the *only*
   decision rule for picking between `apply_func` and `apply`:

   - **Stateless** — output for a row depends only on that row (and
     constants). No information borrowed across rows of the dataset.
     Examples: parsing a date column, dtype casts, `log1p`, substring
     extraction, ratio of two columns, row-wise arithmetic.
     → write a plain `def fn(X): ...` and attach with
     `.skb.apply_func`.

   - **Stateful** — the transform needs a statistic / vocabulary /
     learned parameters fitted on the **training** data and re-applied
     unchanged to the **test** data. Examples: mean/median imputation,
     standard scaling, one-hot or target encoding, PCA, any predictor.
     → use a sklearn estimator (built-in when one exists; otherwise a
     custom `BaseEstimator` / `TransformerMixin` subclass exposing
     `fit` + `transform` / `predict`) and attach with `.skb.apply`.
     **Before naming the estimator, consult the `python-api` skill**
     to confirm the import path and signature — don't guess.

   If a step would silently learn from the test set when called as a
   function, it is stateful — promote it to an estimator.

5. **Leakage rule.** Any computation that uses statistics learned from
   the data (means, medians, quantiles, vocabularies, target
   distribution) MUST be stateful. Calling such a computation as a
   plain function over the whole frame leaks the test set into
   training. Classic traps to call out by name:
   - target encoding (the encoder must `fit` on training y only),
   - target-aware or quantile-based imputation,
   - quantile binning / `KBinsDiscretizer(strategy="quantile")`,
   - any `OrdinalEncoder` / `LabelEncoder` whose categories come from
     the full dataset rather than from `fit` on training only,
   - vocabulary-building text tokenizers, TF-IDF, IDF weights.

   Litmus test: would this output change if I called it on the
   training subset alone vs. on the whole frame? If yes → stateful →
   `.skb.apply` with an estimator, never `.skb.apply_func` with a
   function.

## Decision flow for a new step

1. Does the operation only need the current row (and constants)?
   → **stateless** → pure Python function + `.skb.apply_func`.
2. Otherwise it must learn from training data and reapply on test data.
   → **stateful** → sklearn-compatible estimator + `.skb.apply`.

## Reproducibility mechanics — extending without breaking prior experiments

`iterate-ml-experiment` enforces a hard rule (Stop conditions §
"Prior experiments stay reproducible"): every `done` row in
`JOURNAL.md` History must remain runnable on `main` and produce
the same result. When the next iteration touches a shared
module under `src/<pkg>/` (`pipeline.py`, `features.py`,
`data.py`, `evaluate.py`), the default behavior must preserve
prior experiments' shape.

Three options, **picked by judgment** on the size and clarity
of the change. Don't pick mechanically — read the criterion
and choose.

### Option 1 — parametrize the existing function (with default-preserving flag)

Pick this when the change is **small and well-scoped**:
- a step appended at the end of a chain,
- a single conditional branch in the graph,
- a new stateless transform that adds columns but doesn't
  reshape the existing ones,
- the flag has an obvious default that matches prior behavior.

The flag's default must mirror what prior callers saw before
the change. Prior experiment scripts call the function
unchanged; the new experiment passes the flag.

```python
# Before:
def build_learner(data_dir_preview=None): ...

# After (parametrize for experiment 02):
def build_learner(
    data_dir_preview=None,
    *,
    include_calendar_features: bool = False,
):
    ...
    if include_calendar_features:
        X = X.skb.apply_func(add_calendar_features)
    ...
```

`experiments/01_baseline.py` is unchanged (uses default
`False`); `experiments/02_calendar_features.py` passes
`True`. The prior smoke test still calls `build_learner()`
and sees the baseline shape.

### Option 2 — add a new function called only from the new experiment

Pick this when the change **doesn't fit cleanly behind a flag**:
- a new estimator at the tail of the chain,
- a fundamentally different feature-engineering step that
  reshapes the graph (not just appends),
- option 1's function would grow ugly internal branching.

Pattern: keep the original (`build_learner`) for prior
experiments, add a new function for the new one. The two may
share helpers freely; only the entrypoint diverges.

```python
def build_learner(...): ...  # used by 01_baseline, 02, ...

def build_learner_with_quantile_head(...): ...  # used only by 04_quantile
```

### Option 3 — branch the module

Last resort. Pick this only when the change touches enough
internal structure that options 1 and 2 would obscure the
diff (the whole pipeline shape changes; the data loader has
to produce a different schema). Usually a signal of a deeper
layering issue worth surfacing to the user before cloning.

Pattern: copy `pipeline.py` to `pipeline_v2.py` (or a
descriptive name), edit freely. Prior experiments keep
importing the original. Document the split in the new
experiment's design-note Risks.

### Tripwires

- **3+ flags in one function.** When the same function ends up
  with `include_calendar_features=False, include_X=False,
  include_Y=False, ...`, the parametrization model is leaking.
  Reach for option 2 for the *next* feature.
- **Visible branching in the function body.** When the if-tree
  for the flags makes the function hard to read, reach for
  option 2.
- **A flag changes default behavior of an existing caller.**
  Stop. The rule is broken. Fix it: either keep the default
  preserving, or use option 2.

### Cheap executable check

`iterate-ml-experiment`'s § 3 smoke-test gate runs **all of
`tests/smoke/`**, not just the new experiment's test. If a
prior smoke test goes red after your change, default behavior
isn't preserving the prior experiment's shape — fix it before
declaring the new experiment ready to run.

## Common patterns

A short catalogue of how to express the recurring shapes of a complex
pipeline within the skrub DataOps graph. Look up exact symbols in
`python-api` / `python-api`; the patterns below tell you *which*
shape applies, not the precise signature.

1. **Heterogeneous columns (skrub answer to `ColumnTransformer`).**
   Use skrub column selectors with the `cols=` argument of
   `.skb.apply` to apply a transformer to a column subset. One
   `.skb.apply(...)` per group (numeric / string / categorical)
   instead of building a `ColumnTransformer`.

2. **Default starting point for tabular data.** Reach for
   `skrub.tabular_learner(...)` (or `TableVectorizer` + estimator)
   first. Specialize column-by-column only when the default is
   insufficient.

3. **Multi-table inputs.** Declare each input table as its own
   `skrub.var(...)`. Join with skrub's `Joiner` / `AggJoiner` /
   `MultiAggJoiner` via `.skb.apply(...)`. The graph holds the join
   plan deterministically across train and test.

4. **Meta-estimator at the tail.** `StackingClassifier`,
   `CalibratedClassifierCV`, `TransformedTargetRegressor`, etc., are
   regular sklearn estimators — wrap your predictor first, then
   attach the wrapped object with `.skb.apply` as the final step.

5. **Mark hyperparameter knobs in place.** Wrap values you want the
   tuning skill to search over with `skrub.choose_from` /
   `choose_int` / `choose_float` / `optional` directly inside the
   declaration. Don't import `GridSearchCV` here — the tuning skill
   owns search; this skill only exposes the knobs.

6. **Custom sklearn transformer.** Author one only when (a) no
   built-in fits and (b) the operation is stateful. Subclass
   `BaseEstimator` + `TransformerMixin`, implement `fit(self, X,
   y=None)` to learn state and `transform(self, X)` to apply it; add
   `get_feature_names_out` if downstream consumers need feature
   names. For a stateless op, write a function and use
   `.skb.apply_func` — don't author a transformer.

## Companion skills (read for the *how*)

This skill defines the shape and the stateless/stateful rule. For the
mechanics of the libraries themselves, defer to:

- **`python-api`** — authoritative lookup of scikit-learn's public
  API: what's exported from `sklearn.X`, class/function signatures,
  one-line summaries. **Invoke whenever you need to:**
  - pick the right estimator / transformer / metric / utility for the
    stateful step,
  - confirm an import path (`sklearn.preprocessing.X` vs.
    `sklearn.compose.X`),
  - check a constructor signature or parameter name before writing
    the call,
  - verify that a symbol is part of the public API at all.
  Don't guess sklearn names from memory — consult the skill first.
  **Cache hits first**: check `scratch/api/sklearn/<version>/`
  before WebSearching for narrative pages; cache new findings
  back there (per `python-api` Shape 0/3).
- **`python-api`** — authoritative lookup of skrub's public API:
  top-level estimators, joiners, the DataOps lazy-pipeline framework
  (`.skb` accessor methods, `skrub.var`), column selectors, datasets,
  configuration. **Invoke whenever you need to:**
  - confirm a DataOps method exists on `.skb` and recall its
    signature (e.g. `.skb.apply`, `.skb.apply_func`, `.skb.eval`,
    `.skb.cross_validate`, ...),
  - pick a skrub estimator / joiner / column selector for the
    pipeline,
  - find the import path of a skrub symbol,
  - check that a symbol is part of the public API at all.
  Don't guess skrub names from memory — consult the skill first.
  **Cache hits first**: check `scratch/api/skrub/<version>/`
  before WebSearching for narrative pages; cache new findings
  back there (per `python-api` Shape 0/3).
- **`evaluate-ml-pipeline`** — methodology for evaluating the
  declared pipeline: `skore.evaluate` as the entry point,
  cross-validator selection, metric defaults, report routing.
  **Defer all evaluation / cross-validation / metric decisions to
  it** — this skill stops at the declared object. Note the contract
  with rule 2's `split_kwargs`: structural metadata wired in here is
  what the evaluate skill consumes downstream.
- **`smoke-test-ml-pipeline`** — the executable proof of rule 2's
  early-`mark_as_X` requirement. The smoke test fits the
  declared learner on a portion of the real `data/` source and
  predicts on a *disjoint* portion that carries no pre-history
  buffer; the assertion is structural (`len(predictions) ==
  n_predict_grid_rows`). A correctly built pipeline passes
  trivially; a late-mark pipeline fails on row count. **If the
  smoke test fails, route back to this skill** to fix the graph
  topology — do not loosen the assertion or add a wrapper.
- **`test-ml-pipeline`** — router for `tests/`. The smoke test
  pairs 1:1 with the experiment script; layout is owned there.
- **`python-env-manager`** — detection + install commands for the
  project's environment manager (pixi / uv / poetry / hatch / conda
  / pip+venv). **Invoke whenever** the Stop condition on
  `import skrub` fires, or whenever any other dependency is missing
  from the env. Don't infer the manager or hand-craft the install
  command — that skill owns it.
- **`python-code-style`** — **must be invoked** after writing or
  editing `pipeline.py` / `features.py` / `data.py`. Running
  `pixi run ruff check` directly without invoking this skill
  silently drops the NumPyDoc docstring convention this stack
  expects: ruff's `D`-rules are satisfied by a one-line summary,
  but only the skill body teaches the parameter-shape-in-type-slot,
  `Parameters` / `Returns` / `Raises` sections, and the imperative
  one-line summary. Companion to (not substitute for) the inline
  ruff lookups via `python-env-manager`.
- **Deep-learning declarations** — PyTorch / Lightning / Keras shapes
  that plug in as the predictor. → `references/*.md` inside this
  skill (TBD).
