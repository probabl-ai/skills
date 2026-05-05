# Reporting

Tools for inspecting dataframes interactively in notebooks.

### class `TableReport`
```python
from skrub import TableReport
```
**Signature:** `TableReport(dataframe, n_rows=10, order_by=None, title=None, column_filters=None, verbose=None, max_plot_columns=None, max_association_columns=None, open_tab='table')`

Summarize the contents of a dataframe: per-column statistics, distributions, association heatmap, and a table view. Renders as HTML in Jupyter. `column_filters` accepts custom predicates (see the user guide for the format).

### function `patch_display`
```python
from skrub import patch_display
```
**Signature:** `patch_display(pandas=True, polars=True, verbose=1, max_plot_columns=30, max_association_columns=30)`

Replace the default pandas/polars HTML display with a `TableReport`. Affects all subsequent dataframe displays in the current Python process.

### function `unpatch_display`
```python
from skrub import unpatch_display
```
**Signature:** `unpatch_display(pandas=True, polars=True)`

Undo the effect of `patch_display()`.

### function `column_associations`
```python
from skrub import column_associations
```
**Signature:** `column_associations(df)`

Get measures of statistical association between all pairs of columns. Returns a dataframe of pairwise scores (Cramér's V for categoricals, etc.).
