---
name: evaluate-ml-pipeline
description: >
  Methodology for evaluating a single sklearn-compatible learner (in
  particular, the `SkrubLearner` produced by `build-ml-pipeline`).
  Owns: which entry point to call (`skore.evaluate` first, the
  explicit report classes when needed), which cross-validator to pick
  from scikit-learn's catalogue, how to consume the structural
  metadata (`groups`, `times`, …) attached at build time via
  `.skb.mark_as_X(split_kwargs=...)`. Stops at "what does the report
  say". Defaults (metrics, plots) come from skore; only override on
  explicit user request.

  TRIGGER when: code calls `cross_val_score`, `cross_validate`,
  `classification_report`, or any handwritten metric print
  (`print(mean_squared_error(...))`); code calls
  `.skb.cross_validate(...)` (route through skore for richer output);
  user asks how to score, evaluate, or compare a single learner;
  user asks how to pick a cross-validator; user wants to see a
  report / metrics / diagnostic plots for a fitted learner.

  SKIP when: declaring the pipeline (use `build-ml-pipeline`);
  hyperparameter / model search (separate skill); fitting,
  persisting, or serving the final model; tracking or comparing
  experiments across multiple runs over time (separate skill).

  HOW TO USE: invoke before any evaluation call. **First, read the
  "Stop conditions" block at the top of the body and emit the
  Pre-flight checklist as visible text in your response — both are
  mandatory before any evaluation code is written.** The structural
  facts about the data (group keys, time ordering) should already be
  encoded at the X marker via `split_kwargs` — if they aren't and you
  can't tell from the data, return to `build-ml-pipeline` and ask the
  user. For symbol-level lookups, defer to `python-api` (skore
  symbols) and `python-api` (splitters); don't guess names from
  memory.
---

# Evaluate ML Pipeline

Pick the entry point, pick the cross-validator, route the metadata,
read the report. The pipeline declaration is out of scope (see
`build-ml-pipeline`).

## Stop conditions — read before anything else

- **Missing dependency.** If `import skore` raises in this project's
  env, STOP. **Invoke `python-env-manager`** to detect the manager
  and produce the right install command (the project may not use
  pixi); surface the command to the user and wait for confirmation.
  **Do not drop back to `cross_val_score`, `cross_validate`,
  `classification_report`, or hand-rolled metric prints** — that
  silently rewrites this skill out of the project. See
  `data-science-python-stack` § "Missing dependency".
- **Symbol from memory is forbidden.** Any `skore` entry point
  (`evaluate`, `EstimatorReport`, `CrossValidationReport`,
  `ComparisonReport`) and any sklearn splitter name must come from a
  `Skill(python-api)` or `Skill(python-api)` call **in this turn**.
  "I remember `KFold(n_splits=5)`" is not acceptable.
- **Splitter choice is data-driven, not default-driven.** Pick from
  the `split_kwargs` content at the X marker via the table in rule 3
  — never reach for `KFold(5)` or `StratifiedKFold` out of habit. If
  `split_kwargs` is empty *and* you cannot rule out group / temporal
  structure, return to `build-ml-pipeline` and ask before defaulting.
- **No `Stratified*` for class imbalance.** It compresses across-fold
  variance and produces over-confident error bars. Imbalance does
  not change the splitter choice.
- **CV is necessary but not sufficient for any pipeline with
  history-dependent features.** `skore.evaluate(...)` materializes
  the graph **once** with one env-dict and splits *indices* — it
  never exercises a different env-dict at predict time, which is
  exactly the binding shape production faces. A pipeline that
  loads-then-features-then-splits passes CV trivially and still
  silently drops cold-start rows when handed a fresh
  `learner.predict(env₂)`. The structural check that catches this
  is the smoke test owned by `smoke-test-ml-pipeline` — required
  alongside CV for any pipeline that has a backward shift, lag,
  rolling window, target shift, or join with side history. If
  you produce a CV report and the pipeline has any such step,
  the matching `tests/smoke/test_NN_<short_name>.py` must also
  pass before the experiment can flip to `done` (enforced by
  `iterate-ml-experiment` § 4).
- **All Python execution goes to `scratch/`.** Every Python
  command — version checks, signature lookups, walking the skore
  report's metrics accessors, extracting per-fold values,
  sanity-checking the splitter's fold geometry, multi-symbol
  `inspect.signature(...)` on skore / sklearn classes — lands in
  `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` and runs via
  `pixi run python scratch/<ts>_<short>.py`. **Inline
  `pixi run python -c "..."` is forbidden regardless of length**
  (see `python-api` § Stop conditions). The previous "2-line
  inline cap" is removed.
