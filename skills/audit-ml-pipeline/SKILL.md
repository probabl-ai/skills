---
name: audit-ml-pipeline
description: >
  Owns the `audit/` folder: one `# %%` (jupytext percent) Python file
  per experiment, aligned 1:1 with `experiments/NN_<short_name>.py` and
  `journal/NN_<short_name>.md`, that loads the experiment's skore
  report **read-only** and uses bare-last-expression cells whose
  `__repr__` carries the audit's signal.   The agent executes the audit
  file via `python -m skore_skills cells run`, which streams a
  markdown digest of each cell's stdout + last-expression repr to
  stdout (optionally also to a file). The digest fuels narrative work
  (the `JOURNAL.md` Status + History update, follow-up questions
  about a past experiment, cross-experiment comparison). After each
  digest it asks a deterministic continue-or-close gate; it stops
  after Close audit with the digest and G-AUDIT-FINDING available.
  Never calls `skore.evaluate(...)` or `project.put(...)`.

  TRIGGER — any of:
  - A completed run needs a read-only audit for outcome recording.
  - The user asks "audit experiment 02", "show me what 03 looks
    like", "re-audit 04 against the new report".
  - An experiment was re-run (same `put()` key overwritten) and the
    matching audit file needs re-execution.
  - The user wants a human-readable narrative of a past experiment
    without writing `journal/ideas/` files.

  STOP when `python -m skore_skills status` shows no scaffold
  (`has_src` and `has_journal` both false), no approved design,
  no experiment report, or no agent feature. Explain the missing
  fact and send the user to setup/triage, `evaluate-ml-pipeline`,
  or `model-ml-pipeline`. Do not require `git`. Do not call
  `skore.evaluate` or `project.put`. Also stop when the request
  concerns raw-data exploration or sourcing a future experiment.
  Do not require another action skill to be installed.

  HOW TO USE: confirm the four-way stem pairing exists (`journal/NN_*.md`
  approved + `experiments/NN_*.py` exists + smoke test passed +
  report under that key in the Project), then place
  `audit/NN_<short_name>.py` from `templates/audit.py`, substituting
  the package name + the literal Project init block copied from
  `experiments/<stem>.py`. Execute via
  `python -m skore_skills cells run audit/<stem>.py`.
  Derive G-AUDIT-FINDING from that digest, then ask the fixed
  Additional report view / Custom query / Custom plot / Close audit
  gate. Additional work reruns the same file and gate.
  **Read the Stop conditions and emit the Pre-flight
  checklist before any write or shell command.** Always invoke
  `python -m skore_skills api get` for skore symbol signatures — never write them from
  memory.
---

# Audit ML Pipeline

Per-experiment, human-readable, agent-executable narrative of a skore
report — produced by **executing** a bare-expression `# %%` file and
reading the digest. Read-only against the skore Project.

## Human-facing prose

Details: `setup-workspace` `references/human_facing_prose.md`.
Audit markdown and `#` comments describe **this** report's findings
— not the skills framework, the CLI, or the command that produced
an output. Questions, replies, and the close narrative use the
same data-science language — not skill ids, `G-*` names, or the
wrapper CLI. Trailing locator tokens stay index strings. Do not
put API tutorials, version floors, or locator recipes in
`audit/<stem>.py`. `<!-- results-embed: … -->` is a site marker.
Authoring hints stay in this skill. `style` is ruff only.

## Next-step pointers

| Came here from… | After audit, next is… |
|---|---|
| `model-ml-pipeline` (implement loop) | → Return to the dispatcher for convert / site / git end-turn |
| User free-text ("audit 02", "re-audit 04") | → Surface metrics, then own the close (see § End of turn) |
| Re-run of an existing experiment | → Re-execute the existing audit file; surface diff if metrics changed |

The implement loop dispatches audit **after evaluate and before
record-outcome**. The digest carries the checks summary and metrics
summary. G-AUDIT-FINDING is a separate normalized finding derived
from that digest. `manage-ml-backlog` record-outcome consumes both
and never dispatches audit back.

## Where things live — visual map

