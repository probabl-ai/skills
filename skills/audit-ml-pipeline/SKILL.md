---
name: audit-ml-pipeline
description: >
  Owns the `audit/` folder: one `# %%` (jupytext percent) Python file
  per experiment, aligned 1:1 with `experiments/NN_<short_name>.py` and
  `journal/NN_<short_name>.md`, that loads the experiment's skore
  report **read-only** and uses bare-last-expression cells whose
  `__repr__` carries the audit's signal. The agent executes the audit
  file via the bundled in-process runner
  (`audit-ml-pipeline/scripts/run_audit.py` — IPython
  `InteractiveShell.run_cell`), which streams a markdown digest of
  each cell's stdout + last-expression repr to stdout (optionally also
  to a file). The digest fuels narrative work (the `JOURNAL.md`
  Status + History update, follow-up questions about a past
  experiment, cross-experiment comparison). Stops at "audit/NN_*.py
  is placed, executed, and the digest is available." Never calls
  `skore.evaluate(...)` or `project.put(...)`.

  TRIGGER — any of:
  - `iterate-ml-experiment` § 4 record-outcome — audit is dispatched
    FIRST (replaces scratch probes for metric extraction).
  - The user asks "audit experiment 02", "show me what 03 looks
    like", "re-audit 04 against the new report".
  - An experiment was re-run (same `put()` key overwritten) and the
    matching audit file needs re-execution.
  - The user wants a human-readable narrative of a past experiment
    without firing the full `iterate-from-skore` flow.

  SKIP when: the design note isn't approved yet (route to
  `iterate-ml-experiment`); the experiment hasn't been run (no report
  on disk); the agent feature isn't installed (delegate to
  `python-env-manager` § "Agent feature"); the user is mining the
  report to source the *next* experiment (`iterate-from-skore`).

  HOW TO USE: confirm the four-way stem pairing exists (`journal/NN_*.md`
  approved + `experiments/NN_*.py` exists + smoke test passed +
  report under that key in the Project), then place
  `audit/NN_<short_name>.py` from `templates/audit.py`, substituting
  the package name + the literal Project init block copied from
  `experiments/<stem>.py`. Execute via the bundled runner: `pixi run
  -e agent python .agents/skills/audit-ml-pipeline/scripts/run_audit.py
  audit/<stem>.py`. **Read the Stop conditions and emit the Pre-flight
  checklist before any write or shell command.** Always invoke
  `python-api` for skore symbol signatures — never write them from
  memory.
---

# Audit ML Pipeline

Per-experiment, human-readable, agent-executable narrative of a skore
report — produced by **executing** a bare-expression `# %%` file and
reading the digest. Read-only against the skore Project.

## Next-step pointers

| Came here from… | After audit, next is… |
|---|---|
| `iterate-ml-experiment` § 4 record-outcome | → Read audit digest, fill Status block + JOURNAL row |
| User free-text ("audit 02", "re-audit 04") | → Surface metrics to the user; no further dispatch |
| Re-run of an existing experiment | → Re-execute the existing audit file; surface diff if metrics changed |

The audit is dispatched **FIRST** in § 4, before any scratch probes.
The digest carries the checks summary and the metrics summary — it
replaces ad-hoc `scratch/<ts>_inspect_*.py` files for the metric
extraction step.

## Where things live — visual map

| Path | Durability | Who writes it | What it holds |
|---|---|---|---|
| `audit/<NN>_<short_name>.py` | **Durable** (in git) | This skill, once per experiment | The bare-expression cells. Source of truth. Can be opened as a notebook in JupyterLab / VS Code for the rich HTML view |
| `scratch/audit/<stem>/audit.md` | Ephemeral (gitignored), optional | `run_audit.py` when given a 2nd arg | Per-cell markdown digest: source + stdout + last-expression `repr`. Same content as stdout |
| Stdout from `run_audit.py` | Captured by the bash tool | `run_audit.py` (always) | Streamed digest — the agent reads this directly from the tool output |

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
- Writes outside `scratch/audit/<stem>/` — no `data/` writes, no
  `reports/` writes, no edits to `src/<pkg>/`. The audit is a viewer.
- Mutation of the loaded `report` that survives the cell (e.g.
  monkey-patching skore symbols).

