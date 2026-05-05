# pyarrow

Python bindings to Apache Arrow — the columnar memory format that backs
modern dataframe libraries. Rarely used directly in application code;
install it because something else in the stack needs it.

**Why it sits in the stack:**
- It is the recommended Parquet engine for `pandas`
  (`df.to_parquet(engine="pyarrow")`, `pd.read_parquet(...)`).
- It enables Arrow-backed dtypes in `pandas` 2.x for better string
  handling, nullable types, and faster I/O.
- `polars` uses Arrow internally and shares zero-copy buffers with
  `pyarrow`.
- It is the zero-copy interchange format when converting between
  `pandas` and `polars`.

**Pick pyarrow directly only when:**
- You need Parquet/Feather/Arrow I/O without going through a dataframe
  library.
- You are working at the buffer/dataset level (rare for application
  code).

In practice you install it and let `pandas` or `polars` use it.
