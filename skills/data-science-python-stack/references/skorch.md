# skorch

A scikit-learn-compatible neural-network library that wraps PyTorch.
Lets a `torch.nn.Module` behave like a scikit-learn estimator —
`fit` / `predict` / `score`, plus drop-in use inside `Pipeline`,
`GridSearchCV`, `cross_val_score`, and the rest of the sklearn API.

**Pick skorch when:**
- You have (or want to write) a PyTorch model and you want it to live
  inside a sklearn workflow — pipelines, hyperparameter search,
  cross-validation, the inspection tools.
- You're mixing classical preprocessing (`scikit-learn`, `skrub`) with
  a deep learning estimator and want one consistent API surface.

**Don't pick skorch for:**
- Pure deep-learning training loops where the sklearn API gets in the
  way — write the training loop in `pytorch` directly.
- Models that are not pytorch-based — `keras`'s sklearn wrappers are
  the equivalent escape hatch on the keras side.

**Pair with:**
- `pytorch` — the underlying model.
- `scikit-learn` — the API surface skorch adapts to.
