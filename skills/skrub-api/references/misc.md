# Miscellaneous top-level utilities

Eager helper functions that don't fit into the encoder/joiner/vectorizer buckets.

### function `to_datetime`
```python
from skrub import to_datetime
```
**Signature:** `to_datetime(data, format=None)`

Convert a DataFrame or column to Datetime dtype. The estimator equivalent is `ToDatetime` (see `references/encoders.md`).

### function `deduplicate`
```python
from skrub import deduplicate
```
**Signature:** `deduplicate(X, *, n_clusters=None, ngram_range=(2, 4), analyzer='char_wb', linkage_method='average', n_jobs=None)`

Deduplicate categorical data by hierarchically clustering similar strings. Returns a mapping from each input value to a canonical cluster representative.
