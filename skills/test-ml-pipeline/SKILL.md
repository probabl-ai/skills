---
name: test-ml-pipeline
description: >
  Owns the `tests/` folder of an ML workspace and the pairing
  rule between an experiment and its tests. Lightweight router:
  every test category has its own subskill (`smoke-test-ml-pipeline`
  is the only one for v1; `regression-test-ml-pipeline` /
  `distribution-test-ml-pipeline` etc. plug in as siblings as the
  workspace grows). This skill places an empty `tests/<category>/`
  folder, enforces the stem-pairing rule between
  `tests/<category>/test_NN_<short_name>.py` and
  `experiments/NN_<short_name>.py`, and dispatches to the matching
  subskill when the user asks for a test.

  TRIGGER when: a new design note was just approved by
  `iterate-ml-experiment` and the matching test has to be drafted
  before the experiment can be marked done; the user asks "write
  the smoke test for `02`", "add the regression test", "do we have
  a test for X?"; an experiment script was edited and the
  paired test needs revisiting; about to run `pytest tests/`
  and one of the expected paired tests is missing.

  SKIP when: the design note does not yet exist (route to
  `iterate-ml-experiment` first); the test is for the package's
  internal helpers and unrelated to a specific experiment (regular
  unit tests live wherever the project's `pytest` config picks
  them up — out of scope here); the question is *what does the
  test result mean* rather than *should the test exist* (route to
  the matching subskill).

  HOW TO USE: this skill is a router. Read the dispatch table to
  figure out which subskill owns the test category the user is
  asking about, then hand off. Do not write the test body
  yourself — that belongs to the subskill. Do place the empty
  test file with the matching stem and the pytest scaffolding,
  then hand control over.
---

# Test ML Pipeline (router)

Where tests for an ML workspace live, what gets paired with what,
and which subskill owns the body of each test category.

## First action (every turn)

Before answering anything else:

1. **Confirm an approved design note exists** for the test
   the user is asking about. The pairing rule is hard:
   `tests/<category>/test_NN_<short_name>.py` only exists if
   `journal/NN_<short_name>.md` is at least `approved` and
   `experiments/NN_<short_name>.py` is the matching script. If
   the design note doesn't exist, hand back to `iterate-ml-experiment`.
2. **Emit the Pre-flight checklist** (below) as visible text in
   your response, with each box marked.
3. **Use the Dispatch table** to pick the subskill that owns the
   test category, then hand off.

## Pre-flight — emit this checklist as visible text before any test work

```
Pre-flight (test-ml-pipeline):
- [ ] `journal/NN_<short_name>.md` exists and is at least `approved`
      (or confirmed n/a — about to hand off to `iterate-ml-experiment`)
- [ ] `experiments/NN_<short_name>.py` exists with the matching stem
      (or confirmed n/a — about to hand off to `organize-ml-workspace`)
- [ ] Test category picked: smoke | regression | distribution | …
- [ ] Subskill dispatched: `smoke-test-ml-pipeline` | …
- [ ] Test file stem decided: `tests/<category>/test_NN_<short_name>.py`
- [ ] pytest is on the project's dependency manifest (per
      `data-science-python-stack` § Tier 1)
```

## Stop conditions — read before anything else

- **No test without an approved design note.** Never create
  `tests/<category>/test_NN_*.py` if the matching `journal/NN_*.md`
  isn't on disk and at least `approved`. The design note is the contract;
  the test asserts the contract holds. Reverse order is incoherent.
- **The stem rule is hard.** Test file basename is
  `test_NN_<short_name>.py` (with the `test_` prefix that pytest
  expects); the `NN_<short_name>` portion matches the experiment
  exactly. One experiment → one test file per category. No
  `test_<NN>_v2.py`, no `test_NN_<short_name>_2.py`. If a test
  needs to evolve, edit it in place; the pairing must stay 1:1.
- **One subskill per category.** This skill only places the empty
  test file and hands off. Don't write assertion bodies, fixture
  construction, or test-specific logic in this skill — that belongs
  to the matching subskill (`smoke-test-ml-pipeline`, etc.).
- **pytest is the runner.** Tests are pytest tests, not
  jupytext-style `# %%` scripts. The experiment scripts live in
  `experiments/` and stay `# %%`-style for interactive iteration;
  the tests are binary pass/fail and benefit from pytest's
  reporting. Don't mix the two conventions.

## Layout this skill owns

```
project/
└── tests/
    ├── smoke/
    │   ├── test_01_baseline.py        # ↔ experiments/01_baseline.py
    │   ├── test_02_short_name.py
    │   └── ...
    └── (future: regression/, distribution/, …)
```

The pairing rule:

```
journal/NN_<short_name>.md
experiments/NN_<short_name>.py
tests/<category>/test_NN_<short_name>.py
```

