---
name: organize-ml-workspace
description: >
  Decide where files live in an ML experimentation project: where the
  reusable code goes, where each experiment goes, where reports are
  persisted. Owns the layout, the file-creation rules (one file per
  experiment, ask before editing an existing one), and the
  jupytext-style `# %%` script convention. Stops at "the file exists
  in the right place with the right skeleton". Never imposes a
  `data/` layout — the user owns that.

  TRIGGER when: starting a new ML project / scaffolding a workspace;
  about to create the first experiment file in a project; about to
  create `src/<pkg>/data.py`, `features.py`, `pipeline.py`, or
  `evaluate.py` for the first time; about to write a Jupyter
  notebook (`.ipynb`) for experimentation — redirect to a `# %%`
  script under `experiments/`; user asks where something should
  live, how to organize the project, or how to set up the workspace;
  about to add a *new experiment iteration* (must decide: new file
  vs. edit existing — ask the user).

  SKIP when: the file is clearly part of the package's existing
  module (e.g., adding a function to an already-populated
  `features.py`); pure refactor inside a single existing file;
  pipeline declaration mechanics (`build-ml-pipeline`); evaluation
  mechanics (`evaluate-ml-pipeline`); skore symbol lookup
  (`skore-api`).

  HOW TO USE: **first detect whether a workspace is already in
  place**. If yes, glue to its conventions (do not rename or move
  existing folders). If no, scaffold the default layout below
  (omitting `data/`, `models/`, `tests/`). **Read the "Stop
  conditions" block at the top of the body and emit the Pre-flight
  checklist as visible text in your response — both are mandatory
  before any file is created or edited.** Use the templates in
  `templates/` as the starting content — copy and adapt; do not
  rewrite from scratch. For each new experiment, default to a new
  file in `experiments/`; when the user says "iterate on X", **ask**
  whether to fork into a new file or edit in place.
---

# Organize ML Workspace

Where things live, when to create a new file, what each file is
allowed to contain. Pipeline mechanics, evaluation mechanics, and
skore/skrub/sklearn symbols are out of scope and live in the
sibling skills.

## Stop conditions — read before anything else

- **Missing dependency.** If `import skore` raises in this project's
  env, STOP. **Invoke `python-env-manager`** to detect the manager
  and produce the right install command (the project may not use
  pixi); surface the command to the user and wait for confirmation.
  **Do not drop the `skore.Project` from the experiment script** in
  favor of `mlflow`, ad-hoc pickles, or "just print the metrics" —
  the workspace contract assumes a Project on disk. See
  `data-science-python-stack` § "Missing dependency".
- **Symbol from memory is forbidden.** Any `skore.Project` /
  `project.put` / `skore.evaluate` signature you write must come
  from a `Skill(skore-api)` call **in this turn**. Don't infer
  parameter names from memory.
- **Existing layout wins — detect first.** Run the detection table
  in § "Detection" before scaffolding. Do not rename, relocate, or
  "tidy up" existing folders. Adding files in the wrong location is
  worse than asking.
- **Notebooks are not silent.** If existing `.ipynb` files are
  present in the experiment folder, do not auto-convert to `# %%`
  scripts. Surface the convention shift and ask.
- **Tabular library is asked, not assumed.** Even though `pandas` is
  already pulled in by `skore`, do not silently target it in
  scaffolded code. Ask the user at project start: pandas (free, no
  extra install) or polars (adds an explicit install)? Both are
  valid; one must be the project's chosen tabular library before
  any `data.py` / experiment script is generated. See
  `data-science-python-stack` § "Tier 2 — User choice".

## Pre-flight — emit this checklist as visible text before any code

Before scaffolding or editing any file, output the following block
verbatim in your response. Each box must be backed by an actual
tool call or an explicit decision documented in the response.

