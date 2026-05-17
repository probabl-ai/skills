---
name: data-scientist-companion
description: >
  Front door for an ML / data-science session. Single
  responsibility: read the workspace state on the opening turn,
  pick the right *first* skill to dispatch to, and hand off.
  Never writes a file, never runs a command, never authors a
  design note. Once a sibling skill is dispatched the
  conversation moves into that skill's loop; this skill does not
  re-enter the same turn.

  TRIGGER when (any of these — and only on the opening turn of a
  session, before any sibling skill has been dispatched):
  (1) the current working directory looks ML-ish (any of
      `pyproject.toml` referencing sklearn / skrub / skore,
      `journal/JOURNAL.md`, `experiments/`, `src/<pkg>/pipeline.py`)
      and the user's first message is generic ("let's get
      started", "where do I begin?", "resume", "what's next");
  (2) the user opens with project-level framing — "I want to
      build a model for X", "I have a CSV and want to predict
      Y", "I want to use sklearn / skrub / skore for Z", "help
      me set up an ML project" — without already hitting a
      specific sibling skill's TRIGGER;
  (3) the user explicitly asks "what skills are available?",
      "what can you do here?", "how do I use this set of
      skills?" in an ML context.

  SKIP when: the user's first message clearly fires a sibling
  skill's TRIGGER on its own — pipeline declaration / editing
  (`build-ml-pipeline`), CV / metrics / "score this"
  (`evaluate-ml-pipeline`), "what's the signature of X?"
  (`python-api`), "install X" / `ImportError`
  (`python-env-manager`), "which library for X?"
  (`data-science-python-stack`), "write the smoke test for X"
  (`test-ml-pipeline`); a sibling skill has already been
  dispatched this turn or earlier in the session; the project
  is non-Python or non-ML.

  HOW TO USE: read the workspace state (one shallow `ls` of the
  project root + targeted reads of `pyproject.toml` and
  `journal/JOURNAL.md` if present — no deep walk), emit the
  Pre-flight checklist as visible text, then use the Dispatch
  tables to pick the entry skill and hand off via `Skill(...)`.
  Stop there. Do not author code, scaffold folders, or run any
  command — every action belongs to a sibling.
---

# Data Scientist Companion (router)

The opening turn of an ML / data-science session: detect what
state the workspace is in, decide which sibling skill owns the
user's first ask, and hand off. After dispatch, the sibling's
own TRIGGER / SKIP / HOW TO USE blocks take over — they already
route between each other internally.

## First action (every turn)

Before answering anything else:

1. **Run a shallow workspace probe**: one `ls` of the project
   root, plus `Read` on `pyproject.toml` and
   `journal/JOURNAL.md` if either exists. Do not walk
   `src/`, `experiments/`, or `data/` recursively — depth is
   the sibling skills' concern.
2. **Emit the Pre-flight checklist** (below) as visible text in
   your response, with each box marked.
3. **Pick the entry skill** using the Dispatch tables — user
   signal first, then workspace state.
4. **Hand off** via a `Skill(...)` call and stop. Do not author
   anything in this turn.

## Pre-flight — emit this checklist as visible text before dispatch

```
Pre-flight (data-scientist-companion):
- [ ] Workspace probed: <pyproject.toml present? journal/ present?
      src/<pkg>/ present? experiments/ present?>
- [ ] Tier 1 libs decision deferred to `data-science-python-stack`
      / `python-env-manager` (this skill does not check imports)
- [ ] User signal classified: <one of the rows in Dispatch table B,
      or "generic / project-level">
- [ ] Entry skill picked: <one of the 11 siblings>
- [ ] Handoff via `Skill(<entry-skill>)` is the next call
```

## Stop conditions — read before anything else

- **Route, don't implement.** Never write a file, run a command,
  install a package, scaffold a folder, author a design note, or
  write pipeline code in this skill. If you catch yourself
  reaching for `Write`, `Edit`, `Bash` (other than the one
  shallow `ls`), or `AskUserQuestion` for anything beyond
  picking between two routes — STOP and dispatch.
- **One-shot, not always-on.** This skill fires on the *opening*
  turn. Once a sibling has been dispatched, you are done; the
  conversation moves into the sibling's loop. Do not re-enter
  the same turn, and do not re-route between siblings mid-flow —
  the siblings handle their own handoffs.
- **Detect, don't assume.** The workspace state determines the
  default route. A `journal/JOURNAL.md` means iteration is in
  progress and `iterate-ml-experiment` owns the next move. No
  `pyproject.toml` means env / stack / scaffolding come first.
  A populated `src/<pkg>/` with no `journal/` means scaffolding
  is incomplete. Read first, route second.
- **Defer ambiguity to the user.** If two routes are equally
  valid (e.g., a half-scaffolded workspace where the user could
  either finish setup or open their first experiment), ask the
  user with `AskUserQuestion` *before* dispatching. Don't pick
  silently.
- **No memory-based dispatch.** If the user names a symbol or
  library you'd otherwise look up, the dispatch is still
  `python-api` — don't answer the symbol question yourself.

## Dispatch table A — by workspace state (the default route)

Walk top-to-bottom; the first matching row wins. Use this when
the user's message is generic or project-level (no specific
signal from table B).

