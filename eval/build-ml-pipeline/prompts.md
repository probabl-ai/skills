# build-ml-pipeline eval — golden prompts

Behavioural prompts scored manually against Must / Must NOT bullets.

## How a case is scored

For each case the model is given:
- `skills/build-ml-pipeline/SKILL.md` as the system prompt.
- The case's `User prompt` (verbatim), prefixed with the
  `Assumed workspace state` block.

Case 3 sets `**Tools:** yes` and seeds `references/layer_examples.md`
so the target can `read_file` the history-dependent JOIN example
(the same file `SKILL.md` points at). Other cases stay single-turn.

Pass criterion per case: every `Must do` ticked, zero `Must NOT do`
violated. Overall: ≥ 6/7 cases pass and no Must NOT violated.

---

## CASE_01 — Bare `sklearn.Pipeline` → redirect to skrub DataOps

**User prompt:**
> Set up the baseline pipeline using `sklearn.Pipeline` with a
> `StandardScaler` and `Ridge`. Just write `src/<pkg>/pipeline.py`
> with a `build_pipeline()` function.

**Assumed workspace state:**
- Tabular regression task, mixed-type DataFrame, no cross-row
  features (IID).
- `skrub`, `scikit-learn`, `skore` are installed and importable.
- No existing `src/<pkg>/pipeline.py`.

**Must do:**
- Redirect from bare `sklearn.Pipeline` to a **skrub DataOps graph**
  rooted at `skrub.var(...)`.
- Cite Rule 1 ("Skrub DataOps is the pipeline entry point") or the
  TRIGGER bullet that catches bare sklearn pipelines.
- Name `python -m skore_skills api get` for the skrub symbols
  before writing their calls.
- Propose a `build_learner` function returning
  `predictions.skb.make_learner()` (not a `Pipeline` object).

**Must NOT do:**
- Write `from sklearn.pipeline import Pipeline` as a live import
  in `pipeline.py`.
- Return a `Pipeline([("scaler", StandardScaler()), ...])` object
  from `build_learner` / `build_pipeline`. A docstring that only
  names the forbidden equivalent is not a violation.
- Use `skrub.X(...)` / `skrub.y(...)` as graph roots.

---

## CASE_02 — IID flat-table marker placement

**User prompt:**
> Tabular CSV, columns `[feature_1, feature_2, ..., target, id]`.
> Predict `target`. No time-series, no groups. Write the skrub
> DataOps pipeline.

**Assumed workspace state:**
- skrub installed at 0.9.0.
- Cache exists at `scratch/api/skrub/0.9.0/tabular_pipeline.md`
  (you may treat its content as known).

**Must do:**
- Use a single `skrub.var("<source>", ...)` root for the source.
- Place `mark_as_X()` and `mark_as_y()` directly on the loaded
  source frame (IID branch — no three-layer needed).
- Drop `id` and `target` from X.
- Mention the optional `<source>_preview` keyword on `build_learner`.

**Must NOT do:**
- Introduce a `predict_grid` Layer 1 root when no cross-row features
  exist (over-engineering).
- Use `skrub.X(...)` / `skrub.y(...)` as roots.
- Bake the preview value as a literal string in `pipeline.py`
  (relative path that breaks CWD-dependent runs).

---

## CASE_03 — History-dependent late `mark_as_X` trap

**User prompt:**
> Time-series load forecast. Each row = (timestamp, region, load).
> I want a 24-hour-ahead forecast. Write the loader so it computes
> `y = load.shift(-24)` then drops the rows with `NaN` in `y`, and
> we'll do `mark_as_X` on the result.

**Assumed workspace state:**
- skrub installed at 0.9.0.
- The user is in early baseline construction.
- The skill's `references/` tree is on disk at the project root
  (`references/layer_examples.md`). Open that file with `read_file`
  before proposing Layer 2.

**Tools:** yes

**Sandbox:**
- copy: `skills/build-ml-pipeline/references/layer_examples.md` as `references/layer_examples.md`

**Expect reads:**
- `references/layer_examples.md`

**Must do:**
- Refuse the proposed loader-baked target shift.
- Cite the **late-`mark_as_X` forbidden** rule (cross-row dependency).
- Cite **Layer 1 doesn't know the question** — the 24-hour horizon
  belongs to Layer 2, not the loader.
- Propose the **three-layer pattern**: `history_source` + `predict_grid`
  as Layer 1; Layer 2 aligns into `{X, y}` and marks; Layer 3
  features take X + history as references.
- Layer 2 is a **JOIN** of the predict grid to history at
  `t + 24h` (inner join; no `shift` + `dropna` NaN filter). A small
  `align_xy` estimator is fine if it joins.

**Must NOT do:**
- Accept the loader-baked shift as written.
- Suggest a "wrapper estimator that filters NaN rows" as the fix
  (the named anti-pattern symptom).
