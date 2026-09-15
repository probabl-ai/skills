# evaluate-ml-pipeline eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Standard skore.evaluate entry, IID tabular

**User prompt:**
> Wire `evaluate.py` for the baseline. Tabular regression, no
> groups, no temporal ordering.

**Assumed workspace state:**
- `journal/01_baseline.md` approved.
- `src/<pkg>/pipeline.py` exists with `build_learner` returning a
  `SkrubLearner`. The X-marker has empty `split_kwargs`.
- `experiments/01_baseline.py` is the scaffold placeholder.
- Cache exists at `scratch/api/sklearn/1.8.0/cv_splitters.md`
  covering `KFold` / `GroupKFold` / `TimeSeriesSplit`, and at
  `scratch/api/skore/0.18.0/evaluate.md`.

**Must do:**
- Pick **`skore.evaluate(learner, data={...}, splitter=...)`** as
  the entry point (not `cross_val_score`, not `cross_validate`).
- Map empty `split_kwargs` + IID → **`KFold`** per the mapping table.
- Name `python -m skore_skills api get` for `skore.evaluate` and
  `KFold` signatures (or Read the matching caches already listed).
- Mention `data={...}` (env-dict) for `SkrubLearner`, NOT
  positional `X, y`.

**Must NOT do:**
- Recommend `cross_val_score`, `cross_validate`,
  `classification_report`, or hand-rolled `print(mean_squared_error(...))`.
- Default to `StratifiedKFold` (forbidden — compresses across-fold
  variance, even on imbalance).
- Pre-pin metrics (e.g. `scoring="neg_mean_squared_error"`) — trust
  skore defaults.

---

## CASE_02 — Time-ordered data, mandatory AskUserQuestion

**User prompt:**
> Wire `evaluate.py` for the 24h-ahead load forecast experiment.
> Pick the splitter.

**Assumed workspace state:**
- `journal/02_load_forecast.md` approved.
- `pipeline.py` X-marker has `split_kwargs={"times": ...}` (temporal
  ordering attached at build time).
- Forecast horizon is 24h.
- Cache hit at `scratch/api/sklearn/1.8.0/cv_splitters.md` covering
  `KFold` / `GroupKFold` / `TimeSeriesSplit` — the splitter lookup
  is already satisfied.

**Must do:**
- Name **`AskUserQuestion`** (or a narrative equivalent that lists
  the picks and waits) as the mandatory gate before a splitter is
  locked in. No tools this turn: enumerating the options in the
  message counts as firing the gate.
- Present the **four canonical options** (wording need not be
  verbatim):
  1. `TimeSeriesSplit(gap=horizon)` — safe default
  2. `TimeSeriesSplit(gap=0)` — only on explicit user pick; warn
     about leakage
  3. Custom splitter (purged-and-embargoed / blocked calendar /
     walk-forward)
  4. `KFold` ignoring time — only with explicit user reason
- Cite that `TimeSeriesSplit(n_splits=5)` from memory defaults to
  `gap=0` which silently leaks at non-trivial horizons. Any
  sentence that `gap=0` is the memory default / leaks is enough;
  do not require the exact constructor spelling if `gap=0` is
  named.

**Must NOT do:**
- Skip the four-option ask and lock a splitter with no user pick.
  Naming a **recommended** option (e.g. `TimeSeriesSplit(gap=horizon)`)
  next to the menu, or drafting `evaluate.py` labeled pending
  confirmation, is not a silent pick.
- Default to `KFold` because empty `gap` "feels safer".
- Treat harness "no clarifying questions" hint as waiving the
  mandatory ask.

---

## CASE_03 — `split_kwargs={"groups": ...}` → GroupKFold

**User prompt:**
> Wire `evaluate.py` for a tabular regression where rows are grouped
> by customer.

**Assumed workspace state:**
- `pipeline.py` X-marker has
  `split_kwargs={"groups": data["customer_id"]}`.
- No temporal structure.

**Must do:**
- Paste **`GroupKFold`** from the mapping table (`groups` →
  `GroupKFold`). That identifier is the mapping; do not withhold it.
- `python -m skore_skills api get` for the *signature* may be named
  as the next live turn. Do not fail if signature lookup is BLOCKED
  as long as `GroupKFold` is named.
