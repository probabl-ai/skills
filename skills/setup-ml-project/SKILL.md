---
name: setup-ml-project
description: >
  Coordinate ML project setup. Trigger when the user asks to set up
  or bootstrap a workspace, or when a pipeline stage finds
  status.setup.pending non-empty. Ask only those pending pieces.
  The question tells the user to select each piece they want.
  It starts by saying that before any modeling, the workspace
  should be set up. Do not say the order the pieces will run.
  Do not offer a piece that is already done or declined.
  Then, in that same opening phase, ask the environment manager,
  whether we manage the env, the import name, and git autocommit
  — only for pieces the user selects, and answers that are not
  already recorded. Persist those answers. When Git is selected,
  run the pre-change snapshot check before any setup write. Ask
  to commit the current files only when that check says ask. An
  empty folder or a clean tree records skipped and does not ask.
  Then run only what the user selects. Git may ask once, just
  before the first commit, which unknown files to keep. Return
  to the skill that dispatched this turn.
metadata:
  modelTier: small
---

# Set Up ML Project

Ordering only. Never run a skipped skill's steps from memory.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Questions use data-science labels only (Python environment,
workspace layout, editable install, Git, environment manager,
whether we manage the Python environment, Python import name,
automatic commits). Do not put skill ids, `G-*` names, or the
wrapper CLI in the question.

## Lookup

Run `status` and `env detect` first. Take the first row that
matches. Do not stop after reading the table.

| `setup.pending` | Then |
|---|---|
| empty | step 9. Do not ask. |
| every pending piece's skill id is false | name the missing skills in one line, then step 9 |
| non-empty | step 3 multi-select, then step 4, then the stop row, then the choice table |

Stop row: editable is selected, `has_src` is false, and workspace
is not selected → one-line stop. Do not ask the remaining choices.
Do not scaffold from this skill.

Choice table. Apply every row that matches. Skip a row whose
piece was not selected, was not on the board, or whose value is
already recorded. Ask and persist before any write.

| Selected piece | Recorded state | Action |
|---|---|---|
| Python environment | detected manager is not `"none"`, not ambiguous, not a mismatch, and `policy.env_manager` is unset | persist that manager. Do not ask. |
| Python environment | `env_manager` is `"none"` and `policy.env_manager` is unset, or `ambiguous`, or `mismatch` | ask, then `policy set env_manager` |
| Python environment | `policy.env.managed` is null | ask whether we manage the env (default yes), then persist |
| Workspace layout | fresh or manager-only, `policy.package` unset, `src/<pkg>/` does not name it | ask the import name (folder name is the default), then `policy set package` |
| Git | `policy.git.autocommit` is null | ask `on` or `off` once, then persist |

Then step 7 when Git is selected, then step 8 in order env,
workspace, editable, git, then step 9.

## Sequence

1. Run `python -m skore_skills status` and
   `python -m skore_skills env detect`. `status.skills` is a
   per-id dict, never a boolean. Read `status.setup`. Each piece
   is `done`, `declined`, or `missing`. `setup.pending` is the
   ordered list of `missing` pieces. Do not `env init`,
   `scaffold`, install a package, or `git init` in this opening
   phase.
2. If `setup.pending` is empty, ask nothing. Go to step 9.
   `done` and `declined` pieces are already answered. Do not
   offer them. Do not ask their environment manager, whether we
   manage the env, import name, or automatic commits again.
3. **AskUserQuestion** with `allow_multiple` for `setup.pending`
   only. Start by saying that before any modeling, the workspace
   should be set up. Then the `status` facts each box rests on —
   detected manager, `has_src`, git presence, and which pieces
   are already recorded. Stay within 2–4 lines. Do not say the
   order the selected pieces will run. A file link is an
   addition, never the context. Include a box only when
   **that** id is true **and** the piece is `missing`. Option
   labels (user-visible, no ids):

   - Python environment — `setup.pending` contains `env` and
     `status.skills.setup-python-env` is true
   - Workspace layout — `setup.pending` contains `workspace`
     and `status.skills.setup-workspace` is true
   - Editable install — `status.skills.add-python-package` is
     true, `status.setup.editable` is `missing`, and
     (`has_src` is true **or** workspace is on this board)
   - Git — `setup.pending` contains `git` and
     `status.skills.setup-git` is true

   Map selected labels to `setup-python-env`, `setup-workspace`,
   `add-python-package`, `setup-git` when loading.

   The question's last line is exactly: Select each one you want.
   Write nothing after that line. Do not add a `done` or
   `declined` piece because the layout already looks
   unfinished. If every pending
   piece's skill id is false, skip the ask, name the missing
   skills in one line, and go to step 9.
