---
name: export-ml-project
description: >
  Coordinate on-demand export: executed notebooks and/or an
  offline MkDocs documentation site. Trigger on a generic
  "export" request, or to flip the notebooks/site gates after
  setup.
---

# Export ML Project

Ordering only. Children own convert and site commands.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
The multi-select uses **Executed notebooks** and **Documentation
site**. Do not put skill ids, convert flags, or the wrapper CLI
in the question.

## Sequence

1. `python -m skore_skills status`. Read `policy.notebooks`,
   `policy.site`, and `skills`.
2. **AskUserQuestion** with `allow_multiple`. Say first, in 2–4
   lines, what each box authorizes (toolchain installs, convert
   re-execution, a built site) and that both answers persist as
   policy. A file link is an addition, never the context.

   - Executed notebooks — preselected iff `policy.notebooks` is
     not false (`true` or `null`)
   - Documentation site — preselected iff `policy.site` is not
     false (`true` or `null`)

3. Persist each box this turn: checked →
   `python -m skore_skills policy set notebooks true` (or `site`);
   unchecked → `false`. Do not leave them `null`. Do not write
   notebooks or site into JOURNAL; policy is the record.
4. Load each checked child only if `status.skills.<id>` is true;
   else one-line skip. Do not invent that skill's steps:

   - notebooks → `export-ml-notebook` (installs toolchain if this
     is the first yes, then convert; `--html` only if the user
     wants the notebook viewer on the site)
   - site → `export-ml-site` (installs `mkdocs-material` if first
     yes, init if needed, then build; never convert)

5. Load `triage-ml-task` only if `status.skills.triage-ml-task`
   is true; else stop.

## Stop conditions

- Do not `git end-turn` or `git commit`.
- Do not invent convert or `mkdocs` steps when the child skill is
  missing.
- Do not `pixi add` / `uv add` from this coordinator.
