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

## Terms used in this skill

Read these once; they're referenced throughout.

- **X marker** — the `.skb.mark_as_X()` call that anchors the
  predict-time slice. Everything upstream runs identically at
  fit and predict; everything downstream is per-prediction work.
- **Predict grid** — the rows you want predictions for at predict
  time. For IID flat tables: the loaded frame itself. For
  time-series / panels: a `(group, time)` set.
- **Cold-start row** — a predict-grid row that has no in-slice
  history available (typical for lags at the start of the slice).
- **Predict-time replay** — re-binding the graph to a fresh source
  identifier at predict (e.g. `learner.predict({"data_dir": …})`).
- **Cross-row step** — a feature whose output for a row reads
  values from other rows (lag, rolling window, group aggregation,
  side-table join by time/group, drop_nulls on a shifted column).
- **Layers 1 / 2 / 3** — source / predict-grid + X-marker / features
  after the marker. Defined in Rule 2.

## Next-step pointers — where you go after this skill

| You came here for… | → next |
|---|---|
| Declared pipeline → CV strategy | → `evaluate-ml-pipeline` § G-CV-SPLITTER |
| Declared pipeline → smoke test | → `test-ml-pipeline` → `smoke-test-ml-pipeline` |
| Symbol lookup mid-declaration | → `python-api` (Shape 1 / 1b / 3) |
| Missing skrub/sklearn import | → `python-env-manager` § install |
| Modified `pipeline.py` / `features.py` / `data.py` | → `python-code-style` (ruff + NumPyDoc) |

Always re-emit the Pre-flight checklist with evidence before
declaring the turn done.

## Canonical pipeline shape — IID flat-table

The 90% case. Copy + adapt; replace `TARGET_COL` and the regressor.

```python
import skrub
from sklearn.ensemble import HistGradientBoostingRegressor

from <pkg>.data import TARGET_COL, load_raw


def build_learner(data_dir_preview=None):
    """Return the unfit learner (skrub SkrubLearner)."""
    data_dir = (
        skrub.var("data_dir", value=str(data_dir_preview))
        if data_dir_preview is not None
        else skrub.var("data_dir")
    )

    # Layer 1 + 2: load + mark X / y on the source frame.
    # No cross-row feature steps → marker sits here.
    data = data_dir.skb.apply_func(load_raw)
    X = data.drop(columns=[TARGET_COL]).skb.mark_as_X()
    y = data[TARGET_COL].skb.mark_as_y()

    # Layer 3: estimator at the tail. Feature engineering (if any)
    # chains between mark_as_X and the final .skb.apply.
    predictions = X.skb.apply(
        HistGradientBoostingRegressor(random_state=0), y=y
    )
    return predictions.skb.make_learner()
```

For history-dependent / panel / cold-start cases (≠ IID):
→ `references/layer_examples.md` § history-dependent.

For loader-baked-shift counter-example (what NOT to do):
→ `references/layer_examples.md` § counter-example.

## Stop conditions — read before anything else

Each Stop condition: **rule → symptom → recovery**. Scan top to
bottom; any match means STOP.

### S1. Missing dependency

- **Rule:** `import skrub` raising means `python-env-manager` is
  next, not a substitute library.
- **Symptom:** `ModuleNotFoundError: No module named 'skrub'`.
- **Recovery:** invoke `python-env-manager` for the install
  command. Do NOT substitute with `sklearn.Pipeline` /
  `make_pipeline` / `FunctionTransformer` — that silently rewrites
  this skill out of the project.

### S2. Symbol from memory is forbidden

- **Rule:** every skrub / scikit-learn / skore name must come from
  a `python-api` lookup *this turn*.
- **Symptom:** you type `tabular_learner` (renamed in 0.7+),
  `mark_as_y(col)` (signature dropped the positional in 0.9+), or
  any name "you remember".
- **Recovery:** invoke `python-api`. Recognition is not a lookup;
  names drift between releases.

### S3. Splitter selection is out of scope

- **Rule:** no `KFold` / `StratifiedKFold` / `train_test_split` /
  any splitter import in pipeline code.
