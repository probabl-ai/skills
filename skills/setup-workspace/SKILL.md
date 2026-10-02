---
name: setup-workspace
description: >
  Detect an existing ML workspace or scaffold a fresh one via
  `python -m skore_skills scaffold --package <pkg>`. Cookiecutter
  only: directories, README.md files, and src/<pkg>/ stubs. After
  a first scaffold, turn executed notebooks and the documentation
  site on by default (no ask).

  TRIGGER for a new ML project layout or first scaffold.

  SKIP pipeline, evaluation, exploratory data analysis, and library
  choice.

  HOW TO USE: detect first. For a fresh or manager-only layout,
  resolve G-PKG-NAME via `AskUserQuestion` unless `policy.package`
  or `src/<pkg>/` already names it, then scaffold, then persist
  notebooks/site true when both are still unset. For an existing
  layout, stop without scaffolding or inventing files.
---

# Set Up Workspace

Decide where artifacts live. Do not design an experiment here.

## Human-facing prose

Details: `references/human_facing_prose.md`. Scaffolded design
notes, JOURNAL, and folder READMEs describe **this** workspace's
analysis — not the skills framework, the CLI, or the command that
produced an output. Questions and replies use the same
data-science language (import name, notebooks, documentation
site) — not `G-*` names, catalog skill ids, or the wrapper CLI.
Say "workspace setup", not `setup-workspace`.
`<!-- results-embed: … -->` is a site marker. Authoring hints
stay in this skill. `style` is ruff only.

## Detection

- `src/` or `journal/` present → **existing**. Reuse names and
  folders. Do not scaffold again.
- Manager manifest without `src/<pkg>/` → **manager-only**. Still
  scaffold; keep existing `pyproject.toml`. No `--force`.
- Otherwise → **fresh**. Ask G-PKG-NAME, then scaffold.

## Pre-flight

Tick, then immediately run the matching sequence step. Do not stop
after listing the boxes.

```
- [ ] Layout: fresh | manager-only | existing
- [ ] G-PKG-NAME: ask if fresh/manager-only (unless policy.package or src/<pkg>/ already names it)
- [ ] scaffold --package <pkg> | existing: no scaffold, no invent
- [ ] fresh/manager-only: persist notebooks + site true; install
- [ ] dispatched → return | standalone → git end-turn --stage setup
```

## Sequence

1. If fresh or manager-only, resolve **G-PKG-NAME**. Ask with
   the `AskUserQuestion` tool when it is not already recorded
   (the `src/<pkg>/` import name; folder name as the default
   option). Each ask in this skill states in
   2–4 lines what the answer authorizes — the scaffolded tree, the
   persisted policy key, the toolchain a gate implies — and the
   detected facts it rests on; a file link is an addition, never
   the context. “You pick” / “go fast” does not
   resolve it. Do not confirm in prose instead of the tool. A
   matching `[project] name` + `src/<pkg>/` already resolves it —
   do not re-ask. A recorded `policy.package` also resolves it.
   Do not re-ask. When `setup-ml-project` dispatched this turn
   and `policy.package` is set, do not ask again. When
   `src/<pkg>/` is absent, scaffold that
   name. A `status` package of null does not reopen the ask.
   Persist the resolved import name with
   `python -m skore_skills policy set package <pkg>`.
2. Fresh / manager-only:

   ```bash
   python -m skore_skills scaffold --package <pkg>
   ```

   The CLI writes the tree and each folder `README.md`. Do not
   recreate those files from memory.
3. Existing: do not scaffold again. Do not invent files. No
   rename, no overwrite, no `--force`. Do not persist or ask
   notebooks/site.
4. After scaffold on fresh or manager-only, if
   `policy.notebooks` and `policy.site` are both `null`
   (never set): persist both on this turn —

   `python -m skore_skills policy set notebooks true`

   `python -m skore_skills policy set site true`

   Do not AskUserQuestion for notebooks or site. Persist both
   before the user-facing line. That line says executed
   notebooks and the documentation site are on; the user can
   turn either off later. Do not say they are still unset or
   null. Do not write notebooks or site into JOURNAL; policy
   is the record. Do not ask.

   Same turn after persist:

   Load `add-python-package` only if
   `status.skills.add-python-package` is true **and**
   `policy.env.managed` is true. Else one-line skip: name
   `jupytext` / `nbclient` / `ipywidgets` / `nbconvert` /
   `mkdocs-material`; do
   not invent `pixi add` / `uv add`; skip `site init`. Do not
   invent that skill's steps.

   When that load is allowed:

   - notebooks true → `add-python-package` for `jupytext`,
     `nbclient`, and `ipywidgets` (all `env route` **agent**),
     plus `nbconvert` when site is also true — stage turns write
     the notebook viewer with `--html`. Do not leave them as
     `ask`. Do not convert.
   - site true → `add-python-package` for `mkdocs-material`
     (agent), then `python -m skore_skills site init`.

   If either flag is already `true` or `false`, do not overwrite
   and do not install from this step.
5. If `setup-ml-project` dispatched this turn and is in this
   session, return to it; else stop. Standalone:
   `python -m skore_skills git end-turn --stage setup`. If JSON
   `action` is `invoke`, load `persist-ml-git` only if
   `status.skills.persist-ml-git` is true and stop; it returns to
   triage. If persist is missing, name the pending `staged` paths
   and stop. Otherwise load `triage-ml-task` only if
   `status.skills.triage-ml-task` is true; else stop.

## Stop conditions

- Do not ask env manager, tabular library, or skore mode.
- Do not run `pixi init` / `uv init`.
- Do not env-bootstrap or editable-install. Export toolchain
  (`jupytext`, `nbclient`, `ipywidgets`, `nbconvert`,
  `mkdocs-material`) only
  via `add-python-package` after persisting notebooks/site.
  Never `pixi add` / `uv add` from this skill.
- Do not write experiment or exploratory data analysis bodies.
- Never `git commit` here.
- Do not AskUserQuestion for notebooks or site.
- Do not persist notebooks/site on an existing layout.

## Layout (CLI writes this)

```text
src/<pkg>/
experiments/
journal/
data_analysis/
data/
audit/
tests/smoke/
scratch/
```

Each directory has `README.md`.
