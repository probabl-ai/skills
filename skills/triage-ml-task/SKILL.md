---
name: triage-ml-task
description: >
  Session owner: list installed entry skills and ask which to run.
  Load a skill without asking only when the request is certain to
  be that skill. Trigger on an ambiguous request, a finished stage,
  a workspace-open session, or "what should we do next".
---

# Triage ML Task

This is the session owner. Stage skills do the work; you only
route and ask. Do not execute another skill's methodology.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Questions and replies describe the **work** (explore the data,
build a model) — not skill ids, `G-*` names, or the wrapper CLI.
Run `python -m skore_skills …` yourself; do not quote it.

Every question here carries its own context: 2–4 lines on what the
answer authorizes, the workspace facts it rests on — echoed inline
from `status` (scaffold, `data_analysis`, `loop_stage`) — and what
each option leads to. A file link is an addition, never the
context.

## Procedure

1. Run `python -m skore_skills status`. Read `skills`, `data_analysis`,
   `loop_stage`, and the filesystem snapshot. If `.skore` is
   missing, that is expected. Do not treat a missing file as an
   empty project when `src/` or `journal/` exist.
2. **Certain request** — load that skill. Tell the user the work
   you are starting, not the catalog id. Do not list the catalog.
   `status.skills` is a per-id dict. Load the mapped skill only if
   `status.skills.<id>` is true; else one-line skip and do not
   invent that skill's steps:

   | User intent | Skill |
   |---|---|
   | env / pixi / uv / python environment | `setup-python-env` |
   | scaffold / layout / package folders | `setup-workspace` |
   | git init / first commit / ignore | `setup-git` |
   | add or install a named package | `add-python-package` |
   | exploratory data analysis / explore the data | `explore-ml-data` |
   | evaluate / metrics / CV / run `skore.evaluate` | `evaluate-ml-pipeline` (child gate may STOP) |
   | audit / open / narrate an existing report | `audit-ml-pipeline` (child gate may STOP) |
   | build / model a pipeline | `model-ml-pipeline` |
   | smoke / pytest row-count / why is smoke failing | `smoke-test-ml-pipeline` (debug; does not start evaluate) |
   | backlog / history / record the run / what next | `manage-ml-backlog` |
   | review this stem / review the last experiment | `review-ml-experiment` |
   | I want to try X / here is an idea / what if we / a pasted URL or issue | `shape-user-idea` |
   | papers / literature / what do people do for (no design note in progress) | `search-ml-literature` |
   | notebook / ipynb | `export-ml-notebook` |
   | notebook viewer on the site / executed report | `export-ml-notebook` (`--html`) |
   | website / mkdocs / documentation site | `export-ml-site` |
   | export (generic) | `export-ml-project` |
   | sync / migrate reports / switch skore mode / upload reports to hub or mlflow | `sync-ml-reports` |
   | set up / bootstrap this project (generic) | `setup-ml-project` |
   | “is this leakage” on the table | `explore-ml-data` (even if `data_analysis` is present). Do not load `research-ml-practice`. |
   | research / literature on a modeling design (design note exists or modeling in progress) | `model-ml-pipeline`. Do not load `research-ml-practice`. |
   | which comparison metric / how new rows should be split / which baseline / a problem constraint changed | `frame-ml-problem`. Not a request to run evaluation. |
   | what did we decide / show stored choices / change a stored project choice | `review-ml-choices` |

   An explicit sync, generic export, or changed modeling
   constraint still uses those rows. Do not send them through
   `review-ml-choices`.

   A git init, first commit, or ignore request loads `setup-git`
   and stops. Do not write `git init`, a `.gitignore`, or a commit
   plan. With no shell, the whole answer is that `setup-git` is
   loaded. Do not describe the commands that skill will run.

   "What should we try next?" while `loop_stage` is `backlog` and
   `manage-ml-backlog` is installed loads that skill and stops.
   Do not ask the user to choose explore, build, review, or export.

   Certain EDA: run `python -m skore_skills status`, load
   `explore-ml-data`, stop. Do not inventory `data/`, list
   missingness or distributions, or start EDA methodology.

   Certain generic export: run `python -m skore_skills status`,
   then load `export-ml-project`. Do not list notebook / `--html`
   / site as sibling options.

   **Modeling while `status.data_analysis` is `missing`:** if the certain
   skill is `model-ml-pipeline` (or the user asked to build the
   first experiment) **and** `status.skills.explore-ml-data` is
   true, do not load modeling yet. **AskUserQuestion** two options:
   run exploratory data analysis first (default) vs proceed to
   modeling with user-supplied facts. Do not invent dataset facts
   here. If `data_analysis` is `present` or `skipped`, load
   `model-ml-pipeline` with no extra gate (still only if that id
   is true).

3. **Uncertain** (open session, “what can you do”, finished stage,
   mixed intent) — **AskUserQuestion** with the **installed**
   entry work only. One pick, then load the mapped skill.

   Offer a label only if `status.skills.<id>` is true. User-visible
   labels (no ids):

   - Set up the project → `setup-ml-project`
   - Explore the data → `explore-ml-data`
   - Build a model → `model-ml-pipeline`
   - Review the last experiment → `review-ml-experiment`
   - Record / decide what next → `manage-ml-backlog`
   - Export → `export-ml-project`
   - Sync reports → `sync-ml-reports`
   - Review choices → `review-ml-choices`

   If none of those ids are true, say so in one line; do not
   invent a menu.

   Do not put evaluate or audit on this board (certain requests
   still load `evaluate-ml-pipeline` / `audit-ml-pipeline`). Do
   not put shaping an idea or literature search on this board
   (certain requests and `manage-ml-backlog` still load
   `shape-user-idea` / `search-ml-literature`).

   If `status.data_analysis` is `missing` and
   `status.skills.explore-ml-data` is true, recommend exploring
   the data first. Do not auto-load it. When `data_analysis` is
   `present` or `skipped` and `loop_stage` is `backlog`, recommend
   recording the run / deciding what next when
   `manage-ml-backlog` is true. Do not auto-load it.

   Do not put internals on this board (`build-ml-pipeline`,
   `smoke-test-ml-pipeline` except as a **certain** debug load,
   `frame-ml-problem`, `choose-python-library`,
   `research-ml-practice`, `plot-ml-figure`, stack refs).

## Stop conditions

- Do not design experiments, write pipelines, or run exploratory
  data analysis yourself. Certain EDA is load `explore-ml-data`
  only — no data inventory and no EDA checklist.
- Do not load every skill.
- Do not invent workspace facts when status is unavailable.
- Do not treat a missing `.skore` as an empty project when `src/`
  or `journal/` exist.
- Do not invent a missing skill's steps from memory.
- Do not put `evaluate-ml-pipeline` or `audit-ml-pipeline` on the
  uncertain entry board (certain requests still load them).
- A missing review, backlog, user-idea, or literature skill is
  a one-line skip. Do not invent that skill's procedure.
- Do not put `shape-user-idea` or `search-ml-literature` on the
  uncertain entry board.
- Do not put `frame-ml-problem` on the uncertain entry board
  (a certain metric, split, baseline, or changed-constraint
  request still loads it).
- Certain generic export: run `python -m skore_skills status`,
  load `export-ml-project` only — no sibling-skill menu.

End of every other skill's turn returns here when this skill is
installed.