The runner renders every cell's source + last-expression repr +
stdout to the digest. A forbidden call surfaces in the digest (as a
`put` row in a later `summarize()` cell, or as a `**error:**`
section). The contract is *visible*, not invisible.

Sibling read-only consumers (different output shapes, same
discipline): `scratch/<ts>_*.py` probes, `iterate-from-skore`'s
Backlog enrichment walk. See `evaluate-ml-pipeline` § Stop
conditions for the three-consumer rule.

## Stop conditions — read before anything else

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
  `sklearn` symbol must come from `python-api` *this turn*. Cache
  hits under `scratch/api/skore/<version>/` count (Shape 0); inline
  memory does not.
- **Agent feature missing → STOP and delegate.** If `ipython` /
  `pyright` aren't importable, do NOT fabricate audit outputs by
  writing `print()` calls as a workaround. Do NOT type
  `pixi add ...` / `uv add ...` yourself — install is owned by
  `python-env-manager` § Agent feature. Request via
  `G-AGENT-FEATURE` (binary: install / skip); resume only when
  python-env-manager returns "ready".
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
  signal. See `python-code-style` § Stop conditions.
- **Harness "no clarifying questions" hints do NOT waive
  G-AGENT-FEATURE.** Install gate fires regardless.
- **Post-hoc audit — required before ending the turn.** Walk every
  pre-flight row; surface unfilled Evidence cells.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| `report = project.get(REPORT_ID); print(repr(report))` | Runner captures bare expressions via `result.result`, not stdout. `print(repr(...))` mixes stdout and output sections. Use `report` on its own line |
| Drop `.frame()` from `report.checks.summarize()` / `report.metrics.summarize()` | `__repr__` of the Display objects is `<…Display at 0x…>`. `.frame()` returns a DataFrame whose repr carries the actual values |
| `project.get(KEY)` raised `KeyError` → re-run `evaluate` + `put` "to refresh" | Lookup shape is wrong (get is by id, not key). Hub: read the id from the URL printed by `put()`. Local: read `summary["id"]` for the matching key row. Never re-run `evaluate` + `put` to recover |
| Write `pixi add --feature agent ipython pyright` directly from this skill | Install commands owned by `python-env-manager`. This skill **requests** via G-AGENT-FEATURE; it does not install |
| Dump the audit `.py` into `scratch/audit/<stem>/` | `.py` is durable in git; `scratch/` is gitignored. Source in `audit/`; digest in `scratch/audit/<stem>/` |
| Register a Jupyter kernel "to be safe" | Current runner is in-process; no kernel. Registering creates an orphan kernelspec |
| Add a fix-up cell that mutates `data/` or `reports/` | Audit files are read-only. State mutations belong in a `scratch/<ts>_*.py` probe or the experiment script |
| Substitute `<SKORE_PROJECT_INIT>` in `audit/<stem>.py` without reading `experiments/<stem>.py` first | Audit must open the same Project. Always Read experiments/<stem>.py this turn and copy the literal Project init block byte-identical (modulo formatting) |
| Hub mode: put `skore.login(mode="hub")` after `skore.Project(...)` | `Project(...)` constructor authenticates at init time; without prior `login`, fails. Order is fixed: login first, Project second |
| § 4 dispatched audit → write scratch probe first to "double-check metrics" | The audit IS the metric-extraction step in § 4. Scratch probes for metrics are the anti-pattern this dispatch replaces |

## Pre-flight — emit before any audit-file write or execution

