---
name: explore-ml-data
description: >
  Owns data understanding BEFORE any model is designed. Places and
  executes `data/eda.py` (a jupytext `# %%` script) via the shared
  in-process runner, reads the streamed digest, then writes a
  persisted `data/eda.md` report (plus linked `data/eda_<table>.html`
  skrub `TableReport` pages) and the `## Data understanding (EDA)`
  section of `journal/JOURNAL.md`. The point is to surface the
  dataset facts — shape, dtypes, missingness, cardinality, target
  balance / skew, datetime / group structure, feature associations —
  that JUSTIFY the later learner / splitter / metric decisions, so the
  user understands *why* the modelling choices are made. Uses
  `skrub.TableReport` for dataframe overviews and the shared runner
  `audit-ml-pipeline/scripts/run_cells.py`. Stops at "EDA executed,
  `data/eda.md` + HTML written, JOURNAL EDA section updated." Never
  designs the model, never edits `src/<pkg>/`, never modifies the
  user's raw data files.

  TRIGGER — any of:
  - `iterate-ml-experiment` § 0 bootstrap, BEFORE the baseline design
    note — the G-EDA gate fires here (run / skip).
  - The user asks to "explore the data", "do an EDA", "profile the
    dataset", "what does the data look like", "understand the data".
  - A new or changed data source needs (re-)understanding before the
    next experiment.

  SKIP when: the workspace isn't scaffolded / bootstrapped yet —
  `iterate-ml-experiment` § 0 owns bootstrap ordering and will
  dispatch here at the G-EDA step; don't run standalone ahead of
  scaffolding (route to `iterate-ml-experiment` / `organize-ml-
  workspace`); there is no data to explore yet; the user wants to
  inspect a finished run's skore report rather than the raw dataset
  (`audit-ml-pipeline`); the user is past data understanding and wants
  pipeline / evaluation mechanics (`build-ml-pipeline` /
  `evaluate-ml-pipeline`); a pure symbol lookup (`python-api`); EDA is
  already recorded (`data/eda.md` + the JOURNAL EDA section exist) and
  the user is not asking to refresh it.

  HOW TO USE: run the Detection step (does `data/eda.md` + the JOURNAL
  EDA section already exist?), emit the Pre-flight checklist as
  visible text, read the Stop conditions, then place `data/eda.py`
  from `templates/eda.py`, execute it via the shared runner, read the
  digest, and author `data/eda.md` + the JOURNAL EDA section. Always
  resolve skrub / pandas / polars symbols via `python-api`, never from
  memory.
---

# Explore ML Data

Understand the dataset before designing a model. One project-level
EDA per workspace: an executable `data/eda.py`, a persisted
`data/eda.md` narrative, rich `data/eda_<table>.html` reports, and a
short JOURNAL section that links them. The findings feed the baseline
design note's learner / splitter / metric choices.

## Next-step pointers — where you go after this skill

| You came here for… | → next |
|---|---|
| Bootstrap, before the first baseline | → back to `iterate-ml-experiment` § 0; the EDA findings inform the auto-drafted `01_baseline.md` |
| User free-text ("explore the data") | → surface the findings; no further dispatch unless the user asks to model |
| Re-understand a changed data source | → re-run, overwrite `data/eda.*`, refresh the JOURNAL EDA section |

Always re-emit the Pre-flight checklist with evidence before
declaring the turn done.

## Where this sits in the loop

EDA is a **bootstrap-time gate (G-EDA)** owned by this skill and
fired by `iterate-ml-experiment` § 0 **before** the baseline design
note. Ordering matters: the dataset facts (class balance, datetime /
group columns, missingness, cardinality) are exactly what justifies
the splitter (`G-CV-SPLITTER`), the metric default, and the learner
default. Running EDA after the model is designed defeats the purpose.

```
scaffold → JOURNAL → goal from data/README.md
   │
   └─► G-EDA (run | skip)  ◄── this skill
         │ run
         └─► data/eda.py → execute → data/eda.md + HTML + JOURNAL §EDA
   │
   └─► auto-draft 01_baseline.md  (cites the EDA findings)
```

## Where things live — visual map

