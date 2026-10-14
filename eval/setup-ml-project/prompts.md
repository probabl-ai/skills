# setup-ml-project eval

---

## CASE_01 — Full project setup

**User prompt:**
> Set up this empty folder for a tabular ML project.

**Assumed workspace state:**
- Empty folder; no manager or package name selected.
- `python -m skore_skills status` reports every `skills` entry
  `true`.

**Must do:**
- Read the lookup table and take the matching row (do not stop
  after listing the rows).
- Run `status` and `env detect` before any write.
- AskUserQuestion multi-select of installed pieces (env,
  workspace, editable, git). The preamble starts by saying that
  before any modeling, the workspace should be set up. Do not
  say the order the selected pieces will run. The question's
  last line is exactly: Select each one you want.
  Do not auto-run all four before the answer.
- In that same opening phase, before `env init`, `scaffold`,
  package install, or `git init`, ask the unrecorded choices:
  environment manager, whether we manage the environment, the
  Python import name, and whether later stages commit
  automatically. Persist those answers, then load the selected
  skills. Do not ask tabular library, report destination,
  notebooks, or the documentation site.
- When Git is selected, before `env init` or `scaffold`, load
  `setup-git` for the pre-change snapshot only. An empty folder
  makes `python -m skore_skills git snapshot` return
  `nothing_to_commit`. Persist
  `python -m skore_skills policy set git.snapshot skipped`.
  Do not ask to commit the current files.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Scaffold or ask for the package name before the environment
  manager question.
- Run `env init`, `scaffold`, or `git init` before those opening
  questions are answered.
- Leave the manager, managed-environment, import-name, or
  autocommit question until after a setup command.
- Ask tabular library or report destination, or persist `tabular` /
  `skore_mode`, during setup.
- Run `pip install`.
- Commit without asking.
- Write a runnable baseline experiment.
- Run `git push`.
- Omit a setup box because the folder is empty.
- In the setup multi-select, state the order the selected pieces
  will run.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.
- Ask executed notebooks or documentation site in this meta.
- Ask to commit the current files on this empty folder.
- `git commit` before any setup write.

---

## CASE_02 — Recorded env stays off the board

**User prompt:**
> Continue the setup.

**Assumed workspace state:**
- `status.setup.env` is `done`. `status.setup.pending` is
  `workspace`, `git`. `status.setup.editable` is `missing`.
- `python -m skore_skills status` reports `env_manager: pixi`,
  `policy.env_manager: pixi`, `policy.env.managed: true`,
  `has_src: false`, `git: false`.
- `policy.package` and `policy.git.autocommit` are unset.
- `policy.git.snapshot` is `skipped`.
- `pixi.toml` and a `pixi init` `pyproject.toml` exist; no `src/`.
- Every `skills` entry is `true`.

**Must do:**
- Read `status` first and do not offer Python environment.
- Ask the multi-select with workspace layout, editable install,
  and Git. The preamble starts by saying that before any
  modeling, the workspace should be set up. Do not say the order
  the selected pieces will run. The question's last line is
  exactly: Select each one you want. Editable is on the board
  because workspace is pending and editable is still missing.
- Before any setup command, persist
  `python -m skore_skills policy set setup.<piece> declined` for
  each piece the user does not select.
- Ask the Python import name and automatic commits for the boxes
  the user keeps. Do not ask which manager to use or whether we
  manage the environment.
- If the user keeps workspace + git: load `setup-workspace` then
  `setup-git`; schedule editable only after `has_src`. After each
  loaded skill returns, persist `setup.<piece> done`. Persist
  `setup.editable` done only when `env add --editable --execute`
  exits 0. Do not install sklearn or skrub.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Offer the Python environment box.
- Re-ask which environment manager to use or whether we manage
  the environment.
- Pass `--force` to `scaffold`.
- Wire the editable install before the layout exists.
- Offer a piece whose `status.setup` value is `done`.
- Persist `setup.editable` done when `env add --editable --execute`
  exits non-zero.
- In the setup multi-select, state the order the selected pieces
  will run.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.
- Ask to commit the current files. `git.snapshot` is already
  `skipped`.

---

## CASE_03 — Git skill not installed

**User prompt:**
> Bootstrap this project for me.

**Assumed workspace state:**
- Empty folder.
- `python -m skore_skills status` reports `skills`:
  `setup-python-env: true`, `setup-workspace: true`,
  `setup-git: false`, `choose-python-library: true`,
  `persist-ml-git: false`, `triage-ml-task: true`.

