# PLAN

<!--
This file is the durable index of every experiment in this workspace.
Three sections, in order: Status, History, Backlog. Don't add new
top-level sections; they break the contract that lets future sessions
read this file in two seconds.

Owner: `iterate-ml-experiment` skill. Pair each `plan/NN_short_name.md`
with `experiments/NN_short_name.py` (identical stems).
-->

## Status

- **Project / dataset:** <fill in — e.g., `adult-census` classification>
- **Goal:** <one sentence — what would "done" look like for this project?>
- **Last experiment:** <NN_name> — <status: planned | approved | running | done | abandoned>
- **Last result:** <one-line headline metric, or "n/a" if not yet run>

## History

<!--
One row per experiment, in chronological order. Newest at the bottom.
Status values: planned | approved | running | done | abandoned.
-->

| Stem | Intent (one line) | Status | Headline result | Plan file |
|---|---|---|---|---|
| <!-- e.g. `01_baseline` --> | <!-- "tabular_learner on raw features" --> | <!-- done --> | <!-- "ROC-AUC 0.86 ± 0.01" --> | <!-- [plan](01_baseline.md) --> |

## Backlog

<!--
Indexed table of ideas not yet committed to a `plan/NN_*.md` file.
Each row carries a stable `B<N>` index so the user can pick by
number when picking the next experiment ("go with B2"). The skill
surfaces this table to the user every time it presents the
sourcing menu.

Columns:
  - `#`      — stable index (B1, B2, ...). Don't renumber on
               removal; new rows take the next free B<N>.
  - `Item`   — one-line description of the idea.
  - `Source` — where the idea came from. Use one of:
                 `skore:<stem>`    — written by `iterate-from-skore`
                                     from the report of `<stem>`
                 `my-pick:<stem>`  — agent-synthesized; <stem> is
                                     the experiment whose context
                                     (Implication, Risks, …) fed
                                     the synthesis. Written by § 4
                                     when implications seed future
                                     leads, or by § 2's my-pick
                                     branch when unpicked
                                     candidates are saved
                 `user`            — the user added the row
                                     directly (in conversation)

When an item graduates into a plan file, remove the row from this
table and add the new experiment to History above.
-->

| # | Item | Source |
|---|---|---|
| <!-- B1 --> | <!-- "investigate target-bin>0.95 residual bias via target transform" --> | <!-- `skore:01_baseline` --> |
| <!-- B2 --> | <!-- "audit hourly-vs-15min data resolution split — likely fix for fold variance" --> | <!-- `my-pick:02_calendar_features` --> |
