# Whole-table vectorizers & pipelines

Estimators that operate on a full dataframe and dispatch per-column transformers automatically, plus the `tabular_pipeline` shortcut.

### class `TableVectorizer`
```python
from skrub import TableVectorizer
```
**Signature:** `TableVectorizer(*, cardinality_threshold=40, low_cardinality=<OneHotEncoder>, high_cardinality=<StringEncoder>, numeric=<passthrough>, datetime=<DatetimeEncoder>, specific_transformers=(), n_jobs=None)`

Transform a dataframe to a numerical (vectorized) representation. Routes each column to a per-dtype encoder based on inferred type and cardinality. Output column types:
- `numeric` — numeric columns (default: passthrough)
- `datetime` — datetime columns (default: `DatetimeEncoder`)
- `low_cardinality` — string/categorical columns with cardinality `< cardinality_threshold` (default: `OneHotEncoder`)
- `high_cardinality` — string/categorical columns above the threshold (default: `StringEncoder`)
- `specific_transformers` — `[(transformer, columns), ...]` overrides for named columns.

### class `Cleaner`
```python
from skrub import Cleaner
```
**Signature:** `Cleaner(drop_null_fraction=1.0, drop_if_constant=False, drop_if_unique=False, datetime_format=None, null_strings=None, numeric_dtype=None, cast_to_str=False, n_jobs=1)`

Column-wise consistency checks and sanitization of dtypes, null values and dates. Use as a preprocessing step before training; does **not** vectorize.

### function `tabular_pipeline`
```python
from skrub import tabular_pipeline
```
**Signature:** `tabular_pipeline(estimator, *, n_jobs=None)`

Build a simple machine-learning pipeline for tabular data: a `TableVectorizer` (with sensible defaults per task type) followed by `estimator`. Pass an estimator instance, or one of the strings `"regressor"` / `"regression"` / `"classifier"` / `"classification"` to get a default `HistGradientBoosting*` model.
