<!--
Exploratory data analysis summary for this workspace, written from
the data/eda.py run. Ground every claim in what the run actually
showed — do not invent facts. Keep "Modelling implications" as
candidate suggestions to weigh when designing the model, not final
decisions.
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
to weigh when designing the model. Examples:>

- <imbalanced target (X% positive) → prefer `StratifiedKFold`; report
  ROC-AUC / PR-AUC rather than accuracy.>
- <`<id_col>` repeats across rows → consider `GroupKFold` on it to
  avoid leakage across folds.>
- <`<timestamp>` present and the task is forecasting → consider
  `TimeSeriesSplit`.>
- <high-cardinality categoricals (`<cols>`) → skrub's default
  encoders handle these; flag if any need text encoding.>
- <heavy target skew → consider a target transform; note it as a
  modelling risk.>

## Open questions

<domain ambiguities for the user to confirm before modelling: column
meanings, sentinel values, whether a column is a leak, the true target
definition, etc.>