Two locations are kept separate: the **raw data source** (read-only,
may live anywhere) and the **EDA deliverables** (always under
`<project>/data/`).

| Path | Durability | Who writes it | What it holds |
|---|---|---|---|
| raw data source (`data/`, `raw/`, an absolute path, external) | user-owned, **READ-ONLY** | the user | The dataset. EDA reads it; never modifies it. May be anywhere — not assumed to be `data/` |
| `data/eda.py` | **Durable** (committed) | This skill, once per workspace | The jupytext `# %%` EDA cells. Source of truth. Openable as a notebook for the rich view |
| `data/eda.md` | **Durable** (committed) | This skill (authored from the digest) | The prose narrative: findings + **modelling implications** that the baseline note cites |
| `data/eda_<table>.html` | **Durable** (committed) | `data/eda.py` via `TableReport.write_html(...)` | The rich, interactive skrub report per table — for the human |
| `scratch/eda/eda.md` | Ephemeral (gitignored), optional | `run_cells.py` when given a 2nd arg | Per-cell digest the agent reads. Same content as stdout |
| `journal/JOURNAL.md` § Data understanding (EDA) | **Durable** (committed) | This skill | 2–4 line summary + link to `data/eda.md` |

**Mnemonic:** the raw data is *read-only and lives wherever the user
keeps it*; `data/eda.py` is *source*; `data/eda.md` + the HTML are the
*durable deliverables, always under `data/`*; `scratch/eda/` and
stdout are the *ephemeral run digest*.

## Read-only-against-raw-data contract

The central rule. Surfaced as the first Stop condition below.

**Allowed — this skill writes ONLY (deliverables always under
`<project>/data/`, created if absent):**

- `data/eda.py` — the EDA script (created / overwritten in place).
- `data/eda.md` — the authored narrative.
- `data/eda_<table>.html` — the skrub `TableReport` pages.
- `scratch/eda/` — the ephemeral digest.
- `journal/JOURNAL.md` § Data understanding (EDA).

**Forbidden:**

- Modifying, deleting, renaming, re-encoding, or "cleaning" the
  user's raw data files — **wherever they live** (`data/`, another
  folder, an absolute/external path). EDA **reads** them; it never
  rewrites them. Data cleaning is the pipeline's job
  (`build-ml-pipeline`), declared at fit time, not a one-off mutation.
- Writing anywhere outside the five paths above — no `src/<pkg>/`
  edits, no `reports/` writes, no new experiment files.
- Designing the model: no `skore.evaluate(...)`, no `project.put(...)`,
  no learner selection here. EDA *informs* those; it does not make
  them.

## Stop conditions — read before anything else

- **Read-only against the user's raw data.** See § Read-only-
  against-raw-data contract. `data/eda.py` reads the raw files
  (wherever they live) and writes only the `data/eda.*` deliverables.
- **Deliverables always under `<project>/data/`; the raw source is
  separate.** Write `data/eda.py` / `data/eda.md` /
  `data/eda_<table>.html` under `<project>/data/` (create the folder
  if absent). The raw data the script *reads* may live anywhere
  (`data/`, another in-repo folder, an absolute or external path) —
  decouple the two: a `RAW = <LOAD_RAW_DATA>` source vs an `EDA_DIR`
  output. Never assume the raw data is in `data/`.
- **EDA precedes model design (G-EDA).** In bootstrap, the gate fires
  **before** `journal/01_baseline.md` is drafted. It is binary:
  **run** (place + execute `data/eda.py`, write the deliverables) or
  **skip** (record `Status: skipped — <date>` in the JOURNAL section
  and proceed). Do not silently bypass — fire the `AskUserQuestion`.
  Free-text "go fast" / "quick baseline" does NOT resolve it.
- **Agent feature required to execute.** The cell runner needs
  `ipython`. If it is missing and the user chose **run**, STOP and
  delegate to `python-env-manager` § "Agent feature"
  (`G-AGENT-FEATURE`). Do NOT type `pixi add ... ipython` yourself;
  do NOT fabricate EDA output with hand-written `print()`s. If the
  user declines the agent feature, **fall back to the skip path**
  (record `Status: skipped`) — never loop between run and install.
