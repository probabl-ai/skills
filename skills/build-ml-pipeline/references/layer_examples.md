# Layer examples — worked code

Three worked examples for rule 2's "mark X early, featurize after"
shape. `SKILL.md` has the three-layer rule + decision criterion in
prose; this file has the code you copy / adapt from.

## IID flat-table — marker on the loaded source frame

When no feature step looks across rows, Layer 2 collapses to "load
the data, mark it as X/y, done". The early-mark rule reduces to
"split columns into X and y on the source frame, then chain
features after".

```python
def build_learner(data_dir_preview: str | Path | None = None):
    data_dir = (
        skrub.var("data_dir", value=str(data_dir_preview))
        if data_dir_preview is not None
        else skrub.var("data_dir")
    )
    data = data_dir.skb.apply_func(load_parquet)

    X = data.drop(["id", "target"], axis=1).skb.mark_as_X()
    y = data["target"].skb.mark_as_y()

    X = X.skb.apply_func(feature_engineering_step)
    predictions = X.skb.apply(predictor, y=y)
    return predictions.skb.make_learner()
```

The experiment script supplies an absolute path, anchored on
`PROJECT_ROOT`:

```python
from <pkg> import PROJECT_ROOT
DATA_DIR = PROJECT_ROOT / "data"

learner = build_learner(data_dir_preview=DATA_DIR)
report = skore.evaluate(
    learner, data={"data_dir": str(DATA_DIR)}, splitter=splitter,
)
```

## Counter-example — loader-baked target shift (Don't)

The rationalization the "Layer 1 doesn't know the question" Stop
condition blocks. The target shift in the loader assumes the
framing *"we want to predict load HORIZON hours ahead"*; an
external consumer of the source would derive the raw hourly
series, not this output. The horizon belongs to **Layer 2**, never
Layer 1.

```python
# Don't.
def load_supervised_frame(data_dir):
    raw = read_csvs(data_dir)
    # ↓ target shift — relates rows; requires knowing the horizon
    shifted = raw.with_columns(load.shift(-HORIZON).alias("y"))
    # ↓ drop_nulls on a shifted column — filter by cross-row result
    return shifted.drop_nulls("y")

data = data_dir.skb.apply_func(load_supervised_frame)
X = data.drop("y").skb.mark_as_X()   # marker is "early" only on paper
y = data["y"].skb.mark_as_y()
```

The trap: the smoke test passes trivially (the downstream graph is
IID, so no cross-row reaches downstream of the marker to break),
and the CV report looks fine — which feels like a green light. But
the next experiment that adds lagged-load features against the
raw hourly history cannot compose with this loader, because the
loader has already collapsed the source into a single
horizon-specific materialization. Fix by pushing the shift into
the Layer-2 aligner below.

## History-dependent — early-mark with upstream reference

Layer 1 has at least *two* roots: one or more raw history sources
+ a `predict_grid` describing the rows we want predictions for
(a time range, a list of group IDs, a `(group, time)` set —
whatever shape the problem requires). Layer 2 produces an aligned
`{X, y}` from those roots. Layer 3's history-dependent feature
step takes the X DataOp *and* the raw history DataOp; the feature
function joins real values onto every row in the predict grid.

```python
def build_learner(predict_grid_preview=None, history_source_preview=None):
    predict_grid = (
        skrub.var("predict_grid", value=predict_grid_preview)
        if predict_grid_preview is not None
        else skrub.var("predict_grid")
    )
    history_source = (
        skrub.var("history_source", value=history_source_preview)
        if history_source_preview is not None
        else skrub.var("history_source")
    )

    # Layer 1: raw history, no shifts, no drops
    history = history_source.skb.apply_func(load_history)

    # Layer 2: align predict_grid + history into (X, y).
    # `align_xy` is a small stateful BaseEstimator:
    #   fit_transform → {X, y}; transform → {X, y=None}.
    # See python-api/references/pre_mark_alignment.md for the full
    # production-style walkthrough drawn from this workspace's
    # 01_baseline.
    aligned = skrub.as_data_op(
        {"predict_grid": predict_grid, "history": history}
    ).skb.apply(align_xy)
    X = aligned["X"].skb.mark_as_X()    # rows = the predict grid
    y = aligned["y"].skb.mark_as_y()

    # Layer 3: features AFTER mark_as_X. The feature function
    # takes the X DataOp and the upstream `history` DataOp;
    # the join inside it fills history-dependent values for
    # every row in the predict grid.
    features = X.skb.apply_func(add_history_features, history)
    predictions = features.skb.apply(predictor, y=y)
    return predictions.skb.make_learner()
```

The `align_xy` shape (a small stateful estimator that produces
`{X, y}` at fit and `{X, y=None}` at predict) is one way to encode
Layer 2 — straightforward, lets `mark_as_X` / `mark_as_y` come
immediately after. Other shapes work too (e.g. two parallel
`apply_func` branches that each produce X-aligned rows from
`predict_grid` + `history`, marked separately); pick whichever
expresses the alignment most clearly for the data.

Look up the underlying skrub DataOp / `mark_as_X` / `mark_as_y`
signatures via `python-api` against the installed skrub version.
