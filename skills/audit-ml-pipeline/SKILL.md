---
name: audit-ml-pipeline
description: >
  Owns the `audit/` folder: one `# %%` (jupytext percent) Python file
  per experiment, aligned 1:1 with `experiments/NN_<short_name>.py` and
  `journal/NN_<short_name>.md`, that loads the experiment's skore
  report **read-only** and uses bare-last-expression cells to produce
  auto-displayed reprs the agent can consume. The agent executes the
  audit file via `jupytext --to ipynb` + `jupyter nbconvert --execute`
  + `--to markdown`, lands the executed `.ipynb` and rendered `.md`
  under `scratch/audit/<stem>/`, and reads the markdown to fuel
  narrative work (the `overview/summary.md` refresh, follow-up
  questions about a past experiment, cross-experiment comparison).
  Stops at "audit/NN_*.py is placed, executed, and its markdown
  digest is cached in scratch/audit/<stem>/." Never calls
  `skore.evaluate(...)` or `project.put(...)` — those remain
  experiment-script-only.

  TRIGGER — any of:
  - `iterate-ml-experiment` § 4 record-outcome just finished
    (summary.md refresh is done, JOURNAL.md History row is filled).
  - The user asks "audit experiment 02", "show me what 03 looks
    like", "re-audit 04 against the new report".
  - An experiment was re-run (the same `put()` key was overwritten
    with a new report) and the matching audit file needs refreshing.
  - The user wants a human-readable narrative of a past experiment
    without firing the full `iterate-from-skore` Backlog-enrichment
    flow.

  SKIP when: the design note isn't approved yet (route to
  `iterate-ml-experiment`); the experiment hasn't been run (no report
  on disk → audit has nothing to load — route to
  `iterate-ml-experiment` § 4 or the experiment runner); the agent
  feature (`jupytext` + `ipykernel` + `nbconvert`) isn't installed
  (route to `python-env-manager` § "Agent feature"); the user is
  mining the report to source the *next* experiment
  (`iterate-from-skore` owns Backlog enrichment — different output
  shape).

  HOW TO USE: confirm the four-way stem pairing exists first
  (`journal/NN_*.md` approved + `experiments/NN_*.py` exists + smoke
  test passed + report under that key in the skore Project), then
  place `audit/NN_<short_name>.py` from `templates/audit.py`,
  substituting the package name and experiment key. Execute via the
  two-step path: `jupytext --to ipynb` → `jupyter nbconvert
  --execute --ExecutePreprocessor.kernel_name=<kernel>` → `jupyter
  nbconvert --to markdown --stdout`. **Read the Stop conditions and
  emit the Pre-flight checklist as visible text before any
  filesystem write or shell command.** Always invoke `python-api`
  for skore symbol signatures (`Project`, `summarize`, `get`,
  `diagnosis`, `report.metrics.*`) — never write them from memory.
---

# Audit ML Pipeline

Per-experiment, human-readable, agent-executable narrative of a skore
report — produced by **executing** a bare-expression `# %%` file and
reading the resulting markdown digest. Read-only against the skore
Project.

## Where things live — visual map

Four locations matter. Three are ephemeral (gitignored); only one is
durable. Confusing them is the most common Qwen-class failure mode for
this skill.

| Path | Durability | Who writes it | What it holds |
|---|---|---|---|
| `audit/<NN>_<short_name>.py` | **Durable** (in git) | This skill, once per experiment | The bare-expression cells the agent executes. Source of truth. |
| `scratch/audit/<stem>/audit.ipynb` | Ephemeral | `jupytext --to ipynb` (step 1 of execution) | The unmodified `.py` converted to notebook format. Disposable intermediate. |
| `scratch/audit/<stem>/audit.executed.ipynb` | Ephemeral | `jupyter nbconvert --execute` (step 2) | The notebook with each cell's outputs embedded as JSON. Disposable. |
| `scratch/audit/<stem>/audit.md` | Ephemeral | `jupyter nbconvert --to markdown` (step 3) | Rendered markdown digest. **This is what the agent Reads back.** |