| Path | Durability | Who writes it | What it holds |
|---|---|---|---|
| `audit/<NN>_<short_name>.py` | **Durable** (in git) | This skill, once per experiment | The bare-expression cells. Source of truth. Can be opened as a notebook in JupyterLab / VS Code for the rich HTML view |
| `scratch/audit/<stem>/audit.md` | Ephemeral (gitignored), optional | `cells run` when given a 2nd arg | Per-cell markdown digest: source + stdout + last-expression `repr`. Same content as stdout |
| `scratch/results/<stem>/report.html` `report.txt` `locator.txt` `pipeline.html` | Ephemeral (gitignored) | Evaluate (`experiments/<stem>.py`) | Full-report viewer, text fallback, locator, fitted Method diagram |
| `scratch/results/<stem>/checks.html` `metrics.html` and extra `<slug>.html` / `.png` | Ephemeral (gitignored) | Audit cells | Per-item viewers the site embeds under `## Results`. The digest already carries the text, so no extra `.txt` is written here |
| Stdout from `cells run` | Captured by the bash tool | CLI (always) | Streamed digest — the agent reads this directly from the tool output |

**Mnemonic:** `audit/` is *source* (in git); `scratch/audit/` and
stdout are *output*. Never put the source `.py` under
`scratch/audit/`. Never commit anything under `scratch/audit/`.

## Read-only contract

The central rule. Surfaced as the first Stop condition below.

**Allowed in `audit/<stem>.py`:**

- `skore.Project(...)` — open the project this experiment wrote to.
- `project.summarize()` — list `(key, id)` pairs.
- `project.get(id)` — load a specific report by id.
- Every `report.*` accessor.
- Imports from `<pkg>` (read-only inspection).

**Forbidden in `audit/<stem>.py`:**

- `skore.evaluate(...)` — duplicates the report under the same key
  and pollutes `summarize()`.
- `project.put(...)` — same.
- Writes outside `scratch/audit/<stem>/` and
  `scratch/results/<stem>/` — no `data/` writes, no `reports/`
  writes, no edits to `src/<pkg>/`. The audit is a viewer. Snapshot
  HTML under `scratch/results/<stem>/` is allowed.
- Mutation of the loaded `report` that survives the cell (e.g.
  monkey-patching skore symbols).

The runner renders every cell's source + last-expression repr +
stdout to the digest. A forbidden call surfaces in the digest (as a
`put` row in a later `summarize()` cell, or as a `**error:**`
section). The contract is *visible*, not invisible.

Sibling read-only consumers (different output shapes, same
discipline): `scratch/<ts>_*.py` probes. `review-ml-experiment`
reads the digest as text and does not open the Project. See
`evaluate-ml-pipeline` § Stop conditions for the consumer rule.

## Stop conditions — read before anything else

- **Workspace not scaffolded.** Run `python -m skore_skills status`
  first. If `has_src` and `has_journal` are both false, STOP and
  send the user to `setup-ml-project` / triage. Do not require
  `git`.
- **No report → STOP.** Four-way pairing is hard: run
  `python -m skore_skills design consent --stem <stem>` (`ask` /
  `stop` → do not audit) + `experiments/NN_*.py` + smoke pytest
  passed + a report under that key in the Project. If the report is
  missing, explain and stop. Do not `skore.evaluate` / `project.put`.
  Route to `evaluate-ml-pipeline` or `model-ml-pipeline`. Direct
  "audit 02" uses this same gate.
- **Read-only against the skore Project.** See § Read-only contract.
  Never `skore.evaluate(...)` or `project.put(...)` in an audit file.
- **`project.get(...)` is by id, not key.** For hub mode, read the
  id from the URL printed by `project.put()`:
  `https://…/<workspace>/<project>/<type-plural>/<N>` → id is
  `skore:report:<type-singular>:<N>` (URL segment is plural; id uses
  the singular — drop the trailing `s`, e.g. `cross-validations` →
  `cross-validation`, `estimators` → `estimator`). Hardcode
  `REPORT_ID` in the audit file — no `summarize()` traversal needed.
  For local mode, read the `"id"` column of `project.summarize()` for
  the matching key row. A `KeyError` from `get("<stem>")` means the
  lookup shape is wrong (get is by id), not that the report is
  missing.
- **Symbol from memory is forbidden.** Any `skore` / `skrub` /
  `sklearn` symbol must come from `python -m skore_skills api get` *this turn*. Cache
  hits under `scratch/api/skore/<version>/` count (Shape 0); inline
  memory does not.
