---
name: triage-ml-task
description: >
  Own the canonical ML loop and the human-in-the-loop. Trigger on
  an ambiguous request, a finished stage, a workspace-open session,
  or "what should we do next". Read status, name the current stage,
  and ask one question before naming the next skill.
---

# Triage ML Task

This is the session owner. Stage skills do the work; you only
route and ask.

Canonical stages, one at a time:

1. `setup` — `setup-ml-project`
2. `eda` — `explore-ml-data`
3. `implement` — `model-ml-pipeline` (build then smoke)
4. `evaluate` — `evaluate-ml-pipeline`
5. `audit` — `audit-ml-pipeline`
6. `backlog` — `manage-ml-backlog` when present, otherwise name it
   as the next loop step

## Procedure

1. Run `python -m skore_skills status`.
2. Read `loop_stage` and `policy` (the `workspace` section of
   `.skore`). If `.skore` is missing, that is expected: use the
   filesystem snapshot and inferred `loop_stage`. Do not treat a
   missing file as an empty project when `src/` or `journal/` exist.
3. Ask **exactly one** question:
   - stay on this stage and go deeper,
   - move to the next stage,
   - confirm/persist detected facts into `.skore`,
   - or change a persisted choice (`git.autocommit`, env, tabular).
4. Name the pack or skill to load. Do not execute its methodology.

## Stop conditions

- Do not design experiments, write pipelines, or run EDA yourself.
- Do not load every skill.
- Do not invent workspace facts when status is unavailable.
- Do not treat a missing `.skore` as an empty project when `src/`
  or `journal/` exist.
- Do not install packs without the user's request.
- Do not treat iterate as the session owner.

End of every other skill's turn returns here.