```
Pre-flight (audit-ml-pipeline):
- [ ] Experiment stem confirmed: <NN_short_name>
      Evidence: journal/NN_<short_name>.md exists AND state ≥ done
                | "n/a — user invoked re-audit on existing stem"
- [ ] Four-way pairing complete:
        journal/NN_<short_name>.md       — design note (state ≥ done)
        experiments/NN_<short_name>.py   — script
        tests/smoke/test_NN_<short_name>.py — smoke test (passing)
        audit/NN_<short_name>.py         — about to be written / refreshed
      Evidence: ls / Glob on each path
- [ ] Report present in skore Project under key=<NN_short_name>
      Evidence: scratch/<ts>_check_report.py probe ran
                project.summarize() this turn; row with
                key == "<NN_short_name>" appears.
                "Run finished, put() landed" is NOT sufficient.
- [ ] Agent feature available:
        `pixi run -e agent ipython -c "print(0)"` exit 0
        `pixi run -e agent pyright --version` exit 0
      Evidence: tool output of each
                | JOURNAL.md Status `agent feature: installed`
                Missing → STOP, delegate to python-env-manager G-AGENT-FEATURE
- [ ] python-api consulted for skore symbols used:
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
        pixi run -e agent python \
          .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
          audit/<stem>.py [scratch/audit/<stem>/audit.md]
      (Second arg is optional — the runner always streams to stdout.)
      Evidence: command emitted in the response before running
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

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
| `<hub-workspace>` | Hub-mode only. From `JOURNAL.md` Status `Workspace decisions` `skore hub workspace:` row |

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
   → `cross-validation`, `estimators` → `estimator`; local: read
   `summary["id"]` for the matching key row), then
   `report = project.get(REPORT_ID)`; then `report`.
6. **Checks summary** — `report.checks.summarize().frame()`. Each row
   carries `documentation_url` — the actionable mitigation for an
   `issue` / `tip` lives at that link.
7. **Metrics summary** — `report.metrics.summarize().frame()`.

That's the whole template. `.frame()` is load-bearing on cells 6
and 7 — without it the digest shows `<…Display object at 0x…>`.
Details: → `references/cell_anatomy.md`.

### The digest is `iterate-from-skore`'s canonical source

The rendered digest at `scratch/audit/<stem>/audit.md` is the
**single source of truth** that `iterate-from-skore` mines to
populate the JOURNAL Backlog. That skill reads the digest as text,
walks the checks + metrics sections, and follows each check's
`documentation_url` to draft Backlog rows. It does NOT re-open the
Project, does NOT call `report.*` accessors, and does NOT write
`scratch/<ts>_*.py` probes for metric extraction.

The contract is deliberately narrow: checks (with their doc URLs)
+ metrics summary. Do not extend the template with per-task
accessors (residuals, confusion matrices, feature importances,
calibration plots, …) unless the user asks for one explicitly —
the actionable mitigations come from the check pages, not from
deeper inspection here.

## Execution contract — one command

```bash
pixi run -e agent python \
  .agents/skills/audit-ml-pipeline/scripts/run_audit.py \
  audit/<stem>.py