4. After the answer, and not in the question, persist each piece
   the user does not select:
   `python -m skore_skills policy set setup.<piece> declined`
   (`env`, `workspace`, `editable`, or `git`). Do not persist
   `declined` for a box that was not on the board.
5. Editable selected, `has_src` false, and workspace not selected
   → one-line stop. Do not ask the remaining choices. Do not
   scaffold from this meta.
6. Ask the remaining choices **now**, before any write. Skip a
   question when the user does not select its piece, it was not
   on the board, or the value is already recorded. Each ask
   states in 2–4 lines what the answer authorizes. Order:

   - **Environment manager** — the user selects Python
     environment. If `env_manager` is not `"none"`, `ambiguous` is
     false, `mismatch` is false, and `policy.env_manager` is
     unset, persist that detected manager. Do not ask. Otherwise
     ask when (`env_manager` is `"none"` and
     `policy.env_manager` is unset, or `ambiguous` is true, or
     `mismatch` is true). Ask with `AskUserQuestion`, using
     `recommended` order. PATH is not permission. Do not
     `curl | sh`. Persist
     `python -m skore_skills policy set env_manager <manager>`.
   - **Whether we manage the env** — the user selects Python
     environment and `policy.env.managed` is null. Default yes.
     Persist `policy set env.managed true` or `false`.
   - **Python import name** — the user selects workspace, the
     layout is fresh or manager-only (no `src/` and no
     `journal/`), `policy.package` is unset, and `src/<pkg>/`
     does not already name it. Folder name is the default
     option. “You pick” / “go fast” does not resolve it.
     Persist `policy set package <pkg>`.
   - **Automatic commits** — the user selects Git and
     `policy.git.autocommit` is null. Ask once: should later
     stages persist with `git commit` (`on`) or never (`off`)?
     That answer consents to the first commit. It does not
     authorize tracking unknown hidden files or review paths.
     Persist `policy set git.autocommit on` or `off`.
     That answer does not decide the pre-change snapshot.

   Do not ask notebooks, the documentation site, tabular
   library, or where reports go.
7. Pre-change snapshot, before any setup write. Run this only
   when Git was selected, `status.skills.setup-git` is true, and
   `policy.git.snapshot` is null. Load `setup-git` and do only
   its pre-change snapshot section, then return here. Do not
   `env init`, `scaffold`, or `git ignore-merge` in this step.
   Do not ask the snapshot question in this skill. The loaded
   section asks only when `git snapshot` returns `ask`. `clean`
   and `nothing_to_commit`, including an empty folder, persist
   `skipped` and do not ask. If Git was not selected,
   `git.snapshot` is already set, or `setup-git` is not
   installed, skip this step. A missing `setup-git` is one
   line, then continue. When the check returns `ask`, the
   commit is still offered if autocommit is `off`.
8. Load **selected** skills only, in this order: env →
   workspace → editable (`has_src`) → git. Load `<id>` only if
   `status.skills.<id>` is true; else one-line skip. Do not
   invent that skill's steps. The loaded skills must not ask
   again for a choice persisted in step 6. After each loaded
   skill returns, persist
   `python -m skore_skills policy set setup.<piece> done`.
   For editable, do that only when
   `env add --editable --execute` exits 0. A non-zero exit leaves
   `setup.editable` missing. Do not mark a skipped piece, or a
   piece the user does not select, `done`.
9. Return to the skill that dispatched this turn (a lifecycle
   stage, or triage waiting on a lifecycle request). Do not
   open the entry board and do not start exploratory data
   analysis or a pipeline from here. When the user asked only
   to set up or bootstrap, `status` again and load
   `triage-ml-task` only if `status.skills.triage-ml-task` is
   true; else stop. That handoff may ask what to do next; it
   is not a setup question.

## Stop conditions

- Do not `env init`, `scaffold`, or install a package before
  step 8. Do not `git init` before step 7.
- Do not offer a `done` or `declined` piece again.
- Do not ask tabular library, skore mode, notebooks, or site.
- Do not ask which hidden files or review paths to keep; `setup-git`
  asks that once, before the first commit.
- Do not install sklearn, skrub, or pandas. The selected
  `setup-python-env` skill installs plain `skore` during bootstrap;
  do not install or configure Skore directly from this coordinator.
- Do not write experiment or pipeline bodies.
- Do not commit except by loading `setup-git`.
- Do not abort setup because one skill is missing.
- Do not invent a missing skill's procedure.
- Do not `pixi add` / `uv add` from this coordinator;
  `add-python-package` owns install.