```
Pre-flight (organize-ml-workspace):
- [ ] Tier 1 mandatory libs importable in this env: sklearn, skrub, skore
      (per `data-science-python-stack` § "Tier 1")
- [ ] Tabular library decided + installed: pandas (free via skore) |
      polars (added explicitly) — asked the user when scaffolding fresh
- [ ] Layout detection done: <existing | fresh>
- [ ] Package name resolved: <name> (source: pyproject / pixi / asked)
- [ ] Skill(skore-api) consulted for: Project, put, evaluate
- [ ] Decision recorded: new experiment file vs. edit existing
      (asked the user if this is an iteration)
- [ ] `plan/` scaffolded: empty `PLAN.md` placed (content owned by
      `iterate-ml-experiment`, not this skill)
```

## Scope

- **In scope:** detecting an existing layout, scaffolding a fresh
  one, the `experiments/` script convention (`# %%`, one file per
  experiment), the contract for what `evaluate.py` is allowed to
  contain, the `reports/` location for the skore Project.
- **Out of scope:** what to put inside `pipeline.py` (see
  `build-ml-pipeline`), how to call `skore.evaluate` (see
  `evaluate-ml-pipeline`), skore/skrub/sklearn symbols (see the
  `*-api` skills), data ingestion paths (user-owned).

## Detection — existing workspace first

Before scaffolding anything, look at the project root and infer
whether a layout already exists:

| Signal | Meaning |
|---|---|
| `pyproject.toml` / `pixi.toml` with a project/package name | use that as the package name |
| `src/<pkg>/__init__.py` or `<pkg>/__init__.py` at root | package directory already chosen — keep it |
| `experiments/`, `notebooks/`, `scripts/`, `analyses/` | experiment location already chosen — keep it |
| `plan/`, `plans/`, `proposals/` | plan/iteration location already chosen — keep it |
| `reports/`, `results/`, `runs/` | report location already chosen — keep it |
| `mlflow.db` / `mlruns/` at the project root | tracker artifacts from prior work — **leave them alone**; skore is the canonical tracker for this stack (see `data-science-python-stack`). Note their presence to the user once and move on. |
| Existing `.ipynb` files in the experiment folder | user is on notebooks; **do not silently switch to scripts** — surface the convention shift and ask |

If any of these are present, **glue to the existing convention**.
Do not rename or relocate. Add new files in the locations the
project already uses, with names that match the existing pattern.

If none of these are present, the project is fresh — scaffold the
default layout below.

## Default layout (fresh workspace)

```
project/
├── pyproject.toml          # or pixi.toml — already there in most cases
├── src/<pkg>/
│   ├── __init__.py
│   ├── data.py             # data loading, splits, split_kwargs wiring
│   ├── features.py         # transformers, encoders, feature functions
│   ├── pipeline.py         # the learner declaration (skrub DataOps)
│   └── evaluate.py         # ONLY: CV strategy + (optional) metric overrides
├── plan/                   # iteration log + per-experiment design notes
│   ├── PLAN.md             # session-start log; index of experiments
│   └── 01_baseline.md      # one `.md` per planned experiment, same stem
├── experiments/            # one `# %%` script per experiment
│   └── 01_baseline.py
└── reports/                # skore Project lives here
```

Notes on what is **deliberately absent**:

- **No `data/` directory.** The user decides where data comes from
  (local mount, remote bucket, fixture, fetched dataset). `data.py`
  exposes a loader; the path is a parameter, not a folder we
  invent.
- **No `models/`.** Persistence is out of scope at this stage.
- **No `tests/`.** Out of scope at this stage.

If the user asks for any of those later, add them — don't pre-empt.

## Files in `src/<pkg>/`

Each file has a narrow contract; respect it so experiments compose
predictably.

- **`data.py`** — loaders, the call to materialize `X`, `y`, and
  any `split_kwargs` (groups, time, …) attached at the X marker.
  Pipeline mechanics: see `build-ml-pipeline`.
- **`features.py`** — feature functions and transformers. Pipeline
  mechanics: see `build-ml-pipeline`.
- **`pipeline.py`** — the learner declaration (typically a
  `SkrubLearner`). Returns the unfit object. Pipeline mechanics:
  see `build-ml-pipeline`.
- **`evaluate.py`** — **only** the inputs to `skore.evaluate`:
  - the cross-validator (`splitter = ...`),
  - optional metric overrides if the user has explicitly asked for
    them.

  `evaluate.py` does **not** call `skore.evaluate`, does **not**
  open a `skore.Project`, does **not** persist anything. Those
  steps belong in the experiment script. See
  `evaluate-ml-pipeline` for cross-validator selection.

## Experiments — one file per experiment

Experiments live under `experiments/` as **`.py` scripts with
`# %%` cell markers**, *not* `.ipynb` notebooks. The `# %%`
convention is recognized by VS Code, PyCharm, and `jupytext`, so
the file opens as a notebook in Jupyter while staying clean under
version control.