- Show the `data={...}` env-dict form for a `SkrubLearner`.
- Do NOT use `StratifiedGroupKFold` (forbidden by Stop conditions).

**Must NOT do:**
- Use `StratifiedGroupKFold`.
- Use `LeaveOneGroupOut` (forbidden — per-fold variance too high).
- Pick `KFold` ignoring the group structure.

---

## CASE_04 — Empty `split_kwargs` BUT possible group structure

**User prompt:**
> Wire `evaluate.py`. The data has a `region` column. Not sure if
> we should treat it as a group.

**Assumed workspace state:**
- `pipeline.py` X-marker has empty `split_kwargs`.
- `region` is a potential group key but wasn't wired in.

**Must do:**
- **Refuse to default** to `KFold` silently.
- Route back to `build-ml-pipeline` (NOT this skill) to wire
  `split_kwargs` properly first, OR ask the user whether to treat
  `region` as a group.
- Cite the Stop condition: "If `split_kwargs` is empty *and* you
  cannot rule out group / temporal structure, return to
  `build-ml-pipeline`."

**Must NOT do:**
- Default to `KFold` and proceed.
- Auto-wire `split_kwargs={"groups": data["region"]}` from this
  skill (that's `build-ml-pipeline`'s job).
- Pick `StratifiedKFold` because "stratified is safer".

---

## CASE_05 — Refuse `cross_val_score` / hand-rolled prints

**User prompt:**
> Just use `cross_val_score(learner, X, y, cv=5)` for the baseline
> evaluation and `print(mean_squared_error(...))` for the metric.
> Quick and simple.

**Assumed workspace state:**
- `pipeline.py` returns a `SkrubLearner`.
- skore is installed.

**Must do:**
- Refuse `cross_val_score` and the hand-rolled metric print.
- Cite that `skore.evaluate` is the canonical entry point in this
  stack.
- Cite that `SkrubLearner` does NOT implement sklearn's
  `fit(X, y)` signature — `cross_val_score` will raise.
- Propose `skore.evaluate(learner, data={...}, splitter=...)`
  instead.

**Must NOT do:**
- Write `cross_val_score(...)` in `evaluate.py`.
- Use `print(mean_squared_error(...))` instead of the report
  object.
- Allow the substitution as a "just for now" workaround.

---

## CASE_06 — CV is necessary but not sufficient for history-dep

**User prompt:**
> 02_load_forecast has lag features. CV passes clean — RMSE looks
> fine. Mark it `done` in `JOURNAL.md`.

**Assumed workspace state:**
- `02_load_forecast` ran; CV report is clean.
- `tests/smoke/test_02_load_forecast.py` exists but has NOT been
  run this turn / is currently red on row-count.

**Must do:**
- Refuse to mark `done` without the smoke test passing.
- Cite the Stop condition: "CV is necessary but not sufficient for
  any pipeline with history-dependent features."
- Mention that `skore.evaluate` materializes the graph once with
  one env-dict; the smoke test exercises a fresh env-dict at
  predict time, which is what catches cold-start row drops.
- State that a passing smoke test is still required before the
  caller may flip the status.

**Must NOT do:**
- Edit `journal/02_load_forecast.md` Status to `done`.
- Edit `journal/JOURNAL.md` History row to `done`.
- Treat clean CV as sufficient for a history-dependent pipeline.

---

## CASE_07 — `skore.evaluate` / `project.put` only in experiment script

**User prompt:**
> Add a scratch probe that re-runs `skore.evaluate(learner, ...)` to
> see the updated metrics, then `project.put("02_text_encoder",
> report)` to refresh the cache.

**Assumed workspace state:**
- `experiments/02_text_encoder.py` already produced a report.
- The user wants a "refreshed" version.

**Must do:**
- Refuse the scratch re-run.
- Cite the Stop condition: "`skore.evaluate(...)` and
  `project.put(...)` live only in `experiments/NN_*.py`."
- Cite that re-running from scratch lands a duplicate row under
  the same `key` in `project.summarize()`, polluting the Project's
  report index.
- Recommend using `project.summarize()` + `project.get(id)` for
  read-only inspection, OR re-running the experiment script if a
  fresh report is genuinely needed.

**Must NOT do:**
- Approve the scratch probe with `evaluate` + `put`.
- Treat scratch as a producer of reports.
