---
name: build-ml-pipeline
description: >
  Declare the pipeline from data source to predictor as a **skrub
  DataOps graph** (not as a bare `sklearn.Pipeline`). Every step is
  either a pure-Python function (stateless) attached via
  `.skb.apply_func`, or a sklearn-compatible estimator (stateful)
  attached via `.skb.apply`. Stops at the declared object — no fit,
  split, tuning, persistence, or evaluation.

  TRIGGER — any of:
  - Writing or editing code that declares any link in the chain
    *data source → predictor*: loaders, preprocessing, encoders /
    imputers / scalers, feature steps, composition objects
    (`Pipeline`, `ColumnTransformer`, skrub `tabular_pipeline`,
    `nn.Module`), or the final estimator.
  - A pure-Python data-processing function destined for the
    pipeline path (cleans / derives / reshapes) — whether wrapped
    via `FunctionTransformer`, `skrub.@deferred` / `skrub.var`,
    a custom `BaseEstimator` subclass, or just called in the
    training path before the estimator.
  - A step is added, removed, swapped, or reordered inside an
    existing pipeline declaration.
  - A bare `sklearn.Pipeline` / `make_pipeline` is being used as
    the top-level — fire to redirect into a skrub DataOps graph.
  - The user asks to build / declare / set up a pipeline /
    classifier / regressor for X.

  SKIP when: `.fit(...)` calls / training loops / `Trainer.fit` /
  epoch loops; train/test split or cross-validation splitting;
  hyperparameter search; persistence (`joblib.dump`, checkpointing);
  evaluation / metrics / scoring; inference over a pre-trained
  model; pure EDA; library-choice questions with no concrete
  declaration in play.

  HOW TO USE: consult before the first declarative line and on
  every structural edit (added/swapped step, changed input columns,
  changed estimator family). Don't re-consult for cosmetic edits.
  **First, read the Stop conditions and emit the Pre-flight
  checklist as visible text before any code.** Always invoke
  `python-api` to confirm skrub / sklearn symbol names and
  signatures before typing — don't guess from memory.
---

# Build ML Pipeline (Declaration)

Declarative shape of a Python ML pipeline from data source to
predictor.

## Stop conditions — read before anything else

- **Missing dependency.** If `import skrub` raises, STOP. Invoke
  `python-env-manager` for the right install command (the project
  may not use pixi). **Do not substitute with
  `sklearn.Pipeline` / `make_pipeline` / `FunctionTransformer`** —
  that silently rewrites this skill out of the project.
- **Symbol from memory is forbidden.** Any skrub / scikit-learn /
  skore name must come from a `python-api` lookup *this turn*.
  Recognition is not a lookup; names drift between releases.
- **Splitter selection is out of scope.** Don't import `KFold`,
  `StratifiedKFold`, `train_test_split`, or any splitter in
  pipeline code — that belongs to `evaluate-ml-pipeline`. The
  only CV-related thing this skill handles is wiring
  `split_kwargs` at the X marker (rule 2).
- **`skrub.X(...)` / `skrub.y(...)` are not acceptable as graph
  roots.** They are sugar for `var("X", value).skb.mark_as_X()`
  and `var("y", value).skb.mark_as_y()`, which (1) bake the
  marker at the source — defeating Layer 1 of rule 2; (2) force
  a pre-loaded, pre-split binding so the graph cannot be replayed
  at predict time against a fresh source identifier; (3) collapse
  the three-layer pattern even when the data has cross-row
  features, silently re-enabling the late-`mark_as_X` bug. When
  tempted, return to rule 2 and root on `skrub.var("<source>",
  preview)` instead.