- **Agent feature missing → STOP and delegate.** If `ipython` /
  `ipython` aren't importable, do NOT fabricate audit outputs by
  writing `print()` calls as a workaround. Do NOT type
  `pixi add ...` / `uv add ...` yourself — install is owned by
  `add-python-package` § Agent feature. Request via
  `agent tools (ruff / ipython / ipykernel)` (binary: install / skip); resume only when
  add-python-package returns "ready".
- **Bare expressions, not `print()`.** The runner captures each
  cell's last bare expression via `result.result` and renders its
  `repr`. Wrapping in `print(repr(...))` lands in stdout instead of
  the output section; mixed and harder to scan. Use bare
  expressions; statement-only cells (variable binding) are fine.
- **One audit file per experiment stem (four-way pairing).** No
  `audit_NN_<short_name>_v2.py`. When an experiment is re-run, the
  audit file is **overwritten in place** — same stem, same audit.
- **Executed artifacts go to `scratch/audit/<stem>/`, NOT into
  `audit/`.** Durable artifact is `audit/<stem>.py`; the rendered
  digest is ephemeral.
- **`audit/` is read-only against workspace data.** No writes to
  `data/`, `reports/`, or outside `scratch/audit/<stem>/`.
- **Don't filter warnings in audit cells.** No
  `warnings.filterwarnings(...)` unless the user explicitly asks
  — the runner streams cell stderr into the digest and that's
  signal. See `python -m skore_skills style` § Stop conditions.
- **Harness "no clarifying questions" hints do NOT waive
  agent tools (ruff / ipython / ipykernel).** Install gate fires regardless.
- **Post-hoc audit — required before ending the turn.** Walk every
  pre-flight row; surface unfilled Evidence cells.
- **The post-audit gate is mandatory.** After the first digest and
  every refresh, ask Additional report view / Custom query /
  Custom plot / Close audit in that exact order unless the user
  already explicitly closed the audit. No convert, site build,
  git close, record-outcome, or dispatcher return before Close.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `report = project.get(REPORT_ID); print(repr(report))` | Runner captures bare expressions via `result.result`, not stdout. `print(repr(...))` mixes stdout and output sections. Use `report` on its own line |
| `checks.frame()` instead of the bare `checks` Display | The Display `__repr__` already groups issues and tips with their codes and documentation URLs. `.frame()` flattens that into a table the agent then has to re-read, and drops the severity grouping the review mines |
| `project.get(KEY)` raised `KeyError` → re-run `evaluate` + `put` "to refresh" | Lookup shape is wrong (get is by id, not key). Hub: read the id from the URL printed by `put()`. Local: read `summary["id"]` for the matching key row. Never re-run `evaluate` + `put` to recover |
| Write `pixi add --feature agent ipython` directly from this skill | Install commands owned by `add-python-package`. This skill **requests**; it does not install |
| Dump the audit `.py` into `scratch/audit/<stem>/` | `.py` is durable in git; `scratch/` is gitignored. Source in `audit/`; digest in `scratch/audit/<stem>/` |
| Register a Jupyter kernel "to be safe" | Current runner is in-process; no kernel. Registering creates an orphan kernelspec |
| Add a fix-up cell that mutates `data/` or `reports/` | Audit files are read-only. State mutations belong in a `scratch/<ts>_*.py` probe or the experiment script |
| Substitute `<SKORE_PROJECT_INIT>` in `audit/<stem>.py` without reading `experiments/<stem>.py` first | Audit must open the same Project. Always Read experiments/<stem>.py this turn and copy the literal Project init block byte-identical (modulo formatting) |
| Hub mode: put `skore.login(mode="hub")` after `skore.Project(...)` | `Project(...)` constructor authenticates at init time; without prior `login`, fails. Order is fixed: login first, Project second |
| Implement-loop audit → write scratch probe first to "double-check metrics" | The audit IS the metric-extraction step. Scratch probes for metrics are the anti-pattern this dispatch replaces |

## Pre-flight — emit before any audit-file write or execution