**Must do:**
- Ask the multi-select of **installed** pieces only. The
  preamble starts by saying that before any modeling, the
  workspace should be set up. Do not say the order the selected
  pieces will run. The question's last line is exactly: Select
  each one you want. Omit git because `setup-git` is not
  installed.
- Do not ask about automatic commits.
- In the opening phase, ask the environment manager, whether we
  manage the environment, and the Python import name, then
  persist those answers before `env init` or `scaffold`.
- State in one line that git setup is skipped because `setup-git`
  is not installed.
- Finish the rest of setup rather than stopping at the missing
  skill.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Show a git checkbox or ask the automatic-commit question.
- Run `git init`, `git add`, or `git commit` to cover for the
  missing skill.
- Invent the `setup-git` procedure from memory.
- Load `setup-git` for a pre-change snapshot, or ask to commit
  the current files.
- Treat the missing skill as an error that aborts setup.
- In the setup multi-select, state the order the selected pieces
  will run.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.

---

## CASE_04 — User does not select env

**User prompt:**
> Set up this empty folder for an ML project.

**Assumed workspace state:**
- Empty folder.
- Every `skills` entry is `true`.
- The user does not select Python environment and selects
  workspace, editable, and git.

**Must do:**
- Ask the multi-select with every installed box. The preamble
  starts by saying that before any modeling, the workspace
  should be set up. Do not say the order the selected pieces
  will run. The question's last line is exactly: Select each one
  you want.
- Skip `setup-python-env` in one line because the user did not
  select it.
- Persist `python -m skore_skills policy set setup.env declined`
  before any write.
- Do not ask the environment manager or whether we manage the
  environment.
- Before `scaffold` or `git init`, ask the Python import name and
  whether later stages commit automatically, and persist both.
- Before `scaffold`, load `setup-git` for the pre-change snapshot
  only. An empty folder makes `git snapshot` return
  `nothing_to_commit`. Persist
  `python -m skore_skills policy set git.snapshot skipped`.
  Do not ask to commit the current files.
- Load `setup-workspace` then git after layout exists; do not run
  env init.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `env init` anyway.
- Invent the env manager procedure from memory.
- In the setup multi-select, state the order the selected pieces
  will run.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.
- Ask to commit the current files on this empty folder.

---

## CASE_05 — Editable without workspace or src

**User prompt:**
> Set up this empty folder.

**Assumed workspace state:**
- Empty folder; `has_src` is false.
- Every `skills` entry is `true`.
- The user does not select workspace, git, or env, and selects
  editable.

**Must do:**
- Ask the multi-select. The preamble starts by saying that
  before any modeling, the workspace should be set up. Do not
  say the order the selected pieces will run. The question's
  last line is exactly: Select each one you want.
- Stop in one line: editable needs `src/` or a selected workspace
  skill. Do not scaffold from this meta.
- Do not ask the environment manager, import name, or automatic
  commits after that stop.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `python -m skore_skills scaffold`.
- Run `env add --editable`.
- Ask the import name or the environment-manager question after
  the stop.
- Load `setup-git` for a pre-change snapshot. Git was not
  selected.
- In the setup multi-select, state the order the selected pieces
  will run.

---

## CASE_06 — Detected manager is recorded without asking

**User prompt:**
> Set up this project.

**Assumed workspace state:**
- `pixi.toml` exists. `env detect` reports `env_manager: pixi`,
  `ambiguous: false`, `mismatch: false`.
- `policy.env_manager` is unset. `policy.env.managed`,
  `policy.package`, and `policy.git.autocommit` are unset.
- `policy.git.snapshot` is `skipped`.
- No `src/` and no `journal/`.
- Every `skills` entry is `true`.

**Must do:**
- Ask the multi-select with every installed box. The preamble
  starts by saying that before any modeling, the workspace
  should be set up. Do not say the order the selected pieces
  will run. The question's last line is exactly: Select each one
  you want.
- Do not ask which environment manager to use.
- Persist `python -m skore_skills policy set env_manager pixi`
  before loading `setup-python-env`.
- Still ask whether we manage the environment, the Python import
  name, and automatic commits before any setup command.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask the environment-manager question when detection already
  names pixi.
- Run `env init` or `scaffold` before the remaining opening
  questions are answered.
- In the setup multi-select, state the order the selected pieces
  will run.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.
- Ask to commit the current files. `git.snapshot` is already
  `skipped`.

---

## CASE_07 — Recorded setup asks nothing

**User prompt:**
> Set up this project.

