# keras

High-level, layer-oriented deep learning API. Keras 3 is **multi-backend**
— the same model code can run on top of `pytorch`, TensorFlow, or JAX
— so the backend choice is decoupled from the model code.

**Pick keras when:**
- You want a concise, declarative API for building deep models
  (`Sequential`, `Functional`, layer composition) without writing the
  training loop by hand.
- The team is already keras-fluent or the project predates the
  keras-3 multi-backend split.
- You want one model definition that survives a backend swap — keras
  code does not need to change if the project moves between pytorch,
  TensorFlow, or JAX.

**Don't pick keras for:**
- Classical tabular ML → `scikit-learn`.
- Research or custom architectures where you want explicit control
  over the training loop and tensor ops → use `pytorch` directly.

**Pair with:**
- `pytorch` (or another supported backend) — keras runs on top of it.
- `scikit-learn` — keras ships sklearn-compatible wrappers
  (e.g. `KerasClassifier`, `KerasRegressor`) so a keras model plugs
  into sklearn pipelines, GridSearchCV, and cross-validation with the
  same `fit` / `predict` API as any other estimator.
