---
name: setup-workspace
description: >
  Detect an existing ML workspace or scaffold a fresh one. Owns
  layout, G-PKG-NAME, and G-SKORE-MODE only. Persist those in
  `.skore-workspace.json`. Missing env manager or tabular library
  is a status fact — ask triage; do not dispatch sibling actions.

  TRIGGER for a new ML project, first experiment, first reusable
  modules, notebook-to-script organization, or a new experiment
  iteration.

  SKIP edits inside an already-populated module and pipeline,
  evaluation, or API mechanics owned by sibling skills.

  HOW TO USE: detect first. For a fresh layout resolve package
  name and skore mode, then run
  `python -m skore_skills scaffold --package <pkg>`. For an
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
- **Do not dispatch env or tabular skills.** If `status` shows no
  `env_manager` or `tabular`, say so and ask triage. A manager on
  PATH is context, not permission.
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
that setup is complete and ask triage. Do not create
`experiments/NN_*.py` before its design note is approved.

## Pre-flight

```
- [ ] Layout: fresh | existing/glue
- [ ] G-PKG-NAME: <pkg> | ask
- [ ] G-SKORE-MODE: local | hub | mlflow | ask
- [ ] Command: python -m skore_skills scaffold --package <pkg>
- [ ] Persist: python -m skore_skills policy set package <pkg>
              python -m skore_skills policy set skore_mode <mode>
```

## Fresh scaffold

After gates resolve:

```bash
python -m skore_skills scaffold --package <pkg>
```

The CLI copies packaged templates and substitutes the import name.
Do not reproduce the old per-template write recipe and do not pass
`--force` during normal setup.

Persist after a successful scaffold:

```bash
python -m skore_skills policy set package <pkg>
python -m skore_skills policy set skore_mode local
```

If `status` still shows missing `env_manager` or `tabular`, stop and
ask triage. Do not load `setup-python-env` or `choose-python-library`.

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

The package scaffold must be installed editable before imports are
expected from every CWD. That install is a status fact for triage,
not a dispatch from this skill.

## Existing workspace

Keep the live package name, build system, manager, and folders.
Add only missing glue explicitly needed by the user. No rebuild,
`--force`, or automatic conversion.

## New versus in-place experiment

When iterating a completed experiment, ask:

1. new `NN_<short>_v2.py`, preserving the old result; or
2. edit the existing `NN_<short>.py`, overwriting that experiment
   key and revisiting the paired smoke test.

Do not pick silently and do not edit the design note here. After the
choice, stop and ask triage.

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
