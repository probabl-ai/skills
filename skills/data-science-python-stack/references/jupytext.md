# jupytext

Bridges Jupyter notebooks (`.ipynb`) and plain Python files (`.py`
with `# %%` cell markers — the "percent" format). Lets the source of
truth live as a Python file while still being editable and runnable
in JupyterLab.

**Why this stack uses jupytext:**
- `.ipynb` is JSON with embedded outputs — unfriendly for git diffs,
  PR review, and merge conflicts.
- `.py` with `# %%` markers diffs cleanly, can be imported as a
  module, and runs as a script.
- jupytext can either (a) pair a `.ipynb` with a `.py` so both stay
  in sync, or (b) open a `.py` directly as a notebook in JupyterLab.

**Convention in this stack:**
- Author notebooks as `.py` files with `# %%` cell markers.
- Commit the `.py`; do **not** commit the `.ipynb` (or pair it and
  add `*.ipynb` to `.gitignore`).
- Configure the pairing in `pyproject.toml` or per-notebook metadata.

**Pair with:**
- `jupyterlab` — opens / edits the percent files as notebooks.
- `ipykernel` — the kernel that runs them.
