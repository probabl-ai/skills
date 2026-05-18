---
name: organize-ml-workspace
description: >
  Decide where files live in an ML experimentation project: reusable
  code in `src/<pkg>/`, one `# %%` script per experiment in
  `experiments/`, design notes + index in `journal/`, reports in
  `reports/`, agent-only probes in `scratch/`, narrative digest in
  `overview/summary.md`. Owns the layout, the file-creation rules
  (one file per experiment, ask before editing), and the jupytext
  `# %%` script convention. Never imposes `data/` — the user owns
  that.

  TRIGGER — any of:
  - Starting a new ML project / scaffolding a workspace.
  - About to create the first experiment file in a project.
  - About to create `src/<pkg>/data.py` / `features.py` /
    `pipeline.py` / `evaluate.py` for the first time.
  - About to write a `.ipynb` for experimentation — redirect to a
    `# %%` script under `experiments/`.
  - User asks where something should live, how to organize the
    project, or how to set up the workspace.
  - About to add a new experiment iteration — decide new file vs
    edit existing (ask the user).

  SKIP when: the file is clearly part of an already-populated
  module (e.g., adding a function to existing `features.py`); pure
  refactor inside a single existing file; pipeline declaration
  mechanics (`build-ml-pipeline`); evaluation mechanics
  (`evaluate-ml-pipeline`); skore symbol lookup (`python-api`).

  HOW TO USE: **first run the Detection table** below — if any
  signal matches, glue to existing conventions (do not rename or
  move folders). If no signal matches, scaffold the default
  layout. **Emit the Pre-flight checklist as visible text and read
  the Stop conditions before any file is created or edited.** Use
  templates in `templates/`; copy and adapt, do not rewrite from
  scratch.
---

# Organize ML Workspace

Where things live, when to create a new file, what each file is
allowed to contain.

## First action — track sibling reads (not a blocking gate)

Maintain this read-set as you work. Open each sibling SKILL.md
**just-in-time** when a step in this skill calls for it (e.g. open
`python-env-manager` before G-ENV-MGR; open `iterate-ml-experiment`
before handing off the design-note write). Do not pre-read all nine
at session start — that produces paralysis.

Emit this tracker as visible text once per turn:

```
Sibling skills (open just-in-time when a step requires):
  - data-science-python-stack, python-env-manager, python-api,
    python-code-style, iterate-ml-experiment, build-ml-pipeline,
    evaluate-ml-pipeline, test-ml-pipeline, smoke-test-ml-pipeline
```

## Stop conditions — read before anything else

- **Missing dependency.** If `import skore` raises, STOP. Invoke
  `python-env-manager` for the install command. Do not drop
  `skore.Project` in favor of `mlflow` / pickles / "just print
  metrics" — the workspace contract assumes a Project on disk.
- **Symbol from memory is forbidden.** Any `skore.Project` /
  `project.put` / `skore.evaluate` signature must come from a
  `python-api` call this turn.
- **Existing layout wins — detect first.** Run the Detection table
  before scaffolding. Don't rename, relocate, or "tidy up"
  existing folders.
- **Notebooks are not silent.** Existing `.ipynb` files in the
  experiment folder → surface the convention shift and ask. Don't
  auto-convert.
- **Scratch is read-only against the skore Project.** Probes under
  `scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` may call
  `project.get(...)`, `project.summarize()`, and walk an existing
  report. They **MUST NOT** call `skore.evaluate(...)` or
  `project.put(...)` — those are experiment-script-only. **When
  `project.get(key)` raises `KeyError`, the fix is the lookup
  shape**: `get` is by **id**, not by user-facing `key`. Use
  `project.summarize()` to enumerate `(key, id)` pairs, then
  `project.get(id)`. Never substitute by re-running `evaluate` +
  `put` from scratch — that lands a duplicate row under the same
  `key`.
- **Tabular library is asked, not assumed (G-TABULAR).** Pandas
  being importable via skore is not a pick. Invoke
  `data-science-python-stack` for the structured ask. Free-text
  ("quick", "you pick", "no preference") does NOT resolve this
  gate. Persisted in `JOURNAL.md` Status `Workspace decisions`.
