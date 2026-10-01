# JOURNAL

## Status

| Variable | Value |
|---|---|
| Project / dataset | <fill in — e.g., `adult-census` classification> |
| Goal | <one sentence — what would "done" look like for this project?> |
| Last experiment | <NN_name> — <status: planned \| approved \| running \| done \| abandoned> |
| Last result | <one-line headline metric, or "n/a" if not yet run> |

## Data understanding

| Variable | Value |
|---|---|
| Status | <done \| skipped> — <YYYY-MM-DD> |
| Summary | <2–4 lines — dataset shape, target balance/skew, and the one or two findings that most shape the modelling choices. "n/a" until the data has been explored.> |
| Report | [data_analysis/data_analysis.md](../data_analysis/data_analysis.md) |

## Modeling decisions

| Variable | Value |
|---|---|
| Status | <missing \| draft \| locked> |
| Revised on | <date or n/a> |
| Prediction goal | <probabilities \| point_labels \| intervals \| point_predictions> |
| Deployment | <iid \| time \| groups> |
| Horizon | <n/a, or one or more number-and-unit values> |
| Gap | <n/a or number and unit> |
| Generalize to | <n/a or column> |
| Known at predict | <n/a or columns> |
| Time role | <n/a \| sort_key \| covariate> |
| Metric role | <imposed \| proper_score \| ranking \| thresholded \| point_error> |
| Metric | <comparison name> |
| Baseline | <one of seasonal_naive, group_mean, logistic, production, dummy> |
| Baseline note | <one short phrase> |
| Folds | <integer, at least 1> |

## History

| Stem | Intent (one line) | Status | Headline result | Report | Design note |
|---|---|---|---|---|---|

## Backlog

| # | Item | Source |
|---|---|---|
