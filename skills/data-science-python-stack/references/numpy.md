# numpy

The foundation for n-dimensional numerical arrays in Python. Every other
numerical and ML library in the stack accepts or returns numpy arrays at
some boundary, so it is unavoidable.

**Pick numpy for:**
- Dense numerical data that isn't a labelled table — signals, images,
  embeddings, raw matrices.
- Vectorized math: broadcasting, linear algebra, FFT, random number
  generation.
- Cases where memory layout matters (dtypes, contiguous vs strided
  arrays, views vs copies).

**Don't pick numpy for:**
- Tabular data with column semantics → `pandas` or `polars`.
- Out-of-core or distributed data → numpy is in-memory only.
- GPU compute, autograd, or deep learning → `pytorch` (tensor API
  mirrors numpy and interoperates via the array API standard).
- Scientific computing on top of arrays (stats, optimize, sparse,
  signal) → `scipy`.