```
Pre-flight (audit-ml-pipeline):
- [ ] Experiment stem confirmed: <NN_short_name>
      Evidence: journal/NN_<short_name>.md exists AND state is approved
                | "n/a — user invoked re-audit on existing stem"
- [ ] Four-way pairing complete:
        journal/NN_<short_name>.md       — design note (state approved or done)
        experiments/NN_<short_name>.py   — script
        tests/smoke/test_NN_<short_name>.py — smoke test (passing)
        audit/NN_<short_name>.py         — about to be written / refreshed
      Evidence: ls / Glob on each path
- [ ] Report present in skore Project under key=<NN_short_name>
      Evidence: project.summarize() this turn; row with
                key == "<NN_short_name>" appears.
                "Run finished, put() landed" is NOT sufficient.
- [ ] Agent feature available:
        run `ipython -c "print(0)"` and `ipython --version`
        through the project's composed dev environment
      Evidence: tool output of each
                | JOURNAL.md Status `agent feature: installed`
                Missing → STOP, delegate to add-python-package agent tools (ruff / ipython / ipykernel)
- [ ] API CLI consulted for skore symbols used:
      Project, summarize, get, report.checks.summarize, report.metrics.summarize
      Evidence: Read scratch/api/skore/<version>/<topic>.md (this turn)
                | Write the same (this turn)
                | "n/a — cache hit, file already on disk + Read this turn"
- [ ] Template copy + substitution decided:
        <pkg> → package name from src/<pkg>/
        <NN>_<short_name> → experiment stem
        <SKORE_PROJECT_INIT> → literal block copied from experiments/<stem>.py
      Evidence: Read experiments/<stem>.py this turn for the Project init block;
                Read templates/audit.py this turn before Write audit/<stem>.py
- [ ] Read-only contract acknowledged: audit file contains
      summarize / get / report.* only — no evaluate, no put
      Evidence: explicit grep / Read confirmation of the drafted file
- [ ] Execution command shape confirmed:
        python -m skore_skills cells run audit/<stem>.py [scratch/audit/<stem>/audit.md]
      Evidence: command emitted in the response before running
- [ ] G-AUDIT-FINDING derived from the executed digest
      Evidence: issue/tip counts + ordered codes + optional metric
                context | explicit clean-checks value
- [ ] Post-audit gate answered: additional view | query | plot | close
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

## Before execution

After the four-way pairing, report lookup, agent feature, and API
checks are satisfied, emit 1–3 natural sentences immediately
before writing or running `audit/<stem>.py`. Say that this is
**local read-only report materialization**, not retraining: it
opens the persisted Skore report, renders checks / metrics /
available views, and writes the digest under
`scratch/audit/<stem>/` plus HTML viewers under
`scratch/results/<stem>/`. Name the exact `cells run` command.

Describe cost from facts: report loading and requested view
rendering, not model fits or full CV. Unless an observed duration
is already available, say timing depends on report size and
selected views and do not invent minutes. Emit this preview once
for the initial audit; refresh it only when Additional report
view / Custom query / Custom plot materially changes the work.
The run pauses at the existing post-audit gate before close.

Questions about what the report means are **LLM narrative work**
over the digest; they do not call `evaluate` or `put`. If any
mandatory gate is pending, preview the possible audit but do not
write or execute it.

## Audit file contract — overview

The audit file is **jupytext percent format** (`# %%`). Filename:
`audit/NN_<short_name>.py` — stem matches the experiment exactly.
Template: `templates/audit.py`.

### Substitutions

