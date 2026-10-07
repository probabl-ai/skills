---
name: frame-ml-problem
description: >
  Lock the problem, the deployment setting, the comparison metric,
  the baseline, and the fold count in the journal before any
  model code. Ask every missing decision in one turn, from
  `frame show`. Does not write Python, estimator hyperparameters,
  or splitter constructors.

  TRIGGER when the user asks which metric to compare on, how new
  rows should be split, which baseline to use, or says a problem
  constraint changed. Not when they ask to run evaluation or CV.

  HOW TO USE: run `python -m skore_skills frame show`. Read each
  reference named in `questions` once, ask every key in `missing`
  in one message, and write every answered cell. If a key is
  still unanswered, ask it and stop. If the write fills every
  required cell, run `frame show` again and AskUserQuestion
  Lock / Modify / Stop, then stop. Do not lock in that turn.
  If that command is missing, or the problem is not classification
  or regression, read `references/fallback.md` and do not invent
  the closed menu.
---

# Frame ML Problem

Write `## Modeling decisions` in `journal/JOURNAL.md`. The table
is the contract. This skill does not declare a learner and does
not evaluate one.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Journal cells describe this dataset. Do not name the skills
framework, the CLI, or a splitter class in the table. Questions
use data-science language — not skill ids, `G-*` names, or the
wrapper CLI.

## Procedure

1. Run `python -m skore_skills status`. If `status.setup.pending`
   is non-empty and `status.skills.setup-ml-project` is true,
   load `setup-ml-project` and stop. Do not start this skill.
   When it returns, continue. Do not load it again on this turn.
   If that skill is not installed, name the pending pieces in
   one line and stop. Do not invent `git init`, scaffold, or
   `env init`. If `status.setup.env` or `status.setup.workspace`
   is `declined`, stop in one line. A declined `git` or
   `editable` is not asked again; continue. If `data_analysis` is
   `missing` and `explore-ml-data` is installed, **AskUserQuestion**:
   explore first (default) or continue from facts the user stated.
   Explore loads `explore-ml-data` and stops. Do not invent dataset
   facts. Do not ask this again once `data_analysis` is `present`
   or `skipped`.
2. Run `python -m skore_skills frame show`. When the user is
   changing a locked constraint and named one cell, add
   `--revise`. When they are changing a constraint and did not
   name a cell, **AskUserQuestion** one pick among the filled
   decisions (skip `n/a`) and stop. Do not also ask for a typed
   answer. Do not `--revise`, do not `frame clear`, and do not
   edit the journal on that turn. JSON `action` is
   authoritative. Do not invent a menu. If the command is missing
   or exits without JSON, read `references/fallback.md` and follow
   it. Do not open another reference. Do not guess candidates.
3. `stop` — say the JSON `reason` and stop.
4. `ask` / `uncovered` — read `references/fallback.md` only. Write
   Prediction goal `uncovered` and the prose cells it names. Set
   Status to `draft`. Stop this turn.
5. `ask` / `missing_keys` — read each distinct `reference` in
   `questions` once before asking. Do not open any other file
   under `references/`. Ask every key in `missing` in one
   message. For a question that has `candidates`, those are the
   options. When `candidates` is absent, ask for the value the
   reference describes. Draw on three sources, and only what they
   actually say: the EDA report, free-form text that came with
   the data if any is present (notes, a dictionary, or a README
   beside the raw files), and facts the user stated. If none of
   that text is present, do not invent it. When one of them
   already states the fact, quote it in the question. Write every
   Value cell the user answered in this turn. Do not rename
   Variable cells. Do not stop after the first cell.
   When the deployment makes other rows inapplicable, set those
   cells to `n/a` in the same edit. Horizon, gap, and time role
   are `n/a` unless deployment is time. Generalize-to is `n/a`
   unless deployment is groups. A fold count of `1` is one
   train/test split drawn from a single table. When the EDA
   report, the text shipped with the data, or the user already
   names a separate training table and test table, offer using
   that split in the folds question and write `predefined` if
   they choose it. Do not offer it otherwise. Do not write
   `prefit` in the table. Once any decision cell is filled and
   Status is not `locked`, set Status to `draft`. Do not type
   `Revised on`; only `frame clear` writes that date. If any key in
   `missing` is still unanswered, ask those keys and stop. Do
   not invent their values. Do not show the lock menu. If the
   write fills every required cell, run
   `python -m skore_skills frame show` again in this turn. When
   that returns `ask` / `confirm_lock`, follow step 7 in this
   same turn. Do not defer the lock question. If the second
   `frame show` still returns `missing_keys`, ask those keys
   and stop. Do not set Status to `locked`. The sentences that
   filled the cells are not the Lock choice.
