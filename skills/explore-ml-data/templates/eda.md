<!--
data/eda.md — persisted EDA narrative for this workspace.

Owner: `explore-ml-data`. Authored from the `data/eda.py` run digest;
every claim must be grounded in that digest — do not invent facts.
The `journal/JOURNAL.md` § "Data understanding (EDA)" section links
here; the baseline design note cites the "Modelling implications".

Keep "implications" as *candidate* picks, not decisions — the picks
are owned by their gates (G-CV-SPLITTER, the metric default, the
learner default in the baseline note).
-->

# EDA — <project / dataset name>

_Generated from `data/eda.py` on <YYYY-MM-DD>._

## Dataset at a glance

- **Tables:** <names / count>
- **Shape:** <rows> × <cols> (per table if several)
- **Target:** <column name + task: binary / multiclass / regression | none>
- **Rich reports:** [eda_<table>.html](eda_<table>.html)

## Per-column findings

<dtypes, missingness, cardinality highlights; call out anything
surprising — constant columns, near-duplicate columns, suspicious
sentinel values, unexpected dtypes.>

## Target

<class balance (counts + proportions) for classification, or
distribution summary + skew for regression. State imbalance / skew
explicitly.>

## Structure

<datetime ordering present? group / id-like columns (with the
unique-ratio evidence)? Or "no temporal or group structure found".>

## Associations

<strongest feature↔target links (candidate predictors) and notable
feature↔feature links. **Flag any implausibly perfect association as
a possible leakage risk** and name the column.>

## Modelling implications

<the payoff: translate the findings into candidate modelling choices
the baseline note will weigh. Examples:>

- <imbalanced target (X% positive) → prefer `StratifiedKFold`; report
  ROC-AUC / PR-AUC rather than accuracy.>
- <`<id_col>` repeats across rows → consider `GroupKFold` on it to
  avoid leakage across folds.>
- <`<timestamp>` present and the task is forecasting → consider
  `TimeSeriesSplit`.>
- <high-cardinality categoricals (`<cols>`) → skrub's default
  encoders handle these; flag if any need text encoding.>
- <heavy target skew → consider a target transform; flag in the
  baseline note's Risks.>

## Open questions

<domain ambiguities for the user to confirm before / during the
baseline: column meanings, sentinel values, whether a column is a
leak, the true target definition, etc.>