**Assumed workspace state:**
- `status.setup.env`, `workspace`, `editable`, and `git` are
  `done`. `status.setup.pending` is empty.
- Every `skills` entry is `true`.
- The user asked only to set up. No lifecycle skill is waiting.

**Must do:**
- Run `python -m skore_skills status`.
- Ask nothing about the Python environment, workspace layout,
  editable install, or Git.
- Load `triage-ml-task`. Do not start exploratory data analysis.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- AskUserQuestion for a piece that is already `done`.
- Run `env init`, `scaffold`, or `git init`.
- Ask to commit the current files. Setup is already finished.

---

## CASE_08 — Commit a dirty tree before scaffold

**User prompt:**
> Set up this project.

**Assumed workspace state:**
- `status.setup.env` is `done`. `status.setup.pending` is
  `workspace`, `git`.
- `has_src` is false. A git repository exists. `notes.txt` is
  dirty.
- `policy.package` is `demo`. `policy.git.autocommit` is `on`.
  `policy.git.snapshot` is null.
- `python -m skore_skills git snapshot` returns `action: ask`,
  `reason: dirty`, `repo: true`, `staged` includes `notes.txt`,
  `ambiguous_dotfiles` empty, and `review_paths` empty.
- Every `skills` entry is `true`.
- The user selects workspace layout and Git, not editable
  install, and agrees to the snapshot commit.

**Must do:**
- Ask the multi-select. The preamble starts by saying that
  before any modeling, the workspace should be set up. Do not
  say the order the selected pieces will run. The question's
  last line is exactly: Select each one you want.
- Do not re-ask the import name or automatic commits.
- Before `scaffold`, load `setup-git` for the pre-change snapshot
  only. That commit happens before `scaffold`.
- Then load `setup-workspace`, then `setup-git` for the rest of
  git setup.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `scaffold` or `env init` before the snapshot commit.
- Run `python -m skore_skills git ignore-merge` before that
  commit.
- Skip the snapshot question.
- In the setup multi-select, state the order the selected pieces
  will run.

---

## CASE_09 — Decline the snapshot, then continue setup

**User prompt:**
> Set up this project.

**Assumed workspace state:**
- `status.setup.env` is `done`. `status.setup.pending` is
  `workspace`, `git`.
- `has_src` is false. A git repository exists. `notes.txt` is
  dirty.
- `policy.package` is `demo`. `policy.git.autocommit` is `on`.
  `policy.git.snapshot` is null.
- `python -m skore_skills git snapshot` returns `action: ask`,
  `reason: dirty`, `repo: true`.
- Every `skills` entry is `true`.
- The user selects workspace layout and Git, and declines the
  snapshot commit.

**Must do:**
- Before `scaffold`, load `setup-git` for the pre-change snapshot
  only. Ask, recommending the commit.
- Persist `python -m skore_skills policy set git.snapshot declined`
  by that skill. Do not `git commit`.
- Then load `setup-workspace`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- `git commit` the dirty tree.
- Run `scaffold` before the snapshot question is answered.

---

## CASE_10 — Clean repository skips the snapshot question

**User prompt:**
> Set up this project.

**Assumed workspace state:**
- `status.setup.env` is `done`. `status.setup.pending` is
  `workspace`, `git`.
- `has_src` is false. A git repository exists and the worktree
  is clean.
- `policy.package` is `demo`. `policy.git.autocommit` is `on`.
  `policy.git.snapshot` is null.
- `python -m skore_skills git snapshot` returns `action: skip`,
  `reason: clean`.
- Every `skills` entry is `true`.
- The user selects workspace layout and Git.

**Must do:**
- Before `scaffold`, load `setup-git` for the pre-change snapshot
  only. Persist
  `python -m skore_skills policy set git.snapshot skipped`.
  Do not ask to commit the current files.
- Then load `setup-workspace`.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- AskUserQuestion about committing the current files.
- Run `git commit`.

---

## CASE_11 — Git not selected, no snapshot

**User prompt:**
> Set up this project.

**Assumed workspace state:**
- `status.setup.pending` is `workspace`, `git`. A git repository
  exists and `notes.txt` is dirty. `policy.git.snapshot` is null.
- `policy.package` is `demo`.
- Every `skills` entry is `true`.
- The user selects workspace layout only.

**Must do:**
- Ask the multi-select, then the import name is already recorded,
  so do not ask it.
- Persist `python -m skore_skills policy set setup.git declined`.
- Load `setup-workspace`. Do not load the pre-change snapshot.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Ask to commit the current files.
- Run `git commit` or `git init`.
