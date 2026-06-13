# JOURNAL

<!--
Durable index of every experiment in this workspace. Four sections,
in order: Status, Data understanding (EDA), History, Backlog — keep
them so the file stays quick to scan. Each journal/NN_short_name.md
design note pairs one-to-one with experiments/NN_short_name.py (same
stem).
-->

## Status

- **Project / dataset:** <fill in — e.g., `adult-census` classification>
- **Goal:** <one sentence — what would "done" look like for this project?>
- **Last experiment:** <NN_name> — <status: planned | approved | running | done | abandoned>
- **Last result:** <one-line headline metric, or "n/a" if not yet run>

<!--
Workspace decisions: one-time project-setup choices. Record each when
it is made and treat it as fixed unless you deliberately change one
(e.g. switch pandas → polars), updating the recorded date. Reading
this block on later sessions avoids re-deciding what's already settled.
-->

- **Workspace decisions** (immutable unless the user pivots):
  - tabular library: <pandas | polars> — recorded: <YYYY-MM-DD>
  - env manager: <pixi | uv | poetry | hatch | conda | pip+venv> — recorded: <YYYY-MM-DD>
  - agent feature: <installed | skipped> — recorded: <YYYY-MM-DD>
  - optional features: <name1, name2 | none> — recorded: <YYYY-MM-DD>
  - package name (`src/<pkg>/`): <pkg> — recorded: <YYYY-MM-DD>
  - skore mode: <local | hub | mlflow> — recorded: <YYYY-MM-DD>
  - skore hub workspace: <hub-workspace-name | n/a> — recorded: <YYYY-MM-DD>
  - skore mlflow tracking uri: <mlflow-tracking-uri | n/a> — recorded: <YYYY-MM-DD>
  - CV splitter family: <KFold | StratifiedKFold | GroupKFold | TimeSeriesSplit | other> — recorded: <YYYY-MM-DD>

## Data understanding (EDA)

<!--
Short index entry — the full analysis lives in data/eda.md. If the
data exploration was skipped, keep just the Status: skipped line.
-->

- **Status:** <done | skipped> — <YYYY-MM-DD>
- **Summary:** <2–4 lines — dataset shape, target balance/skew, and the
  one or two findings that most shape the modelling choices. "n/a"
  until the data has been explored.>
- **Report:** [data/eda.md](../data/eda.md)

## History

<!--
One row per experiment, in chronological order. Newest at the bottom.
Status values: planned | approved | running | done | abandoned.
-->

| Stem | Intent (one line) | Status | Headline result | Design note |
|---|---|---|---|---|
| <!-- e.g. `01_baseline` --> | <!-- "tabular_pipeline on raw features" --> | <!-- done --> | <!-- "ROC-AUC 0.86 ± 0.01" --> | <!-- [design note](01_baseline.md) --> |

## Backlog

<!--
Ideas not yet committed to a journal/NN_*.md design note. Each row
has a stable B<N> index so it can be picked by number ("go with B2").

Columns:
  - #      — stable index (B1, B2, ...); don't renumber on removal.
  - Item   — one-line description of the idea.
  - Source — where it came from, e.g. a finding from a prior
             experiment's report (`skore:<stem>`), a synthesized idea
             (`my-pick:<stem>`), or a user request (`user`).

When an item becomes a design note, remove its row here and add the
experiment to History above.
-->

| # | Item | Source |
|---|---|---|
| <!-- B1 --> | <!-- "investigate target-bin>0.95 residual bias via target transform" --> | <!-- `skore:01_baseline` --> |
| <!-- B2 --> | <!-- "audit hourly-vs-15min data resolution split — likely fix for fold variance" --> | <!-- `my-pick:02_calendar_features` --> |
