# `skrub.core`

Base classes and exceptions for extending skrub. Most users never import from here directly — use it when *writing* a custom transformer that integrates with `TableVectorizer` / `ApplyToCols`.

```python
from skrub import core
```

### class `SingleColumnTransformer`
**Signature:** `SingleColumnTransformer()`

Base class for single-column transformers. Subclasses implement `fit_transform(column, y=None)` and `transform(column)` (operating on a single pandas/polars Series, not a DataFrame). Subclasses may raise `RejectColumn` from `fit` to signal the transformer doesn't apply to a given column — when wrapped with `ApplyToCols(allow_reject=True)` or used inside `TableVectorizer`, the column is then passed through or routed elsewhere.

### exception `RejectColumn`
**Signature:** `RejectColumn(...)` (inherits from `ValueError`)

Used by single-column transformers to indicate they do not apply to a column. Catch / raise this rather than a plain `ValueError` so the rest of skrub's plumbing can recognize the rejection.

```python
from skrub.core import SingleColumnTransformer, RejectColumn

class MyEncoder(SingleColumnTransformer):
    def fit_transform(self, column, y=None):
        if column.dtype.kind not in "if":
            raise RejectColumn(f"{column.name!r} is not numeric")
        ...
        return transformed
```