- **Symptom:** you're about to type `from sklearn.model_selection
  import KFold` in `pipeline.py`.
- **Recovery:** that's `evaluate-ml-pipeline`'s territory. This
  skill only wires `split_kwargs` AT the X marker (see Rule 2).

### S4. `skrub.X(...)` / `skrub.y(...)` are not acceptable graph roots

- **Rule:** root on `skrub.var("<source>", value=preview)` instead.
- **Symptom:** code starts with `skrub.X(df)` / `skrub.y(s)`.
- **Recovery:** rewrite to `skrub.var("data_dir", value=...)` →
  `.skb.apply_func(load_fn)` → `.skb.mark_as_X()`. The shortcuts
  (1) bake the marker at the source — defeating Layer 1; (2)
  force a pre-loaded binding, breaking predict-time replay;
  (3) silently re-enable the late-`mark_as_X` bug for cross-row
  features.

### S5. Late `mark_as_X` is forbidden when any feature step is cross-row

- **Rule:** for any cross-row step (lag, rolling, group-agg,
  target shift, side-join, `drop_nulls` on shifted col), the
  X marker goes UPSTREAM of that step. The step references the
  cross-row source as an additional `apply_func` argument
  (Layer 1 source → Layer 3 feature, via the marker bypass).
- **Symptom:** the smoke test fails on `len(predictions) !=
  n_predict_grid_rows`; OR a `feature_steps=[]` toggle appears
  in `build_learner` "to make predict work for cold-start"; OR
  a temp-dir gymnastic at predict time to fake history; OR a
  wrapper estimator whose only job is to filter NaN rows the
  pipeline itself produced. (Don't be misled by syntax —
  `pl.col("x").shift(k)` IS cross-row.)
- **Recovery:** fix the graph topology via Rule 2's three-layer
  model. Don't loosen the smoke-test assertion. Don't wrap the
  predictor. Don't `feature_steps=[]`.
- **Proof:** smoke test (`smoke-test-ml-pipeline`) — pipeline
  with marker in the right place passes by construction.

### S6. Layer 1 doesn't know the question

- **Rule:** Layer 1 (sources + loaders) describes *what data
  exists*. Anything that requires knowing *which rows we want
  predictions for* — any horizon / lag / window / shift — belongs
  to Layer 2 or downstream, never Layer 1.
- **Symptom:** the loader's body contains a `target.shift(-HORIZON)`,
  a `drop_nulls("y")`, or any task-specific filter.
- **Recovery:** push the task-specific operation past the marker
  into Layer 2 (target derivation via a stateful estimator) or
  Layer 3 (history-dependent feature). The smoke test passes
  trivially when the bug is fused into Layer 1 — CV looks fine,
  and the structural debt only surfaces when the *next*
  experiment composes against the raw source.
- **Constructive test:** *would an external consumer — a SQL
  view, a feature store, a second model — derive this same
  output without knowing your task?* No → push it past the
  marker.

### S7. All Python execution goes to `scratch/`

- **Rule:** every Python command (version check, signature
  lookup, data inspection, loader sanity-check, anything) lands
  in `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` and runs via
  `pixi run python scratch/<ts>_<short>.py`.
- **Symptom:** you catch yourself typing `pixi run python -c`
  or `python -c`.
- **Recovery:** write the file first, then execute. **Inline is
  forbidden regardless of length** (see `python-api` § Stop
  conditions). No 2-line carve-out.

### S8. Don't filter warnings

- **Rule:** no `warnings.filterwarnings(...)` in `pipeline.py` or
  scratch probes unless the user explicitly asks. See
  `python-code-style` § Stop conditions.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `tabular_learner` from memory | Renamed to `tabular_pipeline` in skrub 0.7+. Memory typed → ImportError on modern installs |
| `mark_as_y(target_column)` positional arg | Dropped in 0.9+. Use `.skb.select("...")` BEFORE the mark |
| `skrub.X(df)` / `skrub.y(s)` as roots | Forbidden (S4). Use `skrub.var("<source>", value=...)` |
| `value="data/train.parquet"` literal in `pipeline.py` | Resolves against CWD; breaks runs from non-root dirs. Expose `data_dir_preview` as kwarg; caller passes `PROJECT_ROOT / "data"` |
| `feature_steps=[]` toggle "to make predict work" | S5 symptom. Fix the graph, not the predict-time bypass |
| `skore.evaluate(learner, X, y, ...)` | SkrubLearner takes an env-dict. Use `data={"data_dir": ..., ...}` |
| `bare sklearn.Pipeline` as top-level | Rewrite as skrub DataOps graph (Rule 1) |
| Inline `pixi run python -c "..."` | S7. Write to `scratch/<ts>_*.py` instead |

## Pre-flight — emit before any code

Each ticked box requires an actual tool call this turn. Empty
Evidence = unchecked.

```
Pre-flight (build-ml-pipeline):
- [ ] Tier 1 mandatory libs importable: sklearn, skrub, skore
      Evidence: scratch/<ts>_check_tier1.py + `pixi run python …` output.
                **Inline `python -c` is NOT evidence.**