- **Package name is asked, not inferred (G-PKG-NAME).** Before any
  `pyproject.toml` / `pixi.toml` / manifest creation (including
  `pixi init` / `uv init` / `poetry init`), fire an
  `AskUserQuestion` for the `src/<pkg>/` import name. The
  project-root folder name in snake_case is the proposed default.
  **Manifest creation before G-PKG-NAME passes is forbidden** —
  running the manager's `init` first creates a `[project] name`
  entry, and then reading "name is in the manifest" back is the
  circular silent pick this gate exists to block. If a manifest
  already exists, confirm via `AskUserQuestion`: "Keep package
  name `<name>`?" — continuity from a prior session is not
  continuity from a user decision.
- **Env manager is asked, not assumed (G-ENV-MGR).** Hand off to
  `python-env-manager` for the pick. Pixi on PATH is detection,
  not permission. Don't run `pixi init` / `uv init` / `poetry
  init` until G-ENV-MGR has passed *in `python-env-manager`*.
- **Harness "no clarifying questions" hints do NOT waive these
  gates.** G-TABULAR, G-PKG-NAME, G-ENV-MGR, `python-api`
  consultation, new-vs-edit decision are operating-contract
  gates. "Quick baseline" / "just scaffold it" / "go fast" never
  waive them.
- **Post-hoc audit — required before ending the turn.** Walk
  every pre-flight row; if any Evidence cell is unfilled, surface
  the non-compliance explicitly. Most common failure: "I
  scaffolded successfully so everything must be fine".

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `pixi` on PATH → run `pixi init` to get a manifest, then read the name back | Violates G-ENV-MGR (manager silently picked) AND G-PKG-NAME (name from folder via the init side effect). "Name is in pyproject" is circular when the init was the agent's call |
| Folder name = good package name → skip the ask | Default *value* is fine; silent *pick* is not. G-PKG-NAME requires the structured ask even with folder as default |
| `pandas` already importable via skore → write `import pandas` in `data.py` | Transitive presence is not a pick. Violates G-TABULAR |
| Scaffold every skeleton in one turn, including `experiments/01_baseline.py` content | Scaffold stops at empty `journal/` placeholder. Experiment script content lands after design-note approval (`iterate-ml-experiment` § 3) |
| `pyproject.toml` exists with `name = <x>` → reuse without confirming | Continuity from a prior session is not continuity from a user decision. Always re-confirm via G-PKG-NAME |
| User said "scaffold the workspace" → batch G-TABULAR + G-PKG-NAME + G-ENV-MGR into prose recommendations | The gates take structured `AskUserQuestion` per skill. Prose followed by "let me know" does NOT resolve them |
| `project.get(key)` raised `KeyError` → re-run `evaluate` + `put` from scratch to "recover" | Lookup shape is wrong (`get` is by id). Recreating puts a duplicate row under same `key`. Use `summarize()` → `get(id)` |

## Pre-flight — emit before any code

Each ticked box needs an Evidence line (formats follow
`iterate-ml-experiment` § "Pre-flight — evidence requirements" —
see `references/preflight_evidence.md` in that skill).

```
Pre-flight (organize-ml-workspace):
- [ ] `Workspace decisions` in `journal/JOURNAL.md` Status checked
      for pre-recorded gates (tabular, env_manager, package)
      Evidence: lists each <gate>: <value | not recorded>
                | "n/a — JOURNAL.md does not exist yet (truly fresh)"
- [ ] Tier 1 mandatory libs importable: sklearn, skrub, skore
      Evidence: Write scratch/<ts>_check_tier1.py with
                `import sklearn, skrub, skore` + `pixi run python
                scratch/<ts>_check_tier1.py` output.
                **Inline `python -c` is NOT evidence** (see
                `python-api` § Stop conditions).
- [ ] Layout detection done: <existing | fresh>
      Evidence: ls/Glob on project root + matched signal from Detection
- [ ] Tabular library decided (G-TABULAR): pandas | polars
      Evidence: AskUserQuestion id=<id> via data-science-python-stack |
                JOURNAL.md Status (Workspace decisions) | user quote turn N
- [ ] Env manager decided (G-ENV-MGR)
      Evidence: AskUserQuestion id=<id> via python-env-manager |
                JOURNAL.md Status (Workspace decisions)
- [ ] Package name resolved (G-PKG-NAME): <name>
      Evidence: AskUserQuestion id=<id>, answer=<name> |
                JOURNAL.md Status (Workspace decisions) |
                existing manifest's [project].name **confirmed via AskUserQuestion**
                (reading the manifest alone is NOT sufficient)
