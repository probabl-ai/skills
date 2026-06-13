---
name: organize-ml-workspace
description: >
  Decide where files live in an ML experimentation project: reusable
  code in `src/<pkg>/`, one `# %%` script per experiment in
  `experiments/`, design notes + index in `journal/`, reports in
  `reports/`, agent-only probes in `scratch/`. Owns the layout, the
  file-creation rules
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

## Next-step pointers — where you go after this skill

| You came here for… | → next |
|---|---|
| Bootstrap a fresh workspace | → `python-env-manager` § Bootstrap; then `iterate-ml-experiment` § 0 |
| First experiment script | → `iterate-ml-experiment` § 0 for the design note |
| Add a new experiment iteration | → `iterate-ml-experiment` § 1 (new vs edit decision) |
| Pipeline / evaluate / smoke-test content | → `build-ml-pipeline` / `evaluate-ml-pipeline` / `smoke-test-ml-pipeline` |

Always re-emit the Pre-flight checklist with evidence before
declaring the turn done.

## Sibling skills — open just-in-time

Don't pre-read every sibling at session start (paralysis). Open each
sibling SKILL.md when a step calls for it (e.g. open
`python-env-manager` before G-ENV-MGR; open `iterate-ml-experiment`
before handing off the design-note write). Emit this tracker once
per turn:

```
Sibling skills (just-in-time):
  - data-science-python-stack, python-env-manager, python-api,
    python-code-style, iterate-ml-experiment, explore-ml-data,
    build-ml-pipeline, evaluate-ml-pipeline, test-ml-pipeline,
    smoke-test-ml-pipeline
```

## Stop conditions — read before anything else

- **Missing dependency.** If `import skore` raises, STOP. Invoke
  `python-env-manager` for the install command. Do not drop
  `skore.Project` in favor of `mlflow` / pickles / "print metrics"
  — the workspace contract assumes a Project on disk.
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
  `scratch/<ts>_<short>.py` may call `project.get(...)`,
  `project.summarize()`, walk an existing report. They MUST NOT
  call `skore.evaluate(...)` or `project.put(...)`. When
  `project.get(key)` raises `KeyError`, the fix is the lookup
  shape: `get` is by **id**, not by `key`. Use `summarize()` →
  `(key, id)` → `get(id)`. Never substitute by re-running
  `evaluate` + `put`.
- **Tabular library is asked, not assumed (G-TABULAR).** Pandas
  being importable via skore is not a pick. Invoke
  `data-science-python-stack` for the structured ask. Free-text
  ("quick", "you pick") does NOT resolve. Persisted in JOURNAL.md
  Status `Workspace decisions`.
- **Package name is asked, not inferred (G-PKG-NAME).** Before any
  `pyproject.toml` / manifest creation (including `pixi init` /
  `uv init` / `poetry init`), fire an `AskUserQuestion` for the
  `src/<pkg>/` import name. Folder name in snake_case is the
  default. **Manifest creation before G-PKG-NAME passes is
  forbidden** — running `init` first creates a `[project] name`
  entry, and reading "name is in the manifest" back is circular.
  If a manifest exists, confirm via `AskUserQuestion` —
  continuity from a prior session is not continuity from a user
  decision.
- **Skore Project mode is asked, not assumed (G-SKORE-MODE).**
  Before any template instantiation containing
  `skore.Project(...)`, fire an `AskUserQuestion` for `local` |
  `hub` | `mlflow`. Default proposal: `local`. Hub triggers a
  follow-up for the workspace name (org/team on the hub — distinct
  from local-mode `workspace=`); mlflow triggers a follow-up for
  the **MLflow tracking server URI** (`tracking_uri=`) — the agent
  cannot infer it. Persists as `skore mode:` (+ `skore hub
  workspace:` when hub, + `skore mlflow tracking uri:` when
  mlflow). Without it the `<SKORE_PROJECT_INIT>` substitution has
  no shape to fill. Details: → `references/g_skore_mode.md`.
- **Switching skore mode mid-project is forbidden by default.**
  Once recorded, do not silently change. A switch orphans every
  existing report in the prior store — skore has no built-in
  migration. Requires explicit `AskUserQuestion` confirmation
  surfacing the migration burden, then rewrite all
  `<SKORE_PROJECT_INIT>` blocks. Procedure:
  → `references/g_skore_mode.md` § "Switching mid-project".
- **Env manager is asked, not assumed (G-ENV-MGR).** Hand off to
  `python-env-manager`. Pixi on PATH is detection, not permission.
  Don't run `pixi init` / `uv init` / `poetry init` until
  G-ENV-MGR has passed *in `python-env-manager`*.