— same `NN_<short_name>` stem in all three. The `test_` prefix on
the test file basename is the pytest naming convention; everything
after it tracks the experiment.

The `tests/<category>/` subfolder lets the workspace grow more
test types without renaming anything. `tests/smoke/` is the only
required category for v1.

## Test categories — Dispatch table

Use the user's signal first; fall back to the defaults at the
bottom.

| Situation | Subskill |
|---|---|
| Brand-new experiment was just approved; need to wire its smoke test | `smoke-test-ml-pipeline` |
| User says "write the smoke test for `02`", "the smoke test is failing", "what should the smoke test for X assert?" | `smoke-test-ml-pipeline` |
| User says "the metrics drifted between `02` and `03`, can we lock that in?", "regression test against last week's run" | `regression-test-ml-pipeline` *(future — not implemented in v1)* |
| User says "predictions are out of range", "calibration looks off in production", "schema invariants" | `distribution-test-ml-pipeline` *(future — not implemented in v1)* |
| User asks an open-ended "should this experiment have a test?" | **Default to `smoke-test-ml-pipeline`** — the smoke test is required at every iteration; everything else is opt-in. |

The current implementation only ships `smoke-test-ml-pipeline`.
Future categories will land as sibling subskills; the dispatch
table is the contract for adding them.

## The required-test-per-experiment rule

**Every approved experiment must have a passing smoke test before
it can be marked `done` in `JOURNAL.md`.** This is enforced by
`iterate-ml-experiment` § 3 (after design-note approval, before script
creation) and § 4 (before recording outcome): the test is part of
the iteration loop, not an afterthought. If the smoke test fails,
the iteration that follows is on the **pipeline** (re-enter
`build-ml-pipeline`), not on the model — a smoke-test failure is
almost always a structural problem with how the DataOps graph is
laid out, not a metric problem with the predictor.

The smoke test is **non-optional** for every experiment in the
workspace. Other test categories (regression, distribution, …) are
opt-in and added when the workspace's needs warrant them.

## Decision flow

1. Is there an approved `journal/NN_<short_name>.md` and a matching
   `experiments/NN_<short_name>.py`?
   - **No** → hand off to `iterate-ml-experiment` (design note first) or
     `organize-ml-workspace` (script first). Stop.
   - **Yes** → continue.
2. Identify the test category from the user's signal (Dispatch
   table). Default: `smoke`.
3. Place the empty test file at
   `tests/<category>/test_NN_<short_name>.py` with the pytest
   scaffolding (one `def test_*():` function, empty body, a
   `# TODO: filled in by <subskill>` marker). If the file already
   exists, do **not** overwrite.
4. Hand off to the subskill (`smoke-test-ml-pipeline` etc.). The
   subskill writes the assertions, fixture construction, and any
   helpers it needs.
5. Confirm with the user that the subskill's draft is correct
   before running the test (the subskill owns this loop; this
   skill only does placement + dispatch).

## What this skill does NOT do

- Run pytest. Test execution is the user's call (or CI's).
- Write assertion bodies. Each subskill owns the assertions for
  its category.
- Decide whether a test is required. The required-test-per-experiment
  rule (smoke at every iteration) is fixed by this skill; *adding*
  optional categories is a workspace-level decision the user makes,
  not this skill.
- Touch files outside `tests/`. The companion-skill edits to
  `iterate-ml-experiment` / `organize-ml-workspace` /
  `build-ml-pipeline` / `evaluate-ml-pipeline` are on those skills,
  not this one.

## Companion skills

- **`smoke-test-ml-pipeline`** — owns the smoke test contract
  (fixture construction, the diagnostic-by-construction property,
  assertions, failure semantics). The only required test category
  in v1.
- **`organize-ml-workspace`** — scaffolds `tests/<category>/`
  alongside `journal/` / `experiments/` at workspace creation time.
  The placeholder test files are placed by this skill, not by
  `organize-ml-workspace`.
- **`iterate-ml-experiment`** — drives the iteration loop. After
  design-note approval, dispatches to this skill (which dispatches to
  `smoke-test-ml-pipeline`) to draft the matching test. After
  the experiment runs, requires the smoke test to pass before the
  experiment can flip to `done`.
- **`build-ml-pipeline`** — pipeline declaration. The smoke test
  is the executable proof that `build-ml-pipeline`'s X-marker
  rule (mark X early, featurize after, history references via
  upstream nodes) was followed. Smoke test failure typically
  means the pipeline shape is wrong; route back here.
- **`evaluate-ml-pipeline`** — owns the CV protocol. CV is
  necessary but not sufficient when the pipeline has
  history-dependent features; `smoke-test-ml-pipeline` fills the
  gap CV doesn't.
- **`data-science-python-stack`** — declares pytest as a Tier 1
  mandatory dependency for any workspace that uses this skill.
