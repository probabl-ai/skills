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
- AskUserQuestion multi-select of installed pieces (env,
  workspace, editable, git) with **every installed box
  preselected**. Do not auto-run all four before the answer.
- Leave manager, `env.managed`, and package-name questions to
  those skills. Do not ask tabular library or report destination.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Scaffold or ask for the package name before the environment
  manager turn.
- Ask tabular library or report destination, or persist `tabular` /
  `skore_mode`, during setup.
- Run `pip install`.
- Commit without asking.
- Write a runnable baseline experiment.
- Run `git push`.
- Leave a setup box unchecked because the folder is empty.
- Ask executed notebooks or documentation site in this meta.

---

## CASE_02 — Continue setup, all boxes still on

**User prompt:**
> Continue the setup.

**Assumed workspace state:**
- `python -m skore_skills status` reports `env_manager: pixi`,
  `policy.env_manager: pixi`, `has_src: false`, `git: false`.
- `pixi.toml` and a `pixi init` `pyproject.toml` exist; no `src/`.
- Every `skills` entry is `true`.

**Must do:**
- Read `status` first and treat the manager as already resolved.
- Ask the multi-select with **all installed pieces preselected**
  (not only remaining work).
- If the user keeps workspace + git: load `setup-workspace` then
  `setup-git`; schedule editable only after `has_src`. Do not
  install sklearn or skrub. If env remains selected,
  `setup-python-env` may install its required plain Skore; this
  coordinator must not install or configure it directly.
- Do not re-ask which environment manager to use in this meta.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Re-ask which environment manager to use.
- Pass `--force` to `scaffold`.
- Wire the editable install before the layout exists.
- Uncheck env/workspace/git because env already exists.

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
- Ask the multi-select of **installed** pieces only. Omit git
  because `setup-git` is not installed.
- State in one line that git setup is skipped because `setup-git`
  is not installed.
- Finish the rest of setup rather than stopping at the missing
  skill.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `git init`, `git add`, or `git commit` to cover for the
  missing skill.
- Invent the `setup-git` procedure from memory.
- Treat the missing skill as an error that aborts setup.
- Show a git checkbox.

---

## CASE_04 — User unchecks env

**User prompt:**
> Set up this empty folder for an ML project.

**Assumed workspace state:**
- Empty folder.
- Every `skills` entry is `true`.
- The user unchecks Python environment and keeps workspace, editable,
  and git.

**Must do:**
- Ask the multi-select with every installed box preselected.
- Skip `setup-python-env` in one line because the user unchecked it.
- Load `setup-workspace` then git after layout exists; do not run
  env init.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `env init` anyway.
- Invent the env manager procedure from memory.

---

## CASE_05 — Editable without workspace or src

**User prompt:**
> Set up this empty folder.

**Assumed workspace state:**
- Empty folder; `has_src` is false.
- Every `skills` entry is `true`.
- The user unchecks workspace and git, leaves editable checked,
  unchecks env.

**Must do:**
- Stop in one line: editable needs `src/` or a selected workspace
  skill. Do not scaffold from this meta.

**Must NOT do:**
- Put catalog skill ids, HITL, `G-PKG-NAME` / `G-ENV-MGR` / `G-SKORE-MODE` / `G-TABULAR` / `G-CV-SPLITTER`, or `python -m skore_skills` / `env add` in user-facing questions or the close narrative (trailing `G-REPORT-LOCATOR` / `G-AUDIT-FINDING` and unmanaged `pixi add` / `uv add` / `pip install` lines are allowed).
- Run `python -m skore_skills scaffold`.
- Run `env add --editable`.
