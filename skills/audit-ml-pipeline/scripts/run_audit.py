"""Execute a jupytext ``# %%`` audit file and stream per-cell text to stdout.

Skill asset for ``audit-ml-pipeline``. Uses
``IPython.core.interactiveshell.InteractiveShell.run_cell`` to execute
each cell in-process and streams a plain-text markdown digest to
**stdout** (and optionally to a file when a second path argument is
given). The agent reads the digest from the bash tool's output — no
separate ``Read`` step required.

Why IPython, not plain Python
-----------------------------
``# %%`` is IPython's cell convention; ``run_cell`` handles multi-line
statements, syntax errors, and last-expression detection in-process,
and ``repr(result.result)`` on the last bare expression keeps the
output plain text (rich ``_repr_html_`` would swamp the agent's
context).

CLI
---
``python run_audit.py <src.py> [<dst.md>]``

Always streams the digest to stdout. When ``<dst.md>`` is supplied the
digest is also written to that file (parent created if missing).

Output shape::

    # Audit: `<src.py>`

    ## Cell 0: `# %% [markdown]`

    <rendered markdown text>

    ## Cell 1: `# %%`

    ```python
    <cell source>
    ```

    **stdout:**
    ```
    <captured stdout>
    ```

    **output:**
    ```
    <repr(result.result)>
    ```

    **error:** `<ExceptionType: message>`
"""

from __future__ import annotations

import io
import os
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment preparation — must happen BEFORE any library is imported by
# the runner or by cells, so that every subsequent import picks up the
# settings.
# ---------------------------------------------------------------------------

# 1. Non-interactive matplotlib backend.
#    skore.__init__ calls plt.ion() which triggers install_repl_displayhook()
#    → ip.enable_gui() on the bare InteractiveShell, raising
#    NotImplementedError.  Forcing Agg first makes plt.ion() a no-op.
try:
    import matplotlib

    matplotlib.use("Agg")
except ImportError:
    pass

# 2. Suppress progress bars so they don't pollute per-cell stdout captures.
#    - TQDM_DISABLE: silences tqdm (used by some skore / sklearn steps).
#    - RICH_FORCE_TERMINAL=0: tells rich not to assume a real TTY; prevents
#      ANSI codes and spinner output that clutter the plain-text digest.
#    - SKORE_PROGRESS_BAR (skore-specific, best-effort): set to "0" to
#      disable skore's own rich progress panels where supported.
os.environ.setdefault("TQDM_DISABLE", "1")
os.environ.setdefault("RICH_FORCE_TERMINAL", "0")
os.environ.setdefault("SKORE_PROGRESS_BAR", "0")

# ---------------------------------------------------------------------------
# Optional library configuration
# ---------------------------------------------------------------------------

# Pandas: widen display options so DataFrames are not truncated in cell
# outputs — truncation here is silent data loss for the agent.
try:
    import pandas as pd
except ImportError:
    pd = None

if pd is not None:
    pd.set_option(
        "display.max_rows",
        None,
        "display.max_columns",
        None,
        "display.max_colwidth",
        None,
        "display.width",
        None,
    )

from IPython.core.interactiveshell import InteractiveShell  # noqa: E402


class _NoOpDisplayHook:
    """Silent display hook for non-interactive cell execution.

    Replaces ``shell.displayhook`` so bare cell expressions are not
    echoed to stdout by IPython. ``result.result`` is still populated by
    ``run_cell`` independently of the hook, so the runner captures it
    via ``result.result!r``.

    Must carry the attributes that IPython internals and third-party
    libraries check at runtime:

    - ``do_full_cache`` — IPython's ``reset()`` (atexit) checks this.
    - ``is_active``     — rich.Console's IPython integration checks this
                          when deciding whether to use the displayhook as
                          an output channel.
    """

    do_full_cache: bool = False
    is_active: bool = False

    def __call__(self, *args: object, **kwargs: object) -> None:  # noqa: ARG002
        """Discard the display call silently."""