- **Harness "no clarifying questions" hints do NOT waive these
  gates.** G-TABULAR, G-PKG-NAME, G-ENV-MGR, G-SKORE-MODE,
  python-api consultation, new-vs-edit decision are
  operating-contract gates. "Quick" / "go fast" never waives them.
- **Post-hoc audit — required before ending the turn.** Walk every
  pre-flight row; if any Evidence cell is unfilled, surface the
  non-compliance explicitly. Most common failure: "I scaffolded
  successfully so everything must be fine".

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `pixi` on PATH → run `pixi init` to get a manifest, then read the name back | Violates G-ENV-MGR (silent manager pick) AND G-PKG-NAME (name from folder via init side-effect). Circular: the agent created the manifest it now claims to read |
| Folder name = good name → skip the ask | Default *value* is fine; silent *pick* is not. G-PKG-NAME requires the structured ask even with folder as default |
| `pandas` already importable via skore → write `import pandas` in `data.py` | Transitive presence is not a pick. Violates G-TABULAR |
| Scaffold every skeleton in one turn, incl. `experiments/01_baseline.py` body | Scaffold stops at empty `journal/` placeholder. Experiment script content lands after design-note approval (`iterate-ml-experiment` § 3) |
| Scaffold drops `audit/01_baseline.py` at workspace creation | Audit files placed by `audit-ml-pipeline` at § 4 record-outcome. Empty `audit/` at scaffold is correct |
| Forget `audit/` in the scaffold layout | Four-way stem pairing breaks |
| `pyproject.toml` exists with `name = <x>` → reuse without confirming | Always re-confirm via G-PKG-NAME |
| Batch G-TABULAR + G-PKG-NAME + G-ENV-MGR + G-SKORE-MODE into prose recommendations | The gates take structured `AskUserQuestion`. Prose followed by "let me know" does NOT resolve them |
| Skip G-SKORE-MODE because templates use `mode="local"` | Templates carry the `<SKORE_PROJECT_INIT>` marker, not a literal. The gate must fire |
| Pick `mode="hub"` without checking the workspace exists / user has access | Project init fails at first `put()` with an authorization error. Confirm during G-SKORE-MODE, not at execution time |
| Pick `mode="mlflow"` and invent / default the `tracking_uri=` | The tracking URI is server-specific; the agent cannot infer it. Ask the user at the G-SKORE-MODE follow-up. No silent `http://localhost:5000` |
| Substitute `pip install "skore[hub]"` / `"skore[mlflow]"` based on agent guess | Install variant comes from G-SKORE-MODE's recorded answer. `python-env-manager` reads that row, not agent intuition |
| Silently change `skore mode:` mid-project to "fix" a broken init | Switching orphans existing reports. Always explicit `AskUserQuestion` first |
| Hub / mlflow substitution but leaving `workspace=` kwarg | `workspace=` is local-only; hub and mlflow reject it (hub raises `TypeError`; mlflow uses `tracking_uri=`). Substitute the whole block, not just the mode literal |
| mlflow substitution that keeps a `login(mode=...)` call | mlflow mode needs no skore login — auth is the MLflow server's concern. `login` belongs only to hub mode |
| Local `workspace="reports"` (relative) instead of `str(PROJECT_ROOT / "reports")` (absolute) | Relative resolves against CWD; runs from other dirs write the store somewhere unexpected. Always absolute via `PROJECT_ROOT` |
| Putting `skore.login(mode="hub")` after `skore.Project(...)` | `Project(...)` requires authenticated session in hub mode. `login` first |
| Substituting `<SKORE_PROJECT_INIT>` in `audit/<stem>.py` independently of `experiments/<stem>.py` | Audit must open the same Project. Byte-identical copy from the experiment file is the rule |
| Hub workspace name contains `/` (e.g. `acme/datasci`) | The `/` is reserved as separator. Reject at G-SKORE-MODE follow-up |
| `project.get(key)` raised `KeyError` → re-run `evaluate` + `put` to "recover" | Lookup shape wrong (`get` is by id). Use `summarize()` → `get(id)` |

## Pre-flight — emit before any code

Each ticked box needs an Evidence line (format spec in
`iterate-ml-experiment` § "Pre-flight evidence requirements"; see
also `python-env-manager/references/preflight_evidence.md`).

