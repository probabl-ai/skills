# JOURNAL

<!--
This file is the durable index of every experiment in this workspace.
Three sections, in order: Status, History, Backlog. Don't add new
top-level sections; they break the contract that lets future sessions
read this file in two seconds.

Owner: `iterate-ml-experiment` skill. Pair each `journal/NN_short_name.md`
with `experiments/NN_short_name.py` (identical stems).
-->

## Status

- **Project / dataset:** <fill in — e.g., `adult-census` classification>
- **Goal:** <one sentence — what would "done" look like for this project?>
- **Last experiment:** <NN_name> — <status: planned | approved | running | done | abandoned>
- **Last result:** <one-line headline metric, or "n/a" if not yet run>

<!--
Workspace decisions: persistent picks for the config gates that fire in
bootstrap (see `iterate-ml-experiment` § 0 "Bootstrap skips sourcing
menu — NOT the config gates"). Each row records a one-time pick the
user made via `AskUserQuestion`; on every later session, skills read
this block first and skip the matching question.

Immutability rule: rows are immutable unless the user explicitly pivots
("let's switch to polars", "move env to uv"). Do NOT silently update
a row because a newer tool would obviously fit better; surface the
proposal and wait for the user. The `recorded:` date is the date the
row was last user-confirmed.

Adding rows: when a new competing-library job comes into scope
mid-project (e.g. DL is added), the matching skill fires its
`AskUserQuestion`, then this block gets a new row.

Owning skills:
  - tabular library     → data-science-python-stack § Tier 2
  - env manager         → python-env-manager
  - agent feature       → python-env-manager § "Agent feature"
  - optional features   → python-env-manager § "Where does the package belong?"
  - package name        → organize-ml-workspace
  - CV splitter family  → evaluate-ml-pipeline

The 3-feature env layout (default / dev / agent) is enforced by
python-env-manager; no row is collected for it. The `agent feature`
row only records whether the user opted into the agent feature
install (ipython + pyright + pyrightconfig.json) or skipped it.
-->

- **Workspace decisions** (immutable unless the user pivots):
  - tabular library: <pandas | polars> — recorded: <YYYY-MM-DD>
  - env manager: <pixi | uv | poetry | hatch | conda | pip+venv> — recorded: <YYYY-MM-DD>
  - agent feature: <installed | skipped> — recorded: <YYYY-MM-DD>
  - optional features: <name1, name2 | none> — recorded: <YYYY-MM-DD>
  - package name (`src/<pkg>/`): <pkg> — recorded: <YYYY-MM-DD>
  - skore mode: <local | hub> — recorded: <YYYY-MM-DD>
  - skore hub workspace: <hub-workspace-name | n/a> — recorded: <YYYY-MM-DD>
  - CV splitter family: <KFold | StratifiedKFold | GroupKFold | TimeSeriesSplit | other> — recorded: <YYYY-MM-DD>

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
Indexed table of ideas not yet committed to a `journal/NN_*.md` file.
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

When an item graduates into a design note, remove the row from this
table and add the new experiment to History above.
-->

| # | Item | Source |
|---|---|---|
| <!-- B1 --> | <!-- "investigate target-bin>0.95 residual bias via target transform" --> | <!-- `skore:01_baseline` --> |
| <!-- B2 --> | <!-- "audit hourly-vs-15min data resolution split — likely fix for fold variance" --> | <!-- `my-pick:02_calendar_features` --> |