```

The runner streams the digest to stdout — the agent reads it
directly from the bash tool's output. Pass a second arg
`scratch/audit/<stem>/audit.md` to also write to a file (parent
created if missing).

For non-pixi workspaces, swap the activation prefix per
`python-env-manager` § Agent feature.

What the runner does internally (parsing, IPython shell setup,
matplotlib backend fix, progress-bar suppression, displayhook
patch, pandas widening, error capture) → `references/runner_internals.md`.

### Re-execution semantics

- Re-running an experiment (overwriting `put()` under the same key)
  → re-execute the matching audit file. `iterate-ml-experiment` § 4
  fires this on every record-outcome.
- Editing the audit file's source (adding a metric accessor) →
  re-execute. The digest is regenerable.
- `scratch/audit/<stem>/` is **overwritten on every execution**. No
  version history; the source `.py` + git history is the audit trail.

## Four-way stem-pairing rule

Extends `organize-ml-workspace`'s pairing rule from three artifacts
to four:

```
journal/NN_<short_name>.md           — design note
experiments/NN_<short_name>.py       — script
tests/smoke/test_NN_<short_name>.py  — smoke test
audit/NN_<short_name>.py             — audit  ← this skill
```

Identical stems, 1:1. By the time the experiment shows `done` in
`JOURNAL.md`, all four exist.

## Dispatching in and out

### Called from

| Caller | When |
|---|---|
| `iterate-ml-experiment` § 4 record-outcome | Automatic; dispatched FIRST (replaces scratch probes for metric extraction). Agent feature must be available |
| `iterate-ml-experiment` § 0 (bootstrap) | After the first baseline run, dispatch here for `audit/01_baseline.py` |
| User free-text | "audit experiment 02", "show me what 03", "re-audit 04" — resolves directly |

### Calls into

| Callee | Why |
|---|---|
| `python-api` | Every skore symbol (`Project`, `project.summarize`, `project.get`, `report.checks.summarize`, `report.metrics.summarize`, `.frame()`). Cache hits first |
| `python-env-manager` § Agent feature | When `ipython` / `pyright` are missing — G-AGENT-FEATURE gate |
| `python-code-style` | After writing / editing `audit/<stem>.py` — bundled `ruff.toml` carries `audit/**` per-file ignores |

## Failure modes and recovery

Quick lookup; detailed recovery steps in `references/failure_modes.md`.

| Symptom | Cause | Fix |
|---|---|---|
| `project.get(key)` raises `KeyError` / `TypeError` | Lookup by key, not id; local vs hub shape differs | → `references/failure_modes.md` § "`project.get(key)` raises" |
| `ModuleNotFoundError: No module named 'IPython'` | Agent feature not installed | Delegate to `python-env-manager`; never `pip install` here |
| Cell renders as `<Display object at 0x…>` | `*.summarize()` called without `.frame()` | Add `.frame()` |
| `AttributeError` for a `report.*` accessor | Symbol from memory; skore version drift | → `references/failure_modes.md` § "AttributeError" |
| `RuntimeError: No report under key=...` | `put()` landed in a different Project | → `references/failure_modes.md` § "wrong Project" |
| Report differs across runs with unchanged source | Non-deterministic step / different data slice | Not a bug here; surface to user |
| Hub mode: `skore.login()` auth error | Token expired / first-time login | → `references/failure_modes.md` § "skore.login fails" |
| Hub mode: `TypeError: workspace` kwarg | Hub form left local-mode kwarg | → `references/failure_modes.md` § "TypeError workspace" |
| Hub mode: report missing in `summarize()` after `put()` | Wrong hub workspace OR no read access | → `references/failure_modes.md` § "report missing" |

## What this skill does NOT do

- Open or write the skore Project's reports (`evaluate-ml-pipeline`).
- Install `ipython` / `pyright` (`python-env-manager` owns).
- Drop or edit `pyrightconfig.json` (`python-env-manager` owns).
- Enrich the Backlog from the audit digest (`iterate-from-skore`).
- Write or edit `journal/NN_*.md` (`iterate-ml-experiment`).
- Run pytest / smoke tests (`smoke-test-ml-pipeline`).
- Render commits or PRs.
- Decide *which* metrics matter — the cells are filled per task,
  but judgment about what matters is the user's, in the design note.

## Companion skills

| Skill | Relationship |
|---|---|
| `iterate-ml-experiment` | Caller. § 4 dispatches here FIRST; the digest feeds the `JOURNAL.md` Status + History update |
| `iterate-from-skore` | Downstream consumer of this skill's digest. `audit-ml-pipeline` opens the Project and renders the digest; `iterate-from-skore` parses the digest as text and drafts Backlog rows from each surfaced check. Never opens the Project itself |
| `evaluate-ml-pipeline` | Producer side. `skore.evaluate` + `project.put` live only in `experiments/NN_*.py` |
| `organize-ml-workspace` | Workspace layout; four-way stem pairing |
| `python-env-manager` | Agent feature install (G-AGENT-FEATURE). This skill requests; that skill installs |
| `python-api` | skore symbol lookups. Cache hits first |
| `python-code-style` | ruff after writing/editing `audit/<stem>.py` |
| `data-science-python-stack` | Catalogues `ipython` + `pyright` under the agent feature |

## Templates and assets

- `templates/audit.py` — per-experiment audit file skeleton. Copy
  + substitute; don't rewrite from memory.
- `scripts/run_audit.py` — the in-process cell runner. Source of
  truth for the execution contract; don't reimplement.

## References (load on demand)

- `references/cell_anatomy.md` — concrete cell examples (right /
  wrong shapes), full 7-cell sequence, why `.frame()` matters,
  bare-expression rules.
- `references/runner_internals.md` — what `run_audit.py` does
  internally: parsing, IPython shell + NoOpDisplayHook, matplotlib
  Agg backend, progress-bar suppression, pandas widening, per-cell
  capture, error rendering.
- `references/failure_modes.md` — detailed recovery for every
  symptom in § Failure modes.