def parse_cells(text: str) -> list[tuple[str, str]]:
    """Split jupytext percent-format source into ``(marker, body)`` cells.

    Parameters
    ----------
    text : str
        Full source text of the audit ``.py`` file.

    Returns
    -------
    list of (str, str)
        Each pair is ``(cell-marker line, cell body)``. Text before the
        first ``# %%`` marker is discarded.
    """
    cells: list[tuple[str, str]] = []
    marker: str | None = None
    body: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("# %%"):
            if marker is not None:
                cells.append((marker, "".join(body)))
            marker, body = line.rstrip("\n"), []
        else:
            body.append(line)
    if marker is not None:
        cells.append((marker, "".join(body)))
    return cells


def render_markdown_cell(body: str) -> str:
    """Convert a ``# %% [markdown]`` cell body to plain markdown text.

    Strips the leading ``# `` from each comment line and discards
    non-comment lines (blank separators).

    Parameters
    ----------
    body : str
        Cell body (the lines following the ``# %% [markdown]`` marker).

    Returns
    -------
    str
        Rendered markdown text.
    """
    return "\n".join(
        line.removeprefix("# ").rstrip()
        for line in body.splitlines()
        if line.lstrip().startswith("#")
    )


def make_shell() -> InteractiveShell:
    """Build an ``InteractiveShell`` configured for non-interactive use.

    Returns
    -------
    IPython.core.interactiveshell.InteractiveShell
        Singleton shell with a silent ``_NoOpDisplayHook`` installed.
        Using a proper class (not a lambda) ensures that IPython's
        atexit cleanup and rich's console integration find the expected
        ``do_full_cache`` / ``is_active`` attributes without raising
        ``AttributeError``.
    """
    shell = InteractiveShell.instance()
    shell.displayhook = _NoOpDisplayHook()
    return shell


def run(src_path: Path, out_path: Path | None = None) -> None:
    """Execute every cell of ``src_path`` and stream the markdown digest.

    Always writes to stdout.  When ``out_path`` is given the same
    content is also written to that file (parent created if missing).

    Cells are executed in a single shared namespace so imports and
    assignments persist across cells (same as a notebook kernel).  A
    failing cell does not stop the run — the exception lands in the
    cell's ``**error:**`` section and execution continues.

    Parameters
    ----------
    src_path : pathlib.Path
        Path to the source ``# %%`` audit file.  UTF-8 encoded.
    out_path : pathlib.Path or None, optional
        Optional destination file.  When ``None`` the digest is streamed
        to stdout only.
    """
    cells = parse_cells(src_path.read_text(encoding="utf-8"))
    shell = make_shell()
    md: list[str] = [f"# Audit: `{src_path}`\n"]
    for i, (marker, body) in enumerate(cells):
        md.append(f"\n## Cell {i}: `{marker}`\n")
        if "[markdown]" in marker:
            md.append("\n" + render_markdown_cell(body) + "\n")
            continue
        if not body.strip():
            continue
        md.append(f"\n```python\n{body.rstrip()}\n```\n")
        out_buf, err_buf = io.StringIO(), io.StringIO()
        with redirect_stdout(out_buf), redirect_stderr(err_buf):
            result = shell.run_cell(body, store_history=False)
        if out_buf.getvalue():
            md.append(f"\n**stdout:**\n```\n{out_buf.getvalue()}```\n")
        if result.result is not None:
            md.append(f"\n**output:**\n```\n{result.result!r}\n```\n")
        if err_buf.getvalue():
            md.append(f"\n**stderr:**\n```\n{err_buf.getvalue()}```\n")
        if not result.success and result.error_in_exec is not None:
            exc = result.error_in_exec
            md.append(f"\n**error:** `{type(exc).__name__}: {exc}`\n")

    digest = "".join(md)
    sys.stdout.write(digest)
    sys.stdout.flush()

    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(digest, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point: ``python run_audit.py <src.py> [<dst.md>]``.

    Always streams the digest to stdout.  The optional second argument
    ``<dst.md>`` causes the digest to also be written to that file.

    Parameters
    ----------
    argv : list of str or None, optional
        Override for ``sys.argv[1:]``.

    Returns
    -------
    int
        ``0`` on success, ``2`` on wrong argument count.
    """
    args = sys.argv[1:] if argv is None else argv
    if not (1 <= len(args) <= 2):
        print(__doc__, file=sys.stderr)
        return 2
    out_path = Path(args[1]) if len(args) == 2 else None
    run(Path(args[0]), out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