| Placeholder | Replaced with |
|---|---|
| `<pkg>` | The importable package name (from `src/<pkg>/`) |
| `<NN>_<short_name>` | The experiment stem (e.g. `02_target_transform`) |
| `<SKORE_PROJECT_INIT>` | The full Project init block (including any preceding `skore.login(...)` call for hub mode), copied **byte-identical** from `experiments/<stem>.py` |
| `<project-name>` | The `name=` argument from `experiments/<stem>.py` (read it; don't invent) |
| `<hub-workspace>` | Hub-mode only. Copy from the `workspace=` argument in `experiments/<stem>.py` |
| `<REPORT_LOCATOR>` | The normalized post-put locator handed off by evaluate. If absent, derive it from the selected id and backend rules below; never guess a URL |

`<SKORE_PROJECT_INIT>` and `<project-name>` are the most error-prone
substitutions: the audit must open the same Project the experiment
wrote to. **Always `Read experiments/<stem>.py` this turn** to lift
the literal init block; never reconstruct from memory of the
`skore mode:` decision alone.

### Cell sequence (what each cell does)

Brief outline; full anatomy with concrete examples →
`references/cell_anatomy.md`.

1. **Module docstring (markdown cell)** — what this file is, the
   read-only rule.
2. **Imports (code cell)** — `import skore`, `from <pkg> import ...`.
3. **Open the Project (bare-expression cell)** — `project =
   skore.Project(...)`; then `project` on its own line.
4. **List reports** — `summary = project.summarize()`; then `summary`.
5. **Load the report** — set `REPORT_ID` from the URL printed by
   `project.put()` (hub: `"skore:report:<type-singular>:<N>"` — URL
   path segment is plural, id uses singular, e.g. `cross-validations`
   → `cross-validation`, `estimators` → `estimator`; local **and
   mlflow**: read `summary["id"]` for the matching key row), then
   `report = project.get(REPORT_ID)`. Write `report._repr_html_()`
   to `scratch/results/<stem>/report.html` and the normalized
   locator to `scratch/results/<stem>/locator.txt` (confirm
   `_repr_html_` with `api get`), then `report` as the last
   expression.
6. **Persisted report** — substitute the exact normalized locator
   from evaluate. For a direct audit, use the selected `REPORT_ID`
   and `policy.skore_mode`: local links `../reports/`; Hub uses the
   exact saved `put` URL (or a clearly labeled project link);
   MLflow uses an emitted run URL or records tracking URI +
   experiment id + run id. If no authoritative locator exists,
   write `n/a — backend did not expose a locator`. Do not call
   `put`, inspect private storage, or invent a frontend URL.
7. **Checks summary** — `checks = report.checks.summarize()`, write
   `checks._repr_html_()` to `scratch/results/<stem>/checks.html`,
   then `checks` as the last expression. Its repr groups the walk by
   severity; every `issue` / `tip` line ends with the documentation
   URL holding the actionable mitigation (custom `CSTM*` checks may
   have none).
8. **Metrics summary** — same snapshot pattern for
   `report.metrics.summarize()` into
   `scratch/results/<stem>/metrics.html`, then `metrics` last.
9. **Available report accessors** — call `help()` on
   `report.metrics`, `report.checks`, and any other namespace that
   exists (`inspection`, `data`, …). `help()` prints its tree and
   returns `None`, so the runner captures it as stdout; nothing is
   written to disk. Skip a namespace that is absent. Do not call
   plot accessors here.

That's the core template. Leave a bare Display as the last
expression: editors render `_repr_html_`, the runner records the
`repr`, and both are informative — no `.frame()` and no text
snapshot. Extra Display cells are appended only after the user
picks Additional report view. Details: →
`references/cell_anatomy.md`.

### The digest is the review's canonical source

The rendered digest at `scratch/audit/<stem>/audit.md` is the
**single source of truth** that `review-ml-experiment` reads to
write `journal/ideas/<stem>-<slug>.md`. That skill reads the digest
as text, walks `Issues:` then `Tips:` in `## Checks summary`, and
does not re-open the Project, call `report.*`, or write
`scratch/<ts>_*.py` probes for metric extraction.
`manage-ml-backlog` later triages those files into Backlog rows.

The contract stays narrow: persisted-report locator + checks +
metrics summary. The review must not walk extra Display headings.
Do not
put ROC / confusion-matrix / importance cells in the core
template. After Close-audit extras, those cells use their own
`## <title>` headings. If the user explicitly asks for a custom
figure that `help()` did **not** list, load
`plot-ml-figure` if installed **before writing the cell**; never
replace a skore Display. Save PNG (or HTML) and leave the figure
visible; never `plt.close` in the audit notebook.

## G-AUDIT-FINDING

After every successful `cells run`, run
`python -m skore_skills audit finding --stem <stem>` (or pass the
digest path). Paste JSON `finding` **verbatim**. Do not rewrite
codes, counts, or the metric clause. Missing digest → JSON
`finding` is `n/a — audit digest unavailable`.

Extra Display cells do not change G-AUDIT-FINDING (re-run the
command; it still reads only checks + metrics).

Return G-AUDIT-FINDING verbatim with the digest and
G-REPORT-LOCATOR from `python -m skore_skills loop locator --stem
<stem>`. `manage-ml-backlog` writes the finding to the design
note's Status block. Recompute it after every added view, query,
or plot because the digest is overwritten.

## Continue auditing

After the initial digest and every successful refresh, unless the
user already said to close, **AskUserQuestion** with one pick in
this exact order. None is recommended or preselected.

**Gate context.** Ahead of the question, state in 2–4 lines what
the answer authorizes and the facts it rests on — echoed inline
from this turn's digest (the checks and metrics just read, the
Display names the trees actually list) — plus what each option
does. A file link is an addition, never the context.

