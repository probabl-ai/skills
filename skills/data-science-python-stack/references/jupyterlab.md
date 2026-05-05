# jupyterlab

The standard browser-based IDE for Jupyter notebooks. Used in this
stack to edit and execute notebooks — preferably notebooks whose
source of truth is a Python file (via `jupytext`).

**Use jupyterlab for:**
- Editing and running `.ipynb` notebooks or jupytext-paired `.py`
  files.
- Interactive data exploration with rich output (tables, plots,
  widgets).
- Local development; for shared infra the user may have JupyterHub
  set up separately.

**Pair with:**
- `ipykernel` — the Python kernel that runs notebook code.
- `jupytext` — keeps notebooks under version control as `.py` files.

**Watch out for:**
- Out-of-order execution and hidden state are real risks. Restart and
  run-all before trusting a notebook's state.
- `.ipynb` JSON has embedded outputs that bloat git diffs — that's
  why this stack uses `jupytext` to keep the source of truth as `.py`.