**Mnemonic:** `audit/` is *source* (one file per experiment, in git);
`scratch/audit/` is *output* (one directory per experiment, regenerable).
Never put the source `.py` under `scratch/audit/`. Never commit anything
under `scratch/audit/`.

## Anatomy of an audit file — concrete example

A well-formed audit cell ends with a **bare expression**. A
malformed one wraps in `print()` or stores the value in a variable
that's never displayed.

```python
# %% Right — bare expression auto-displays its repr
summary = project.summarize()
summary
```

```python
# %% Right — multiple statements, bare expression at the end
report = project.get(id_)
report
```

```python
# %% Right — statement-only is fine (no output expected)
KEY = "02_target_transform"
```

```python
# %% WRONG — print() loses rich repr; clutters the human-reading view
report = project.get(id_)
print(repr(report))  # <- drop the print, leave `report` as bare expr
```

```python
# %% WRONG — value computed but not displayed; cell shows no output
report = project.get(id_)
metrics = report.metrics  # <- add `metrics` on its own line at the end
```

```python
# %% WRONG — never call evaluate or put from an audit file
report = skore.evaluate(learner, ...)  # <- read-only contract violated
project.put(KEY, report)               # <- duplicates the row; pollutes summarize()
```

In notebook execution (which is how the agent runs audit files):
- The **last expression** of a code cell is auto-displayed if it's a
  bare expression (no assignment, no statement keyword, no `print`).
- Rich `_repr_html_` is preferred over `__repr__` when both exist
  (skore reports use this — the HTML repr lands in the markdown
  digest with embedded tables/plots).
- Assignment-only / statement-only cells produce **no output and no
  error** — they execute silently. This is the right shape for setup
  cells (imports, KEY = ..., etc.).

## Read-only contract

The central rule of this skill — referenced from every workflow
skill that touches audit files, surfaced as the first Stop
condition below, and structurally enforced by what's allowed in
the audit-file template.

**Allowed in `audit/<stem>.py`:**

- `skore.Project(...)` — open the project this experiment wrote to.
- `project.summarize()` — list the `(key, id)` pairs.
- `project.get(id)` — load a specific report by id.
- Every `report.*` accessor: `report.metrics`, `report.diagnosis()`,
  per-task plots, calibration, slice breakdowns, etc.
- Imports from `<pkg>` (read-only inspection of project utilities).

**Forbidden in `audit/<stem>.py`:**

- `skore.evaluate(...)` — the experiment script's job, not the
  audit's. Calling it from an audit file lands a **duplicate row
  under the same key** in `project.summarize()` and pollutes the
  cross-experiment metrics view that `overview/summary.md` reads
  from.
- `project.put(...)` — same reason; never persists from an audit.
- Writes outside `scratch/audit/<stem>/` — no `data/` writes, no
  `reports/` writes, no edits to `src/<pkg>/`. The audit is a
  viewer.
- Mutation of the loaded `report` object in a way that survives the
  cell (e.g., monkey-patching skore symbols). The audit observes,
  does not transform.

**Why this is enforceable in practice.** The audit file is
executed by `jupyter nbconvert --execute`, which runs every cell
to completion and embeds outputs in the executed `.ipynb`. A
forbidden call doesn't silently corrupt state — it surfaces in the
executed notebook (as a `put` row in a later `summarize()` cell,
or as an exception if the test environment forbids it). The
read-only contract is therefore *visible* in the markdown digest
the agent reads back; violations are reviewable, not invisible.

Sibling read-only consumers of the same Project (different output
shapes, same discipline): `scratch/<ts>_*.py` probes,
`iterate-from-skore`'s Backlog enrichment walk. See
`evaluate-ml-pipeline` § "Stop conditions" for the three-consumer
rule.

## Stop conditions — read before anything else