- **`skore.evaluate(...)` and `project.put(...)` live only in
  `experiments/NN_*.py`.** The experiment script is the sole
  producer of a report in the workspace's skore Project.
  Re-running `evaluate` from a `scratch/` probe, an `audit/` file,
  a notebook, or a one-off Python file in `src/` duplicates the
  report under the same `key` and pollutes `project.summarize()`
  — the cross-experiment metrics view that `overview/summary.md`
  reads from. **Two read-only consumers** of the Project share
  the same `summarize()` → `get(id)` → `report.*` discipline:
  `scratch/<ts>_*.py` probes (owned by `organize-ml-workspace`
  § "Scratch is read-only") and `audit/<stem>.py` files (owned by
  `audit-ml-pipeline`, executed via its bundled in-process IPython
  runner; output digest at `scratch/audit/<stem>/audit.md`).
  Neither calls `evaluate(...)` or `put(...)`. A third consumer,
  `iterate-from-skore`, does not open the Project at all — it
  reads the audit's digest as text and converts the surfaced
  checks into Backlog candidates. The trap the two Project-side
  consumers share: `project.get(key)` raising `KeyError` reads as
  "the report is missing" but actually means "the lookup shape is
  wrong — `get` is by id, not
  by `key`". Never substitute by re-running `evaluate` + `put`.
  See `python-api` § "Lookup failure ≠ artifact missing" for the
  general registry-lookup discipline.
- **The time-ordered splitter AskUserQuestion is non-skippable,
  even under harness-level "no clarifying questions"
  instructions.** When the data is temporal, the four-option
  pick from rule 3 is an operating-contract gate, not a
  clarifying question. The harness's "no clarifying questions"
  hint applies to agent-discretionary asks (ambiguous wording,
  unclear intent); it never overrides a gate a skill explicitly
  mandates. The same override rule applies to every other
  mandatory `AskUserQuestion` in this stack —
  `python-env-manager` § "Where does the package belong?",
  `data-science-python-stack` § Tier 2 (pandas vs polars),
  `iterate-ml-experiment` § 1 (sourcing menu), `iterate-from-user`
  § "The entry-point AskUserQuestion". When in doubt: the user's
  approval is the gate, not the harness's instruction text.

## Pre-flight — emit this checklist as visible text before any code

Before writing the evaluation call, output the following block
verbatim in your response. Each box must be backed by an actual
tool call or an explicit decision documented in the response.

```
Pre-flight (evaluate-ml-pipeline):
- [ ] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (per `data-science-python-stack` § "Tier 1")
- [ ] Skill(python-api) consulted for skore symbols (evaluate /
      report classes): <symbols>
      Evidence: Read scratch/api/skore/<version>/<topic>.md (this turn)
                | Write scratch/api/skore/<version>/<topic>.md (this turn)
                | "n/a — no new skore symbol introduced this turn"
      "Read python-api SKILL.md" alone is NOT evidence.
- [ ] Call site for `skore.evaluate(...)` / `project.put(...)`
      is `experiments/NN_*.py` (not `scratch/`, not a notebook,
      not `src/<pkg>/`). See Stop condition
      "`skore.evaluate(...)` and `project.put(...)` live only in
      `experiments/NN_*.py`".
      Evidence: Write experiments/<NN>_<name>.py (this turn) |
                "the call already lives in an existing experiments/ file"
- [ ] Skill(python-api) consulted for sklearn splitter: <name>
      Evidence: Read scratch/api/sklearn/<version>/cv_splitters.md
                (or topic-matching file, this turn)
                | Write of the same (this turn)
                | "n/a — splitter is one already in src/<pkg>/evaluate.py
                  and its arguments are unchanged"
      "Read python-api SKILL.md" alone is NOT evidence.
- [ ] split_kwargs at the X marker read: <groups | time | none>
- [ ] Splitter chosen via rule 3 mapping table: <name + reason>
- [ ] Data-passing form picked: <X, y> | <data={...}>
- [ ] Smoke test status (per `smoke-test-ml-pipeline`):
        passing  — CV report can be persisted and experiment can
                   flip to `done`;
        failing  — pipeline has a structural bug; route back to
                   `build-ml-pipeline` (CV report can still be
                   produced, but the experiment stays `approved`,
                   not `done`, until smoke passes);
        n/a      — pipeline has no history-dependent step (rare
                   for time-series / panel data; explain why in
                   the response).
- [ ] If a probe is needed in this turn (skore report walk,
      metric extraction, splitter fold inspection), the payload
      goes to `scratch/<ts>_<short>.py`, **not inline `pixi run
      python -c "..."`**. No inline allowance — all Python
      execution goes to scratch.
```

## Scope

- **In scope:** choosing the evaluation entry point, picking a
  cross-validator, wiring `split_kwargs` into the splitter, reading
  the report, deciding when to escalate to explicit report classes.
- **Out of scope:** pipeline declaration, hyperparameter search,
  persistence, serving, multi-run tracking.

