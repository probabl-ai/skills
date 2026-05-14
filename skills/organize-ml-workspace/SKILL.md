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
  (`python-api`).

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
  from a `Skill(python-api)` call **in this turn**. Don't infer
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
- [ ] `pyproject.toml` present at the project root, declaring the
      `src/<pkg>/` package; editable install wired via
      `python-env-manager` § "Editable workspace package"
- [ ] Skill(python-api) consulted for: Project, put, evaluate
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
  `python-api` skill), data ingestion paths (user-owned).

## Detection — existing workspace first

Before scaffolding anything, look at the project root and infer
whether a layout already exists:

| Signal | Meaning |
|---|---|
| `pyproject.toml` with `[project] name = ...` and `[tool.setuptools.packages.find]` (or `[tool.poetry.packages]`, `[tool.hatch.build.targets.wheel]`) | the package is declared and installable — use this name; verify the editable install is wired (`python-env-manager` § "Editable workspace package") |
| `pixi.toml` / `[tool.poetry]` / `[tool.uv]` carrying a project/package name with **no** `pyproject.toml` `[project]` table | the manager knows the project but the package isn't declared as installable — flag this and offer to add `pyproject.toml` |
| `src/<pkg>/__init__.py` or `<pkg>/__init__.py` at root | package directory already chosen — keep it |
| `<pkg>.egg-info/` at the project root or under `src/` | a stale or out-of-band `pip install -e .` ran at some point; if the manager's manifest does **not** carry the editable entry, surface this as drift and offer to clean up + wire it through the manager |
| `experiments/`, `notebooks/`, `scripts/`, `analyses/` | experiment location already chosen — keep it |
| `plan/`, `plans/`, `proposals/` | plan/iteration location already chosen — keep it |
| `reports/`, `results/`, `runs/` | report location already chosen — keep it |
| `tests/` | test location already chosen — keep it; per-test-category subfolders (`tests/smoke/`, `tests/regression/`, …) are owned by `test-ml-pipeline` |
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
├── pyproject.toml          # declares src/<pkg>/ as the installable package
├── <manager manifest>      # pixi.toml / poetry / uv / hatch / environment.yml
│                           # (carries runtime deps; pyproject.toml does not)
├── src/<pkg>/
│   ├── __init__.py         # exposes PROJECT_ROOT for CWD-independent paths
│   ├── data.py             # data loading, splits, split_kwargs wiring
│   ├── features.py         # transformers, encoders, feature functions
│   ├── pipeline.py         # the learner declaration (skrub DataOps)
│   └── evaluate.py         # ONLY: CV strategy + (optional) metric overrides
├── plan/                   # iteration log + per-experiment design notes
│   ├── PLAN.md             # session-start log; index of experiments
│   └── 01_baseline.md      # one `.md` per planned experiment, same stem
├── experiments/            # one `# %%` script per experiment
│   └── 01_baseline.py
├── tests/                  # pytest tests; pairs 1:1 with experiments
│   └── smoke/              # body owned by `smoke-test-ml-pipeline`;
│                           # per-experiment files placed by
│                           # `test-ml-pipeline` once each plan is approved
├── overview/               # cross-experiment project digest
│   └── summary.md          # agent-authored narrative; refreshed by
│                           # `iterate-ml-experiment` § 4 via scratch probe
├── scratch/                # agent-only scratch space (gitignored except README)
│   └── README.md           # documents the timestamped-filename convention
└── reports/                # skore Project lives here
```

**The package is installable.** `pyproject.toml` declares the
`src/<pkg>/` directory as a Python package, and the project's env
manager installs it in **editable** mode (so edits to source are
picked up without reinstalling). This is what lets experiment
scripts say `from <pkg>.pipeline import build_learner` from any CWD,
no `PYTHONPATH=src` hack required. The wiring is per-manager — see
`python-env-manager` § "Editable workspace package" for the exact
command (e.g. `pixi add --pypi --editable .`).

Runtime dependencies (sklearn, skrub, skore, the tabular library)
live in the **manager's manifest** (`pixi.toml`,
`[tool.poetry.dependencies]`, `[tool.uv]`, `environment.yml`, …),
not in `pyproject.toml`'s `[project.dependencies]`. The
`pyproject.toml` template ships with **no runtime deps** for that
reason.

Notes on what is **deliberately absent**:

- **No `data/` directory.** The user decides where data comes from
  (local mount, remote bucket, fixture, fetched dataset). `data.py`
  exposes a loader; the path is a parameter, not a folder we
  invent.
- **No `models/`.** Persistence is out of scope at this stage.

`tests/smoke/` is part of the default scaffold (with one
placeholder `tests/smoke/test_01_baseline.py`); the body of every
test file is owned by `smoke-test-ml-pipeline`, the layout and
the stem-pairing rule by `test-ml-pipeline`. This skill only
places the empty subfolder + the placeholder file.

`overview/` is part of the default scaffold too. It carries a
single file — `summary.md` — that is the agent's read target
for the project-level narrative (complementing `plan/PLAN.md`'s
index role). The per-experiment `plan/NN_*.md` files remain the
source of truth (frozen Method / Risks); `summary.md` is the
*curated* view across them, plus the cross-experiment metrics
table extracted from the skore Project.

**`summary.md` is agent-authored prose, not script output.**
`iterate-ml-experiment` § 4 rewrites it by hand after every
outcome recording: the agent runs a one-off probe under
`scratch/<ts>_refresh_summary.py` to extract `project.summarize()`
and the `## Status` blocks from `plan/NN_*.md`, then writes a
curated narrative to `summary.md` (not a verbatim dump). This
skill places the `summary.md` placeholder from
`templates/summary.md` at scaffold time; § 4 of
`iterate-ml-experiment` rewrites it on first outcome and keeps
it fresh.