- [ ] `pyproject.toml` present at root declaring `src/<pkg>/`;
      editable install wired via `python-env-manager` § "Editable workspace"
      Evidence: Read pyproject.toml (this turn) + manager's editable-install call
- [ ] python-api consulted for: Project, put, evaluate
      Evidence: Read scratch/api/skore/<v>/{project_local,evaluate}.md
                | Write of the same files (this turn)
                | "n/a — symbols already in workspace cache"
- [ ] Decision: new experiment file vs edit existing (asked the user
      if this is an iteration)
      Evidence: AskUserQuestion id=<id> | user quote turn N |
                "n/a — first experiment in a fresh workspace"
- [ ] `journal/` scaffolded with empty placeholder JOURNAL.md
      Evidence: Write journal/JOURNAL.md (this turn) | "already exists"
```

## Scope

- **In scope:** detection of existing layout, scaffolding of fresh
  layout, the `experiments/` convention (`# %%`, one file per
  experiment), `evaluate.py` contract, `reports/` location.
- **Out of scope:** what to put inside `pipeline.py`
  (`build-ml-pipeline`), how to call `skore.evaluate`
  (`evaluate-ml-pipeline`), skore/skrub/sklearn symbols
  (`python-api`), data ingestion paths (user-owned).

## Detection — existing workspace first

Before scaffolding, look at the project root:

| Signal | Meaning |
|---|---|
| `pyproject.toml` with `[project] name = ...` and `[tool.setuptools.packages.find]` (or `[tool.poetry.packages]`, `[tool.hatch.build.targets.wheel]`) | Package declared and installable — use this name; verify editable install via `python-env-manager` |
| `pixi.toml` / `[tool.poetry]` / `[tool.uv]` with a name but **no** `pyproject.toml` `[project]` table | Manager knows the project but the package isn't installable — flag, offer to add `pyproject.toml` |
| `src/<pkg>/__init__.py` or `<pkg>/__init__.py` at root | Package dir already chosen — keep it |
| `<pkg>.egg-info/` at root or under `src/` | Stale or out-of-band `pip install -e .` ran; flag drift, offer to wire through the manager |
| `experiments/`, `notebooks/`, `scripts/`, `analyses/` | Experiment location chosen — keep it |
| `journal/`, `plans/`, `proposals/` | Journal location chosen — keep it |
| `reports/`, `results/`, `runs/` | Report location chosen — keep it |
| `tests/` | Test location chosen — keep it; per-category subfolders owned by `test-ml-pipeline` |
| `mlflow.db` / `mlruns/` at root | Tracker artifacts from prior work — leave alone, skore is canonical. Note once, move on. |
| `.ipynb` files in the experiment folder | User is on notebooks — do not silently switch to scripts; surface the shift and ask |

**Any signal present → glue to the existing convention.** No renames, no relocates. **None present → fresh scaffold** per below.

## Default layout (fresh workspace)