### File-creation rule

- **Plan first, then code.** Before creating
  `experiments/NN_short_name.py`, the matching
  `plan/NN_short_name.md` must exist and have been validated by the
  user. Plan content (sections, validation checklist) is owned by
  `iterate-ml-experiment`; this skill only enforces the
  pairing — same stem, planned-before-coded.
- **New experiment → new file.** Default to creating a new file:
  `NN_short_name.py` (e.g. `02_text_encoder.py`,
  `03_grouped_cv.py`). The numeric prefix preserves the iteration
  order in `ls`. The companion `plan/NN_short_name.md` shares the
  exact same stem.
- **Iterating on an existing experiment → ask first.** When the
  user says "let's tweak experiment 02" or "iterate on the text
  encoder run", do not assume. Ask:
  > Should this be a new experiment file (e.g.
  > `04_text_encoder_v2.py`) or an in-place edit of
  > `02_text_encoder.py`?

  In-place edits overwrite the prior result in the skore Project
  if the same key is reused — flag this if the user picks
  in-place.

### What an experiment script does

Every experiment script follows the same shape: open the
`skore.Project`, build the learner, evaluate it, store the
report. Use `templates/experiment.py` as the starting content —
copy it, rename it, adapt the imports.

The script is responsible for:

1. opening (or attaching to) the `skore.Project` rooted at
   `reports/` (see "Project parameters" below),
2. importing the learner from `<pkg>.pipeline` and the CV from
   `<pkg>.evaluate`,
3. calling `skore.evaluate(...)`,
4. calling `project.put("<experiment-key>", report)` to persist
   the report under a stable key.

Confirm exact signatures via `skore-api` before writing the call;
do not guess parameter names from memory. Cross-validator choice
is in `evaluate-ml-pipeline`.

### Project parameters

The `skore.Project` constructor takes — at minimum — three things
the experiment script must set explicitly:

| Parameter | Value to use |
|---|---|
| `workspace` | `"reports"` (the folder defined in the layout above; the Project writes its store inside it) |
| `name` | a short, stable project name **inferred from context** — see below |
| `mode` | `"local"` by default |

**Picking `name`.** Do not leave it as a placeholder. Derive it
from whatever is most identifying in the project, in this order:
1. the project / package name from `pyproject.toml` or
   `pixi.toml`;
2. the dataset name if the loader makes it obvious (e.g.
   `"adult-census"`, `"taxi-trips"`);
3. the working-directory name as a last resort.

Use kebab-case, keep it short, and **reuse the same `name` across
all experiments in the workspace** — that's what lets every
experiment's report land in the same Project for later comparison.
If the user has already opened a Project earlier in the
conversation with a different `name`, keep theirs.

**`mode="local"` is the current default.** Don't switch to other
modes (hub, mlflow) unless the user asks. Consult `skore-api` for
the supported values and the full constructor signature.

### Experiment key convention

Use the file's stem as the report key (e.g.
`01_baseline.py` → `"01_baseline"`). One file → one key → one
report. This is what makes `ComparisonReport` across experiments
trivial later.

