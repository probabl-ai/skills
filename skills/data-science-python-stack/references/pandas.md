# pandas

The classic Python dataframe library. Mature, pervasive, central to the
PyData ecosystem — almost every other library in this stack accepts pandas
DataFrames somewhere on its API surface.

**Pick pandas when:**
- The user prefers it (ask at project start) or the project already uses it.
- You need interop with a library that requires pandas specifically
  (statsmodels, some seaborn workflows, older sklearn paths).
- Ecosystem breadth matters — every tutorial, StackOverflow answer, and
  downstream library assumes pandas.

**Avoid pandas when:**
- The user is open to `polars` and the project is greenfield: polars is
  faster and has cleaner semantics (no index, no SettingWithCopyWarning,
  saner groupby/window operations).
- Datasets are larger than RAM — pandas is in-memory only.

**Watch out for:**
- The index. Resetting, multi-indexing, and silent alignment behaviour
  cause more bugs than any other pandas feature.
- Copy-on-write (default since 2.2) — assignment semantics are stricter
  than older code expects.
- Pair with `pyarrow` as the Parquet engine and (optionally) the dtype
  backend for better string and nullable-type handling.
