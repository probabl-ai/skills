# scipy

Scientific computing library built on `numpy`. Covers what numpy
intentionally leaves out: statistical tests, optimization, signal
processing, sparse matrices, special functions, integration,
interpolation, advanced FFT, advanced linear algebra.

**Pick scipy when:**
- You need a statistical test (`scipy.stats`).
- You need numerical optimization (`scipy.optimize`).
- You need sparse matrices (`scipy.sparse`) — including as inputs to
  scikit-learn estimators that accept sparse data.
- You need signal / image processing primitives, interpolation, ODE
  solvers, or special functions.

**Array API support:**
- A growing portion of scipy supports the **array API standard**, so
  array-API-compatible libraries (`numpy`, `pytorch`, `cupy`) can flow
  through the same scipy entry points and stay on their original
  device — including GPU via `pytorch`.

**Don't pick scipy for:**
- Tabular data manipulation → `pandas` or `polars`.
- The plain n-d array primitives — that's `numpy`'s job. scipy *uses*
  numpy; it doesn't replace it.

**Pair with:**
- `numpy` — the foundation. scipy is the next layer up.
- `pytorch` — via the array API, where scipy supports it, for GPU
  scientific computing.
- `scikit-learn` — many sklearn estimators accept `scipy.sparse`
  matrices natively.
