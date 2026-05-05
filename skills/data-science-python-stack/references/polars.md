# polars

A fast, modern dataframe library written in Rust. Designed from scratch
with cleaner semantics than pandas: no index, strict schemas, explicit
lazy evaluation, expression-based transformations.

**Pick polars when:**
- The user has agreed to use it (ask at project start).
- Throughput on medium-to-large data (~10⁶+ rows) matters and you don't
  want to reach for a distributed system.
- Lazy / streaming execution is useful to keep memory bounded.
- You want predictable, well-typed transformations — fewer foot-guns
  than pandas.

**Avoid polars when:**
- The team is pandas-native and switching costs aren't justified.
- You need direct interop with libraries that only accept pandas
  (statsmodels, some plotting paths). Convert at the boundary or stay
  with pandas.

**Watch out for:**
- The API is *not* a drop-in pandas replacement. The mental model is
  "expressions evaluated against a query plan," not "operations on a
  frame."
- Eager vs lazy: prefer `lazy()` + `collect()` for non-trivial pipelines
  to get query optimization.
