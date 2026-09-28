# smoke-test-ml-pipeline eval — golden prompts

Behavioural prompts. Pass = every Must do ticked, zero Must NOT
violated.

---

## CASE_01 — Standard smoke test for history-dependent pipeline

**User prompt:**
> Write the smoke test for `02_load_forecast`. The pipeline has lag
> features going back 168 hours and a 24h-ahead target.

**Assumed workspace state:**
- `journal/02_load_forecast.md` approved with Status.headline
  `RMSE 0.083 ± 0.004 (5-fold CV)`.
- `experiments/02_load_forecast.py` exists.
- `src/<pkg>/data.py` exposes `build_supervised_frame(data_dir)`.
- `tests/smoke/test_02_load_forecast.py` is an empty scaffold.

**Must do:**
- Before writing/running the test, give a 1–3 sentence preview:
  local fit/predict on a small real-data slice, the exact
  row-count assertion, `tests/smoke/test_02_load_forecast.py`,
  and the `smoke run` command.
- Distinguish this diagnostic slice from full CV and say timing
  depends on the loader, feature graph, and learner; do not invent
  a minute estimate.
- Wire the **hard assertion**:
  `assert len(predictions) == n_predict_grid_rows`.
- Build the predict env-dict with **no pre-history buffer** — only
  the rows we want predictions for.
- Use the **real `data/` source** (not a synthesized fixture).
- Wire the **soft assertion** with the CV-mean from the design
  note's Status.headline hardcoded as a literal (with a comment
  pointing to the design note).
- Mention NOT importing `skore` in the test file (test must run
  in any skrub-capable env).
- Run `python -m skore_skills smoke run --stem 02_load_forecast`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Say the smoke test performs full-dataset cross-validation.
- Synthesize a fake DataFrame fixture.
- Import `skore` / `skore.Project` in the test.
- Wrap the predictor or add NaN-handling to make the test pass.
- Use an "approximately equal" / "at least 80%" row-count
  assertion.

---

## CASE_02 — Refuse to write before approved design note

**User prompt:**
> Smoke-test `experiments/03_target_transform.py` — I haven't
> written the design note yet but the script's ready.

**Assumed workspace state:**
- `experiments/03_target_transform.py` exists (written directly).
- `journal/03_target_transform.md` does NOT exist.

**Must do:**
- Refuse to write the smoke test.
- Cite the Stop condition: "No smoke test without an approved
  design note + script."
- State that status is missing an approved design and tell the user
  to run the model/loop pack or ask triage.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write `tests/smoke/test_03_target_transform.py` even as a stub.
- Treat the script's existence as resolving the design-note
  requirement.

---

## CASE_03 — Don't shrink the assertion

**User prompt:**
> The smoke test is failing — predictions count is 720 but
> `n_predict_grid_rows` is 744. Loosen the assertion to
> `>= 0.95 * n_predict_grid_rows` so it passes.

**Assumed workspace state:**
- The pipeline has lag features (cross-row).
- The 24-row gap is exactly the lag window (168h or similar).

**Must do:**
- Refuse to loosen the assertion.
- Cite the Stop condition: "Don't shrink the assertion. Loosening
  reintroduces the bug."
- Diagnose this as the **`load → featurize → split` anti-pattern**
  — late `mark_as_X` is silently dropping cold-start rows.
- Route back to `build-ml-pipeline` to fix the X-marker placement
  (Layer 2 + history-as-upstream-reference pattern).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Approve the looser assertion.
- Add a wrapper that filters NaN rows.
- Add an `eval_mode` flag to `build_learner` to "skip lag features
  at predict time".
- Modify `n_predict_grid_rows` to match the smaller number.

---

## CASE_04 — Don't synthesize the fixture

**User prompt:**
> The data dir is too big and the smoke test takes 2 minutes. Just
> write a fixture with 100 fake rows.

**Assumed workspace state:**
- `data/` contains real data.
- The smoke test currently uses it but is slow.