- Suggest `feature_steps=[]` toggle in `build_learner` to "make
  predict work" (also a named anti-pattern symptom).

---

## CASE_04 — `skrub.X / skrub.y` as roots — refuse

**User prompt:**
> Here's my draft:
>
> ```python
> X = skrub.X(data.drop(["id", "target"], axis=1))
> y = skrub.y(data["target"])
> ```
>
> Continue from here — add the encoder and the predictor.

**Assumed workspace state:**
- skrub installed at 0.9.0.
- `data` is already a loaded DataFrame.

**Must do:**
- Refuse `skrub.X(...)` / `skrub.y(...)` as graph roots.
- Cite the Stop condition explicitly (sugar that bakes the marker
  at the source; defeats Layer 1).
- Propose the source-bound alternative: `skrub.var("<source>",
  preview)` then `.skb.mark_as_X()` on that frame. When the source
  is a path/dir, that includes `.skb.apply_func(load_*)` before
  the marker. When the workspace already has a loaded DataFrame,
  `skrub.var(..., value=preview)` + `.skb.mark_as_X()` counts —
  do not require a loader call.
- Surface that this is a refactor and offer to do it (or ask user).

**Must NOT do:**
- Continue adding steps to the `skrub.X` / `skrub.y` skeleton
  silently.
- Auto-rewrite without surfacing the source-bound alternative to
  the user.

---

## CASE_05 — Stateful step misclassified as stateless (leakage)

**User prompt:**
> Add target encoding for the `category` column. Just write a
> `def target_encode(df): ...` that computes the mean target per
> category and replaces the column. Attach it with `.skb.apply_func`.

**Assumed workspace state:**
- skrub installed at 0.9.0.
- An existing skrub DataOps graph with `mark_as_X` / `mark_as_y`
  in place.

**Must do:**
- Refuse the `apply_func` route for this step.
- Cite the **statelessness rule** (stateful → estimator) and/or the
  **leakage rule** (uses statistics learned from data → must be
  stateful) — target encoding learns category → mean from training
  y.
- Propose a sklearn-compatible estimator (`BaseEstimator` +
  `TransformerMixin` or an existing `TargetEncoder`) attached via
  `.skb.apply`.
- Name `python -m skore_skills api get
  sklearn.preprocessing.TargetEncoder` (or equivalent) before
  writing its call.

**Must NOT do:**
- Accept `apply_func(target_encode)` as written.
- Propose the function with a "compute mean on training only via
  manual filtering" workaround.

---

## CASE_06 — Reproducibility: add a feature without breaking prior

**User prompt:**
> For experiment 02, I want to add calendar features (day-of-week,
> hour-of-day). `build_learner` is shared with 01_baseline. How
> should I extend `pipeline.py` so that 01 still runs the same?

**Assumed workspace state:**
- `src/<pkg>/pipeline.py` has `build_learner(data_dir_preview=None)`.
- `experiments/01_baseline.py` uses `build_learner()` (no kwargs).
- Calendar features = a stateless step appending a few columns.

**Must do:**
- Recommend **Option 1 — parametrize the existing function with a
  default-preserving flag** (small, scoped, append-shaped → fits
  Option 1's criterion).
- Show a flag whose **default keeps `build_learner()` as today**
  (`include_calendar_features: bool = False` is an example, not
  required spelling).
- Mentioning `tests/smoke/` as the cheap reproducibility check is
  optional. Do not fail if the flag pattern is present.

**Must NOT do:**
- Recommend Option 3 (branch the module) for an appendable step.
- Recommend changing `build_learner`'s default behavior (the named
  tripwire "A flag changes default behavior of an existing caller").
- Suggest adding the calendar features unconditionally to
  `build_learner`.

---

## CASE_07 — `split_kwargs` group structure

**User prompt:**
> Tabular regression on (customer_id, claim_amount, ...). Multiple
> rows per customer. Build the pipeline.

**Assumed workspace state:**
- skrub installed at 0.9.0.
- IID-shaped features (no cross-row history) but rows are grouped
  by customer.

**Must do:**
- Identify the group structure (multiple rows per `customer_id`).
- Wire `mark_as_X(split_kwargs={"groups": data["customer_id"]})` at
  the X marker.
- Cite that `split_kwargs` is the metadata `evaluate-ml-pipeline`
  consumes downstream for the splitter.
- Mention asking the user whether grouping is intended (named
  ask: "anything ending in `_id`, columns called `subject` /
  `session` / `region`").

**Must NOT do:**
- Pick the cross-validator in pipeline code (`splitter=GroupKFold(...)`,
  `cv=GroupKFold`, `skore.evaluate(..., splitter=...)`). Naming
  `GroupKFold` only as what `evaluate-ml-pipeline` owns later is
  not a violation.
- Leave `split_kwargs` empty without surfacing the group question.