```
Pre-flight (organize-ml-workspace):
- [ ] `Workspace decisions` in `journal/JOURNAL.md` Status checked
      for pre-recorded gates (tabular, env_manager, package, skore mode)
      Evidence: lists each <gate>: <value | not recorded>
                | "n/a — JOURNAL.md does not exist yet (truly fresh)"
- [ ] Tier 1 mandatory libs importable: sklearn, skrub, skore
      Evidence: Write scratch/<ts>_check_tier1.py + `pixi run python …` output.
                **Inline `python -c` is NOT evidence**.
- [ ] Layout detection done: <existing | fresh>
      Evidence: ls/Glob on project root + matched signal from Detection
- [ ] G-TABULAR resolved: pandas | polars
      Evidence: AskUserQuestion id=<id> via data-science-python-stack |
                JOURNAL.md Status (Workspace decisions) | user quote turn N
- [ ] G-ENV-MGR resolved
      Evidence: AskUserQuestion id=<id> via python-env-manager |
                JOURNAL.md Status (Workspace decisions)
- [ ] G-PKG-NAME resolved: <name>
      Evidence: AskUserQuestion id=<id>, answer=<name> |
                JOURNAL.md Status (Workspace decisions) |
                existing manifest's [project].name **confirmed via AskUserQuestion**
                (reading the manifest alone is NOT sufficient)
- [ ] G-SKORE-MODE resolved: local | hub | mlflow
      Evidence: AskUserQuestion id=<id>, answer=<local|hub|mlflow> |
                JOURNAL.md Status (Workspace decisions) `skore mode:` row
      If hub: also captures `skore hub workspace:` row.
      If mlflow: also captures `skore mlflow tracking uri:` row.
- [ ] `pyproject.toml` present at root declaring `src/<pkg>/`;
      editable install wired via `python-env-manager` § Editable workspace
      Evidence: Read pyproject.toml (this turn) + manager's editable-install call
- [ ] python-api consulted for: Project, put, evaluate
      Evidence: Read scratch/api/skore/<v>/{project_local,evaluate}.md
                | Write of the same files (this turn)
                | "n/a — symbols already in workspace cache"
- [ ] Decision: new experiment file vs edit existing
      Evidence: AskUserQuestion id=<id> | user quote turn N |
                "n/a — first experiment in a fresh workspace"
- [ ] `journal/` scaffolded with empty placeholder JOURNAL.md
      Evidence: Write journal/JOURNAL.md (this turn) | "already exists"
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

## Detection — existing workspace first

| Signal | Meaning |
|---|---|
| `pyproject.toml` with `[project] name` + `[tool.setuptools.packages.find]` (or poetry / hatch equivalents) | Package declared installable — use this name; verify editable install via `python-env-manager` |
| `pixi.toml` / `[tool.poetry]` / `[tool.uv]` with name but **no** `[project]` table | Manager knows the project but package isn't installable — flag, offer to add `pyproject.toml` |
| `src/<pkg>/__init__.py` or `<pkg>/__init__.py` at root | Package dir already chosen — keep it |
| `<pkg>.egg-info/` at root or under `src/` | Stale out-of-band `pip install -e .` — flag drift, offer to wire via manager |
| `experiments/`, `notebooks/`, `scripts/`, `analyses/` | Experiment location chosen — keep it |
| `audit/` with `# %%` files | Audit location chosen — keep it; body owned by `audit-ml-pipeline` |
| `journal/`, `plans/`, `proposals/` | Journal location chosen — keep it |
| `reports/`, `results/`, `runs/` | Report location chosen — keep it |
| `tests/` | Test location chosen — keep it |
| `mlflow.db` / `mlruns/` at root | Prior tracker artifacts — leave alone; skore is canonical |
| `.ipynb` files in experiment folder | User is on notebooks — surface the shift and ask; don't auto-switch |

**Any signal present → glue to existing convention.** No renames,
no relocates. **None present → fresh scaffold** (below).

→ next: G-PKG-NAME, then `python-env-manager` for G-ENV-MGR.

## Default layout (fresh workspace)