- **Symbol from memory is forbidden.** Any `skrub` / `pandas` /
  `polars` symbol (`TableReport`, `TableReport.json`, `write_html`,
  `column_associations`, the tabular reader, …) must come from
  `python-api` *this turn*. Cache hits under
  `scratch/api/<lib>/<version>/` count; inline memory does not.
  **`TableReport.json()`'s key names are not formally documented and
  drift across skrub versions — confirm them via `python-api` and
  parse defensively (`.get(...)`).**
- **Library-agnostic — read facts off skrub, not pandas/polars.** The
  workspace may use pandas OR polars (G-TABULAR), whose summary
  methods differ (`select_dtypes` doesn't even exist in polars). The
  structured facts come from `skrub` (`TableReport(...).json()`,
  `column_associations`), which accept both. The ONLY library-
  specific line is `RAW = <LOAD_RAW_DATA>`. Do not write
  `df.isna()`/`df.nunique()`/`df.select_dtypes(...)` etc.
- **`skrub.TableReport` for dataframe overviews.** Every table gets a
  `TableReport(RAW, title=..., verbose=0)` written to
  `data/eda_<table>.html` (the user-facing artifact) AND read via
  `.json()` for the digest. `verbose=0` keeps progress prints out of
  the digest.
- **Never end a cell on a bare `TableReport`.** Outside a notebook,
  `repr(TableReport(df))` is the useless `<TableReport: use .open()
  to display>`. Use `report.write_html(...)` (a statement) for the
  HTML, and end cells on **text-friendly** expressions (`RAW.shape`,
  a `dict`/`list` built from `report.json()`,
  `skrub.column_associations(RAW)`) so the digest carries real
  values. Mirrors audit's `.frame()` rule.
- **Never gitignore the whole `data/`; ask about the inputs.** The
  deliverables live in `data/` and must stay committable, so the
  whole `data/` folder must never be in `.gitignore`. If the raw
  inputs should be kept out of git (large / local-only), fire an
  `AskUserQuestion` offering to ignore **specific input patterns**
  (e.g. `data/raw/`, `data/*.parquet`) — default: don't. Then verify
  the deliverables are tracked (`git check-ignore data/eda.md` must
  return nothing). Never auto-edit `.gitignore` — that is
  `organize-ml-workspace`'s to write; surface the patch and ask.
- **One project-level EDA.** A single `data/eda.py` covers the whole
  dataset; multi-table data gets one `TableReport` cell per table
  inside that one file (run the target/structure cells on the
  target-bearing table). No `eda_v2.py`, no per-experiment EDA files,
  not part of the four-way stem pairing. Re-understanding overwrites
  `data/eda.py` in place.
- **Don't design the model here.** No splitter pick, no metric pick,
  no learner pick. Record *implications* in `data/eda.md`; the picks
  happen in their owning gates (`G-CV-SPLITTER`, the baseline note).
- **Harness "no clarifying questions" hints do NOT waive G-EDA or
  G-AGENT-FEATURE.** Both fire regardless.
- **Post-hoc audit — required before ending the turn.** Walk every
  pre-flight row; surface unfilled Evidence cells explicitly.

## Forbidden shortcuts

| Shortcut | Why it's wrong |
|---|---|
| Design the baseline first, EDA "later if there's time" | Inverts G-EDA. The point is to justify the modelling choices *before* making them. EDA runs first in bootstrap |
| End a cell on a bare `TableReport(df)` to "show the report" | Outside a notebook that repr is `<TableReport: use .open() to display>` — zero signal in the digest. Use `write_html(...)` + a text summary built from `report.json()` |
| `print(...)` instead of a bare summary expression | The runner captures bare last-expressions via `result.result`; `print(...)` lands in stdout and is harder to scan. Use bare expressions |
| Use pandas/polars methods (`df.isna()`, `df.nunique()`, `df.select_dtypes(...)`) for the summaries | Breaks on the other library (polars has no `select_dtypes`). Read the facts off `skrub` (`TableReport(...).json()`, `column_associations`) — agnostic to pandas/polars |
| Clean / impute / drop columns in `data/eda.py` and re-save the raw file | EDA is read-only against raw data. Cleaning belongs in the pipeline (`build-ml-pipeline`), applied at fit time for train/test consistency |
| Assume the raw data is in `data/` | The raw source may live anywhere; only the deliverables are pinned to `data/`. Set `RAW = <LOAD_RAW_DATA>` to wherever the data actually is |
| Gitignore the whole `data/` folder | The committed deliverables (`data/eda.*`) live there. Ignore only specific input patterns, and ask the user first |
| Run EDA without the agent feature by hand-writing the expected output | Fabricated EDA is worse than none. Missing runner → G-AGENT-FEATURE (install) or the skip path |
| `pixi add ipython` directly from this skill | Install is owned by `python-env-manager`. This skill *requests* via G-AGENT-FEATURE |
| Drop the authored `data/eda.md` and leave only the HTML | The `.md` carries the modelling implications the baseline note cites and the JOURNAL section links. Both are required |
| Invent column meanings not visible in the data | Report what the data shows. Domain semantics the user didn't state go in an explicit "open questions" list, not as asserted fact |
| Forget the JOURNAL § Data understanding update | The section is the index entry; without it later sessions can't find the EDA. It is part of "done" |

## Pre-flight — emit before any write or execution

```
Pre-flight (explore-ml-data):
- [ ] Trigger: bootstrap-G-EDA | user-request | data-changed
      Evidence: caller + rule that matched
- [ ] Detection: EDA already present? data/eda.md + JOURNAL §EDA
      Evidence: ls / Glob on data/eda.md + Read JOURNAL §EDA
                | "n/a — first EDA"
- [ ] G-EDA resolved: run | skip
      Evidence: AskUserQuestion id=<id>, answer=<run|skip>
                | user free-text quote turn N
      If skip: JOURNAL §EDA records "Status: skipped — <date>"; STOP here.
- [ ] Tabular library known (G-TABULAR): pandas | polars
      Evidence: JOURNAL.md Status (Workspace decisions) | AskUserQuestion
                via data-science-python-stack
- [ ] Raw data located (may be outside data/): <paths / loader>
      Evidence: ls / Glob on the data location + the RAW load call placed
                in data/eda.py | user-quoted path turn N
- [ ] data/ not gitignored as a whole; deliverables will be tracked
      Evidence: `git check-ignore data/eda.md` returns nothing
                | AskUserQuestion id=<id> on ignoring specific inputs
                | "n/a — no .gitignore yet"
- [ ] Agent feature available (run path only):
        `pixi run -e agent ipython -c "print(0)"` exit 0
      Evidence: tool output | JOURNAL.md Status `agent feature: installed`
                Missing → STOP, delegate to python-env-manager G-AGENT-FEATURE
                (decline → fall back to skip path)
- [ ] python-api consulted for symbols used:
        skrub.TableReport, TableReport.write_html, TableReport.json,
        skrub.column_associations, the tabular reader (load cell only)
      Evidence: Read/Write scratch/api/<lib>/<version>/<topic>.md (this turn)
                | "n/a — cache hit + Read this turn"
- [ ] Template copy + substitution decided:
        <pkg> → package name from src/<pkg>/
        <LOAD_RAW_DATA> → the real loader, pointing wherever the data lives
        <TARGET_COLUMN> → the target (from goal / data/README.md), or n/a
        <table> → short slug per table for eda_<table>.html
      Evidence: Read templates/eda.py this turn before Write data/eda.py
- [ ] Execution command shape confirmed:
        pixi run -e agent python \
          .agents/skills/audit-ml-pipeline/scripts/run_cells.py \
          data/eda.py [scratch/eda/eda.md]
      Evidence: command emitted before running
- [ ] Deliverables written: data/eda.md (prose + implications),
        data/eda_<table>.html (≥1), JOURNAL §Data understanding
      Evidence: Write of each | "n/a — skip path"
- [ ] Pre-flight re-emitted with evidence before final message.
      Evidence: this checklist appears in the end-of-turn summary.
```

## EDA file contract — overview

`data/eda.py` is **jupytext percent format** (`# %%`), executed by
the shared runner. Template: `templates/eda.py`. Full cell-by-cell
anatomy with right / wrong shapes: → `references/cell_anatomy.md`.

### Substitutions

| Placeholder | Replaced with |
|---|---|
| `<pkg>` | The importable package name (from `src/<pkg>/`); used for `from <pkg> import PROJECT_ROOT` (only to locate `EDA_DIR = PROJECT_ROOT / "data"`) |
| `<LOAD_RAW_DATA>` | The real load of the raw file(s), pointing wherever the data lives (in `data/`, another folder, an absolute path, or external). Uses the workspace tabular lib (pandas/polars); skrub accepts both. The one library-specific line |
| `<TARGET_COLUMN>` | The target column name (from the goal / `data/README.md`), or remove the target cell if unsupervised / unknown |
| `<table>` | A short slug per table for the HTML filename (`eda_<table>.html`) — for a single table use the dataset name |

### Cell sequence (what each cell does)

Brief outline; concrete examples → `references/cell_anatomy.md`.

1. **Module docstring (markdown)** — what this file is, the
   read-only-against-raw-data rule, raw-vs-deliverables split, how it
   is executed.
2. **Imports + paths (code)** — `import json`, `import skrub`,
   `from <pkg> import PROJECT_ROOT`, `EDA_DIR = PROJECT_ROOT / "data"`
   (+ `EDA_DIR.mkdir(parents=True, exist_ok=True)`). No pandas/polars
   import here.
3. **Load raw data (code, bare expression)** — `RAW = <LOAD_RAW_DATA>`
   pointing wherever the data lives; end on `RAW.shape`.
4. **Per-table overview (code)** — `report = skrub.TableReport(RAW,
   title=..., verbose=0)`; `report.write_html(EDA_DIR /
   "eda_<table>.html")`; then `summary = json.loads(report.json())`
   and end on a `dict`/`list` of per-column dtype / null / cardinality
   facts. One such cell per table.
5. **Target analysis (code, bare expression)** — pick the target's
   entry out of `summary["columns"]`; it carries value counts
   (classification) or a distribution summary (regression). Drives the
   metric default and whether the splitter should stratify.
6. **Structure signals (code, bare expression)** — datetime columns
   (from skrub's inferred dtypes, catches string dates) and high
   unique-ratio id/group columns. Drives the `G-CV-SPLITTER` choice
   (`TimeSeriesSplit` / `GroupKFold`).
7. **Associations (code, bare expression)** —
   `skrub.column_associations(RAW)` to flag strong predictors and
   possible leakage.
8. **End (markdown)** — reminder that the agent now authors
   `data/eda.md` + the JOURNAL section from this digest.

`write_html(...)` is load-bearing on the overview cells (the human
artifact). `verbose=0` and the bare `report.json()`-derived
expressions are load-bearing for a clean, library-agnostic digest.
For multi-table data, run cells 5–7 on the target-bearing table; for
very large data, load a row sample (see `references/cell_anatomy.md`).

## Execution contract — one command

```bash
pixi run -e agent python \
  .agents/skills/audit-ml-pipeline/scripts/run_cells.py \
  data/eda.py
```

The runner (shared with `audit-ml-pipeline`) streams the digest to
stdout — the agent reads it directly from the bash tool output. Pass
a second arg `scratch/eda/eda.md` to also write the digest to a file.
For non-pixi workspaces, swap the activation prefix per
`python-env-manager` § "Agent feature".

**This skill ships no runner of its own** — there is no
`explore-ml-data/scripts/`. Always invoke the shared
`audit-ml-pipeline/scripts/run_cells.py` at the path above; don't
look for or fork a local copy.

**Prerequisites for the run path:** the workspace package must be
importable (`from <pkg> import PROJECT_ROOT` — editable install done
during scaffold) and `skrub` installed (Tier 1). If either import
fails, the digest shows the `ImportError`; route to
`python-env-manager` for the missing piece rather than working around
it.

### Re-execution semantics

- A changed / added data source → overwrite `data/eda.py`, re-run,
  re-author `data/eda.md` + HTML, refresh the JOURNAL section.
- `scratch/eda/` is overwritten on every run. The durable record is
  `data/eda.py` + `data/eda.md` + git history.

## Authoring `data/eda.md`

After the run, read the digest and write `data/eda.md` from
`templates/eda.md`. It is prose, grounded in the digest — no invented
facts. Required sections:

- **Dataset at a glance** — tables, rows × columns, target.
- **Per-column findings** — dtypes, missingness, cardinality
  highlights, anything surprising.
- **Target** — balance / skew; class counts or distribution summary.
- **Structure** — datetime ordering, groups / ids (or "none found").
- **Associations** — strong feature↔target / feature↔feature links;
  flag possible leakage explicitly.
- **Modelling implications** — the payoff section. Translate findings
  into *candidate* picks the baseline note will weigh: e.g.
  "imbalanced target → `StratifiedKFold` + look at ROC-AUC / PR-AUC,
  not accuracy"; "`user_id` repeats across rows → consider
  `GroupKFold`"; "timestamp present → `TimeSeriesSplit` if forecasting".
  These are *implications*, not decisions — the gates own the picks.
- **Open questions** — domain ambiguities for the user to confirm.

Link each `data/eda_<table>.html` from the relevant section.

## JOURNAL § Data understanding (EDA)

`iterate-ml-experiment`'s `JOURNAL.md` carries a top-level
`## Data understanding (EDA)` section (placed right after `##
Status`). This skill owns its content:

```
## Data understanding (EDA)

- **Status:** done — <YYYY-MM-DD>   <!-- or: skipped — <YYYY-MM-DD> -->
- **Summary:** <2–4 lines: dataset shape, target balance/skew, the
  one or two findings that most shape the modelling choices>
- **Report:** [data/eda.md](../data/eda.md)
```

Keep it to a few lines — it is an index entry, not the report. The
detail lives in `data/eda.md`. On the **skip** path, only the
`Status: skipped` line is required.

## Dispatching in and out

### Called from

| Caller | When |
|---|---|
| `iterate-ml-experiment` § 0 bootstrap | Automatic; G-EDA fires **before** the baseline design note |
| User free-text | "explore the data", "do an EDA", "profile the dataset" — resolves directly |

### Calls into

| Callee | Why |
|---|---|
| `python-env-manager` § Agent feature | When `ipython` is missing on the run path — G-AGENT-FEATURE |
| `python-api` | Every skrub / pandas / polars symbol. Cache hits first |
| `data-science-python-stack` | G-TABULAR (pandas / polars) if not yet recorded; skrub `TableReport` reference |
| `python-code-style` | After writing `data/eda.py` — ruff format / check |

## What this skill does NOT do

- Design, select, or evaluate a model (`build-ml-pipeline` /
  `evaluate-ml-pipeline` / `iterate-ml-experiment`).
- Pick the CV splitter or metric — it only surfaces the *evidence*
  for those picks.
- Edit `src/<pkg>/` or the experiment / audit files.
- Clean, transform, or re-save the user's raw data.
- Install `ipython` / `pyright` (`python-env-manager` owns).
- Open or write the skore Project.
- Render commits or PRs.

## Companion skills

| Skill | Relationship |
|---|---|
| `iterate-ml-experiment` | Caller. § 0 fires G-EDA before the baseline note; the EDA findings seed the note's Method / Risks |
| `audit-ml-pipeline` | Owns the shared cell runner `scripts/run_cells.py` this skill executes; same bare-expression discipline |
| `organize-ml-workspace` | Workspace layout; `data/` is user-owned — this skill is the one exception that writes `data/eda.*` into it |
| `python-env-manager` | Agent feature install (G-AGENT-FEATURE). This skill requests; that skill installs |
| `python-api` | skrub / pandas / polars symbol lookups. Cache hits first |
| `data-science-python-stack` | G-TABULAR; skrub `TableReport` is catalogued there |
| `python-code-style` | ruff after writing `data/eda.py` |

## Templates and assets

- `templates/eda.py` — the `data/eda.py` skeleton. Copy + substitute;
  don't rewrite from memory.
- `templates/eda.md` — the `data/eda.md` report skeleton.

The cell runner is **not** owned here — it is
`audit-ml-pipeline/scripts/run_cells.py` (shared). Don't fork it.

## References (load on demand)

- `references/cell_anatomy.md` — concrete cell examples (right /
  wrong shapes), the `TableReport` repr trap, the full cell
  sequence, and how each finding maps to a downstream gate.
