"""Turn jupytext percent ``# %%`` files into notebooks.

``convert`` executes the source. ``fill`` writes the same notebook
with empty outputs and does not start a kernel.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

MISSING = "jupytext and nbclient are required; add them with add-python-package"
MISSING_FILL = "jupytext and nbformat are required; add them with add-python-package"
MISSING_IPYWIDGETS = "ipywidgets is required; add it with add-python-package"
MISSING_NBCONVERT = "nbconvert is required; add it with add-python-package"
TEMPLATE_DIR = Path(__file__).with_name("site_assets")
INLINE_SETUP = "%matplotlib inline"

try:
    import jupytext
    import nbformat
except ImportError:  # pragma: no cover - exercised by hiding modules in tests
    jupytext = None
    nbformat = None

try:
    from nbclient import NotebookClient
except ImportError:  # pragma: no cover - exercised by hiding the module in tests
    NotebookClient = None

try:
    import ipywidgets
except ImportError:  # pragma: no cover - exercised by hiding the module in tests
    ipywidgets = None


def source_fingerprint(src: Path) -> str:
    """Return the SHA-256 fingerprint stored with a generated notebook."""
    return hashlib.sha256(src.read_bytes()).hexdigest()


def _cells(notebook: Any) -> list[Any]:
    return notebook.cells if hasattr(notebook, "cells") else notebook["cells"]


def _set_source_fingerprint(notebook: Any, fingerprint: str) -> None:
    metadata = (
        notebook.metadata
        if hasattr(notebook, "metadata")
        else notebook.setdefault("metadata", {})
    )
    metadata["skore_skills"] = {"source_sha256": fingerprint}


def _value(item: Any, key: str, default: Any = None) -> Any:
    return getattr(item, key, item.get(key, default))


def _clear_code_outputs(notebook: Any) -> None:
    for cell in _cells(notebook):
        if _value(cell, "cell_type", "code") != "code":
            continue
        if hasattr(cell, "outputs"):
            cell.outputs = []
            cell.execution_count = None
            continue
        cell["outputs"] = []
        cell["execution_count"] = None


def render_digest(src: Path, notebook: Any) -> str:
    """Render executed notebook cells as the plain Markdown audit digest."""
    rendered = [f"# Cells: `{src}`\n"]
    for index, cell in enumerate(_cells(notebook)):
        cell_type = _value(cell, "cell_type", "code")
        marker = "# %% [markdown]" if cell_type == "markdown" else "# %%"
        rendered.append(f"\n## Cell {index}: `{marker}`\n")
        source = _value(cell, "source", "")
        if cell_type == "markdown":
            rendered.append(f"\n{source.rstrip()}\n")
            continue
        if source.strip():
            rendered.append(f"\n```python\n{source.rstrip()}\n```\n")
        for output in _value(cell, "outputs", []):
            output_type = _value(output, "output_type", "")
            if output_type == "stream":
                name = _value(output, "name", "stdout")
                text = _value(output, "text", "")
                rendered.append(f"\n**{name}:**\n```\n{text}```\n")
            elif output_type in {"execute_result", "display_data"}:
                data = _value(output, "data", {})
                text = data.get("text/plain") if isinstance(data, dict) else None
                if text is not None:
                    rendered.append(f"\n**output:**\n```\n{text}\n```\n")
            elif output_type == "error":
                name = _value(output, "ename", "Error")
                value = _value(output, "evalue", "")
                rendered.append(f"\n**error:** `{name}: {value}`\n")
    return "".join(rendered)


def convert(
    src: Path,
    out: Path | None = None,
    *,
    html: bool = False,
    digest: Path | None = None,
) -> Path:
    """Read a percent-format ``.py``, execute it, and write ``.ipynb``.

    Injects ``%matplotlib inline`` for the kernel run so seaborn /
    matplotlib last expressions emit ``image/png``, then strips that
    setup cell so it is not in the written notebook.

    Parameters
    ----------
    src : pathlib.Path
        Jupytext percent-format source.
    out : pathlib.Path, optional
        Destination notebook. Defaults to the same stem next to ``src``.
    html : bool, optional
        When true, also write ``<stem>.nb.html`` next to ``src``.

    Returns
    -------
    pathlib.Path
        Path of the ``.ipynb`` written.

    Raises
    ------
    ImportError
        When jupytext, nbclient, ipywidgets, or (if ``html``) nbconvert
        is not importable.
    FileNotFoundError
        When ``src`` is missing.
    """
    if jupytext is None or nbformat is None or NotebookClient is None:
        raise ImportError(MISSING)
    if ipywidgets is None:
        raise ImportError(MISSING_IPYWIDGETS)
    assert jupytext is not None
    assert nbformat is not None
    assert NotebookClient is not None
    if not src.is_file():
        raise FileNotFoundError(f"notebook source not found: {src}")
    dest = src.with_suffix(".ipynb") if out is None else out
    dest.parent.mkdir(parents=True, exist_ok=True)
    notebook = jupytext.read(src)
    cells = _cells(notebook)
    cells.insert(0, nbformat.v4.new_code_cell(INLINE_SETUP))
    client = NotebookClient(
        notebook,
        timeout=600,
        kernel_name="python3",
        resources={"metadata": {"path": os.fspath(src.parent.resolve())}},
    )
    client.execute()
    del cells[0]
    _set_source_fingerprint(notebook, source_fingerprint(src))
    nbformat.write(notebook, dest)
    if html:
        to_html(dest, src.with_name(f"{src.stem}.nb.html"))
    if digest is not None:
        digest.parent.mkdir(parents=True, exist_ok=True)
        digest.write_text(render_digest(src, notebook), encoding="utf-8")
    return dest


def fill(src: Path, out: Path | None = None, *, html: bool = False) -> Path:
    """Read a percent-format ``.py`` and write an ``.ipynb`` with no outputs.

    Does not start a kernel. Code cells are cleared so a source-only
    notebook is what the site embeds.

    Parameters
    ----------
    src : pathlib.Path
        Jupytext percent-format source.
    out : pathlib.Path, optional
        Destination notebook. Defaults to the same stem next to ``src``.
    html : bool, optional
        When true, also write ``<stem>.nb.html`` next to ``src``.

    Returns
    -------
    pathlib.Path
        Path of the ``.ipynb`` written.

    Raises
    ------
    ImportError
        When jupytext, nbformat, or (if ``html``) nbconvert is not importable.
    FileNotFoundError
        When ``src`` is missing.
    """
    if jupytext is None or nbformat is None:
        raise ImportError(MISSING_FILL)
    assert jupytext is not None
    assert nbformat is not None
    if not src.is_file():
        raise FileNotFoundError(f"notebook source not found: {src}")
    dest = src.with_suffix(".ipynb") if out is None else out
    dest.parent.mkdir(parents=True, exist_ok=True)
    notebook = jupytext.read(src)
    _clear_code_outputs(notebook)
    _set_source_fingerprint(notebook, source_fingerprint(src))
    nbformat.write(notebook, dest)
    if html:
        to_html(dest, src.with_name(f"{src.stem}.nb.html"))
    return dest


def to_html(src: Path, out: Path) -> Path:
    """Write a self-contained HTML rendering of an executed ``.ipynb``.

    Parameters
    ----------
    src : pathlib.Path
        Executed notebook.
    out : pathlib.Path
        Destination HTML file.

    Returns
    -------
    pathlib.Path
        Path written.

    Raises
    ------
    ImportError
        When nbconvert is not importable.
    FileNotFoundError
        When ``src`` is missing.
    """
    if not src.is_file():
        raise FileNotFoundError(f"notebook not found: {src}")
    try:
        from nbconvert import HTMLExporter
    except ImportError as exc:
        raise ImportError(MISSING_NBCONVERT) from exc
    exporter = HTMLExporter(
        template_name="lab",
        template_file=os.fspath(TEMPLATE_DIR / "skore_notebook.html.j2"),
    )
    exporter.embed_images = True
    body, _resources = exporter.from_filename(os.fspath(src))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(body, encoding="utf-8")
    return out