```
project/
├── pyproject.toml          # declares src/<pkg>/ as installable
├── <manager manifest>      # pixi.toml / poetry / uv / hatch / environment.yml
├── src/<pkg>/
│   ├── __init__.py         # exposes PROJECT_ROOT
│   ├── data.py             # data loading, splits, split_kwargs
│   ├── features.py         # transformers, encoders, feature fns
│   ├── pipeline.py         # the learner declaration (skrub DataOps)
│   └── evaluate.py         # ONLY: CV strategy + optional metric overrides
├── journal/
│   ├── JOURNAL.md          # session-start log; index of experiments
│   └── 01_baseline.md      # one `.md` per planned experiment
├── experiments/
│   └── 01_baseline.py      # one `# %%` script per experiment
├── audit/
│   └── 01_baseline.py      # body owned by audit-ml-pipeline (read-only)
├── tests/
│   └── smoke/              # body owned by smoke-test-ml-pipeline
├── scratch/                # agent-only (gitignored entirely)
└── reports/                # skore Project lives here
```

**The package is installable.** `pyproject.toml` declares
`src/<pkg>/`; the manager installs in **editable** mode so
`from <pkg>.pipeline import build_learner` works from any CWD.
Wiring per-manager: `python-env-manager` § Editable workspace.

**Runtime deps (sklearn, skrub, skore, tabular) live in the
manager's manifest**, not in `[project.dependencies]`.

**Deliberately absent:** no `data/` (user-owned), no `models/`
(out of scope). Add later only on user request — don't pre-empt. The
sole writer into `data/` is `explore-ml-data`, and only its own EDA
deliverables (`data/eda.py` / `data/eda.md` / `data/eda_<table>.html`);
the user's raw data is never modified by any skill.

## File-creation rules

### Design note first, then code

Before creating `experiments/NN_<short_name>.py`, the matching
`journal/NN_<short_name>.md` must exist and have been validated by
the user. Design-note content is owned by `iterate-ml-experiment`;
this skill only enforces the pairing.

### Four-way stem pairing

Every experiment is identified by `NN_<short_name>` in four places:

```
journal/NN_<short_name>.md            (design note)
experiments/NN_<short_name>.py        (script)
tests/smoke/test_NN_<short_name>.py   (smoke test)
audit/NN_<short_name>.py              (audit file — read-only)
```

By the time the experiment flips to `done` in JOURNAL.md, all four
exist. The design note is written first; the script lands on approval;
the smoke test body is filled by `smoke-test-ml-pipeline`; the
audit file is placed and executed by `audit-ml-pipeline` at § 4
record-outcome.

The audit file is **read-only** against the workspace's skore
Project and data — see `audit-ml-pipeline` § Read-only contract.

### New experiment → new file. Iterating → ask first.

Default: new file. `02_text_encoder.py`, `03_grouped_cv.py`. The
numeric prefix preserves iteration order under `ls`.

When the user says "let's tweak experiment 02", **do not assume**.
Fire `AskUserQuestion`:

> Should this be a new experiment file (e.g.
> `04_text_encoder_v2.py`) or an in-place edit of
> `02_text_encoder.py`?

In-place edits **overwrite the prior result in the skore Project**
if the same key is reused — flag this. In-place also requires
revisiting the matching smoke test
(→ `smoke-test-ml-pipeline`).

## Decision flow (12 steps — full version in `references/scaffold_steps.md`)

| # | Step | Owner |
|---|---|---|
| 1 | Read project root; Detection table matches → glue (stop). No match → continue | this skill |
| 2 | **G-PKG-NAME** structured ask. Record in `Workspace decisions`. No manager `init` until this passes | this skill |
| 2a | **G-SKORE-MODE** ask: local | hub | mlflow (+ hub workspace name if hub; + MLflow tracking URI if mlflow). Determines `<SKORE_PROJECT_INIT>` form + skore install variant. → `references/g_skore_mode.md` | this skill |
| 3 | Drop `pyproject.toml` from `templates/pyproject.toml` (substitute `<pkg>`). Hand off to `python-env-manager` for editable install | this skill → env-manager |
| 4 | Create `src/<pkg>/` with skeletons from `templates/src_*.py` | this skill |
| 5 | Create `experiments/01_baseline.py` from `templates/experiment.py` (substitute `<pkg>`, `<SKORE_PROJECT_INIT>` per G-SKORE-MODE, `<project-name>`) | this skill |
| 6 | Create empty `tests/smoke/`. Verify pytest on manifest | this skill |
| 6a | Create empty `audit/` | this skill |
| 7 | Create `journal/JOURNAL.md` one-line placeholder; `iterate-ml-experiment` rewrites it | this skill |
| 8 | Create empty `scratch/` (no README — owned by `python-api`) | this skill |
| 9 | Create empty `reports/` | this skill |
| 10 | Touch `.gitignore` — drop template if none; else suggest patch (always ask about `reports/`). **Never ignore the whole `data/`** (EDA deliverables live there); to keep raw inputs out of git, ignore specific input paths only and ask | this skill |
| 11 | **Hand off to `python-code-style`** § Initial setup for `ruff.toml` + first pass — invoking the skill teaches NumPyDoc and (once files carry real content) contextualizes their comments to the problem | this skill → python-code-style |
| 12 | Hand back to the relevant sibling (`iterate-ml-experiment` for design note, etc.) | this skill → next caller |

→ next: `iterate-ml-experiment` § 0 (bootstrap) for the first
design note.

## Files in src/<pkg>/

Each has a narrow contract:

- **`__init__.py`** — exposes `PROJECT_ROOT` (absolute, derived
  from `__file__`, not CWD). Modules needing project-relative
  paths import this constant. Requires editable install.
- **`data.py`** — loaders, materialization of `X`, `y`, any
  `split_kwargs` (groups, time, …) at the X marker. Pipeline
  mechanics in `build-ml-pipeline`.
- **`features.py`** — feature functions and transformers.
- **`pipeline.py`** — the learner declaration (a `SkrubLearner`).
  `build_learner` exposes `data_dir_preview=None` so the
  experiment script can pass an absolute path from `PROJECT_ROOT`.
- **`evaluate.py`** — **only** the inputs to `skore.evaluate`:
  the cross-validator (`splitter = ...`), optional metric
  overrides. Does NOT call `skore.evaluate`, does NOT open a
  Project, does NOT persist.

## Experiment scripts — `experiments/NN_*.py`

`# %%` cell markers, not `.ipynb`. Template:
`templates/experiment.py`. What the script does:

