# pytorch

Tensor library for n-dimensional numerical data with autograd, GPU /
Apple-Silicon (MPS) support, and the broadest deep-learning ecosystem
on top. Default deep-learning framework for this stack, and the GPU
alternative to numpy for raw numerical work.

**Pick pytorch when:**
- You need GPU (CUDA, ROCm) or MPS acceleration for numerical work
  beyond what numpy's CPU-only model can deliver.
- You need automatic differentiation — training neural networks,
  optimizing custom losses, anything gradient-based.
- The task is **deep learning**: NLP, computer vision, sequence models,
  embeddings, custom architectures.

**Don't pick pytorch for:**
- Classical tabular ML — `scikit-learn` is the right tool, and its
  array API support means it can still consume torch tensors on GPU
  for the estimators that opt in.
- Plain in-memory CPU numerical work where `numpy` (+ `scipy`) is
  enough — pulling in torch just to get an array library is overkill.

**Pair with:**
- `skorch` — exposes a `torch.nn.Module` behind the sklearn API
  (`fit` / `predict`, GridSearchCV, pipelines).
- `keras` — high-level, layer-oriented API; runs on top of pytorch
  as a backend (Keras 3 is multi-backend).
- `scikit-learn` via the array API standard — torch tensors flow into
  supported sklearn estimators without conversion.
- `scipy` — a growing portion of scipy supports the array API and
  accepts torch tensors directly, including on GPU.
