---
name: export-ml-notebook
description: >
  Convert a jupytext percent `# %%` Python file into an executed
  `.ipynb` with cell outputs. Pass `--html` when the notebook
  should also become a viewer on the site. Trigger on notebook,
  ipynb, HTML, or executed-report requests, or when export-ml-project
  dispatches notebooks.
---

# Export ML Notebook

Source of truth stays the `# %%` `.py`. This skill only writes
derived `.ipynb` (and optional `.nb.html`). Do not rewrite the
`.py` from the notebook. `cells run` is not a substitute.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Tell the user the written `.ipynb` (and HTML viewer) paths. Do
not quote `notebook convert`, `--html`, or `site build` as
something they should run.

While `policy.notebooks` is true, `explore-ml-data`,
`model-ml-pipeline`, and `audit-ml-pipeline` already convert the
percent file they wrote that turn. This skill owns on-demand
conversions, other sources, and turning the flag on when it is
`null` or false.

## Sequence

1. `python -m skore_skills status`. Read `policy.notebooks` and
   `skills`.
2. If `policy.notebooks` is `null`: persist
   `python -m skore_skills policy set notebooks true`. Do not
   AskUserQuestion. Then load `add-python-package` for `jupytext`
   and `nbclient` (agent) and continue.
3. If `policy.notebooks` is false: say executed notebooks are
   off; offer to turn them on. Do not convert until the policy
   is true.
4. Convert the requested percent file (default `data_analysis/data_analysis.py` when
   the user did not name one):

   ```bash
   python -m skore_skills notebook convert data_analysis/data_analysis.py
   ```

   Convert injects `%matplotlib inline` for the kernel run so
   seaborn / matplotlib last expressions emit `image/png`, then
   strips that setup cell from the written notebook. Do not put
   `%matplotlib inline` in the `.py` (`style` / ruff would reject
   it).

   If the user wants the executed notebook on the site, load
   `add-python-package` for `nbconvert` (agent) and pass `--html`
   (writes a self-contained `<stem>.nb.html` next to the `.py`).
   The site embeds that file in the associated exploratory data
   analysis or design report
   with open-separately and fullscreen controls.

   Optional `--out path.ipynb`. Keep `*.ipynb` gitignored unless
   the user asks `setup-git` to track them.

   Convert-only requests (executed notebook / ipynb / convert,
   no HTML or site viewer): run **only** that `notebook convert`
   line, with no `--html`. Tell the user the written `.ipynb`
   path. Do not mention `--html` or `site build` as an optional
   aside.
5.    After `--html`, if `policy.site` is true, `export-ml-site`
   is installed, run `python -m skore_skills site build` so the
   viewer is packaged. Run `--html` and `site build` **only**
   when the user asked for HTML or a site viewer. Convert
   without `--html` does not rebuild the site. Skip in one line
   otherwise. Name a build error; do not fail the convert. Point
   the user at the HTML viewer / `report.html`, not the CLI.

## Stop conditions

- Do not `git commit` or `git end-turn`.
- Do not run `cells run` as a substitute for convert.
- Do not `pixi add` / `uv add`; load `add-python-package`.
- Missing skill or missing source → one-line skip.
- Do not name `--html` or `python -m skore_skills site build`
  unless the user asked for HTML or a site viewer. Tell the user
  paths, not the CLI.