| Label | Contract |
|---|---|
| Additional report view | Menu labels are **exactly** the names under the `Displays` group of this turn's `help()` trees in the digest. Confirm the picked name with `python -m skore_skills api get`. The list is task-dependent — a regression report has no `roc`. Omit anything the trees do not list; never show remembered Display names. Ask one pick before editing. |
| Custom query | Wait for one concrete read-only question about the loaded report. Append only the minimal accessor cells needed to answer it. Prefer a name from the trees when it answers the question. |
| Custom plot | Only when the trees have no Display for this chart. Load `plot-ml-figure` only if `status.skills.plot-ml-figure` is true; else one-line skip and return to this gate. Append read-only plot cells and keep the figure as notebook output. |
| Close audit | Continue to the existing dispatched or direct close. |

Additional report view / Custom query / Custom plot all edit the
same durable `audit/<stem>.py`, **below** `## Core audit complete`.
After an edit: run `style`, then `cells run` to overwrite
`scratch/audit/<stem>/audit.md`, derive G-AUDIT-FINDING again
with `python -m skore_skills audit finding --stem <stem>`
(from checks + metrics only), and re-present this same gate. Do
not convert notebooks, build the site, run `git end-turn`,
record-outcome, or return to the dispatcher while an additional
step is active. The audit remains read-only: no `evaluate`, no
`put`, and no workspace-data mutation.

### Extra Display cells

Slug = the accessor name `help()` listed under `Displays`. Do not
invent slugs from docs memory.

1. Markdown cell `## <human title>` — not `## Checks summary` or
   `## Metrics summary`.
2. Code cell: call the accessor; confirm `_repr_html_` with
   `api get` on the returned Display.
3. Write `scratch/results/<stem>/<slug>.html` from `_repr_html_()`
   when it exists. Only when it does not, save `<slug>.png` so the
   site can still embed a figure.
4. Last expression: the bare Display.
5. Failed or inapplicable accessors stay in `scratch/` probes.
   Do not add a Results subsection for them.

`manage-ml-backlog` turns each extra `<slug>` viewer (other than
`report`, `checks`, `metrics`) into a `###` Results heading with
`<!-- results-embed: <slug> -->`, summarizing it from the digest
cell that produced it.

## Execution contract — one command

Before the first `cells run` for a stem, run
`python -m skore_skills review consent --stem <stem>`.
- `stop` — name the missing `report.html` and stop.
- `ask` — emit the cost preview (local read of the persisted
  report; every skore check; can be slow; name
  `audit/<stem>.py` and `scratch/audit/<stem>/audit.md`; do not
  invent minutes) and **AskUserQuestion** Review (Recommended) /
  Skip / Stop. Do not `cells run` until **Review**. If this turn
  already answered **Review** (including from
  `review-ml-experiment`), do not ask again.
- `proceed` — digest exists. Do not `cells run` unless the user
  explicitly asked to re-audit; that re-audit asks the gate again.

```bash
python -m skore_skills cells run audit/<stem>.py scratch/audit/<stem>/audit.md
python -m skore_skills audit finding --stem <stem>
```

Paste JSON `finding` verbatim. The CLI streams the digest to stdout when the dest arg is omitted; the second arg also writes the file. Details:
`python -m skore_skills cells run --help`.

### Executed notebook

If `policy.notebooks` is true and `export-ml-notebook` is
installed, run `python -m skore_skills notebook convert
audit/<stem>.py` after **Close audit**, with `--html` when
`policy.site` is also true. The audit has no page of its own: the
site places its viewer under the matching design note's
`## Notebooks` section, after the evaluation notebook. Missing
jupytext / nbclient →
one-line skip naming `add-python-package`; do not fail the audit,
do not `pixi add`.

### Re-execution semantics

- Re-running an experiment (overwriting `put()` under the same key)
  → re-execute the matching audit file. `manage-ml-backlog` § 4
  fires this on every record-outcome.
- Editing the audit file's source (adding a metric accessor) →
  re-execute. The digest is regenerable.
