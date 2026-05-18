# Common patterns — full catalogue

Recurring shapes of a complex pipeline expressed within the skrub
DataOps graph. SKILL.md has the one-line summaries; this file has
the worked patterns. Look up exact symbols in `python-api` — the
patterns tell you *which* shape applies, not the precise signature.

## 1. Heterogeneous columns (skrub answer to `ColumnTransformer`)

Use skrub column selectors with the `cols=` argument of `.skb.apply`
to apply a transformer to a column subset. One `.skb.apply(...)`
per group (numeric / string / categorical) instead of building a
`ColumnTransformer`.

```python
from skrub import selectors as s

X = X.skb.apply(StandardScaler(), cols=s.numeric())
X = X.skb.apply(OneHotEncoder(handle_unknown="ignore"), cols=s.categorical())
X = X.skb.apply(TextEncoder(), cols=s.string())
```

The DataOps graph composes these into a deterministic chain.
`ColumnTransformer` works too but loses the readable
top-to-bottom shape.

## 2. Default starting point for tabular data

Reach for `skrub.tabular_pipeline(...)` (or `TableVectorizer` +
estimator) **first**. Specialize column-by-column only when the
default is insufficient.

```python
import skrub
from sklearn.ensemble import RandomForestRegressor

predictions = X.skb.apply(skrub.tabular_pipeline(), y=y)
# or, with an explicit predictor:
X_vec = X.skb.apply(skrub.TableVectorizer())
predictions = X_vec.skb.apply(RandomForestRegressor(), y=y)
```

## 3. Multi-table inputs

Declare each input table as its own `skrub.var(...)`. Join with
skrub's `Joiner` / `AggJoiner` / `MultiAggJoiner` via
`.skb.apply(...)`. The graph holds the join plan deterministically
across train and test.

```python
orders = skrub.var("orders_path").skb.apply_func(load_orders)
products = skrub.var("products_path").skb.apply_func(load_products)
customers = skrub.var("customers_path").skb.apply_func(load_customers)

joined = orders.skb.apply(
    skrub.Joiner(products, on="product_id"),
)
joined = joined.skb.apply(
    skrub.AggJoiner(customers, on="customer_id", operations=["mean", "count"]),
)

X = joined.drop(["order_id", "label"]).skb.mark_as_X()
y = joined["label"].skb.mark_as_y()
```

## 4. Meta-estimator at the tail

`StackingClassifier`, `CalibratedClassifierCV`,
`TransformedTargetRegressor`, etc., are regular sklearn estimators
— wrap your predictor first, then attach the wrapped object with
`.skb.apply` as the final step.

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression

inner = LogisticRegression()
calibrated = CalibratedClassifierCV(inner, method="isotonic", cv=5)

predictions = X.skb.apply(calibrated, y=y)
```

## 5. Mark hyperparameter knobs in place

Wrap values you want the tuning skill to search over with
`skrub.choose_from` / `choose_int` / `choose_float` / `optional`
directly inside the declaration. **Don't import `GridSearchCV`
here** — the tuning skill owns search; this skill only exposes the
knobs.

```python
from sklearn.ensemble import RandomForestRegressor

predictor = RandomForestRegressor(
    n_estimators=skrub.choose_int(50, 500, name="n_estimators"),
    max_depth=skrub.choose_from([None, 5, 10, 20], name="max_depth"),
    min_samples_leaf=skrub.choose_int(1, 10, name="min_samples_leaf"),
)
predictions = X.skb.apply(predictor, y=y)
```

The tuning skill discovers the knobs by walking the graph.

## 6. Custom sklearn transformer

Author one **only when** (a) no built-in fits and (b) the
operation is stateful. Subclass `BaseEstimator` + `TransformerMixin`,
implement `fit(self, X, y=None)` to learn state and `transform(self, X)`
to apply it; add `get_feature_names_out` if downstream consumers
need feature names.

For a stateless op, write a function and use `.skb.apply_func` —
don't author a transformer.

```python
from sklearn.base import BaseEstimator, TransformerMixin

class QuantileRankEncoder(BaseEstimator, TransformerMixin):
    """Encode numeric columns by their training-set quantile rank."""

    def __init__(self, n_bins: int = 100):
        self.n_bins = n_bins

    def fit(self, X, y=None):
        self.quantiles_ = {
            col: np.quantile(X[col], np.linspace(0, 1, self.n_bins + 1))
            for col in X.columns
        }
        return self

    def transform(self, X):
        X = X.copy()
        for col, q in self.quantiles_.items():
            X[col] = np.searchsorted(q, X[col]) / self.n_bins
        return X

    def get_feature_names_out(self, input_features=None):
        return np.asarray(input_features)
```

Attach via `.skb.apply(QuantileRankEncoder(), cols=s.numeric())`.

## When the pattern you need isn't here

Drop a `scratch/<ts>_<short>.py` probe to explore the skrub
surface (`dir(skrub)`, `dir(some_node.skb)`), or WebFetch the skrub
narrative docs for the installed version via `python-api` Shape 3.
Cache new findings to `scratch/api/skrub/<version>/<topic>.md`.