```
project/
├── pyproject.toml          # declares src/<pkg>/ as installable
├── <manager manifest>      # pixi.toml / poetry / uv / hatch / environment.yml
│                           # (runtime deps; pyproject.toml does not carry them)
├── src/<pkg>/
│   ├── __init__.py         # exposes PROJECT_ROOT for CWD-independent paths
│   ├── data.py             # data loading, splits, split_kwargs
│   ├── features.py         # transformers, encoders, feature fns
│   ├── pipeline.py         # the learner declaration (skrub DataOps)
│   └── evaluate.py         # ONLY: CV strategy + optional metric overrides
├── journal/                # iteration log + per-experiment design notes
│   ├── JOURNAL.md          # session-start log; index of experiments
│   └── 01_baseline.md      # one `.md` per planned experiment, same stem
├── experiments/            # one `# %%` script per experiment
│   └── 01_baseline.py
├── tests/
│   └── smoke/              # body owned by smoke-test-ml-pipeline;
│                           # files placed by test-ml-pipeline once
│                           # each design note is approved
├── overview/
│   └── summary.md          # agent-authored narrative; refreshed by
│                           # iterate-ml-experiment § 4
├── scratch/                # agent-only (gitignored entirely)
└── reports/                # skore Project lives here
```

**The package is installable.** `pyproject.toml` declares
`src/<pkg>/` as a Python package; the manager installs it in
**editable** mode so `from <pkg>.pipeline import build_learner`
works from any CWD. Wiring is per-manager — see
`python-env-manager` § "Editable workspace".

**Runtime dependencies (sklearn, skrub, skore, tabular library)
live in the manager's manifest**, not in
`pyproject.toml`'s `[project.dependencies]`. The
`pyproject.toml` template ships with **no runtime deps**.

**Deliberately absent:**

- **No `data/`** — user decides where data comes from. `data.py`
  exposes a loader; the path is a parameter.
- **No `models/`** — persistence is out of scope at this stage.

If the user asks for `data/` or `models/` later, add them — don't
pre-empt.

## File-creation rules

### Design note first, then code

Before creating `experiments/NN_<short_name>.py`, the matching
`journal/NN_<short_name>.md` must exist and have been validated
by the user. Design-note content is owned by
`iterate-ml-experiment`; this skill only enforces the pairing —
same stem, planned-before-coded.

### Three-way stem pairing

Every experiment is identified by `NN_<short_name>` in three places:

```
journal/NN_<short_name>.md            (design note)
experiments/NN_<short_name>.py        (script)
tests/smoke/test_NN_<short_name>.py   (smoke test)
```

By the time it can flip to `done` in `JOURNAL.md`, all three exist.
The design note is written first (`iterate-ml-experiment`); the
script lands on approval; the smoke test body is filled by
`smoke-test-ml-pipeline`. The `test_` prefix is pytest convention;
the `NN_<short_name>` portion matches exactly.

### New experiment → new file. Iterating → ask first.

Default: new file. `02_text_encoder.py`, `03_grouped_cv.py`. The
numeric prefix preserves iteration order under `ls`.

When the user says "let's tweak experiment 02" or "iterate on the
text encoder", **do not assume**. Fire `AskUserQuestion`:

> Should this be a new experiment file (e.g.
> `04_text_encoder_v2.py`) or an in-place edit of
> `02_text_encoder.py`?

In-place edits **overwrite the prior result in the skore Project**
if the same key is reused — flag this if the user picks in-place.
In-place also requires revisiting the matching smoke test (route to
`smoke-test-ml-pipeline`).

## Decision flow (compact — full version in references/scaffold_steps.md)

1. **Read project root.** Detection table matches → glue (stop).
   No match → fresh scaffold (continue).
2. **G-PKG-NAME** structured ask. Folder name in snake_case is the
   proposed default; user confirms or overrides. Record in
   `Workspace decisions`. **No manager `init` until this passes.**
3. **Drop `pyproject.toml`** from `templates/pyproject.toml`,
   substituting `<pkg>`. Hand off to `python-env-manager` for the
   editable install — don't run install commands yourself
   (G-ENV-MGR must pass there first).
4. Create `src/<pkg>/` with skeletons from `templates/src_*.py`
   and `templates/src___init__.py`.
5. Create `experiments/` and seed `01_baseline.py` from
   `templates/experiment.py`, substituting `<pkg>` (the
   `from <pkg> import ...` literals are load-bearing; the other
   placeholders sit in markdown / strings and are filled by
   `iterate-ml-experiment` § 3 later).
6. Create **empty** `tests/smoke/`. Do NOT drop placeholder test
   files — `test-ml-pipeline`'s Stop condition forbids tests
   before the matching design note is approved. Verify pytest is
   on the manifest.
7. Create `journal/` with a one-line **placeholder** `JOURNAL.md`
   (`# PLAN\n\n<!-- placeholder; populated by iterate-ml-experiment -->`).
   `iterate-ml-experiment` rewrites it from its own template.
8. Create `overview/` and drop the placeholder `summary.md` from
   `templates/summary.md`. `iterate-ml-experiment` § 4 rewrites by
   hand on every outcome recording. **No Python in `overview/`** —
   `summary.md` is agent-authored prose, not script output.
9. Create empty `scratch/`. **Do NOT** drop a README — the scratch
   convention is owned by `python-api` § "Scratch traceability".
10. Create empty `reports/` (skore writes into it on first run).
11. **Touch `.gitignore`.** Drop `templates/.gitignore` if none.
    If one exists, surface missing entries as a suggested patch;
    don't auto-edit. **`reports/` is always asked.**
12. **Hand off to `python-code-style` § "Initial setup"** to drop
    `ruff.toml` and run the first ruff pass. Invoking the skill is
    what teaches the NumPyDoc convention — copying the template by
    hand silently drops it.
13. Hand back to the relevant sibling: `iterate-ml-experiment` for
    design-note content, etc.

## Files in src/<pkg>/

