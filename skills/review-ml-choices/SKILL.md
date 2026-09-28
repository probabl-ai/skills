---
name: review-ml-choices
description: >
  Show the project choices already stored in status and let the
  user change one by re-entering the skill that owns it. Trigger
  when the user asks what we decided, what the current settings
  are, or to change a stored project choice.

  SKIP an explicit sync, export, or “a constraint changed”
  request — those load sync-ml-reports, export-ml-project, or
  frame-ml-problem directly.

  HOW TO USE: run `review choices`, show that board, then load
  one owning skill. Do not policy set from here.
---

# Review ML Choices

Show stored choices. A change loads the skill that already owns
that decision. Do not write `.skore` or the journal from here.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
The board uses data-science labels: where reports go, executed
notebooks, documentation site, git commits, who manages the
environment, data analysis, and each filled framing cell
(prediction goal, deployment, metric, validation, and the
others below). Do not put skill
ids, `G-*` names, or the wrapper CLI in the question.

## Sequence

1. Run `python -m skore_skills review choices`. The JSON is the
   board. Do not rebuild which rows are offered. Do not run
   `frame show` or `frame clear` here.
2. **AskUserQuestion**, one pick. Say first, in 2–4 lines, what a
   change authorizes — re-entering that setup, not a silent flag
   flip — and echo the current values from the JSON. A file link
   is an addition, never the context.

   Options are **Keep these** plus one option per `changeable`
   row and one option per `framing` row. `read_only` and
   `not_offered` are context, not options. Use each row's
   `value`. For `not_offered`, say that row's `reason`. When
   `framing_reason` is set, say it and do not offer framing rows.
3. **Keep these** → stop. Do not load a skill.
4. One `changeable` row → load that row's `skill` and stop. Do
   not `policy set`. Do not run the child's commands from memory.

   - `skore_mode` → the user asked to change where reports go.
   - `notebooks_site` → notebooks and the documentation site.
   - `git_autocommit` → the user asked to change that choice.
   - `env_managed` → do not run `env add-skore` here. If the
     recorded destination is `hub` or `mlflow`, do not use
     `--mode local`.
   - `data_analysis` when `action` is `rerun` → do not write a
     JOURNAL `skipped` row. The written analysis stays; the
     change is to run it again.
5. One `framing` row → load `frame-ml-problem` naming that
   row's `id`. Do not blank the cell here.
6. A request to change a `read_only` row: say that row's
   `reason` and stop. Do not load `setup-workspace` to rename.
   Do not `policy set`.

## Stop conditions

- Do not `policy set` any key.
- Do not edit JOURNAL, including a Data understanding `skipped`
  row.
- Do not load `sync-ml-reports` when `policy.skore_mode` is
  unset.
- Do not `env add-skore`, `git commit`, or scaffold `src/`.
- If the owning skill is not installed, show the value and skip
  the change in one line. Do not invent that skill's steps.
