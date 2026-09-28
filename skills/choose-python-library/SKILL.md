---
name: choose-python-library
description: >
  Resolve a genuine choice between Python libraries for one job,
  then ask `add-python-package` to add the chosen dependency.
  Trigger for competing-library questions or an optional package not
  already fixed by the project stack — at first use (tabular
  exploration, pipeline, or eval extras), never during workspace
  setup.
---

# Choose Python Library

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Present library options as a data-science choice for this job.
Do not name skill ids or the wrapper CLI in the question.

1. State the job and constraints.
2. Run `python -m skore_skills env stack`. A job listed under
   `competing` is a genuine choice; anything the policy already
   fixes (`mandatory`, `stage`, `export`) is settled — use it
   rather than reopening the choice. Do not read the packaged
   JSON file directly; it lives inside the installed package.
3. For a genuine choice, present the smallest useful option set and
   ask the user. Do not pick silently.
4. After the user chooses, load `add-python-package` when
   `status.skills` reports it installed. If it is not installed,
   name the package and stop. Do not call `env add` from this
   skill. Typical callers: `explore-ml-data` (pandas vs polars),
   later extras (tuning). Not `setup-workspace`. Plotting jobs:
   load `plot-ml-figure` if installed; do not present matplotlib
   vs seaborn vs plotly.
5. Confirm symbols with `python -m skore_skills api get <dotted>`
   before writing calls. Scope for one package is
   `python -m skore_skills env route <pkg>`, not a guess.

## Stop conditions

- Do not install every candidate.
- Do not use popularity alone as a technical decision.
- Do not run pip directly in a managed project.
- Do not substitute black/isort for Ruff or sklearn Pipeline for
  skrub DataOps; those choices are already fixed.
- Do not present matplotlib vs seaborn vs plotly; that job is
  `plot-ml-figure`.