## Core rules

1. **`skore.evaluate(...)` is the entry point.** It is a dispatcher
   that returns the right report for the task and `splitter`
   argument. **Never** hand-roll `cross_val_score` + manual metric
   prints, and don't drop back to bare sklearn for evaluation. If you
   see existing `cross_val_score` / `cross_validate` /
   `classification_report` / `mean_squared_error` calls in the diff,
   redirect them through `skore.evaluate`. Consult `python-api` for
   the exact signature.

   **Two data-passing forms — pick the one that matches the
   estimator:**

   - sklearn-style: `skore.evaluate(estimator, X, y, splitter=...)`
     for any estimator whose `fit` is `(X, y)`.
   - env-dict-style: `skore.evaluate(learner, data={"X": X, "y": y,
     ...}, splitter=...)` for a skrub `SkrubLearner` (its `fit`
     takes a single environment dict mapping `skrub.var(name=...)`
     names to values). This is the right form for the pipelines
     produced by `build-ml-pipeline`.

   `X`/`y` and `data` are mutually exclusive. The same split applies
   to `CrossValidationReport(...)`; `EstimatorReport(...)` uses
   `train_data=` / `test_data=` for the env-dict equivalent of
   `X_train` / `y_train` / `X_test` / `y_test`. The full interop
   pattern (env-dict-style vs sklearn-style, how `data={...}` keys
   map to `skrub.var` roots, key conventions in the Project store)
   is in `python-api/references/skrub_interop.md`; for exact
   signatures, look them up via `python-api` against the installed
   skore version.

2. **Escalate to explicit report classes only when `evaluate` is too
   coarse.** The escalation order:

   - `EstimatorReport` — single fit on a held-out set (no CV); use
     when CV is wasteful (e.g., evaluating the final model on all
     data after CV has already been done).
   - `CrossValidationReport` — k-fold over one learner with access
     to per-fold artifacts.
   - `ComparisonReport` — two or more learners side-by-side.

   See `references/reports.md` for the escalation table; defer all
   API details to `python-api`.

3. **Pick the cross-validator from the structural facts of the data
   — not by default.** The data tells you what splitter is correct.
   The structural facts arrive at the X marker through
   `split_kwargs` (set by `build-ml-pipeline` at declaration time).
   Mapping rules:

   | `split_kwargs` content | Splitter |
   |---|---|
   | `groups` | `GroupKFold` |
   | temporal ordering | **ask the user** (see "Time-ordered data" below) |
   | none | `KFold` (or `RepeatedKFold` for small / noisy data) |

   Imbalanced classification *does not* change the choice — use
   plain `KFold` / `GroupKFold`. See "Avoid by default" below.

   **Avoid by default:**
   - **Stratified variants** (`StratifiedKFold`,
     `StratifiedGroupKFold`, `StratifiedShuffleSplit`,
     `RepeatedStratifiedKFold`) — they reduce across-fold variance
     by construction, producing over-confident error bars on the
     score. Don't reach for them on imbalance.
   - **`LeaveOneOut` / `LeaveOneGroupOut` / `LeavePGroupsOut`** —
     high per-fold variance; aggregate hides the noise. Use
     `KFold` / `GroupKFold` with 5–10 splits instead.

   See `references/cross-validation.md` § "Avoid" for the reasoning.
   Wiring details: `references/metadata-routing.md`.

   **Time-ordered data — `AskUserQuestion` is mandatory.** When
   the data is temporal, fire `AskUserQuestion` *before* picking
   a splitter, with **four explicit options**:

   1. **`TimeSeriesSplit(gap=horizon)`** — growing-window train,
      contiguous test, embargo equal to the forecast horizon.
      The safe default for any horizon-`h` forecasting task: it
      prevents the train tail from leaking into the test head
      by up to one horizon. Follow up to surface `n_splits` /
      `test_size` / `max_train_size`.
   2. **`TimeSeriesSplit(gap=0)`** — only on the user's explicit
      pick. Warn in the option description that with horizon
      `h > 0`, the last `h` rows of every training fold predict
      values whose target time is *inside* the test fold; the
      reported metric is optimistic.
   3. **Custom splitter** — purged-and-embargoed (finance),
      blocked calendar windows, walk-forward with refit
      cadence. Pick this when the time structure has more shape
      than `TimeSeriesSplit` captures. See
      `references/custom-splitter.md`.
   4. **`KFold` ignoring time** — only when the user confirms
      the temporal structure shouldn't drive splitting (e.g.
      the time column is a covariate but the task is treated
      as IID). The skill should *not* recommend this option on
      time-ordered data without an explicit user reason.

   **No silent default.** Even if the data looks "obviously
   `TimeSeriesSplit`", the user picks via `AskUserQuestion`.
   The gap parameter is the one most often wrong by default —
   `TimeSeriesSplit(n_splits=5)` from memory uses `gap=0`,
   which silently leaks for any non-trivial horizon. The
   structured pick exists to make that visible. Ambiguous free
   text ("just pick something", "you decide") routes to a
   clarifying `AskUserQuestion`; don't infer.

   Separately, ask whether the time column should stay as a
   covariate or be dropped from the feature matrix (encoders
   can extract calendar patterns from a timestamp; the user's
   call). This is a follow-up question, not a substitute for
   the splitter pick.

   If `split_kwargs` is empty *and* you cannot confirm there's
   no structure (from build-time checks or from the user), do
   not silently default. Return to `build-ml-pipeline` and ask
   the user first.

