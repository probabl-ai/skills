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
- Emit the Pre-flight then ask (do not stop after listing boxes).
- Run `status` and `env detect` before any write.
- AskUserQuestion multi-select of installed pieces (env,
  workspace, editable, git). The question's last line is exactly: Select each
  one you want.
  Do not auto-run all four before the answer.
- In that same opening phase, before `env init`, `scaffold`,
  package install, or `git init`, ask the unrecorded choices:
  environment manager, whether we manage the environment, the
  Python import name, and whether later stages commit
  automatically. Persist those answers, then load the selected
  skills. Do not ask tabular library, report destination,
  notebooks, or the documentation site.

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
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.
- Ask executed notebooks or documentation site in this meta.

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
- `pixi.toml` and a `pixi init` `pyproject.toml` exist; no `src/`.
- Every `skills` entry is `true`.

**Must do:**
- Read `status` first and do not offer Python environment.
- Ask the multi-select with workspace layout, editable install,
  and Git. The question's last line is exactly: Select each one you want. Editable is on
  the board because workspace is pending and editable is still
  missing.
- Before any setup command, persist
  `python -m skore_skills policy set setup.<piece> declined` for
  each piece the user does not select.
- Ask the Python import name and automatic commits for the boxes
  the user keeps. Do not ask which manager to use or whether we
  manage the environment.
- If the user keeps workspace + git: load `setup-workspace` then
  `setup-git`; schedule editable only after `has_src`. After each
  loaded skill returns, persist `setup.<piece> done`. Do not
  install sklearn or skrub.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Offer the Python environment box.
- Re-ask which environment manager to use or whether we manage
  the environment.
- Pass `--force` to `scaffold`.
- Wire the editable install before the layout exists.
- Offer a piece whose `status.setup` value is `done`.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.

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
  question's last line is exactly: Select each one you want.
  Omit git because `setup-git` is not installed.
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
- Treat the missing skill as an error that aborts setup.
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
- Ask the multi-select with every installed box. The question's
  last line is exactly: Select each one you want.
- Skip `setup-python-env` in one line because the user did not
  select it.
- Persist `python -m skore_skills policy set setup.env declined`
  before any write.
- Do not ask the environment manager or whether we manage the
  environment.
- Before `scaffold` or `git init`, ask the Python import name and
  whether later stages commit automatically, and persist both.
- Load `setup-workspace` then git after layout exists; do not run
  env init.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `env init` anyway.
- Invent the env manager procedure from memory.
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.

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

---

## CASE_06 — Detected manager is recorded without asking

**User prompt:**
> Set up this project.

**Assumed workspace state:**
- `pixi.toml` exists. `env detect` reports `env_manager: pixi`,
  `ambiguous: false`, `mismatch: false`.
- `policy.env_manager` is unset. `policy.env.managed`,
  `policy.package`, and `policy.git.autocommit` are unset.
- No `src/` and no `journal/`.
- Every `skills` entry is `true`.

**Must do:**
- Ask the multi-select with every installed box. The question's
  last line is exactly: Select each one you want.
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
- In the question, ask the user to uncheck a box, or say that a
  box starts checked. A recorded status is not the box's starting
  state.

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