- [ ] Tabular library identified: pandas | polars
      Evidence: JOURNAL.md Status (Workspace decisions) | user quote
                | "n/a — pandas already in loader signature"
- [ ] python-api consulted for skrub symbols this turn
      Evidence: Read scratch/api/skrub/<v>/<topic>.md (this turn)
                | "n/a — no new skrub symbol this turn"
- [ ] python-api consulted for sklearn symbols this turn
      Evidence: Read scratch/api/sklearn/<v>/<topic>.md (this turn)
                | "n/a — no new sklearn symbol this turn"
- [ ] Source-binding pattern chosen
      Evidence: list each planned `skrub.var("<name>")` and state
                whether it's a source identifier (e.g. `data_dir`)
                or a predict-grid descriptor. IID: one `skrub.var`
                rooted on the loaded frame is enough.
- [ ] X-marker placement decided
      Evidence: name the DataOp node where `.skb.mark_as_X()` lands.
                IID: on the loaded source frame. Panel / cold-start:
                on the predict-grid node, BEFORE any history-dep step.
- [ ] (Cross-row pipelines only) Each cross-row step references the
      upstream history DataOp as an extra `apply_func` arg
      Evidence: name each step + its history-DataOp argument
                | "n/a — no cross-row steps"
- [ ] Layer 1 audit — every `apply_func` upstream of `mark_as_X`
      passes the constructive test (S6)
      Evidence: per-step "external consumer would derive this: yes/no"
- [ ] Preview value handling
      Evidence: `build_learner` exposes `data_dir_preview=None` kwarg;
                no relative-path literal baked into `pipeline.py`
- [ ] split_kwargs at the X marker decided: groups | time | none
      Evidence: name the column(s) wired OR "n/a — i.i.d., no group
                or time structure"
- [ ] Smoke test wired (`tests/smoke/test_NN_<short_name>.py`)
      Evidence: per `smoke-test-ml-pipeline`; trivial assertions if no
                history-dep
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

## Scope

- **In scope:** how the pipeline *object* is composed — source
  wiring, preprocessing/feature steps, estimator at the tail.
- **Out of scope:** fitting, splitting, tuning, persisting,
  evaluating — those have their own skills.

## Core rules

### Rule 1 — Skrub DataOps is the pipeline entry point

Declare the pipeline as a skrub DataOps graph rooted at one or
more `skrub.var(...)` calls — **not** as a bare
`sklearn.Pipeline`. The `skrub.X(...)` / `skrub.y(...)` shortcuts
are not acceptable roots (see S4). Look up the underlying
signatures via `python-api`.

Reference: https://skrub-data.org/stable/data_ops.html

→ next: Rule 2 (where the marker goes).

### Rule 2 — Mark X early; featurize after

The marker is the **shared-vs-predict-specific boundary**.

**One question to place the marker:** *does any feature step look
at rows other than the one currently being processed?*

| Answer | Placement | Pattern |
|---|---|---|
| **No** (per-row math, stateful encoders that learn at fit and apply per-row) | Marker on the loaded source frame | Canonical IID example above |
| **Yes** (lag / rolling / cross-row join / target-shift) | Marker UPSTREAM of every cross-row step | Three-layer model below |

**The three logical layers:**

- **Layer 1 — Sources.** One `skrub.var(...)` per input identifier:
  raw history file(s) / URL(s) / table name(s), side tables, and —
  for time-series / cold-start panels — the *predict-time-grid
  description* (`start`/`end` range, list of `(group_id, time)`).
  The loader for each source is its first `.skb.apply_func`.
  Loaders are pure functions of a single source identifier.
  **Do not load + featurize in one `apply_func`** — that fuses
  Layers 2 + 3 with the loader and breaks predict-time replay.

- **Layer 2 — Predict-time grid + X marker.** A DataOp whose
  rows are exactly the predict grid.
  - IID flat tables: this IS the loaded source frame.
  - Time-series / panel: the `(group, time)` grid derived from
    Layer 1's predict-time bounds.

  **`mark_as_X` and `mark_as_y` go here.** Target derivation that
  requires history (and `drop_nulls` on `y`) belongs to a small
  stateful `BaseEstimator` with `fit_transform → {X, y}` /
  `transform → {X, y=None}`, attached at this layer.

- **Layer 3 — Feature engineering.** `apply_func` chained on the
  X-branch **after** `mark_as_X`. History-dependent steps take the
  X DataOp as their first argument **and** the relevant Layer-1
  source DataOp(s) as additional arguments — history is
  *referenced*, not bound to X. The same history node materializes
  the full available history at fit and at predict, so a backward
  lag computed for a row in the predict grid sees real values from
  the train history — **no cold-start NaN**.