- **Read-only against the skore Project.** See § "Read-only
  contract" above. An audit file MAY call `skore.Project(...)`,
  `project.summarize()`, `project.get(id)`, and every `report.*`
  accessor. It MUST NOT call `skore.evaluate(...)` or
  `project.put(...)`. Both belong to `experiments/NN_*.py` only
  (see `evaluate-ml-pipeline` § "Stop conditions"). Re-running
  `evaluate` + `put` from an audit file duplicates the report
  under the same key and pollutes `project.summarize()` — the
  cross-experiment metrics view that `overview/summary.md` reads
  from.
- **`project.get(...)` is by id, not key.** Resolve the id by
  filtering `project.summarize()` rows for `key == "<stem>"`, then
  passing the resulting id to `get`. A `KeyError` from
  `project.get("<stem>")` means the lookup shape is wrong, not that
  the report is missing. See `python-api` § "Lookup failure ≠
  artifact missing" and `organize-ml-workspace` § "Scratch is
  read-only against the skore Project".
- **Symbol from memory is forbidden.** Any `skore` / `skrub` /
  `sklearn` symbol that appears in an audit file (`Project`,
  `summarize`, `get`, `report.metrics.*`, plot accessors) must come
  from a `python-api` lookup *this turn*. Recognition is not a
  lookup. Cache hits under `scratch/api/skore/<version>/` count
  (Shape 0); inline memory does not.
- **Agent feature missing → STOP and route.** If `jupytext` /
  `nbconvert` / a registered `ipykernel` for the project is missing,
  do not fabricate audit outputs by writing `print()` calls into the
  audit file as a workaround. Route to `python-env-manager` §
  "Agent feature", install via the right manager-scoped command,
  register the kernel (`python -m ipykernel install --user --name
  <project>`), and only then proceed. The bare-expression contract
  is what makes the audit file readable; substituting `print()`
  silently rewrites the convention out of the project.
- **Bare expressions, not `print()`.** The audit file's value comes
  from each cell's last expression being auto-displayed by IPython
  when the notebook executes. Wrapping in `print(repr(...))` works
  for plain text but loses rich repr (`_repr_html_`, plot mime
  types), and it clutters the human-reading version of the file.
  Use bare expressions; if a step is statement-only (variable
  binding, side effect), that's fine — the cell will simply have
  no output.
- **One audit file per experiment stem (four-way pairing).** The
  stem `NN_<short_name>` appears in exactly four places:
  `journal/NN_<short_name>.md`, `experiments/NN_<short_name>.py`,
  `tests/smoke/test_NN_<short_name>.py`, `audit/NN_<short_name>.py`.
  No `audit_NN_<short_name>_v2.py`. No alternate suffixes. When an
  experiment is re-run, the audit file is **overwritten in place**
  — same key, same audit.
- **Executed artifacts go to `scratch/audit/<stem>/`, not into
  `audit/`.** The durable artifact is `audit/<stem>.py` (the source
  cells). The intermediate `.ipynb` and the rendered `.md` are
  *ephemeral* per-execution outputs and land in
  `scratch/audit/<stem>/`. Per `python-api` § "`scratch/`
  conventions — probes vs. cache", scratch is gitignored; the
  executed digest is regenerable from the source any time.