`scratch/` is the agent's traceability folder. The agent uses
it for any *ad-hoc* multi-line Python that isn't a reusable
artifact — inspecting a persisted skore report, walking
`report.diagnosis()` to fill a Status block, extracting a
metric. The convention is **one file per probe**, named
`scratch/<YYYY-MM-DD>_<HHMMSS>_<short-name>.py`. Files are
**append-only after success** — once a script executes cleanly,
the file is frozen; re-probes use a fresh timestamp.
**Overwriting within the same loop is OK only when the prior
run errored** (typo, wrong API) — the agent patches and re-runs
until it succeeds, and only the working version is kept.
Contents are gitignored; only the `scratch/README.md` is tracked
(it documents the convention for human readers). This rule
complements the experiment-script cleanliness rule below.

If the user asks for `data/` or `models/` later, add them — don't
pre-empt.

## Files in `src/<pkg>/`

Each file has a narrow contract; respect it so experiments compose
predictably.

- **`__init__.py`** — exposes `PROJECT_ROOT`, the absolute path to
  the project root, derived from `__file__` and not from the CWD.
  Any module or experiment that needs to resolve a project-relative
  path imports `PROJECT_ROOT` instead of hard-coding `"data"` /
  `"./data"` / similar. Default body in `templates/src___init__.py`:

  ```python
  from pathlib import Path
  PROJECT_ROOT = Path(__file__).resolve().parents[2]
  ```

  This relies on the package being **editable-installed** (so
  `__file__` lives under the source tree, not in `site-packages`).
  Editable install is wired by `python-env-manager` § "Editable
  workspace package".
- **`data.py`** — loaders, the call to materialize `X`, `y`, and
  any `split_kwargs` (groups, time, …) attached at the X marker.
  Pipeline mechanics: see `build-ml-pipeline`.
- **`features.py`** — feature functions and transformers. Pipeline
  mechanics: see `build-ml-pipeline`.
- **`pipeline.py`** — the learner declaration (typically a
  `SkrubLearner`). Returns the unfit object. The `build_learner`
  signature should expose the source-binding preview as an
  **optional** keyword (e.g. `data_dir_preview: str | Path | None
  = None`) — see `build-ml-pipeline` rule 2 — so the experiment
  script can pass an absolute path resolved from `PROJECT_ROOT`.
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
- **Three-way stem pairing.** Every experiment is identified by a
  single `NN_<short_name>` stem that appears in **three** places:

  ```
  plan/NN_<short_name>.md                       (design note)
  experiments/NN_<short_name>.py                (script)
  tests/smoke/test_NN_<short_name>.py           (smoke test)
  ```

  All three exist for every experiment by the time it can flip
  to `done` in `PLAN.md`. The plan is written first
  (`iterate-ml-experiment`); the script and the test are placed
  by this skill on plan approval; the smoke test body is filled
  in by `smoke-test-ml-pipeline`. The `test_` prefix on the
  test file is the pytest naming convention; the
  `NN_<short_name>` portion matches the experiment exactly.
- **New experiment → new file.** Default to creating a new file:
  `NN_short_name.py` (e.g. `02_text_encoder.py`,
  `03_grouped_cv.py`). The numeric prefix preserves the iteration
  order in `ls`. The companion `plan/NN_short_name.md` and
  `tests/smoke/test_NN_short_name.py` share the exact same stem.
- **Iterating on an existing experiment → ask first.** When the
  user says "let's tweak experiment 02" or "iterate on the text
  encoder run", do not assume. Ask:
  > Should this be a new experiment file (e.g.
  > `04_text_encoder_v2.py`) or an in-place edit of
  > `02_text_encoder.py`?

  In-place edits overwrite the prior result in the skore Project
  if the same key is reused — flag this if the user picks
  in-place. **In-place edits also require revisiting the matching
  smoke test** (`tests/smoke/test_02_text_encoder.py`), since
  the test asserts properties of the pipeline shape; route to
  `smoke-test-ml-pipeline` to confirm the assertions still hold.

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

