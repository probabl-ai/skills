# skrub

> **Always install the latest `skrub`.** The DataOps graph API
> (`skrub.var`, `.skb.apply`, `.skb.apply_func`, `mark_as_X` /
> `mark_as_y`, `SkrubLearner`) and the env-dict it expects at fit
> time evolve across minor versions; older versions silently diverge
> from the examples in `build-ml-pipeline` and `skrub-api`. Use
> `skrub = ">=<latest>"` as a floor; refresh the floor on every
> install.

A scikit-learn-compatible library for the messy data-cleaning step that
sits *before* a sklearn pipeline. Works with both `pandas` and `polars`.

**Core idea: dataframe transformations as a computation graph.**
Real-world data wrangling is usually a pile of ad-hoc dataframe
operations — string cleanup, datetime parsing, joining lookup tables,
encoding high-cardinality categoricals. These are easy to get wrong
because the *exact same* transformation must be applied at training
*and* inference time. Skrub lets you express those operations as
functions over dataframes, compose them into a graph, and replay the
graph deterministically across train and test splits. Any
scikit-learn-compatible component can sit as a node in the graph —
sklearn transformers and estimators directly, but also `skorch` or
`keras` wrappers around deep models — so the whole "clean + model"
pipeline is one fitted object.

**Pick skrub when:**
- The dataset has high-cardinality categoricals, free-text fields,
  datetimes, or needs joins between several tables before modelling.
- You want train/test consistency for the data-cleaning layer
  guaranteed by construction, not by discipline.
- You want a lighter API for common preprocessing tasks that
  scikit-learn supports more verbosely.
- You want a **quick traditional-ML baseline with automatic
  preprocessing** — skrub picks sensible encoders per column type and
  hands you a working estimator, so you can compare any later modelling
  effort against a real baseline instead of a guess.
- You want a quick interactive overview of a dataframe (`TableReport`).

**Pair with:**
- `scikit-learn` — graph nodes can be sklearn transformers and
  estimators directly.
- `skorch` / `keras` — deep models exposed through the sklearn API
  drop into the same graph.
- `pandas` or `polars` — both supported.

**Don't use skrub for:**
- Pure modelling steps with already-clean numeric features —
  scikit-learn alone is enough.