- `scratch/audit/<stem>/` is **overwritten on every execution**. No
  version history; the source `.py` + git history is the audit trail.

## Four-way stem-pairing rule

Extends `setup-workspace`'s pairing rule from three artifacts
to four:

```
journal/NN_<short_name>.md           — design note
experiments/NN_<short_name>.py       — script
tests/smoke/test_NN_<short_name>.py  — smoke test
audit/NN_<short_name>.py             — audit  ← this skill
```

Identical stems, 1:1. By the time the experiment shows `done` in
`journal/JOURNAL.md`, all four exist.

## Dispatching in and out

### Called from

| Caller | When |
|---|---|
| `review-ml-experiment` | After Review, before idea files and record-outcome |
| `model-ml-pipeline` | Does not load this skill; it loads `review-ml-experiment` |
| `evaluate-ml-pipeline` | Standalone evaluate may run audit before its close |
| User free-text | "audit experiment 02", "show me what 03", "re-audit 04" — resolves directly |

### Calls into

| Callee | Why |
|---|---|
| `python -m skore_skills audit finding` | After `cells run`. Paste JSON `finding` verbatim |
| `python -m skore_skills loop locator` | G-REPORT-LOCATOR from `locator.txt` or the audit file |
| `python -m skore_skills loop artifacts` | Direct-audit close: `record` before site / `git end-turn` |
| `add-python-package` | When `ipython` is missing |
| `manage-ml-backlog` (record-outcome mode) | End of turn on a direct free-text audit — hands over the digest so the History row and design-note Status block get written |
| `python -m skore_skills style` | After writing / editing `audit/<stem>.py` — bundled `ruff.toml` carries `audit/**` per-file ignores. Ruff only; it does not rewrite comments. Do not write workflow/process prose in the audit file |

## End of turn

**Dispatched** (`model-ml-pipeline` or `manage-ml-backlog` this
turn), after **Close audit**: run
`python -m skore_skills audit finding --stem <stem>` and
`python -m skore_skills loop locator --stem <stem>`. Return the
digest, JSON `finding`, JSON `locator`, and an optional
headline to that caller. Stop. Do not run record-outcome,
`notebook convert`, `site build`, `git end-turn`, or triage
here — the caller owns that close. Do not paste the direct-audit
close as a preview of what the dispatcher will run.

**Direct free-text audit, after Close audit:** this skill owns the close. Run
`python -m skore_skills loop artifacts --stem <stem>` (`record`
expected) and `loop locator --stem <stem>`. Then User-facing
close. The JSON `locator` **must** appear in that message
before site build or `git end-turn`.

### User-facing close

Direct free-text only. The user-facing message is a short story
plus links. It is not Pre-flight, not a dump of
`scratch/audit/<stem>/audit.md`, and not finding/locator alone.
Dispatched audit never writes this block.

1. **Narrative first** — 2–6 sentences from Checks + Metrics in
   the digest (issues/tips that matter, headline metric). Do not
   invent a metric. Do not paste the digest wholesale.
2. **Open these** — resolved absolute paths. When `site build`
   ran or is about to, link the site and not the design note:
   `[report.html](<workspace>/report.html)` and
   `html/<stem>.html`. Otherwise
   `[journal/<stem>.md](journal/<stem>.md)`.
3. **Normalized tokens second** — JSON `locator` verbatim first
   among tokens (local: also the absolute `reports/` path), then
   G-AUDIT-FINDING verbatim. Index strings, not the narrative.

Load `manage-ml-backlog` in **record-outcome mode** only if
`status.skills.manage-ml-backlog` is true and hand it
the digest, G-AUDIT-FINDING, and locator, so the run reaches
`journal/JOURNAL.md` History and
the design-note Status block. Missing skill → one-line skip; do
not write History from this skill. That mode records and returns; it
does not re-dispatch this skill and does not open the sourcing
menu. Never mark `done` while smoke is red. This runs **before**
site build so the updated journal files are on disk when the site
is staged and `git end-turn` stages the turn.

The `notebook convert` for `audit/<stem>.py` already ran above.
If `policy.site` is true, `export-ml-site` is installed, run
`python -m skore_skills site build` so the audit viewer reaches
the experiment page. Skip in one line otherwise. Name a build
error; do not fail the audit turn. Name `report.html` (and
`html/<stem>.html`) in the User-facing close when the build ran.
Do not also send the user to the markdown.