## Decision flow

1. Read the project root. Does an ML layout already exist
   (signals above)?
   - **Yes** → glue. Add new files in the existing folders with
     names matching the existing pattern. Stop.
   - **No** → scaffold the default layout. Continue.
2. Determine the package name (from `pyproject.toml` /
   `pixi.toml` if present; otherwise ask the user).
3. Create `src/<pkg>/` with the four skeletons (use
   `templates/src_*.py`). Create empty `__init__.py`.
4. Create `experiments/` and seed it with `01_baseline.py` from
   `templates/experiment.py`.
5. Create `plan/` with a one-line **placeholder** `PLAN.md`
   (literally `# PLAN\n\n<!-- placeholder; populated by iterate-ml-experiment on first invocation -->`).
   This skill **does not** read `iterate-ml-experiment`'s
   template — each skill owns its own template surface. Hand
   off immediately; `iterate-ml-experiment` rewrites `PLAN.md`
   from its own `templates/PLAN.md` and writes the matching
   `plan/01_baseline.md`, validated **before** the experiment
   script runs.
6. Create `reports/` (empty — skore writes into it on first run).
7. **Touch `.gitignore`.** If the project root has no
   `.gitignore`, drop `templates/.gitignore` (with the
   `reports/` line included by default). If a `.gitignore`
   already exists, **do not overwrite it** — instead, scan for
   the entries this stack expects (`__pycache__/`, `.pixi/`,
   `mlruns/` + `mlartifacts/`, `*.db` + `*.db-journal`,
   `*.ipynb`) and surface any missing ones to the user as a
   suggested patch (don't auto-edit). The `reports/` line is
   **always asked** — some teams commit their skore store
   selectively, others gitignore it entirely; never default
   without checking.
8. Hand back to the relevant sibling skill: `build-ml-pipeline`
   for what goes inside `pipeline.py`, `evaluate-ml-pipeline` for
   what `splitter` should be in `evaluate.py`,
   `iterate-ml-experiment` for the plan content and the
   conversational loop with the user.

## Templates

- `templates/experiment.py` — the recurring artifact. Copied for
  every new experiment.
- `templates/src_data.py`, `templates/src_features.py`,
  `templates/src_pipeline.py`, `templates/src_evaluate.py` — the
  one-time skeletons for the package.
- `templates/.gitignore` — the one-time `.gitignore` dropped at
  scaffold time when the project root has none. If a
  `.gitignore` already exists, **don't overwrite** — surface
  missing entries as a suggested patch instead.

Copy, don't rewrite. The templates encode the contracts above
(especially the narrow scope of `evaluate.py`).

## Companion skills

- **`iterate-ml-experiment`** — owns `plan/PLAN.md` and the
  per-experiment `plan/NN_*.md` design notes. This skill places
  the empty `plan/` folder; that skill fills it. Hand off any time
  a new experiment is being proposed, before the experiment
  script is written.
- **`build-ml-pipeline`** — what goes inside `pipeline.py`,
  `features.py`, `data.py` (declarative side).
- **`evaluate-ml-pipeline`** — what `splitter` should be in
  `evaluate.py`, and how the experiment script calls
  `skore.evaluate`.
- **`skore-api`** — `skore.Project`, `skore.evaluate`,
  `project.put` signatures. Don't guess from memory.
- **`skrub-api`** / **`sklearn-api`** — symbols used inside the
  `src/<pkg>/` files.
- **`python-env-manager`** — detection + install commands for the
  project's environment manager (pixi / uv / poetry / hatch / conda
  / pip+venv). **Invoke whenever** Tier 1 (sklearn / skrub / skore)
  is missing, the tabular-library install needs to run, or a fresh
  workspace needs bootstrapping (default recommendation: pixi).
- **`data-science-python-stack`** — *what* to install (Tier 1
  mandatory + Tier 2 user-choice + Tier 3 optional). Pair with
  `python-env-manager` for the *how*.
