# Source binding patterns

The `value` of a root `skrub.var(name, value=...)` is the most consequential
choice in a DataOps pipeline: it determines whether the loader (and any
external state behind it) is *inside* the graph or *outside* it.

This file catalogues which forms to **encourage** on new pipelines, which
to **discourage** outright, and which are tolerable but worth offering the
user a cleaner alternative.

## Encourage — bind the source *identifier*

The bound value is a small, swappable handle to the source. The loader is
the first `.skb.apply_func` in the graph. At fit / cross-validate time the
env-dict is one binding per source; swapping a source is a one-string
change.

The `value=` keyword on `skrub.var` is the **preview** — it controls only
what `learner.skb.preview()` shows during interactive iteration. Expose it
as an optional caller-supplied parameter on `build_learner`; never bake a
relative-path literal into `pipeline.py` (that would resolve against the
CWD at execution time and silently break runs from anywhere but the
project root).

```python
def build_learner(path_preview: str | Path | None = None):
    path = (
        skrub.var("path", value=str(path_preview))
        if path_preview is not None
        else skrub.var("path")
    )
    data = path.skb.apply_func(load_parquet)
    ...
```

The experiment script then passes an absolute path resolved from the
package's `PROJECT_ROOT` (no `value=` baked into `pipeline.py`):

```python
from <pkg> import PROJECT_ROOT
TRAIN_PATH = PROJECT_ROOT / "data/train.parquet"

learner = build_learner(path_preview=TRAIN_PATH)
report = skore.evaluate(
    learner, data={"path": str(TRAIN_PATH)}, splitter=splitter,
)
```

Common identifier types:

| Source            | Bound value                                | First step                     |
|-------------------|--------------------------------------------|--------------------------------|
| Local file        | `"data/train.parquet"`                     | `pl.read_parquet` / `pd.read_*`|
| URL               | `"https://example.com/file.csv"`           | HTTP fetch + parse             |
| Cloud object      | `"s3://bucket/key"` (or signed URL)        | `fsspec` / `s3fs` reader       |
| DB table          | `"events"` (+ a separate connection var)   | `pl.read_database` / SQL query |
| SQL query         | `"SELECT … WHERE date >= '…'"`             | `pl.read_database`             |
| HuggingFace ID    | `"squad"` (+ split var)                    | `datasets.load_dataset`        |

For multi-source pipelines, declare one `skrub.var(...)` per source and
join inside the graph (see SKILL pattern 3).

## Discourage — bind a materialized DataFrame produced outside the graph

The loader runs in module-level / driver code, the graph receives an
already-materialized object. Swapping the source means re-loading and
re-splitting outside the graph each time — the env-dict can no longer
own the source.

```python
# DON'T
df = pl.read_parquet("data/train.parquet")          # loader outside the graph
data = skrub.var("data", df)

# DON'T
X_value, y_value = split(df)                        # split outside the graph
X = skrub.X(X_value)
y = skrub.y(y_value)

# DON'T — same antipattern wearing a mustache
def build_pipeline():
    df_preview = load_parquet("data/train.parquet") # loader inside build, not graph
    return skrub.var("data", df_preview)...

# DON'T — relative-path literal baked into the graph
def build_pipeline():
    path = skrub.var("path", value="data/train.parquet")  # CWD-dependent
    return path.skb.apply_func(load_parquet)...
# The loader IS in the graph here, which is correct. The bug is that the
# preview value `"data/train.parquet"` resolves against the CWD at execution
# time — fine from the project root, broken from anywhere else. Expose the
# preview as an optional parameter on `build_pipeline` and let the caller
# pass an absolute path (e.g. `<pkg>.PROJECT_ROOT / "data/train.parquet"`).
```

`skrub.X(...)` and `skrub.y(...)` are also discouraged as roots in
general: they are literally `var("X", value).skb.mark_as_X()` and
`var("y", value).skb.mark_as_y()`, which forces both the variable
name and the marker at the root. Mark
X / y *at the X / y split* inside the graph instead.

## OK but offer the user an upgrade

These are forms that work for the moment but where the canonical
source-bound pattern is strictly better. When you encounter one, finish
the immediate task first, then offer the user a refactor — don't
auto-rewrite.

- **Inherited / existing pipeline using the materialized-data form.**
  The pipeline already runs and is being edited for an unrelated
  reason. Offer: "this graph binds the loaded DataFrame; want me to
  refactor it to bind the path so swapping sources becomes a one-line
  env-dict change?"

- **Notebook scratch cells that are being promoted to a module.** A
  one-off cell where the data was loaded above is fine while it stays
  a one-off. Once it's being moved into a reusable function or
  imported elsewhere, the materialized-data binding becomes a
  liability. Offer the source-bound rewrite at that point.

- **In-memory data that *will* eventually come from a file / DB.** The
  data is currently a fixture or quick simulation, but the user has
  said the real source will be an external one. Offer: "want me to
  introduce the loader as the first graph step now, so swapping in
  the real source later is one binding?"

- **Genuine in-memory / synthetic data with no external source ever**
  (simulation outputs, randomly generated test fixtures, in-memory
  transforms of an upstream pipeline owned by the same script). No
  upgrade is needed — there is no identifier to swap. Bind the
  generated object directly.

## How to decide on a fresh declaration

1. Is there an external source identifier (path, URL, table, query)?
   Yes → bind the identifier; the loader is the first
   `.skb.apply_func`. **Expose the preview as an optional caller-supplied
   parameter** on `build_pipeline` (e.g. `path_preview: str | Path | None
   = None`); the experiment script passes an absolute path resolved from
   `<pkg>.PROJECT_ROOT`. Do not bake a relative-path literal into the
   `value=` of `skrub.var`.
2. No — the data is generated in-process? Bind the generated object
   directly via `skrub.var`. The synthetic case is the only case where
   binding a materialized object is the intended form.

Mark X and y inside the graph at the split point in either case.

## Companion references

- `python-api/references/pre_mark_alignment.md` — the full 3-layer
  walkthrough showing how source-bound vars at Layer 1 feed the
  pre-mark alignment at Layer 2 and the history-dependent features
  at Layer 3.
- `python-api/references/skrub_interop.md` — how the env-dict at
  `skore.evaluate(learner, data={...})` time binds those same
  source variables for fit / CV.