Each has a narrow contract:

- **`__init__.py`** — exposes `PROJECT_ROOT` (absolute, derived
  from `__file__`, not CWD). Any module that needs a
  project-relative path imports `PROJECT_ROOT` instead of
  hard-coding `"data"` / `"./data"`. Requires editable install
  (so `__file__` lives in the source tree).
- **`data.py`** — loaders, materialization of `X`, `y`, and any
  `split_kwargs` (groups, time, …) at the X marker. Pipeline
  mechanics: `build-ml-pipeline`.
- **`features.py`** — feature functions and transformers.
- **`pipeline.py`** — the learner declaration (a `SkrubLearner`).
  `build_learner` exposes the source-binding preview as an
  optional keyword (`data_dir_preview=None`) so the experiment
  script can pass an absolute path from `PROJECT_ROOT`.
- **`evaluate.py`** — **only** the inputs to `skore.evaluate`:
  the cross-validator (`splitter = ...`), optional metric
  overrides. Does **not** call `skore.evaluate`, does **not**
  open a `skore.Project`, does **not** persist anything. Those
  belong in the experiment script.

## Experiment scripts — `experiments/NN_*.py`

`# %%` cell markers, not `.ipynb`. The convention is recognized by
VS Code, PyCharm, and `jupytext`.

**What the experiment script does** (template:
`templates/experiment.py` — copy, rename, adapt):

1. Open / attach to the `skore.Project` at `reports/`.
2. Import the learner from `<pkg>.pipeline` and CV from
   `<pkg>.evaluate`.
3. Call `skore.evaluate(...)`.
4. Call `project.put("<experiment-key>", report)`.

Confirm signatures via `python-api`. Cross-validator choice is
`evaluate-ml-pipeline`.

**Experiment scripts stay clean of agent-only `print(...)`.**
Inspection lives in `scratch/`. One exception: a bare `report`
expression in jupytext context — that's a notebook-display side
effect, not a debug print.

**Experiment key convention** — the file's stem (e.g.
`01_baseline.py` → `"01_baseline"`). One file → one key → one
report.

**Project parameters.** `skore.Project(workspace="reports",
name=..., mode="local")`. Pick `name` from project / package name
(`pyproject.toml`), then dataset name, then folder name. Use
kebab-case, reuse across experiments. `mode="local"` by default;
don't switch to other modes without explicit user ask.

## Companion skills

- **`iterate-ml-experiment`** — owns `journal/JOURNAL.md` and the
  per-experiment design notes. This skill places the empty
  `journal/`; that skill fills it.
- **`build-ml-pipeline`** — what goes inside `pipeline.py`,
  `features.py`, `data.py`.
- **`evaluate-ml-pipeline`** — what `splitter` should be in
  `evaluate.py`, and how the experiment script calls
  `skore.evaluate`.
- **`test-ml-pipeline`** — owns `tests/<category>/` layout +
  stem-pairing rule.
- **`smoke-test-ml-pipeline`** — fills the smoke-test body once
  the matching design note is approved.
- **`python-api`** — `skore.Project`, `skore.evaluate`,
  `project.put` signatures. Don't guess.
- **`python-env-manager`** — detection + install commands. Invoke
  whenever Tier 1 is missing, tabular install is needed, or fresh
  scaffolding (default pixi).
- **`data-science-python-stack`** — *what* to install. Pair with
  `python-env-manager` for the *how*.
- **`python-code-style`** — drops `ruff.toml` and runs first
  ruff pass (Decision flow step 12). **Invoke at scaffold time** —
  copying the template by hand drops the NumPyDoc contract.

## Templates

- `templates/experiment.py` — recurring artifact, copied per new
  experiment.
- `templates/summary.md` — placeholder dropped at scaffold;
  rewritten by `iterate-ml-experiment` § 4.
- `templates/pyproject.toml` — declares `src/<pkg>/` as
  installable; runtime deps in manager's manifest.
- `templates/src___init__.py` — package init with
  `PROJECT_ROOT`.
- `templates/src_data.py` / `src_features.py` / `src_pipeline.py` /
  `src_evaluate.py` — one-time skeletons.
- `templates/.gitignore` — dropped at scaffold if none exists.

**Copy, don't rewrite.** Section names and structure encode the
contracts.

## References (load on demand)

- `references/scaffold_steps.md` — full prose elaboration of the
  13-step Decision flow with examples and rationale.