Run `python -m skore_skills git end-turn --stage evaluate` — the
audit continues the evaluate stage; there is no `audit` stage on
that command. If JSON `action` is `invoke`, load `persist-ml-git`
only if `status.skills.persist-ml-git` is true and stop; that
skill returns to triage. If persist is missing, name the pending
`staged` paths and stop. Otherwise load `triage-ml-task` only if
`status.skills.triage-ml-task` is true; else stop. Do not run
`git commit` in this skill.

## Failure modes and recovery

Quick lookup; detailed recovery steps in `references/failure_modes.md`.

| Symptom | Cause | Fix |
|---|---|---|
| `project.get(key)` raises `KeyError` / `TypeError` | Lookup by key, not id; local vs hub shape differs | → `references/failure_modes.md` § "`project.get(key)` raises" |
| `ModuleNotFoundError: No module named 'IPython'` | Agent feature not installed | Delegate to `add-python-package`; never `pip install` here |
| Cell renders as `<Display object at 0x…>` | skore too old to give the Display a text repr | Add `.frame()` to that cell only; leave the rest bare |
| `AttributeError` for a `report.*` accessor | Symbol from memory; skore version drift | → `references/failure_modes.md` § "AttributeError" |
| `RuntimeError: No report under key=...` | `put()` landed in a different Project | → `references/failure_modes.md` § "wrong Project" |
| Report differs across runs with unchanged source | Non-deterministic step / different data slice | Not a bug here; surface to user |
| Hub mode: `skore.login()` auth error | Token expired / first-time login | → `references/failure_modes.md` § "skore.login fails" |
| Hub mode: `TypeError: workspace` kwarg | Hub form left local-mode kwarg | → `references/failure_modes.md` § "TypeError workspace" |
| Hub mode: report missing in `summarize()` after `put()` | Wrong hub workspace OR no read access | → `references/failure_modes.md` § "report missing" |

## What this skill does NOT do

- Open or write the skore Project's reports (`evaluate-ml-pipeline`).
- Install `ipython` (`add-python-package` owns).
- Write `journal/ideas/` files (`review-ml-experiment` owns that).
- Write or edit `journal/NN_*.md` or `journal/JOURNAL.md` directly. At end
  of turn, dispatch `manage-ml-backlog` record-outcome mode
  instead — that skill owns every journal write.
- Run pytest / smoke tests (`smoke-test-ml-pipeline`).
- Render commits or PRs.
- Decide *which* metrics matter — the cells are filled per task,
  but judgment about what matters is the user's, in the design note.

## Companion skills

| Skill | Relationship |
|---|---|
| `manage-ml-backlog` | Downstream record-outcome consumer; never dispatches audit from record-outcome mode |
| `review-ml-experiment` | Loop caller. Parses the digest as text and writes one idea file per candidate. Never opens the Project |
| `evaluate-ml-pipeline` | Producer side. `skore.evaluate` + `project.put` live only in `experiments/NN_*.py` |
| `setup-workspace` | Workspace layout; four-way stem pairing |
| `add-python-package` | Agent feature install (agent tools (ruff / ipython / ipykernel)). This skill requests; that skill installs |
| `python -m skore_skills api get` | skore symbol lookups, including `help` and extra Display methods. Cache hits first |
| `plot-ml-figure` | Custom plot gate only when the `help()` trees have no Display |
| `python -m skore_skills style` | ruff after writing/editing `audit/<stem>.py` |
| `choose-python-library` / `python -m skore_skills env stack` | Agent tools (`ipython`, `ipykernel`) live under the agent feature |

## Templates and assets

- `templates/audit.py` — per-experiment audit file skeleton. Copy
  + substitute; don't rewrite from memory.


## Need a package?

When an import is missing, load `add-python-package` if
`status.skills.add-python-package` is true. That skill owns
`env add` and the unmanaged ask. Do not run `env add` here.
If the skill is not installed, name the package and stop.

## References (load on demand)

- `references/cell_anatomy.md` — concrete cell examples (right /
  wrong shapes), core sequence, why the bare Display serves both
  audiences, extra Display snapshot contract, bare-expression rules.
- `references/runner_internals.md` — leftover runner internals
  (IPython, Agg). Prefer `--help` / the package docstring.
- `references/failure_modes.md` — detailed recovery for every
  symptom in § Failure modes.
