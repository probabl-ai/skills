# Audit ML Pipeline — Runner internals

What `scripts/run_cells.py` does internally — parsing, shell setup,
environment fixes, per-cell capture. Cross-referenced from SKILL.md
§ "Execution contract".

`run_cells.py` is a **generic** jupytext cell runner: it is owned by
this skill but shared with `explore-ml-data` (which executes
`data/eda.py` the same way). It is content-agnostic — it knows
nothing about skore reports or TableReports. Keep it that way: any
change here must serve both callers, never hard-code audit-specific
behaviour.

Load when:

- A cell is producing output you didn't expect (where does that
  ANSI escape come from? why is `Out[0]:` in the digest?).
- The runner errors and you need to know which subsystem is at
  fault.
- You're considering modifying `run_cells.py` — read this first.

## CLI shape

```
python run_cells.py <src.py> [<dst.md>]
```

Always streams the digest to **stdout**. When `<dst.md>` is given,
the digest is also written to that file (parent created if missing).
The agent typically calls without the second arg and reads the
digest from the bash tool's output directly.

## Environment preparation — module-level

Before any library is imported by the runner OR by cells, the
module-level setup does four things:

### 1. Non-interactive matplotlib backend

```python
import matplotlib
matplotlib.use("Agg")
```

Why: `skore.__init__` calls `plt.ion()`, which calls
`install_repl_displayhook()`, which calls
`ip.enable_gui(ipython_gui_name)` on the bare `InteractiveShell` —
raising `NotImplementedError: Implement enable_gui in a subclass`.
Forcing `Agg` first makes `plt.ion()` a no-op (no GUI loop to
install).

### 2. Suppress progress bars

```python
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("RICH_FORCE_TERMINAL", "0")
os.environ.setdefault("SKORE_PROGRESS_BAR", "0")
```

- `TQDM_DISABLE`: silences tqdm (some sklearn / skrub steps use it).
- `RICH_FORCE_TERMINAL=0`: tells rich not to assume a TTY; prevents
  ANSI codes and spinner output cluttering the plain-text digest.
- `SKORE_PROGRESS_BAR=0`: best-effort skore-specific progress
  panel disable.

### 3. Pandas display options (when pandas is importable)

```python
pd.set_option(
    "display.max_rows", None,
    "display.max_columns", None,
    "display.max_colwidth", None,
    "display.width", None,
)
```

The runner is the only display surface the agent gets. Truncation
here is silent data loss; widen everything. Pandas is an optional
import — if absent (a polars workspace), this step is skipped.

### 4. `_NoOpDisplayHook` class

```python
class _NoOpDisplayHook:
    do_full_cache: bool = False
    is_active: bool = False
    def __call__(self, *args, **kwargs) -> None:
        ...
```

Installed as `shell.displayhook = _NoOpDisplayHook()`.

Why a class, not a lambda:

- IPython's `reset()` (atexit) reads `shell.displayhook.do_full_cache`
  — a bare lambda raises `AttributeError`.
- rich.Console's IPython integration reads `ip.displayhook.is_active`
  to decide whether to use the displayhook as an output channel — a
  bare lambda raises `AttributeError`.

A proper class with the two attributes satisfies both checks while
keeping the call itself silent (so bare-expression cells don't echo
`Out[N]: <repr>` to stdout — `result.result` is populated
independently of the displayhook).

## Cell parsing

```python
def parse_cells(text: str) -> list[tuple[str, str]]:
```

Splits the source on `# %%` markers. Each cell is `(marker_line,
body)`. Text before the first marker is discarded (the file should
start with a marker per jupytext conventions).

## Per-cell execution

For each `(marker, body)`:

1. Markdown cells (`# %% [markdown]`): strip `# ` prefixes, render
   the body lines into the digest as plain markdown.
2. Code cells: write the source as a fenced code block, then
   execute via:
   ```python
   with redirect_stdout(out_buf), redirect_stderr(err_buf):
       result = shell.run_cell(body, store_history=False)
   ```

The shared `InteractiveShell` namespace means imports and
assignments persist across cells (same as a notebook kernel).

## Output rendering

Per cell, in order:

1. **stdout** — `out_buf.getvalue()` if non-empty, fenced.
2. **output** — `repr(result.result)` if the cell has a last
   bare expression (auto-displayed by IPython into `result.result`).
3. **stderr** — `err_buf.getvalue()` if non-empty, fenced.
4. **error** — `<type>: <message>` if `result.success is False`
   AND `result.error_in_exec is not None`.

A failing cell does NOT stop the run — exceptions land in their
cell's `**error:**` section and execution continues with the next
cell.

## What the runner does NOT do

- Spawn a Jupyter kernel. The shell is in-process.
- Convert to `.ipynb`. No notebook representation; only the
  markdown digest.
- Request `_repr_html_`. Plain `repr()` only.
- Run code outside cells. Anything before the first `# %%` marker
  is discarded.
- Run remote / network probes (unless a cell does).
- Verify the read-only contract programmatically. The contract is
  *visible* in the digest (forbidden calls surface as errors or as
  unexpected `summarize()` rows), but the runner doesn't reject
  them statically.

## When you'd modify `run_cells.py`

- Adding another environment-prep step (new library that needs
  config before import).
- Changing the digest format (e.g. adding cell timing).
- Changing the output target (stdout, file, both, neither).

**Always update the SKILL.md § Execution contract and this
reference together** — they're paired documentation. Because
`explore-ml-data` shares this runner, also re-check that skill's
§ "Execution contract" when the CLI shape or digest format changes.
