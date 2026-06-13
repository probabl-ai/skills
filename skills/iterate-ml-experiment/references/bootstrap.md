# Bootstrap — full procedure

The first session in an ML workspace. SKILL.md § 0 has the compact
version; this file has the full procedure with examples.

A workspace is in bootstrap mode when one of:

- `journal/JOURNAL.md` is missing.
- `journal/JOURNAL.md` is the one-line placeholder dropped by
  `organize-ml-workspace`.
- `journal/JOURNAL.md` exists but has no rows in History.

In bootstrap, the session-start ritual does **not** apply (no last
experiment to summarize, no backlog). Instead:

## Step 1 — Scaffold first if needed

If the workspace itself isn't in place (no `src/`, no `experiments/`,
no `journal/`), hand off to `organize-ml-workspace`. Come back here
when its placeholder `JOURNAL.md` exists.

## Step 2 — Rewrite `JOURNAL.md` from this skill's template

Read `templates/JOURNAL.md` and write it to `journal/JOURNAL.md`,
replacing the placeholder. **This skill — not
`organize-ml-workspace` — owns design-note content.**

## Step 3 — Derive a goal default from `data/README.md`

Read `data/README.md` (or whatever dataset card / problem statement
sits at the project root) **before** asking the user. Synthesize
one sentence of the form:

> "minimize `<metric>` on `<split>` for `<task description>`"

Propose it; the user confirms or amends. **Do not prompt with a
blank.** If no README / dataset card exists, then ask — but make
that the exception, not the default.

## Step 3.5 — Explore the data before designing the model (G-EDA)

Before drafting the baseline, dispatch to `explore-ml-data`. This is
the **G-EDA** gate — binary **run** / **skip**:

- **run** → the skill places and executes `data/eda.py` via the
  shared cell runner, writes `data/eda.md` (findings + modelling
  implications) and `data/eda_<table>.html`, and fills the
  `## Data understanding (EDA)` section of `JOURNAL.md`. Requires the
  agent feature (`ipython`); if missing, `explore-ml-data` routes to
  `python-env-manager` § Agent feature (`G-AGENT-FEATURE`) — so on the
  run path the agent feature can get installed here, at bootstrap,
  before the baseline. The raw data may live outside `data/`; reuse
  the location already found when deriving the goal in Step 3 rather
  than re-discovering it.
- **skip** → only the `## Data understanding (EDA)` section's
  `Status: skipped — <date>` line is written; proceed to the baseline.
  If the user picks **run** but then **declines** the agent-feature
  install, fall back to this skip path (record `Status: skipped`) —
  do not loop between run and install.

Why before the baseline: the dataset facts EDA surfaces (target
balance / skew, datetime / group structure, missingness,
cardinality, leakage flags) are exactly what justifies the learner
and metric defaults in Step 4 and informs the CV strategy chosen
later at the evaluation step. Designing first and exploring later
defeats the purpose and is the named anti-pattern.

Free-text "go fast" / "quick baseline" does NOT resolve G-EDA — fire
the `AskUserQuestion` (run / skip).

## Step 4 — Auto-draft `journal/01_baseline.md` via the consultation chain

The baseline is forced, not invented — but its defaults come from
sibling skills, not from memory (and from the Step 3.5 EDA findings
when EDA ran):

- **Learner default**: consult `build-ml-pipeline` for what a
  "baseline" means for the data shape (tabular regression /
  classification → `skrub.tabular_pipeline`; other shapes have
  their own defaults).
