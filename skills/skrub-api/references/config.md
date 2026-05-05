# Configuration

Global skrub configuration. Settings affect things like default subsampling, table-report verbosity, and where datasets are cached.

### function `get_config`
```python
from skrub import get_config
```
**Signature:** `get_config()`

Return the current skrub configuration as a dict.

### function `set_config`
```python
from skrub import set_config
```
**Signature:** `set_config(use_table_report_data_ops=None, table_report_verbosity=None, max_plot_columns=None, max_association_columns=None, subsampling_seed=None, enable_subsampling=None, float_precision=None, cardinality_threshold=None, data_dir=None, eager_data_ops=None)`

Set global skrub configuration. Pass only the parameters you want to change; others are unaffected.

### function `config_context`
```python
from skrub import config_context
```
**Signature:** `config_context(*, use_table_report_data_ops=None, table_report_verbosity=None, max_plot_columns=None, max_association_columns=None, subsampling_seed=None, enable_subsampling=None, float_precision=None, cardinality_threshold=None, data_dir=None, eager_data_ops=None)`

Context manager for global skrub configuration — restores the previous values on exit.

```python
with config_context(enable_subsampling=False):
    learner.fit(env)
```

## Configurable settings (current set)

| name | purpose |
|---|---|
| `use_table_report_data_ops` | use `TableReport` to render previews of DataOps |
| `table_report_verbosity` | level of detail in `TableReport` |
| `max_plot_columns` | max number of columns plotted in `TableReport` |
| `max_association_columns` | max number of columns in the association heatmap |
| `subsampling_seed` | seed used by `.skb.subsample(...)` |
| `enable_subsampling` | globally enable/disable `.skb.subsample(...)` |
| `float_precision` | display precision for floats in `TableReport` |
| `cardinality_threshold` | default `cardinality_threshold` for `TableVectorizer` |
| `data_dir` | directory for cached datasets (see `skrub.datasets.get_data_dir`) |
| `eager_data_ops` | force eager evaluation of DataOps (for debugging) |