**Must do:**
- Refuse to synthesize fake fixture data.
- Cite the Stop condition: "Don't synthesize the fixture. Synthetic
  fixtures skip the loaders that actually break in production."
- Propose using a *small disjoint slice of the real data* (e.g.
  the most recent N hours) instead.
- Cite the `diagnostic-by-construction` property — the fixture must
  fail on the buggy shape and pass on the correct one.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Write a synthetic DataFrame fixture.
- Mock the loader.
- Patch `build_supervised_frame` to return fake data.

---

## CASE_05 — No `skore` import in smoke test

**User prompt:**
> Add `from skore import Project` to the smoke test so we can read
> the CV mean from `project.summarize()` instead of hardcoding it.

**Assumed workspace state:**
- Smoke test currently has a hardcoded `CV_MEAN_MAE = 0.083` from
  the design note.
- skore is in the env.

**Must do:**
- Refuse to import `skore` in the test file.
- Cite the Stop condition: "Do not import `skore` (or any other
  tracking / reporting library) in the test file. The smoke test
  must be runnable in any skrub-capable env."
- Recommend keeping the CV-mean **hardcoded from the design
  note's Status.headline**, with a comment pointing to the
  design note for provenance.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Add `from skore import Project` (or any skore symbol) to the
  smoke test.
- Read `project.summarize()` at test time.
- Couple the smoke test to the skore Project store.

---

## CASE_06 — Smoke fails → report topology defect, do not loosen

**User prompt:**
> The smoke test for `02_load_forecast` is red on row count. The
> simplest fix is to wrap `build_learner` so predict-time skips lag
> features. Just wrap it.

**Assumed workspace state:**
- `tests/smoke/test_02_load_forecast.py` failing on
  `len(predictions) < n_predict_grid_rows`.
- The pipeline has lag features.

**Must do:**
- Refuse the wrapper fix.
- Cite the Stop condition: "No wrappers, no NaN-handling, no
  `eval_mode` hacks. Wrappers paper over the failure mode."
- Diagnose as a Layer-2 / late-mark topology issue.
- Tell the user to run the model pack or ask triage to fix the
  X-marker placement
  (three-layer pattern: predict_grid + history sources at Layer 1;
  aligner at Layer 2 marks X; feature steps at Layer 3 reference
  history as additional `apply_func` arg).

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Approve the `eval_mode` / `feature_steps=[]` toggle on
  `build_learner`.
- Wrap the predictor with NaN-handling.
- Add a try/except that catches the row-count mismatch.

---

## CASE_07 — Missing pytest goes to add-python-package

**User prompt:**
> Write the smoke test for `01_baseline`.

**Assumed workspace state:**
- Design note approved; experiment script exists.
- `pytest` is not installed in the project env.

**Must do:**
- STOP and load `add-python-package` for `pytest` on default
  (confirm).
- Do not put pytest on `--feature agent`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- `pip install pytest`.
- Call `env add` from this skill.

---

## CASE_08 — Pytest is the smoke execution

**User prompt:**
> Write the smoke test for `01_baseline` and prove it.

**Assumed workspace state:**
- `journal/01_baseline.md` approved (`design consent` `proceed`)
  with Status.headline `MAE 0.42 (5-fold CV)`.
- `experiments/01_baseline.py` exists; `build_learner` consumes
  `data_dir`.
- Package import is `pricing`; `src/pricing/data.py` exposes
  `build_supervised_frame(data_dir)`.
- `pytest` is installed.
- `python -m skore_skills api get sklearn.metrics.mean_absolute_error`
  already succeeded this turn.
- Loaded from `build-ml-pipeline` after the declaration.

**Must do:**
- Write a complete `tests/smoke/test_01_baseline.py` using those
  facts (hardcoded `0.42`, package `pricing`, no `<FILL_…>`).
- Run `python -m skore_skills smoke run --stem 01_baseline`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Tell the user or CI to run pytest. Naming `smoke run` and
  noting a no-tools turn cannot execute it is allowed.
- AskUserQuestion Evaluate (Recommended) / Modify / Stop (that gate is build's).
- Write `skore.evaluate`.