- **Cross-validation strategy**: NOT fixed in the design note. The
  splitter is data-driven and chosen at the evaluation step
  (`G-CV-SPLITTER`, owned by `evaluate-ml-pipeline`) once the
  pipeline's X-marker / `split_kwargs` exist — so the design note only
  records that the CV strategy is decided then, it does not commit a
  specific splitter. (EDA's structure signals still *inform* that
  later choice; they don't pre-empt it.)
- **Metric default**: consult `python-api` for what
  `skore.evaluate` reports by default for the task type.

### Mismatch handling

If a default conflicts with the project goal — e.g., the README
requires Squared Error but skore's default is RMSE — **flag it in the
Risks section** of `01_baseline.md`. Don't silently override the
default; surface the tension to the user. Splitter concerns (group /
temporal structure, fold cost) are surfaced and resolved at the
evaluation step, not pre-committed here.

## Step 5 — The user's role: approve or amend, not invent

Skip the strategy dispatch entirely for the baseline. The user
reads the auto-drafted design note and either approves or asks
for amendments.

## Step 6 — Exit bootstrap

Once `01_baseline.md` is approved and recorded in `JOURNAL.md`
History, the workspace exits bootstrap. Every session afterwards
uses § 1 of `SKILL.md` (Session start, iterate mode).

---

## Bootstrap skips the sourcing menu — NOT the config gates

The most common bootstrap failure shape is the agent treating
"bootstrap = forced baseline" as "bootstrap = silent everything".
**Wrong.** Bootstrap forbids the sourcing menu only; every other
gate the workflow normally fires still fires.

### Skipped in bootstrap (by design)

- Sourcing menu (`skore` / `user` / `my-pick` / `B<N>`) — no prior
  report, no backlog, no history.
- "Resume / record outcome / propose next" pick from § 1 — no last
  experiment, three branches ill-defined.

### MUST still fire in bootstrap — config gates

| Gate ID | Picks | Owning skill | When it fires |
|---------|-------|--------------|---------------|
| `G-PKG-NAME` | `src/<pkg>/` import name | `organize-ml-workspace` | **Before** any `pyproject.toml` / `pixi.toml` creation |
| `G-ENV-MGR` | Python env manager (`pixi`, `uv`, `poetry`, `hatch`, `conda`, `pip+venv`). The 3-feature layout (`default` / `dev` / `agent`) is enforced automatically — no scope sub-pick. | `python-env-manager` | **Before** any `pixi init` / `pixi add` / equivalent |
| `G-TABULAR` | Tabular library (`pandas` / `polars`) + other Tier 2 contested-library picks | `data-science-python-stack` | **Before** any `Write` of `data.py` / experiment script importing the contested library |
| `G-SKORE-MODE` | Skore Project mode (`local` / `hub` / `mlflow`) + hub workspace name or MLflow tracking URI | `organize-ml-workspace` | **Before** any `pyproject.toml` write / the skore install variant |
| `G-EDA` | Explore the data (run / skip) | `explore-ml-data` | **Before** the `journal/01_baseline.md` draft — so EDA findings can inform the learner / metric defaults and the later CV-strategy choice |
| `G-AGENT-FEATURE` | Install `ipython` + `pyright` (install / skip) | `python-env-manager` | **Conditional** — fires when G-EDA = run and the agent feature isn't present (the EDA cell runner needs `ipython`). Otherwise deferred to the first audit at § 4. Decline → EDA falls back to skip |
| `G-DESIGN` | Explicit user approval of `journal/01_baseline.md` | `iterate-ml-experiment` § 3 | **Before** any `Write` of `experiments/01_baseline.py` / `src/<pkg>/*.py` content authored from the design note |
| `G-CV-SPLITTER` | Cross-validator family for `skore.evaluate` (`KFold`, `GroupKFold`, `TimeSeriesSplit`, ...) | `evaluate-ml-pipeline` | **Inside the § 3 chain, AFTER G-DESIGN** — at the evaluate step, before any `Write` of `src/<pkg>/evaluate.py`; mandatory even when `split_kwargs` is empty (the empty case is itself a justified pick). NOT an upfront config gate |
| `G-RUN` | "Run now" vs "leave for later" once smoke tests pass | `iterate-ml-experiment` § 3 | **Before** the shell call that executes `experiments/01_baseline.py` |

Each gate's owning skill is responsible for the actual
`AskUserQuestion` mechanics; this table is the **bootstrap
contract** that says they all still fire even though the sourcing
menu doesn't. The persistent gates (`G-PKG-NAME`, `G-ENV-MGR`,
`G-TABULAR`, `G-SKORE-MODE`, and the post-build `G-CV-SPLITTER`) are
recorded in `JOURNAL.md` Status `Workspace decisions` so a later
session reads the decision instead of re-asking; `G-EDA` is recorded
in the `Data understanding (EDA)` section. `G-DESIGN`, `G-RUN`, and
`G-AGENT-FEATURE` are not `Workspace decisions` rows — `G-DESIGN` /
`G-RUN` are per-experiment, and the agent-feature status has its own
row owned by `python-env-manager`.

### Free-text doesn't resolve config gates

A user message resolves a config gate **only if it names one of
the gate's options**. "Quick baseline" / "go fast" / "you pick" /
"whatever is standard" do NOT resolve any of the gates above;
they fall through to the structured `AskUserQuestion`.