| Workspace state | Entry skill |
|---|---|
| No `pyproject.toml`, no `src/`, no `experiments/`, no `journal/` — empty / brand-new directory | `python-env-manager` (bootstrap pixi by default) → then `data-science-python-stack` → then `organize-ml-workspace` |
| `pyproject.toml` exists but the project hasn't picked a tabular library or installed Tier 1 (sklearn / skrub / skore) | `data-science-python-stack` |
| Env + stack settled, but no `src/<pkg>/`, no `experiments/`, no `journal/` | `organize-ml-workspace` |
| `src/<pkg>/` populated but no `journal/JOURNAL.md` | `organize-ml-workspace` (it owns dropping the empty `JOURNAL.md`) |
| `journal/JOURNAL.md` exists (even if empty / placeholder) | `iterate-ml-experiment` |

## Dispatch table B — by user signal (takes priority when present)

Match the user's first message against this table before falling
back to table A. A clear user signal always wins over the
default workspace route.

| User signal | Entry skill |
|---|---|
| "what's the signature of X?", "what does X return?", "how do I call …?", "which submodule owns Y?" | `python-api` |
| "install X", "X is missing", "`ImportError`", "add Y to deps", "which env manager does this project use?" | `python-env-manager` |
| "which library for X?", "pandas vs polars?", "should I use xgboost / mlflow?" | `data-science-python-stack` |
| "fit and score this", "cross-validate", "give me metrics for X", "what's the right CV here?" | `evaluate-ml-pipeline` |
| "build a pipeline for X", "add a preprocessor / encoder / scaler", "wire up an estimator", "swap step Y in the pipeline" | `build-ml-pipeline` |
| "set up the project", "scaffold a workspace", "where should this file live?", "new experiment file vs. edit existing?" | `organize-ml-workspace` |
| "what's next", "resume", "where were we", "propose the next experiment", "let's iterate", "record the outcome of X" | `iterate-ml-experiment` |
| "lint", "format", "run ruff", "docstring style" | `python-code-style` |
| "write the smoke test for X", "the smoke test is failing", "do we have a test for Y?" | `test-ml-pipeline` |

If two rows seem to match (e.g., "build the pipeline and tell me
what the right CV is"), pick the **earlier-in-the-loop** entry —
build before evaluate, evaluate before iterate, etc. The sibling
will dispatch onward when its work is done.

## Decision flow

1. **Probe** the workspace (one shallow `ls` + the two targeted
   `Read`s above).
2. **Classify the user signal**. Is the first message
   specific enough to match a row in table B? If yes, dispatch
   there.
3. **Otherwise dispatch by workspace state** (table A, top-to-
   bottom).
4. **Ambiguous?** Ask the user with `AskUserQuestion`
   (2-4 options, one per candidate sibling). Pick the dispatch
   from the answer.
5. **Hand off** via `Skill(<entry-skill>)` and stop.

## What this skill does NOT do

- **Implement anything.** No scaffolding (→ `organize-ml-workspace`),
  no pipeline code (→ `build-ml-pipeline`), no evaluation
  (→ `evaluate-ml-pipeline`), no tests (→ `test-ml-pipeline`),
  no installs (→ `python-env-manager`), no lint runs
  (→ `python-code-style`), no design notes
  (→ `iterate-ml-experiment`).
- **Re-route between siblings.** Once a sibling owns the turn,
  it manages its own handoffs (every sibling carries a TRIGGER /
  SKIP block and a Companion-skills section). Don't second-guess
  from the outside.
- **Answer API questions.** Even if the user opens with "what's
  the signature of `cross_validate`?", dispatch to `python-api` —
  don't recall the signature from memory.
- **Pick the strategy for `iterate-ml-experiment`.** The
  `iterate-from-*` sub-skills are picked inside
  `iterate-ml-experiment`'s sourcing menu, not here.

## Companion skills — the full set this skill dispatches to

ML pipeline lifecycle:

- **`build-ml-pipeline`** — declare the pipeline (data source →
  predictor) as a skrub DataOps graph. Stops at the declared
  object.
- **`evaluate-ml-pipeline`** — evaluate a single sklearn-
  compatible learner via skore. Picks the entry point and the
  cross-validator.
- **`test-ml-pipeline`** — router for the workspace's `tests/`
  folder. Dispatches to `smoke-test-ml-pipeline` (the only
  category in v1).
- **`smoke-test-ml-pipeline`** — diagnostic-by-construction
  pytest that proves the X-marker rule.

Iteration loop:

- **`iterate-ml-experiment`** — owns `journal/JOURNAL.md` and
  per-experiment design notes; drives the propose / approve /
  implement / record loop.
- **`iterate-from-skore`** — sources the next experiment from
  `report.diagnosis()` on the previous run. Picked inside
  `iterate-ml-experiment`'s sourcing menu, not here.
- **`iterate-from-user`** — sources the next experiment from
  user input (free-text / article / resource link). Same
  picking rule as above.

Workspace and tooling:

- **`organize-ml-workspace`** — file layout, `# %%` script
  convention, where reports live, one-file-per-experiment rule.
- **`python-code-style`** — ruff (lint + format) + numpydoc.
  Runs after Python files are touched.
- **`python-env-manager`** — detects the project's env manager
  (pixi / uv / poetry / hatch / conda / pip+venv) and issues
  the right install command. Defaults to pixi when bootstrapping.
- **`data-science-python-stack`** — opinionated one-library-per-
  job stack, tiered into mandatory / user-choice / optional /
  transitive.

API reference:

- **`python-api`** — API discovery for any installed Python
  package: `inspect.signature`, `dir`, versioned-docs search +
  cache. Carries conceptual orientation for sklearn / skrub /
  skore.