6. When the user named one cell and Status is `draft`, do not
   use the lock menu as the change. Run
   `python -m skore_skills frame clear --cell <key>` for that
   cell and stop. Do not write the new value. Do not name any
   other cell as cleared. The command's JSON `blanked` list is
   the record. Status stays `draft`. `frame clear` stamps
   `Revised on`; do not type that date. The next `frame show` asks
   only keys that are still empty or invalid.
7. `ask` / `confirm_lock` or `ask` / `revise` — quote JSON
   `context` inline in 2–4 lines, then one single-choice
   **AskUserQuestion** using only JSON `choices`, in that order,
   and stop. `confirm_lock` labels are **Lock** / **Modify** /
   **Stop**. `revise` labels are **Modify** / **Keep** / **Stop**.
   Do not also ask for a typed answer. The user sentence that
   opened this screen is not a choice. Do not set Status to
   `locked` in that same turn.
   - `lock` on a later turn sets Status to `locked`.
   - `modify` on a revise, when the user named one cell: run
     `python -m skore_skills frame clear --cell <key>` and stop.
     Do not write the new value. Do not type `Revised on`; the
     command stamps that date. Do not blank any other cell by
     hand. The next `frame show` asks only keys that are still
     empty or invalid.
     `modify` with no named cell writes nothing and does not
     `frame clear`: **AskUserQuestion** one pick among the filled
     decisions (skip `n/a`) and stop. Do not also ask for a typed
     answer.
   - `keep` leaves the locked table unchanged.
   - `stop` writes nothing further.
8. `proceed` — the table is locked. If `translation` is null, say
   that this lock has no splitter translation. Do not load
   `build-ml-pipeline` and do not return to `model-ml-pipeline`.
   Stop. If `model-ml-pipeline` dispatched this turn, return to
   that coordinator and stop. Do not start build, write a design
   note, or run the git close from here. Otherwise run
   `python -m skore_skills git end-turn --stage implement`. If
   JSON `action` is `invoke`, load `persist-ml-git` only if
   `status.skills.persist-ml-git` is true and stop. Otherwise
   load `triage-ml-task` only if that skill is installed.

## Stop conditions

- Do not write Python, a pipeline, a test, or a design note.
- Do not put a class name or a constructor argument in the journal.
  `TimeSeriesSplit`, `KFold`, `GroupKFold`, and `gap=` stay out of
  the table.
- Do not re-ask a key that is absent from `missing`.
- Do not add an option that is absent from `candidates`.
- Do not open a reference the JSON did not name, except
  `references/fallback.md` when the command is missing.
- A locked table changes only through `frame show --revise`, then
  the same fill and confirm gates. `keep` does not edit it.
- On `modify`, `frame clear` is the only journal edit, and only
  for the cell the user named. It stamps `Revised on`; do not
  type that date. Do not rewrite `experiments/`,
  `audit/`, or a report in this skill.
- After a cell is blanked, do not run an existing experiment
  script. Say that it still uses the previous splitter and
  metric. The next build or evaluate rewrites it after the table
  is locked again.