**Worked examples** (full code, IID + history-dependent +
counter-example): → `references/layer_examples.md`. Also see
`python-api/references/pre_mark_alignment.md` for the
production-style three-layer walkthrough drawn from this
workspace's 01_baseline.

**Preview value is a caller-supplied parameter, not a literal in
`pipeline.py`.** `value=` controls what `learner.skb.preview()`
sees during interactive iteration — nothing else. A literal like
`value="data/train.parquet"` resolves against CWD and silently
breaks runs not started from the project root. Expose the preview
as an optional kwarg on `build_learner` and leave it `None` for
production fit / cross-validate.

**Downstream evaluation contract.** A `SkrubLearner` does NOT
implement sklearn's `fit(X, y)` signature — it takes an
environment dict. Pair with
`skore.evaluate(learner, data={"data_dir": ..., ...}, splitter=...)`,
never with `skore.evaluate(learner, X, y, ...)` (raises). See
`evaluate-ml-pipeline`; confirm signatures via `python-api`.

**Cross-validation metadata at the X marker.** If the data has
group structure (subjects, sessions, customer IDs, repeated
measures) or temporal ordering, attach the relevant column at
`.skb.mark_as_X(split_kwargs={...})`:

```python
X = data.drop(columns=[...]).skb.mark_as_X(
    split_kwargs={"groups": data["customer_id"]},
)
```

Keys map to the cross-validator's `split(X, y, **split_kwargs)`
(e.g. `groups`). **Ask the user** when you can't tell from data
alone whether such structure exists — name suspect columns
(anything ending in `_id`, columns called `subject` / `session` /
`region`, any `date` / `timestamp` for temporal ordering) and
ask whether to wire them. Don't silently leave `split_kwargs`
empty when group structure is plausible — that produces optimistic
CV downstream. Choosing the splitter itself is
`evaluate-ml-pipeline`'s job; this skill only wires the metadata.

**When editing an existing pipeline that uses `skrub.X` /
`skrub.y` or binds materialized data:** do not auto-rewrite.
Surface the source-bound alternative and ask whether to refactor.
Full catalogue: → `references/source-binding.md`.

→ next: Rule 3 (attach mechanism).

### Rule 3 — Attach data modifications via `.skb`

Two attach points:

- `.skb.apply_func(fn)` — wraps a callable that transforms data.
- `.skb.apply(estimator)` — wraps any sklearn-compatible estimator
  (transformer in the middle, or the final predictor).

When to use `skrub.deferred` instead of `apply_func`: rare —
only when the callable must combine **multiple DataOps** at once
(e.g. a custom join over two tables). Even then, check whether a
skrub joiner (`Joiner` / `AggJoiner` / `MultiAggJoiner`) covers it
first. Default: `.skb.apply_func`. Details:
→ `references/source-binding.md`.

→ next: Rule 4 (function vs estimator).

### Rule 4 — Stateless → function. Stateful → estimator.

The *only* decision rule for picking `apply_func` vs `apply`:

- **Stateless** — output for a row depends only on that row (and
  constants). No info borrowed across rows.
- **Stateful** — needs statistics / vocabulary / learned
  parameters fit on **training** data and re-applied unchanged to
  **test** data.

```python
# Stateless — pure function + apply_func
import numpy as np

X = X.skb.apply_func(lambda df: df.assign(log_price=np.log1p(df["price"])))

# Stateful — estimator + apply
from sklearn.preprocessing import StandardScaler

X = X.skb.apply(StandardScaler())
```

If a step would silently learn from the test set when called as
a plain function, it is stateful — promote it.

→ next: Rule 5 (leakage check).

### Rule 5 — Leakage rule

Any computation using statistics learned from the data (means,
medians, quantiles, vocabularies, target distribution) MUST be
stateful. Calling such a computation as a plain function over the
whole frame leaks test into training.

```python
# WRONG — pct rank fits on the full frame, leaks test into training
X = X.skb.apply_func(lambda df: df.assign(p=df["x"].rank(pct=True)))

# RIGHT — quantile transformer learns on training fold only
from sklearn.preprocessing import QuantileTransformer

X = X.skb.apply(QuantileTransformer(output_distribution="uniform"))
```

Classic traps by name:

- target encoding (must `fit` on training y only),
- target-aware or quantile-based imputation,
- quantile binning / `KBinsDiscretizer(strategy="quantile")`,
- `OrdinalEncoder` / `LabelEncoder` whose categories come from
  the full dataset rather than `fit` on training only,