4. **Trust skore's metric defaults; override only on explicit user
   request.** `skore.evaluate` picks task-appropriate metrics
   automatically (regression: MSE/RMSE/MAE/R²; binary: accuracy,
   precision, recall, F1, ROC-AUC; multiclass: macro/micro variants;
   multilabel: per-label + averages). Override only when the user
   says so — e.g., "use RMSE", "report ROC-AUC". Don't pre-emptively
   pin metrics or pass a `scoring=...` argument unless asked.

5. **Custom splitter — only when sklearn doesn't have it.** Examples
   that justify one: purged-and-embargoed time-series CV (finance),
   blocked spatial CV. The contract is small: `split` +
   `get_n_splits`. See `references/custom-splitter.md`. Otherwise,
   prefer the sklearn built-in.

## Decision flow

1. Is the goal to *score* one learner, or to *compare* ≥ 2?
   - One → `skore.evaluate(...)` (default), escalate to
     `CrossValidationReport` or `EstimatorReport` only if needed.
   - ≥ 2 → `ComparisonReport`.
2. Read `split_kwargs` at the X marker.
3. Map to a splitter using the table in rule 3.
4. Pick the data-passing form (rule 1): `data={"X": X, "y": y, ...}`
   for a `SkrubLearner`, positional `X, y` otherwise.
5. Pass the splitter via `splitter=...` to the chosen entry point.
6. Inspect the report; override metrics only on explicit user
   request.

## Companion skills

- **`python-api`** — every skore symbol used here. Mandatory before
  naming `evaluate`, `EstimatorReport`, `CrossValidationReport`,
  `ComparisonReport`. Don't guess from memory. **Cache hits
  first**: check `scratch/api/skore/<version>/` before
  WebSearching for narrative pages; cache new findings back
  there (per `python-api` Shape 0/3).
- **`python-api`** — every splitter used here. Mandatory before
  naming `KFold`, `GroupKFold`, `TimeSeriesSplit`, etc. **Cache
  hits first**: check `scratch/api/sklearn/<version>/` before
  WebSearching.
- **`build-ml-pipeline`** — upstream pipeline shape and where
  structural metadata is attached via `split_kwargs`. Return there
  if the metadata you need at evaluation time isn't wired in,
  *or* if the smoke test (below) fails on row count — that's a
  graph-topology bug owned by `build-ml-pipeline` (rule 2,
  early-`mark_as_X`).
- **`smoke-test-ml-pipeline`** — the structural check CV cannot
  do by construction: predict on a *different* env-dict from the
  one used at fit, assert the prediction count matches the
  predict-grid row count exactly. Required alongside CV for any
  pipeline with a history-dependent step. The CV report and the
  smoke test are independent artifacts — both must be in place
  before an experiment can flip to `done`.
- **`audit-ml-pipeline`** — read-only consumer of the report
  this skill's `skore.evaluate(...)` produced. The experiment
  script puts the report; the audit file loads it via
  `project.summarize()` → `project.get(id)` and renders a
  markdown digest for the agent (no `evaluate`, no `put`).
  Fires at `iterate-ml-experiment` § 4 record-outcome.
- **`test-ml-pipeline`** — router for `tests/`. Owns layout and
  the stem pairing between an experiment and its smoke test.
- **`python-env-manager`** — detection + install commands for the
  project's environment manager (pixi / uv / poetry / hatch / conda
  / pip+venv). **Invoke whenever** the Stop condition on
  `import skore` fires, or whenever any other dependency is missing
  from the env. Don't infer the manager or hand-craft the install
  command — that skill owns it.
- **`python-code-style`** — **must be invoked** after writing or
  editing `src/<pkg>/evaluate.py` (and, if a custom splitter is
  authored, the module that holds it). Running `pixi run ruff
  check` directly without invoking this skill silently drops the
  NumPyDoc docstring convention this stack expects: ruff's
  `D`-rules pass on a one-line summary, but only the skill body
  teaches the parameter-shape-in-type-slot, `Parameters` /
  `Returns` / `Yields` sections, and the imperative one-line
  summary.