1. Open / attach to the `skore.Project` at `reports/` (or hub /
   mlflow server, per `skore mode:`).
2. Import the learner from `<pkg>.pipeline` and CV from
   `<pkg>.evaluate`.
3. Call `skore.evaluate(...)`.
4. Call `project.put("<experiment-key>", report)`.

Confirm signatures via `python-api`. Cross-validator choice is
`evaluate-ml-pipeline`.

**Project init substitution** — the `<SKORE_PROJECT_INIT>` marker
in `templates/experiment.py` is replaced at scaffold time per the
recorded `skore mode:` decision. Three forms (local / hub / mlflow),
side-by-side anatomy, audit-file copy rule:
→ `references/g_skore_mode.md`.

**Experiment scripts stay clean of agent-only `print(...)`.**
Inspection lives in `scratch/`. One exception: a bare `report`
expression — that's a notebook-display side effect.

**Experiment key convention** — the file's stem (e.g.
`01_baseline.py` → `"01_baseline"`). One file → one key → one
report.

## Companion skills

| Skill | Relationship |
|---|---|
| `iterate-ml-experiment` | Owns `journal/JOURNAL.md` and per-experiment design notes. This skill places empty `journal/`; that skill fills it |
| `explore-ml-data` | Owns the EDA deliverables inside the user's `data/` (`data/eda.py`, `data/eda.md`, `data/eda_<table>.html`) — the one exception to "this skill doesn't touch `data/`". Reads raw data, never rewrites it |
| `build-ml-pipeline` | Body of `pipeline.py`, `features.py`, `data.py` |
| `evaluate-ml-pipeline` | Body of `evaluate.py`; CV strategy |
| `test-ml-pipeline` | Layout of `tests/<category>/` + stem-pairing rule |
| `smoke-test-ml-pipeline` | Body of the smoke test once design note is approved |
| `audit-ml-pipeline` | Body of `audit/`. Read-only against the workspace |
| `python-api` | skore / skrub / sklearn signatures |
| `python-env-manager` | Detection + install commands + bootstrap |
| `data-science-python-stack` | What to install (Tier 1/2/3) |
| `python-code-style` | `ruff.toml` drop + NumPyDoc convention (step 11) |

## Templates

- `templates/experiment.py` — copied per new experiment
- `templates/pyproject.toml` — declares `src/<pkg>/` as installable
- `templates/src___init__.py` — package init with `PROJECT_ROOT`
- `templates/src_data.py` / `src_features.py` / `src_pipeline.py` /
  `src_evaluate.py` — one-time skeletons
- `templates/.gitignore` — dropped at scaffold if none exists

**Copy, don't rewrite.** Section names encode contracts.

## References (load on demand)

- `references/scaffold_steps.md` — full prose elaboration of the
  13-step Decision flow with examples and rationale.
- `references/g_skore_mode.md` — the G-SKORE-MODE gate in detail:
  the three project init forms (local / hub / mlflow) side-by-side,
  anatomy of the `<SKORE_PROJECT_INIT>` substitution, switching
  mid-project, out-of-scope notes (running the MLflow server, Skore
  Hub account creation).