Confirm exact signatures via `python-api` before writing the call;
do not guess parameter names from memory. Cross-validator choice
is in `evaluate-ml-pipeline`.

**Experiment scripts stay clean of agent-only debug prints.**
`print(report)` / `print(<intermediate>)` / `print("checking
...")` added *for the agent's benefit* don't belong in
`experiments/NN_*.py` — once the run is recorded they're noise
to anyone reading the script later. When the agent needs to
inspect what an experiment produced (metrics, residuals,
calibration, anything from `report.diagnosis()`), it writes a
`scratch/<YYYY-MM-DD>_<HHMMSS>_<short>.py` script that opens
the persisted skore Project and pulls what it needs. The
experiment script's job is `build → evaluate → put`; everything
downstream is the agent's scratch problem, not the script's.

One exception where a bare expression is legitimate in scripts:
a `report` line in jupytext context (Layer 4 of the `# %%`
notebook idiom) renders the report inline when the script is
opened as a notebook — that's not a debug print, it's a
notebook-display side effect with no runtime cost as a CLI
script.

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
modes (hub, mlflow) unless the user asks. Consult `python-api` for
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
3. **Drop `pyproject.toml`** at the project root from
   `templates/pyproject.toml`, substituting `<pkg>`. Skip if a
   `pyproject.toml` already declares the package via `[project]` +
   a build backend's package-discovery section. Then **hand off to
   `python-env-manager` § "Editable workspace package"** to wire
   the editable install for the project's manager (e.g. `pixi add
   --pypi --editable .`). Do not run the install command yourself
   — that's the env-manager skill's job.
4. Create `src/<pkg>/` with the skeletons. Use
   `templates/src___init__.py` for `__init__.py` (carries
   `PROJECT_ROOT`) and `templates/src_*.py` for `data.py`,
   `features.py`, `pipeline.py`, `evaluate.py`.
5. Create `experiments/` and seed it with `01_baseline.py` from
   `templates/experiment.py`, **substituting `<pkg>`** with the
   package name resolved in step 2 (same substitution as step 3
   for `pyproject.toml`). This is load-bearing: the `<pkg>`
   literals appear in `from <pkg> import ...` statements and are
   Python syntax errors if left in place — `python-code-style`'s
   ruff pass at step 12 will fail on them otherwise. The other
   placeholders in the template (`<short title>`, `YYYY-MM-DD`,
   `<project-name>`, `<experiment-key>`) sit inside markdown
   comments or string literals and don't break syntax; leave
   them for `iterate-ml-experiment` § 3 to fill in when the
   experiment script is rewritten with real content after the
   implementation chain.
6. Create the **empty** `tests/smoke/` folder. Do **not** drop a
   placeholder test file here — `test-ml-pipeline`'s Stop condition
   forbids a test file before the matching plan is approved, and
   no plan exists yet at scaffold time. Per-experiment placeholders
   land later via `test-ml-pipeline` (called from
   `iterate-ml-experiment` § 3 once a plan is approved). Verify
   pytest is on the manifest (per `data-science-python-stack`
   § Tier 1); if not, hand off to `python-env-manager` to add it.
7. Create `plan/` with a one-line **placeholder** `PLAN.md`
   (literally `# PLAN\n\n<!-- placeholder; populated by iterate-ml-experiment on first invocation -->`).
   This skill **does not** read `iterate-ml-experiment`'s
   template — each skill owns its own template surface. Hand
   off immediately; `iterate-ml-experiment` rewrites `PLAN.md`
   from its own `templates/PLAN.md` and writes the matching
   `plan/01_baseline.md`, validated **before** the experiment
   script runs.
8. Create `overview/` and drop the **placeholder `summary.md`**
   from `templates/summary.md`. The placeholder documents the
   expected structure (project narrative + cross-experiment
   metrics table + per-experiment Status blocks) and carries a
   `_No experiments recorded yet._` line so the file is
   meaningful at scaffold time. `iterate-ml-experiment` § 4
   rewrites it by hand on every outcome recording (the agent
   runs a scratch probe to extract metrics + Status blocks,
   then writes a curated narrative). **No Python script in
   `overview/`** — `summary.md` is agent-authored prose, not
   script output.
9. Create `scratch/` and drop `templates/scratch_README.md`
   inside as `scratch/README.md`. The folder is the agent's
   ad-hoc scratch space (one file per probe, timestamped, see
   the README for the full convention); only the README is
   tracked in git, the rest is ignored via step 11's
   `.gitignore` step.