- **Late `mark_as_X` is forbidden when any feature step has a
  cross-row dependency.** A step is cross-row when its output for
  a row depends on values from *other rows*. Common forms — all
  the same shape from the marker's perspective:
  - backward shift / lag,
  - rolling window,
  - group-by / window aggregation spanning rows,
  - target-shift (forward shift on `y`),
  - join with side history,
  - filter-by-other-rows (e.g. `drop_nulls` on a shifted column).

  Don't be misled by syntax — `pl.col("x").shift(k)` is a self-join
  with a shifted key, not per-row. When any cross-row step is
  present, `mark_as_X` / `mark_as_y` must come **before** it, and
  the step must reference the relevant cross-row source as an
  additional `apply_func` argument (rule 2's three-layer model).
  Otherwise predict-time replay drops cold-start rows silently.

  **Symptoms of late `mark_as_X`** (all tells that the topology is
  wrong, fix the *graph*, do not paper over):
  - a `feature_steps=[]` toggle in `build_learner` "to make predict
    work for cold-start";
  - a temp-dir gymnastic at predict time to fake history;
  - a wrapper estimator whose only job is to filter NaN rows the
    pipeline itself produced.

  The smoke test (`smoke-test-ml-pipeline`) is the executable proof
  that the topology is right; CV alone passes either shape.
- **Layer 1 doesn't know the question.** The source describes
  *what data exists*; the predict grid describes *which rows we
  want answers for*. Anything that requires the latter — any
  cross-row computation, any horizon / lag / window — is Layer 2
  or downstream, never Layer 1.

  **Constructive test for any step in the loader:** *would an
  external consumer of the source — a SQL view, a feature store,
  a second model — derive this same output, without knowing your
  task?* If yes → Layer 1. If knowing "which rows we want
  predictions for" is required → Layer 2 or 3.

  The "downstream graph is IID, smoke passes trivially" argument
  is the rationalization this rule blocks: when the task is fused
  into Layer 1, smoke passes by construction, CV looks fine, and
  the structural debt only surfaces when the *next* experiment
  tries to compose anything new against the raw source.
- **Multi-line probes go to `scratch/`, not inline.** Any Python
  investigation longer than 2 lines lands in
  `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` (per `python-api`
  § "Scratch traceability"), not in `pixi run python -c "..."`.
  The 2-line cap is contract.

## Pre-flight — emit before any code

Each ticked box requires an actual tool call this turn. Leave
unchecked otherwise.

```
Pre-flight (build-ml-pipeline):
- [ ] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (per `data-science-python-stack` § "Tier 1")
- [ ] Tabular library identified: pandas | polars
      (informs the loader; if not set, return to organize-ml-workspace)
- [ ] python-api consulted for skrub symbols: <symbols, or "none">
      Evidence: Read scratch/api/skrub/<v>/<topic>.md (this turn)
                | "n/a — no new skrub symbol this turn"
- [ ] python-api consulted for sklearn symbols: <symbols, or "none">
      Evidence: Read scratch/api/sklearn/<v>/<topic>.md (this turn)
                | "n/a — no new sklearn symbol this turn"
- [ ] Source-binding pattern chosen: one or more skrub.var roots
      (identifiers for raw history sources + predict-grid identifier
       when the pipeline has any history-dependent feature)
- [ ] X-marker placement decided:
        IID flat-table → directly on the loaded source frame; OR
        panel / time-series / cold-start → on the predict-grid node
        *before* any history-dependent featurization (lags, rolling
        windows, target shifts, side-table joins by time/group).
- [ ] Per history-dependent feature step: takes the X DataOp as its
      first argument **and** the upstream history DataOp(s) as
      additional argument(s) — history is referenced, not bound to X.
- [ ] Layer 1 audit — for every `apply_func` upstream of `mark_as_X`,
      apply the constructive test ("would an external consumer derive
      this without knowing my task?"). Any "no" → push it past the
      marker into Layer 2 or 3.
- [ ] Preview value handling: `build_learner` exposes `<source>_preview`
      as optional kwarg; caller passes an absolute path. No
      relative-path literal baked into `pipeline.py`.
- [ ] split_kwargs at the X marker decided: groups | time | none.
- [ ] Smoke test wired (`tests/smoke/test_NN_<short_name>.py`) — per
      `smoke-test-ml-pipeline`; trivial assertions if no history-dep.
```

`none` for the API skills is only acceptable when no external symbol
is being introduced. If you find yourself wanting to fill `none`
because you "already know" the name, that's a Stop-condition
violation — consult.

## Scope

- **In scope:** how the pipeline *object* is composed — source
  wiring, preprocessing/feature steps, estimator at the tail.
- **Out of scope:** fitting, splitting, tuning, persisting,
  evaluating — those have their own skills.

## Core rules

### Rule 1 — Skrub DataOps is the pipeline entry point

Declare the pipeline as a skrub DataOps graph rooted at one or more
`skrub.var(...)` calls — **not** as a bare `sklearn.Pipeline`. The
`skrub.X(...)` / `skrub.y(...)` shortcuts are not acceptable roots
(see Stop conditions). Look up the underlying signatures via
`python-api` against the installed skrub.

Reference: https://skrub-data.org/stable/data_ops.html

### Rule 2 — Mark X early; featurize after

The marker is the **shared-vs-predict-specific boundary**.
Everything *upstream* of `mark_as_X` runs identically at fit and at
predict on whatever sources are bound. Everything *downstream* is
per-prediction-slice work on the X-side.

**Where the marker goes — one question:** *does any feature step
look at rows other than the one currently being processed?*

- **Yes (lag / rolling / cross-row join / target-shift)** → marker
  must be *upstream* of every cross-row step; each such step
  references the cross-row source via a node that bypasses the
  marker. Use the **three-layer model** below.
- **No (per-row math, stateful encoders that learn at fit and
  apply per-row at predict)** → marker can land anywhere; the IID
  example covers it.

**The three logical layers:**

- **Layer 1 — Sources.** One `skrub.var(...)` per input
  identifier: raw history file(s) / URL(s) / table name(s), side
  tables, and — for time-series / cold-start panels — the
  *predict-time-grid description* (a `start`/`end` range, a list of
  `(group_id, time)` tuples). The loader for each source is its
  first `.skb.apply_func`; loaders are pure functions of a single
  source identifier. **Do not load + featurize in one
  `apply_func`** — that fuses Layers 2 and 3 with the loader and
  breaks predict-time replay.
- **Layer 2 — Predict-time grid + alignment.** A DataOp whose rows
  are exactly the rows we want predictions for. For IID flat
  tables this is the loaded source frame itself; for time-series
  / panel data it is the `target_time` grid (or `(group, time)`
  grid) derived from Layer 1's predict-time bounds. **`mark_as_X`
  and `mark_as_y` go here.** Target derivation that requires
  history (and `drop_nulls` on `y`) belongs to a small stateful
  `BaseEstimator` with `fit_transform → {X, y}` / `transform →
  {X, y=None}`, attached at this layer.
- **Layer 3 — Feature engineering.** `apply_func` chained on the
  X-branch **after** `mark_as_X`. History-dependent steps take the
  X DataOp as their first argument *and* the relevant Layer-1
  source DataOp(s) as additional arguments; history is
  *referenced*, not bound to X. The same history node materializes
  the full available history at fit and at predict, so a backward
  lag computed for a row in the predict grid sees real values
  from the train history — no cold-start NaN.

**Worked examples** (full code, IID + history-dependent +
counter-example): `references/layer_examples.md`. Also see
`python-api/references/pre_mark_alignment.md` for the
production-style three-layer walkthrough drawn from this
workspace's 01_baseline.

**Preview value is an optional caller-supplied parameter, not a
literal in `pipeline.py`.** `value=` controls what
`learner.skb.preview()` sees during interactive iteration —
nothing else. A literal like `value="data/train.parquet"` resolves
against CWD at execution time and silently breaks runs that
aren't started from the project root. Expose the preview as an
optional kwarg on `build_learner` and leave it `None` for
production fit / cross-validate.

**Downstream evaluation contract.** A `SkrubLearner` does NOT
implement sklearn's `fit(X, y)` signature — it takes an
environment dict. Pair with
`skore.evaluate(learner, data={"path": ..., ...}, splitter=...)`,
never with `skore.evaluate(learner, X, y, ...)` (which raises).
See `evaluate-ml-pipeline`; confirm signatures via `python-api`.

**Cross-validation metadata at the X marker.** If the data has
group structure (subjects, sessions, customer IDs, repeated
measures) or temporal ordering, attach the relevant column at
`.skb.mark_as_X(split_kwargs={...})`. Keys map to the
cross-validator's `split(X, y, **split_kwargs)` (e.g. `groups`).

```python
X = data.drop([...]).skb.mark_as_X(
    split_kwargs={"groups": data["customer_id"]},
)
```

**Ask the user when you can't tell from data alone** whether such
structure exists — name suspect columns (anything ending in
`_id`, columns called `subject` / `session` / `region`, any
`date` / `timestamp` for temporal ordering) and ask whether to
wire them. Don't silently leave `split_kwargs` empty when group
structure is plausible — that produces optimistic CV downstream.
Choosing the splitter itself is owned by `evaluate-ml-pipeline`;
this skill only wires the metadata.

When **editing** an existing pipeline that uses `skrub.X` /
`skrub.y` or binds materialized data: do not auto-rewrite.
Surface the source-bound alternative and ask whether to refactor.
Full catalogue: `references/source-binding.md`.

### Rule 3 — Every data modification is a function or an estimator

Two attach points via `.skb`:

- `.skb.apply_func(fn)` — wraps a callable that transforms data.
- `.skb.apply(estimator)` — wraps any sklearn-compatible estimator
  (transformer in the middle, or the final predictor).

**Prefer `.skb.apply_func` over `skrub.deferred`.** `deferred`
turns a plain callable into one that returns a `DataOp` when
applied to `DataOp` arguments; equivalent to `.skb.apply_func` for
unary stateless steps. Pick `.skb.apply_func` so the chain reads
top-to-bottom. Use `deferred` only when the callable must combine
**multiple DataOps** at once (e.g. a custom join over two
tables). Even there, check first whether a skrub joiner
(`Joiner` / `AggJoiner` / `MultiAggJoiner`) already covers it.

### Rule 4 — Stateless → function. Stateful → estimator.

The *only* decision rule for picking `apply_func` vs `apply`:

- **Stateless** — output for a row depends only on that row (and
  constants). No info borrowed across rows. Examples: parsing a
  date, dtype casts, `log1p`, row-wise arithmetic.
  → plain `def fn(X): ...` + `.skb.apply_func`.

- **Stateful** — needs statistics / vocabulary / learned
  parameters fit on the **training** data and re-applied unchanged
  to the **test** data. Examples: mean/median imputation, standard
  scaling, one-hot / target encoding, PCA, any predictor.
  → sklearn estimator (built-in or custom `BaseEstimator` /
  `TransformerMixin`) + `.skb.apply`.

If a step would silently learn from the test set when called as a
function, it is stateful — promote it.

### Rule 5 — Leakage rule

Any computation using statistics learned from the data (means,
medians, quantiles, vocabularies, target distribution) MUST be
stateful. Calling such a computation as a plain function over the
whole frame leaks test into training. Classic traps by name:

- target encoding (must `fit` on training y only),
- target-aware or quantile-based imputation,
- quantile binning / `KBinsDiscretizer(strategy="quantile")`,
- `OrdinalEncoder` / `LabelEncoder` whose categories come from
  the full dataset rather than `fit` on training only,
- vocabulary-building text tokenizers, TF-IDF, IDF weights.

**Litmus test:** would this output change if I called it on the
training subset alone vs the whole frame? If yes → stateful →
`.skb.apply` with an estimator, never `.skb.apply_func`.

## Decision flow for a new step

1. Does the operation only need the current row (and constants)?
   → **stateless** → pure Python function + `.skb.apply_func`.
2. Otherwise it must learn from training data and reapply on test.
   → **stateful** → sklearn-compatible estimator + `.skb.apply`.

## Reproducibility — extending without breaking prior experiments

`iterate-ml-experiment` enforces a hard rule: every `done` row in
`JOURNAL.md` History must stay runnable on `main` and produce the
same result. When touching a shared module under `src/<pkg>/`,
**default behavior must preserve prior experiments' shape**.

**Three options, picked by judgment** (full procedures + worked
examples: `references/reproducibility_mechanics.md`):

- **Option 1 — parametrize the existing function** (with a
  default-preserving flag). Pick when the change is small and
  scoped: a step appended at the end, a single conditional, a
  stateless transform that adds columns without reshaping
  existing ones. **The flag's default mirrors prior behavior.**
  Prior experiment scripts call the function unchanged; the new
  one passes the flag.

- **Option 2 — add a new function called only from the new
  experiment.** Pick when the change doesn't fit cleanly behind a
  flag: new estimator at the tail, a step that reshapes the
  graph, or Option 1 would grow ugly internal branching. Keep
  the original; add a sibling. Share helpers freely; only the
  entrypoint diverges.

- **Option 3 — branch the module.** Last resort. Only when the
  change touches enough internal structure that Options 1 and 2
  would obscure the diff. Usually a signal of a deeper layering
  issue worth surfacing to the user.

### Tripwires (load-bearing)

- **3+ flags in one function** → parametrization is leaking. Reach
  for Option 2 for the *next* feature.
- **Visible branching in the function body** that makes it hard
  to read → reach for Option 2.
- **A flag changes default behavior of an existing caller** →
  STOP. Rule broken. Either keep the default preserving, or use
  Option 2.

### Cheap executable check

`iterate-ml-experiment` § 3 smoke-test gate runs **all of
`tests/smoke/`**, not just the new one. A prior smoke test going
red after a change = default behavior not preserved. Fix before
declaring the new experiment ready.

## Common patterns

Short catalogue of recurring shapes. Look up exact symbols in
`python-api`; the patterns tell you *which* shape applies, not
the precise signature. Full catalogue with code:
`references/common_patterns.md`.

1. **Heterogeneous columns** — skrub column selectors with `cols=`
   on `.skb.apply` (one apply per group), not `ColumnTransformer`.
2. **Default starting point for tabular data** — reach for
   `skrub.tabular_pipeline(...)` or `TableVectorizer` + estimator
   first; specialize column-by-column only when default is
   insufficient.
3. **Multi-table inputs** — one `skrub.var(...)` per table; join
   with skrub `Joiner` / `AggJoiner` / `MultiAggJoiner` via
   `.skb.apply(...)`.
4. **Meta-estimator at the tail** — `StackingClassifier`,
   `CalibratedClassifierCV`, `TransformedTargetRegressor`. Wrap
   the predictor first, then attach via `.skb.apply` as the final
   step.
5. **Mark hyperparameter knobs in place** — wrap with
   `skrub.choose_from` / `choose_int` / `choose_float` / `optional`
   inside the declaration. Don't import `GridSearchCV` here; the
   tuning skill owns search.
6. **Custom sklearn transformer** — author only when (a) no
   built-in fits and (b) the operation is stateful. Subclass
   `BaseEstimator` + `TransformerMixin`. For a stateless op,
   write a function and use `.skb.apply_func`.

## Companion skills

- **`python-api`** — authoritative lookup of sklearn / skrub /
  skore public API. **Invoke whenever** you need to pick a symbol,
  confirm an import path, check a constructor signature, or
  verify a name is part of the public API. Don't guess from
  memory. Cache hits first via Shape 0.
- **`evaluate-ml-pipeline`** — owns `skore.evaluate`,
  cross-validator selection, metric defaults. **Defer all
  evaluation / CV / metric decisions to it** — this skill stops at
  the declared object. Note the contract with rule 2's
  `split_kwargs`: structural metadata wired here is what the
  evaluate skill consumes.
- **`smoke-test-ml-pipeline`** — executable proof of rule 2's
  early-mark requirement. Fits the learner on a portion of real
  `data/` and predicts on a *disjoint* portion with no
  pre-history buffer; assertion is structural
  (`len(predictions) == n_predict_grid_rows`). Correctly built
  pipeline passes trivially; late-mark fails on row count.
  **If smoke fails, route back here** — fix the topology, don't
  loosen the assertion.
- **`test-ml-pipeline`** — router for `tests/`. Smoke test pairs
  1:1 with the experiment script; layout is owned there.
- **`python-env-manager`** — detection + install commands. Invoke
  when `import skrub` raises or any dependency is missing.
- **`python-code-style`** — **must be invoked** after writing or
  editing `pipeline.py` / `features.py` / `data.py`. Direct
  `pixi run ruff check` skips the NumPyDoc docstring convention.
- **Deep-learning declarations** — `references/*.md` inside this
  skill (TBD).

## References (load on demand)

- `references/source-binding.md` — full catalogue of source-binding
  patterns (encouraged / discouraged / OK-but-offer-upgrade).
- `references/layer_examples.md` — worked code for the IID flat-table
  case, the loader-baked-shift counter-example, and the
  history-dependent three-layer pattern.
- `references/reproducibility_mechanics.md` — full Option 1/2/3
  procedures with code, plus the tripwire criterion.
- `references/common_patterns.md` — full catalogue of recurring
  pipeline shapes with code snippets.

> **Companion skill (planned): `review-ml-pipeline`** —
> methodological review of an existing declaration (leakage audit,
> statelessness check, step ordering, scope creep). When it flags
> a problem, return here to fix.
