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
metadata:
  role: helper
  modelTier: small
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

## Lookup

Detect the layout, then take the one row that matches and run its
steps from the Sequence below. Do not stop after reading the table.

| Layout | Import name | Steps | Notebooks and site |
|---|---|---|---|
| fresh | not recorded. "you pick", "go fast", and "no preference" do not record it | 1 only, then stop. Call `AskUserQuestion` (folder name is the default option). Do not scaffold this turn. | do not persist |
| fresh | `policy.package` or `src/<pkg>/` already names it | 1 (no ask), 2, 4, 5. Do not write `experiments/01_baseline.py` or any experiment body, even if asked so it can run right away. | step 4 |
| manager-only | not recorded. "you pick", "go fast", and "no preference" do not record it | 1 only, then stop. Call `AskUserQuestion`. Do not scaffold this turn. | do not persist |
| manager-only | `policy.package` or `src/<pkg>/` already names it | 1 (no ask), 2, 4, 5. Do not write experiment bodies. | step 4 |
| existing | user asks to re-run `skore.evaluate` or `project.put` | Refuse and stop. Say evaluation and `project.put` are not this skill. Do not paste that snippet. | do not ask, persist, or install |
| existing | any other request | 3, 5 | do not ask, persist, or install |

An unresolved import name is the ask row only. Steps 2, 4, and 5
run on a later turn, once `policy.package` or `src/<pkg>/` names
it. Step 4 does not overwrite a flag that is already `true` or
`false`. Step 5: a turn dispatched by `setup-ml-project` returns
to it; a standalone turn runs `git end-turn --stage setup`.

## Sequence

1. If fresh or manager-only, resolve **G-PKG-NAME**. When it is
   not already recorded, call `AskUserQuestion` and stop this
   turn. Do not persist `policy.package` and do not scaffold
   until a later turn. “You pick” / “go fast” / “no preference”
   does not record it. The question is the `src/<pkg>/` import
   name, with the folder name as the default option. Each ask
   states in 2–4 lines what the answer authorizes — the
   scaffolded tree, the persisted policy key, the toolchain a
   gate implies — and the detected facts it rests on; a file
   link is an addition, never the context. Do not confirm in
   prose instead of the tool. A matching `[project] name` +
   `src/<pkg>/` already resolves it — do not re-ask. A recorded
   `policy.package` also resolves it. Do not re-ask. When
   `setup-ml-project` dispatched this turn and `policy.package`
   is set, do not ask again. Scaffold is step 2, and only once
   the name is already resolved. A `status` package of null does
   not reopen the ask. Persist a resolved import name with
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

- "You pick", "go fast", and "no preference" do not resolve the
  import name. Call `AskUserQuestion` and stop. Do not scaffold
  or persist in that turn, and do not use the folder name yourself.
- Do not write `experiments/01_baseline.py` or any experiment
  body. "So we can run it right away" is not a reason. Scaffold
  writes `experiments/README.md` only.
- Do not re-run `skore.evaluate` or `project.put`, and do not
  paste that snippet. A `KeyError` from `project.get` is not a
  scaffold turn. Say evaluation and `project.put` are not this
  skill, and stop.
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
