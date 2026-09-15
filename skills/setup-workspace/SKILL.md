---
name: setup-workspace
description: >
  Detect an existing ML workspace or scaffold a fresh one. Reusable
  code lives in `src/<pkg>/`; experiments are `# %%` scripts;
  design notes and index live in `journal/`; reports in `reports/`;
  agent probes in `scratch/`. Existing conventions always win.

  TRIGGER for a new ML project, first experiment, first reusable
  modules, notebook-to-script organization, or a new experiment
  iteration.

  SKIP edits inside an already-populated module and pipeline,
  evaluation, or API mechanics owned by sibling skills.

  HOW TO USE: detect first. For a fresh layout resolve package,
  tabular library, environment manager, and skore mode gates, then
  run `python -m skore_skills scaffold --package <pkg>`. For an
  existing layout, glue to it without renaming or overwriting.
---

# Organize ML Workspace

Decide where artifacts live. Do not design an experiment here.

## Stop conditions

- **Existing layout wins.** Never rename, relocate, tidy, or
  overwrite detected folders.
- **G-PKG-NAME is asked, not inferred.** On a fresh/incomplete
  layout, ask for the `src/<pkg>/` import name and propose the
  snake-case folder name as default. “You pick” does not resolve it.
  A complete `[project] name` + matching `src/<pkg>/` resolves it.
- **G-ENV-MGR is owned by `setup-python-env`.** A manager on PATH
  is context, not permission. Do not run `pixi init` before the gate.
- **G-TABULAR is asked through `choose-python-library`.** Do not
  silently choose pandas.
- **G-SKORE-MODE is asked:** local, hub, or mlflow; local is the
  proposed default. Keep a recorded mode unless an explicit migration
  is approved.
- **Design note first.** Scaffold may create a commented/empty
  `experiments/01_baseline.py` shell, never a runnable learner /
  `skore.evaluate` / `project.put` body.
- **Scratch is read-only against skore Project.** Never evaluate or
  put from a probe. `Project.get` is by id: use `summarize()` to map
  key to id before treating a KeyError as a missing report.
- Existing `.ipynb` files require a user decision before conversion.

## Detection

Inspect root `pyproject.toml`, `src/`, `experiments/`, `journal/`,
and manager manifests.

- Any coherent signal → **existing/glue**. Reuse package and paths.
- No signals → **fresh**. Resolve all gates before scaffolding.
- Manifest without matching `src/<pkg>/` → incomplete; reconfirm
  package name rather than inventing it.

For a request to add an experiment to an existing workspace, report
that setup is complete and ask the user to run the model/loop pack or
ask triage. Do not create `experiments/NN_*.py` before its design
note is approved.

## Pre-flight

```
- [ ] Layout: fresh | existing/glue
- [ ] G-PKG-NAME: <pkg> | ask
- [ ] G-TABULAR: pandas | polars | ask
- [ ] G-ENV-MGR: <manager> | setup-python-env
- [ ] G-SKORE-MODE: local | hub | mlflow | ask
- [ ] Command: python -m skore_skills scaffold --package <pkg>
```

## Fresh scaffold

After gates resolve:

```bash
python -m skore_skills scaffold --package <pkg>
```

The CLI copies packaged templates, substitutes the import name, and
writes the full journal index (Status, Data understanding, History,
Backlog). Do not reproduce the old per-template write recipe and do
not pass `--force` during normal setup.

The default workspace contract is:

```text
src/<pkg>/                 reusable data/features/pipeline/evaluate
experiments/               one # %% script per approved experiment
journal/JOURNAL.md         status + history index
journal/NN_<short>.md      design note
audit/                     per-experiment read-only audit scripts
tests/smoke/               paired smoke tests
scratch/                   ephemeral, gitignored agent work
reports/                   durable human-facing exports
data/                      user-owned inputs; EDA deliverables only
```

The package scaffold must be installed editable through
`setup-python-env` before imports are expected from every CWD.

## Existing workspace

Keep the live package name, build system, manager, and folders.
Add only missing glue explicitly needed by the user. No rebuild,
`--force`, or automatic conversion.

## New versus in-place experiment

When iterating a completed experiment, ask:

1. new `NN_<short>_v2.py`, preserving the old result; or
2. edit the existing `NN_<short>.py`, overwriting that experiment
   key and revisiting the paired smoke test.

Do not pick silently and do not edit the design note here.

## Pairing

Use one stem across:

```text
journal/NN_<short>.md
experiments/NN_<short>.py
tests/smoke/test_NN_<short>.py
audit/NN_<short>.py
```

## References

- `references/g_skore_mode.md`
- `references/scaffold_steps.md` (rationale/legacy only; CLI is
  primary)
