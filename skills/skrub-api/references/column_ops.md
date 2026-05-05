# Column-level selection & wrapping

Top-level transformers for selecting/dropping columns and for applying a transformer to a subset of columns. For composing complex column predicates, see `references/selectors.md`.

### class `SelectCols`
```python
from skrub import SelectCols
```
**Signature:** `SelectCols(cols)`

Select a subset of a DataFrame's columns. `cols` is a column name, list of names, or a `skrub.selectors` selector.

### class `DropCols`
```python
from skrub import DropCols
```
**Signature:** `DropCols(cols)`

Drop a subset of a DataFrame's columns.

### class `Drop`
```python
from skrub import Drop
```
**Signature:** `Drop()`

Single-column transformer that drops the column it is applied to. Mostly useful when wrapped with `ApplyToCols(...)` or with a selector inside `TableVectorizer.specific_transformers`.

### class `ApplyToCols`
```python
from skrub import ApplyToCols
```
**Signature:** `ApplyToCols(transformer, cols=all(), *, allow_reject=False, keep_original=False, rename_columns='{}', n_jobs=None)`

Apply a transformer to selected columns in a dataframe. The default `cols=all()` comes from `skrub.selectors.all()`.

- `allow_reject=True` — silently skip columns where `transformer` raises `RejectColumn`.
- `keep_original=True` — keep the original columns alongside the transformed output.
- `rename_columns` — Python format string applied to each output column name (e.g. `"{}_scaled"`).

Use this to lift a single-column transformer (one that operates on a `pd.Series`/polars Series) into a dataframe-level transformer.
