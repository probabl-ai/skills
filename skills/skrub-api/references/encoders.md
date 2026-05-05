# Single-column encoders & cleaners

These are sklearn-compatible transformers that operate on individual columns. Most subclass `skrub.core.SingleColumnTransformer` and may *reject* a column at fit time (raising `RejectColumn`) when their input dtype is unsuitable. Wrap them with `ApplyToCols` (see `column_ops.md`) or let `TableVectorizer` apply them automatically.

## Datetime

### class `DatetimeEncoder`
```python
from skrub import DatetimeEncoder
```
**Signature:** `DatetimeEncoder(resolution='hour', add_weekday=False, add_total_seconds=True, add_day_of_year=False, periodic_encoding=None)`

Extract temporal features such as month, day of the week, … from a datetime column.

### class `ToDatetime`
```python
from skrub import ToDatetime
```
**Signature:** `ToDatetime(format=None)`

Parse datetimes represented as strings and return `Datetime` columns.

## High-cardinality string encoders

### class `GapEncoder`
```python
from skrub import GapEncoder
```
**Signature:** `GapEncoder(n_components=10, batch_size=1024, gamma_shape_prior=1.1, gamma_scale_prior=1.0, rho=0.95, rescale_rho=False, hashing=False, hashing_n_features=4096, init='k-means++', max_iter=5, ngram_range=(2, 4), analyzer='char', add_words=False, random_state=None, rescale_W=True, max_iter_e_step=1, max_no_improvement=5, verbose=0)`

Encode string columns by constructing latent topics.

### class `MinHashEncoder`
```python
from skrub import MinHashEncoder
```
**Signature:** `MinHashEncoder(*, n_components=30, ngram_range=(2, 4), hashing='fast', minmax_hash=False, n_jobs=None)`

Encode string categorical features by applying the MinHash method to n-gram decompositions of strings.

### class `SimilarityEncoder`
```python
from skrub import SimilarityEncoder
```
**Signature:** `SimilarityEncoder(*, ngram_range=(2, 4), analyzer='char', categories='auto', dtype=numpy.float64, handle_unknown='ignore', handle_missing='', hashing_dim=None, n_jobs=None)`

Encode string categories to a similarity matrix, to capture fuzziness across a few categories.

### class `StringEncoder`
```python
from skrub import StringEncoder
```
**Signature:** `StringEncoder(n_components=30, vectorizer='tfidf', ngram_range=(3, 4), analyzer='char_wb', stop_words=None, random_state=None, vocabulary=None)`

Generate a lightweight string encoding of a given column using tf-idf vectorization and truncated singular value decomposition (SVD).

### class `TextEncoder`
```python
from skrub import TextEncoder
```
**Signature:** `TextEncoder(model_name='intfloat/e5-small-v2', n_components=30, device=None, batch_size=32, token_env_variable=None, cache_folder=None, store_weights_in_pickle=False, random_state=None, verbose=False)`

Encode string features by applying a pretrained language model downloaded from the HuggingFace Hub.

## Type casters

### class `ToCategorical`
```python
from skrub import ToCategorical
```
**Signature:** `ToCategorical()`

Convert a string column to Categorical dtype.

### class `ToFloat`
```python
from skrub import ToFloat
```
**Signature:** `ToFloat()`

Convert a column to 32-bit floating-point numbers.

## Numeric scaling

### class `SquashingScaler`
```python
from skrub import SquashingScaler
```
**Signature:** `SquashingScaler(max_absolute_value=3.0, quantile_range=(25.0, 75.0))`

Perform robust centering and scaling followed by soft clipping.

## Column dropping

### class `DropUninformative`
```python
from skrub import DropUninformative
```
**Signature:** `DropUninformative(drop_if_constant=False, drop_if_unique=False, drop_null_fraction=1.0)`

Drop column if it is found to be uninformative according to various criteria.
