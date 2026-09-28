---
name: setup-ml-project
description: >
  Coordinate first-time ML project setup. Trigger when the user asks
  to set up or bootstrap a complete ML workspace. Ask a multi-select
  of installed pieces (env, workspace, editable, git), all
  preselected; run only what stays checked.
---

# Set Up ML Project

Ordering only. Never run a skipped skill's steps from memory.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
The multi-select uses data-science labels only (Python
environment, workspace layout, editable install, Git). Do not
put skill ids, `G-*` names, or the wrapper CLI in the question.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] status (read skills + has_src)
- [ ] ask which pieces (all installed boxes preselected)
- [ ] load selected | skip
- [ ] status again; load triage-ml-task only if
      status.skills.triage-ml-task is true
```

## Sequence

1. Run `python -m skore_skills status`. `status.skills` is a
   per-id dict, never a boolean.
2. **AskUserQuestion** with `allow_multiple`. Say first, in 2–4
   lines, what the answer authorizes (which pieces run, in which
   order) and the `status` facts each box rests on — detected
   manager, `has_src`, git presence. A file link is an addition,
   never the context. Include a box only when **that** id is true.
   Option labels (user-visible, no ids):

   - Python environment
   - Workspace layout
   - Editable install — show when
     `status.skills.add-python-package` is true and (`has_src`
     is true **or** workspace is on this board)
   - Git

   Map checked labels to `setup-python-env`, `setup-workspace`,
   `add-python-package`, `setup-git` when loading.

   **Preselect every installed piece** (all boxes on). Do not
   leave a box off because the layout already looks done. The
   user may uncheck.
3. Load **still-checked** skills only, in this order: env →
   workspace → editable (`has_src`) → git. Load `<id>` only if
   `status.skills.<id>` is true; else one-line skip. Do not
   invent that skill's steps.
4. Unchecked or that id is false → one-line skip.
5. Editable checked, `has_src` false, and workspace not selected
   → one-line stop. Do not scaffold from this meta.
6. `status` again. Load `triage-ml-task` only if
   `status.skills.triage-ml-task` is true; else stop. Do not
   start exploratory data analysis or a pipeline.

## Stop conditions

- Do not pick package name or env manager here; the loaded skills
  ask those.
- Do not ask tabular library, skore mode, notebooks, or site.
- Do not install sklearn, skrub, or pandas. The selected
  `setup-python-env` skill installs plain `skore` during bootstrap;
  do not install or configure Skore directly from this coordinator.
- Do not write experiment or pipeline bodies.
- Do not commit except by loading `setup-git`.
- Do not abort setup because one skill is missing.
- Do not invent a missing skill's procedure.
- Do not `pixi add` / `uv add` from this coordinator;
  `add-python-package` owns install.