10. Create `reports/` (empty — skore writes into it on first run).
11. **Touch `.gitignore`.** If the project root has no
   `.gitignore`, drop `templates/.gitignore` (with the
   `reports/` and `scratch/*` + `!scratch/README.md` lines
   included by default). If a `.gitignore` already exists,
   **do not overwrite it** — instead, scan for the entries
   this stack expects (`__pycache__/`, `.pixi/`, `*.egg-info/`,
   `mlruns/` + `mlartifacts/`, `*.db` + `*.db-journal`,
   `*.ipynb`, `scratch/*` + `!scratch/README.md`) and surface
   any missing ones to the user as a suggested patch (don't
   auto-edit). The `reports/` line is **always asked** — some
   teams commit their skore store selectively, others gitignore
   it entirely; never default without checking. The
   `scratch/*` + `!scratch/README.md` pair is the **default**
   (matches the agent-scratch traceability rule); ask before
   omitting.
12. **Drop `ruff.toml` and run the first ruff pass.** Hand off
    to `python-code-style` § "Initial setup". That skill owns its
    own `templates/ruff.toml`, writes it to the project root, and
    runs `ruff format` + `ruff check` against the modules dropped
    at step 4. **Do not copy `templates/ruff.toml` by hand and
    run ruff yourself** — invoking the skill is what teaches the
    agent the NumPyDoc docstring convention (parameter shape in
    the type slot, `Parameters` / `Returns` / `Raises` sections,
    blank line after the one-line summary); the config alone
    only enforces ruff's `D`-rules, which a one-line docstring
    silently satisfies. The skill is mandatory at this step;
    skipping it is the most common way agents drop the NumPyDoc
    contract on Day 1.
13. Hand back to the relevant sibling skill: `build-ml-pipeline`
    for what goes inside `pipeline.py`, `evaluate-ml-pipeline` for
    what `splitter` should be in `evaluate.py`,
    `iterate-ml-experiment` for the plan content and the
    conversational loop with the user, `test-ml-pipeline` /
    `smoke-test-ml-pipeline` for the body of
    `tests/smoke/test_*.py`.

## Templates

- `templates/experiment.py` — the recurring artifact. Copied for
  every new experiment.
- `templates/summary.md` — the placeholder `summary.md` dropped
  at scaffold time under `overview/summary.md`. Documents the
  expected structure (project narrative + cross-experiment
  metrics + per-experiment Status blocks). Rewritten in full by
  `iterate-ml-experiment` § 4 after the first outcome recording.
- `templates/scratch_README.md` — dropped once at scaffold time
  as `scratch/README.md`. Documents the agent's scratch-folder
  convention (timestamped filenames, gitignored contents,
  append-only-after-success) for human readers of the repo.
- `templates/pyproject.toml` — declares the `src/<pkg>/` package as
  installable; runtime deps stay in the manager's manifest. Dropped
  once at scaffold time. Pair with `python-env-manager` § "Editable
  workspace package" to wire the install.
- `templates/src___init__.py` — the package's `__init__.py`,
  carrying `PROJECT_ROOT` for CWD-independent path resolution.
- `templates/src_data.py`, `templates/src_features.py`,
  `templates/src_pipeline.py`, `templates/src_evaluate.py` — the
  one-time skeletons for the package modules.
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
- **`test-ml-pipeline`** — owns `tests/<category>/` layout and
  the stem-pairing rule between an experiment and its tests.
  Lightweight router; dispatches to per-category subskills.
- **`smoke-test-ml-pipeline`** — fills the placeholder smoke
  test body once the matching plan is approved. The smoke test
  is required for every experiment per
  `iterate-ml-experiment` § 3 / § 4.
- **`python-api`** — `skore.Project`, `skore.evaluate`,
  `project.put` signatures. Don't guess from memory.
- **`python-api`** / **`python-api`** — symbols used inside the
  `src/<pkg>/` files.
- **`python-env-manager`** — detection + install commands for the
  project's environment manager (pixi / uv / poetry / hatch / conda
  / pip+venv). **Invoke whenever** Tier 1 (sklearn / skrub / skore)
  is missing, the tabular-library install needs to run, or a fresh
  workspace needs bootstrapping (default recommendation: pixi).
- **`data-science-python-stack`** — *what* to install (Tier 1
  mandatory + Tier 2 user-choice + Tier 3 optional). Pair with
  `python-env-manager` for the *how*.
- **`python-code-style`** — drops `ruff.toml` at the project root
  and runs the first ruff pass against the modules placed at
  step 4 of the Decision flow. **Invoke at scaffold time** (per
  Decision flow step 12); the ruff config alone is necessary
  but not sufficient — only the skill body teaches the NumPyDoc
  docstring convention this stack expects. Copying the template
  by hand and running ruff directly is the failure mode.