- **`audit/` is read-only against the workspace's data too.** No
  writes to `data/`, no writes to `reports/`, no writes outside
  `scratch/audit/<stem>/`. The audit file is a viewer, not a
  producer. If a step would mutate state, it belongs in a probe
  under `scratch/<ts>_*.py` (per `python-api` § "Scratch
  conventions") or in the experiment script.
- **Harness "no clarifying questions" hints do NOT waive the
  agent-feature install gate.** When `python-env-manager` fires
  `G-AGENT-FEATURE` to install the agent feature, that is an
  operating-contract gate — not a clarifying question. "Quick" /
  "just go" / "you decide" never waives it.

## Forbidden shortcuts (observed-in-real-traces patterns)

| Shortcut | Why it feels right | Why it's wrong |
|---|---|---|
| `report = project.get(id_); print(repr(report))` | Explicit, matches the `print()` convention from regular scripts | Loses rich `_repr_html_` (the report's HTML view with embedded tables/plots is what makes the audit useful). Clutters the human-reading view of the file. Use `report` on its own line — IPython auto-displays it. |
| `jupytext --execute audit/<stem>.py` (one step) | Fewer commands, looks cleaner than the two-step path | jupytext's in-process execute resolves the kernel from the current Python executable, which fails in non-Jupyter envs ("No kernel found that matches…"). Probe-verified failure mode. Always two-step: `jupytext --to ipynb` then `nbconvert --execute --ExecutePreprocessor.kernel_name=<kernel>`. |
| `project.get(KEY)` raised `KeyError` → re-run `skore.evaluate` + `project.put` from the audit file to "refresh" the report | Looks like the report is missing; regenerating seems harmless | Lookup shape is wrong (`get` is by id, not by key). Re-running lands a **duplicate row under the same key** and pollutes `project.summarize()` — which `overview/summary.md` reads from. Use `summarize()` → filter by `key == "<stem>"` → `get(id)`. Never substitute. |
| Dump the audit `.py` into `scratch/audit/<stem>/` alongside the executed `.ipynb` | "All audit stuff in one folder" | The `.py` is durable source-of-truth in git; `scratch/` is gitignored. Splitting them is the rule: source in `audit/`, ephemerals in `scratch/audit/<stem>/`. |
| `ipykernel` is already pip-installed → skip `python -m ipykernel install --user --name <kernel>` | Looks like a duplicate install | `ipykernel` the package and a *registered kernelspec* are different things. nbconvert resolves `--ExecutePreprocessor.kernel_name` against `~/Library/Jupyter/kernels/<name>/` (or platform equivalent). Without the explicit register step, execution fails. |
| Hallucinate a `report.diagnose()` / `report.diagnostic()` / `report.diagnostics` accessor because the right name "should be obvious" | Confident-sounding API guess | Symbol-from-memory failure. Real accessors come from `python-api` Shape 1 lookup against the installed skore version. Cache hits first (`scratch/api/skore/<version>/`). The bare-expression contract surfaces the failure at execution time as `AttributeError` — useful, but cheaper to look up than to execute and fix. |
| Add a fix-up cell that mutates `data/` or `reports/` from inside the audit file | "While I'm in here…" | Audit files are **read-only against the workspace**. Writes outside `scratch/audit/<stem>/` are a contract violation. State mutations belong in a `scratch/<ts>_*.py` probe (per `python-api` § "`scratch/` conventions — probes vs. cache") or the experiment script. |
| Substitute `<SKORE_PROJECT_INIT>` in `audit/<stem>.py` from the recorded `skore mode:` decision without reading `experiments/<stem>.py` first | "I know the form; the gate says hub/local" | The audit must open the **exact same Project** the experiment wrote to. A typo, formatting drift, or wrong workspace name silently opens a different store and `summarize()` returns "missing report". Always `Read experiments/<stem>.py` this turn and copy the literal Project init block (and any preceding `login` call) into the audit file. Byte-identical modulo formatting. See `organize-ml-workspace` § G-SKORE-MODE "Anatomy of substitution". |
| Hub mode: put `skore.login(mode="hub")` after `skore.Project(...)` because the audit is "just inspecting" | Login looks like setup that "should happen first only when needed" | The Project constructor authenticates against the hub at init time; without a prior `login`, it fails. Order is fixed: `login` first, `Project` second. Same shape as the experiment's; copy it. |

## Pre-flight — emit before any audit-file write or execution

```
Pre-flight (audit-ml-pipeline):
- [ ] Experiment stem confirmed: <NN_short_name>
      Evidence: journal/NN_<short_name>.md exists AND is at least `done`
                (Read journal/JOURNAL.md History this turn for state)
                | "n/a — user invoked re-audit on an existing stem"
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
                "Run finished, put() landed" is NOT sufficient —
                only `summarize()` confirms the report is on disk.
- [ ] Agent feature available (jupytext, nbconvert, ipykernel
      kernelspec named after the project):
        `pixi run -e dev jupytext --version` exit 0
        `pixi run -e dev jupyter --version` exit 0
        `jupyter kernelspec list` shows the project's kernel
      Evidence: tool output of each (or the equivalent for the
                workspace's env manager — see `python-env-manager` §
                "Agent feature").
                Missing → STOP and route to python-env-manager.
- [ ] python-api consulted for skore symbols used in the audit file:
      Project, summarize, get, report.diagnosis, report.metrics.*
      Evidence: Read scratch/api/skore/<version>/<topic>.md (this turn)
                | Write the same (this turn)
                | "n/a — cache hit, file already on disk + Read this turn"
- [ ] Template copy + substitution decided:
        <pkg> → package name from src/<pkg>/
        <NN>_<short_name> → experiment stem
        <project-name> → skore Project name from experiments/<stem>.py
      Evidence: Read experiments/<stem>.py this turn for the project
                name + key literal; Read templates/audit.py this turn
                before Write audit/<stem>.py
- [ ] Read-only contract acknowledged: audit file contains
      summarize / get / report.* only — no evaluate, no put
      Evidence: explicit grep / Read confirmation of the drafted file
- [ ] Executed artifacts target chosen: `scratch/audit/<stem>/`
      Evidence: mkdir -p scratch/audit/<stem>/ (this turn)
- [ ] Execution command shape confirmed (two-step):
        jupytext --to ipynb audit/<stem>.py -o scratch/audit/<stem>/audit.ipynb
        jupyter nbconvert --execute --to notebook \
          --ExecutePreprocessor.kernel_name=<kernel> \
          --output audit.executed.ipynb \
          scratch/audit/<stem>/audit.ipynb
        jupyter nbconvert --to markdown --stdout \
          scratch/audit/<stem>/audit.executed.ipynb \
          > scratch/audit/<stem>/audit.md
      Evidence: each command emitted in the response before running
```

## Scope

- **In scope:** placing `audit/<stem>.py` from the template
  (substituting package name, experiment stem, project name);
  executing it via jupytext + nbconvert; rendering markdown to
  `scratch/audit/<stem>/audit.md`; reading the markdown back into
  the agent's context for narrative use; refreshing on re-run.
- **Out of scope:** producing reports (that's `evaluate-ml-pipeline`
  + `experiments/NN_*.py`); enriching the Backlog from a diagnosis
  (that's `iterate-from-skore`); writing the per-experiment design
  note (that's `iterate-ml-experiment`); installing the agent
  feature (that's `python-env-manager`).

## The audit file contract

### Format and substitutions

The audit file is **jupytext percent format** (`# %%` cell markers),
matching the convention used in `experiments/` and owned by
`organize-ml-workspace`. Filename: `audit/NN_<short_name>.py` — the
stem matches the experiment exactly (four-way pairing rule above).

Template lives at `templates/audit.py`. Substitutions when filling
the per-experiment file:

| Placeholder | Replaced with |
|---|---|
| `<pkg>` | The project's importable package name (from `src/<pkg>/`) |
| `<NN>_<short_name>` | The experiment stem (e.g. `02_target_transform`) |
| `<SKORE_PROJECT_INIT>` | The full Project init block (and, for hub mode, the preceding `skore.login(mode="hub")` call). The form depends on the workspace's `skore mode:` decision recorded in `JOURNAL.md` Status `Workspace decisions` (see `organize-ml-workspace` § "G-SKORE-MODE"). MUST match the form used in `experiments/<stem>.py` exactly |
| `<project-name>` | The `name=` argument (local mode) or the part after `/` in `"<hub-workspace>/<project-name>"` (hub mode), as used in `skore.Project(...)` in `experiments/<stem>.py` — read it from there, do not invent it |
| `<hub-workspace>` | Hub-mode only. The Skore Hub workspace identifier from `JOURNAL.md` Status `Workspace decisions` `skore hub workspace:` row — distinct from the local-mode `workspace=` kwarg |

`<SKORE_PROJECT_INIT>` and `<project-name>` are the most
error-prone substitutions: the audit file MUST open the same
Project the experiment wrote to, so the init block has to match
exactly. **Always `Read experiments/<stem>.py` this turn to lift
the literal Project init block** — never reconstruct it from
memory of the `skore mode:` decision alone. The contract: copy the
exact same `skore.Project(...)` call (and any preceding `login`
call for hub mode) from the experiment script into the audit
file.

### Cell structure — what each cell does

The template ships with the following cell sequence; adapt the
**Metric accessors** block per task, leave the rest as-is unless a
specific experiment needs more.

1. **Module-level docstring (markdown cell).** What this file is,
   the read-only rule, where the executed digest lands. Verbatim
   from the template.
2. **Imports (code cell).** `import skore` and `from <pkg> import
   PROJECT_ROOT`. No statement-only branching here.
3. **Open the Project (code cell, bare expression at the end).**
   `project = skore.Project(...)` then `project` on its own line.
   The cell's output is the Project's repr — useful for confirming
   the right project, the right workspace, the right mode.
4. **List the available reports (code cell, bare expression at the
   end).** `summary = project.summarize()` then `summary` — the
   cell's output is the cross-experiment `(key, id)` table.
5. **Resolve this experiment's id (code cell, bare expression).**
   Filter `summary` by `key == "<NN>_<short_name>"`, extract the
   id; `id_` on its own line so the cell shows it.
6. **Load the report (code cell, bare expression).** `report =
   project.get(id_)` then `report` — auto-displays the report's
   rich repr (HTML when available, plain otherwise).
7. **Diagnosis (code cell, bare expression).**
   `report.diagnosis()` — auto-displays the v1 diagnostic surface.
8. **Per-task metric accessors (one bare expression per cell).**
   `report.metrics`, then any task-specific accessors the design
   note's Method called out. One per cell so each lands as its own
   output in the markdown digest — easier for the agent to scan.

Statement-only cells (variable binding, side effects) are fine and
produce no output in the digest. Don't pad them with `print(repr(...))`
to "force" output; that's the anti-pattern the bare-expression
contract exists to avoid.

## Execution contract — two-step

The reliable execution shape — verified by the skill's bundled
probe before this contract was committed:

```bash
# (1) Convert .py percent format to .ipynb. No execution yet.
pixi run -e dev jupytext --to ipynb \
  audit/<stem>.py -o scratch/audit/<stem>/audit.ipynb

# (2) Execute the .ipynb with the project's registered kernel.
pixi run -e dev jupyter nbconvert --execute --to notebook \
  --ExecutePreprocessor.kernel_name=<kernel> \
  --output audit.executed.ipynb \
  scratch/audit/<stem>/audit.ipynb

# (3) Render the executed notebook to markdown for agent consumption.
pixi run -e dev jupyter nbconvert --to markdown --stdout \
  scratch/audit/<stem>/audit.executed.ipynb \
  > scratch/audit/<stem>/audit.md
```

(For non-pixi workspaces, replace `pixi run -e dev` with the
manager's equivalent — see `python-env-manager` § "Agent feature"
for the per-manager invocation. `<kernel>` is the kernel name
registered at agent-feature install time and recorded in
`JOURNAL.md` Status `Workspace decisions` as `agent kernel:`; the
audit skill does not register kernels itself.)

Why **two steps**, not `jupytext --execute` in one call: jupytext's
in-process execute path needs to resolve a kernelspec from the
current Python executable, which fails in non-Jupyter Python envs
(verified — see the probe under "Why the contract is what it is"
below). The two-step path with an explicit
`--ExecutePreprocessor.kernel_name` is reliable.

### Why the contract is what it is (one-paragraph rationale)

The probe that verified this contract executed a sample
`# %%` file with four cells covering: a bare expression (auto-
displays repr), a statement-only cell (no output, no error), a
follow-up bare expression, and a class with both `__repr__` and
`_repr_html_`. The executed notebook preserved auto-display in
`cell.outputs[*].data["text/plain"]`, the statement-only cell
produced zero outputs (no `print` fallback was needed), and the
rich `_repr_html_` was preferred over plain `__repr__` in the
markdown rendering. The single-step `jupytext --execute` path
failed with "No kernel found that matches the current python
executable"; the two-step path with explicit `kernel_name`
succeeded. The contract reflects what was observed, not what was
assumed.

### Re-execution semantics

Same key, same audit:

- **Re-running an experiment** (overwriting the put under the same
  key) means the matching audit file should be **re-executed** —
  the underlying `report` may have changed even though the source
  cells didn't. `iterate-ml-experiment` § 4 fires the audit skill
  on every record-outcome, including re-runs.
- **Editing the audit file's source** (adding a metric accessor
  for a question the agent now wants answered) triggers re-execution
  too — the executed digest is regenerable.
- The `scratch/audit/<stem>/` directory is **overwritten on every
  execution**. There is no version history; the source `.py` plus
  git history is the audit's audit trail.

## Four-way stem-pairing rule

This skill extends the pairing rule owned by
`organize-ml-workspace` from three artifacts to four:

```
journal/NN_<short_name>.md           — design note
experiments/NN_<short_name>.py       — script
tests/smoke/test_NN_<short_name>.py  — smoke test
audit/NN_<short_name>.py             — audit  ← this skill
```

Identical stems, 1:1. By the time an experiment shows `done` in
`JOURNAL.md` AND its summary has been refreshed in
`overview/summary.md`, all four exist. Whichever skill lands first
in a session reads the other three's presence as the precondition.

## Dispatching in and out

### Called from

- **`iterate-ml-experiment` § 4** — automatic dispatch after the
  summary.md refresh; the agent feature must be available
  (`G-AGENT-FEATURE` resolved). If unavailable, § 4 routes to
  `python-env-manager` first, returns here once install is done.
- **`iterate-ml-experiment` § 0 (bootstrap)** — after the first
  baseline run, dispatch here for `audit/01_baseline.py` once the
  baseline's report is in the Project.
- **User free-text** — "audit experiment 02", "show me what 03
  looks like", "re-audit 04 against the new report". Free-text
  resolves directly to this skill.

### Calls into

- **`python-api`** for every skore symbol the audit file uses
  (Project, summarize, get, diagnosis, metric accessors). Cache
  hits first (Shape 0), then Shape 1 if the symbol isn't cached
  yet. Inline `pixi run python -c "..."` is forbidden (per
  `python-api` § Stop conditions).
- **`python-env-manager`** when the agent feature is missing.
  Hand off, return when install is done; do not run install
  commands directly from this skill.
- **`python-code-style`** after writing or editing
  `audit/<stem>.py` — the bundled `ruff.toml`'s `audit/**`
  per-file ignores match `experiments/**` (module docstring +
  function docstring exemptions for cell-marker files).

## Failure modes and recovery

- **`project.get(key)` raises `KeyError`.** Lookup shape is wrong.
  Use `summarize()` to enumerate `(key, id)` pairs, filter by the
  experiment stem, pass the resulting id to `get`. Never substitute
  by re-running `evaluate` + `put`. See `python-api` § "Lookup
  failure ≠ artifact missing".
- **`nbconvert --execute` fails with "No kernel matches".** The
  agent feature's kernel isn't registered (or is registered under
  a different name than the audit file is requesting). Route to
  `python-env-manager` § "Agent feature" → kernel registration
  step. Do not change the audit file's execution command to
  guess at a different kernel name.
- **Markdown render fails / is empty.** Usually means the executed
  `.ipynb` has errored cells. Read
  `scratch/audit/<stem>/audit.executed.ipynb` directly — JSON
  `cell.outputs[*]` will carry `output_type: "error"` with `ename`
  / `evalue` / `traceback`. Fix the audit file (most likely a stale
  symbol from memory — confirm via `python-api`); never silently
  skip the failing cell.
- **Audit cell uses an accessor that doesn't exist in this skore
  version.** Symptom: `AttributeError: 'EstimatorReport' object has
  no attribute '...'`. Cause: symbol drift between skore releases.
  Consult `python-api` against the installed version (Shape 1 or
  Shape 3) and update the audit cell to use the current accessor.
- **Report differs between runs even when source code didn't
  change.** Most often: the experiment was re-run with a different
  data slice, or a non-deterministic step (RNG seed) shifted. Not
  a bug in this skill; surface to the user before assuming the
  audit changed.
- **Hub mode: `skore.login(mode="hub")` fails with an
  authentication error.** Token expired or the user hasn't logged
  in on this machine yet. Surface the failure verbatim; do not
  retry from a `scratch/` probe — `login` is interactive (browser
  or API key prompt) and belongs in the audit file's own
  execution. Re-run `pixi run -e dev jupyter nbconvert --execute
  audit/<stem>.ipynb` after the user has refreshed credentials.
- **Hub mode: `TypeError: Project.__init__() got an unexpected
  keyword argument 'workspace'`.** The `<SKORE_PROJECT_INIT>`
  substitution dropped the hub form but left a `workspace=` kwarg
  in the call. `workspace=` is local-mode-only — hub mode rejects
  it. Re-check the audit file's Project init block against the
  experiment script's (they must match), or re-substitute the
  marker from a clean template.
- **Hub mode: report appears missing in `summarize()` but the
  experiment script reported a successful `put()`.** Two
  possibilities: (1) the audit is opening a different hub
  workspace than the experiment wrote to (verify the
  `<hub-workspace>` part of the name matches `Workspace
  decisions`); (2) the user's credentials don't have read access
  to the workspace they wrote to (rare; surface the access issue
  to the user, do not silently fall back to local mode).

## Companion skills

- **`iterate-ml-experiment`** — the caller. Owns the iteration
  loop; § 4 dispatches here. The audit run's markdown digest
  feeds the `overview/summary.md` refresh.
- **`iterate-from-skore`** — sibling consumer of the same report.
  Different output shape: iterate-from-skore returns
  Backlog-candidate rows + a one-paragraph summary (for sourcing
  the *next* experiment); audit-ml-pipeline returns a per-
  experiment markdown narrative (for understanding the *current*
  one). Both are read-only; both go through `project.summarize()`
  → `project.get(id)` → `report.*`.
- **`evaluate-ml-pipeline`** — owns the producer side. Its Stop
  condition that `skore.evaluate(...)` + `project.put(...)` live
  *only* in `experiments/NN_*.py` is what makes the read-only
  contract here coherent.
- **`organize-ml-workspace`** — owns the workspace layout. Reads
  `audit/` as a peer of `experiments/` / `journal/` /
  `tests/smoke/`; enforces the four-way stem pairing.
- **`python-env-manager`** — owns the agent feature install
  (jupytext, ipykernel, nbconvert) and the kernel registration.
  Invoked when the agent feature is missing.
- **`python-api`** — every skore symbol the audit file uses.
  Mandatory before naming any accessor. Cache hits first
  (`scratch/api/skore/<version>/`).
- **`python-code-style`** — ruff after writing/editing
  `audit/<stem>.py`. The bundled `ruff.toml` carries `audit/**`
  per-file ignores so cell-marker docstring rules don't fire.
- **`data-science-python-stack`** — `jupytext`, `nbconvert`,
  `ipykernel` live in this stack's **agent feature** (not Tier 1).
  Bringing them in is a `python-env-manager` G-AGENT-FEATURE
  decision.

## Templates

- `templates/audit.py` — the per-experiment audit file skeleton in
  jupytext percent format. Copy, substitute `<pkg>` /
  `<NN>_<short_name>` / `<project-name>`, adapt the metric-accessor
  cells per task. Don't rewrite from memory.

## What this skill does NOT do

- Open or write the skore Project's reports (`evaluate-ml-pipeline`).
- Install jupytext / ipykernel / nbconvert (`python-env-manager`).
- Register the project's kernelspec (`python-env-manager`).
- Enrich the Backlog from the diagnosis (`iterate-from-skore`).
- Write or edit `journal/NN_*.md` (`iterate-ml-experiment`).
- Run pytest / smoke tests (`smoke-test-ml-pipeline`).
- Render commits or PRs.
- Decide *which* metrics matter for the task — the audit file's
  metric-accessor cells are filled per task, but the *judgment*
  about what matters is the user's, captured in the design note.