- vocabulary-building text tokenizers, TF-IDF, IDF weights.

**Litmus test:** would this output change if I called it on the
training subset alone vs the whole frame? If yes → stateful →
`.skb.apply` with an estimator, never `.skb.apply_func`.

→ next: Decision flow.

## Decision flow for a new step

1. Does the operation only need the current row (and constants)?
   → **stateless** → pure Python function + `.skb.apply_func`.
2. Otherwise it must learn from training data and reapply on test.
   → **stateful** → sklearn-compatible estimator + `.skb.apply`.

→ next: Reproducibility (when touching shared modules).

## Reproducibility — extending without breaking prior experiments

`iterate-ml-experiment` enforces a hard rule: every `done` row in
`JOURNAL.md` History must stay runnable on `main` and produce the
same result. When touching a shared module under `src/<pkg>/`,
**default behavior must preserve prior experiments' shape**.

**Three options, picked by judgment** (full procedures + worked
examples: → `references/reproducibility_mechanics.md`):

- **Option 1 — parametrize the existing function** (with a
  default-preserving flag). Pick when the change is small and
  scoped: a step appended at the end, a single conditional, a
  stateless transform that adds columns without reshaping
  existing ones. **The flag's default mirrors prior behavior.**
- **Option 2 — add a new function called only from the new
  experiment.** Pick when the change doesn't fit cleanly behind a
  flag: new estimator at the tail, a step that reshapes the
  graph, or Option 1 would grow ugly internal branching.
- **Option 3 — branch the module.** Last resort. Only when the
  change touches enough internal structure that Options 1 and 2
  would obscure the diff. Usually a signal of a deeper layering
  issue worth surfacing to the user.

### Tripwires (load-bearing)

- **3+ flags in one function** → parametrization is leaking;
  reach for Option 2 next.
- **Visible branching in the function body** that makes it hard
  to read → reach for Option 2.
- **A flag changes default behavior of an existing caller** →
  STOP. Rule broken. Either keep the default preserving, or use
  Option 2.

### Cheap executable check

`iterate-ml-experiment` § 3's smoke-test gate runs **all** of
`tests/smoke/`, not just the new one. A prior smoke test going
red after a change = default behavior not preserved. Fix before
declaring the new experiment ready.

→ next: Common patterns (for recurring shapes).

## Common patterns

Short catalogue. Look up exact symbols in `python-api`. Full
catalogue with code: → `references/common_patterns.md`.

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
   `skrub.choose_from` / `choose_int` / `choose_float` /
   `optional` inside the declaration. Don't import `GridSearchCV`
   here; the tuning skill owns search.
6. **Custom sklearn transformer** — author only when (a) no
   built-in fits and (b) the operation is stateful. Subclass
   `BaseEstimator` + `TransformerMixin`. For a stateless op,
   write a function and use `.skb.apply_func`.

## Companion skills

| Skill | Relationship |
|---|---|
| `python-api` | Authoritative lookup of sklearn / skrub / skore. Invoke whenever picking a symbol; cache hits first (Shape 0) |
| `evaluate-ml-pipeline` | Owns `skore.evaluate`, CV selection, metric defaults. Consumes the `split_kwargs` wired at the X marker |
| `smoke-test-ml-pipeline` | Executable proof of Rule 2's early-mark. Smoke failure → route back here; fix the topology, don't loosen the assertion |
| `test-ml-pipeline` | Router for `tests/`. Smoke test pairs 1:1 with the experiment script |
| `python-env-manager` | Detection + install commands. Invoke when `import skrub` raises |
| `python-code-style` | **Must be invoked** after writing or editing `pipeline.py` / `features.py` / `data.py`. Direct `pixi run ruff check` drops the NumPyDoc convention |

## References (load on demand)

- `references/source-binding.md` — full catalogue of source-binding
  patterns (encouraged / discouraged / OK-but-offer-upgrade) +
  the `apply_func` vs `deferred` decision.
- `references/layer_examples.md` — worked code for the IID
  flat-table case, the loader-baked-shift counter-example, and
  the history-dependent three-layer pattern.
- `references/reproducibility_mechanics.md` — full Option 1 / 2 /
  3 procedures with code, plus the tripwire criterion.
- `references/common_patterns.md` — full catalogue of recurring
  pipeline shapes with code snippets.

> **Companion skill (planned): `review-ml-pipeline`** —
> methodological review of an existing declaration (leakage audit,
> statelessness check, step ordering, scope creep). When it flags
> a problem, return here to fix.
