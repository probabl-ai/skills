"""Lookup public Python symbols against the running interpreter."""

from __future__ import annotations

import importlib
import inspect
import pydoc
from pathlib import Path
from typing import Any


def package_version(name: str) -> str:
    """Return ``name.__version__`` for an importable package.

    Parameters
    ----------
    name : str
        Top-level package name.

    Returns
    -------
    str
        The version string, or ``"unknown"`` if the attribute is missing.

    Raises
    ------
    ImportError
        If ``name`` cannot be imported.
    """
    module = importlib.import_module(name)
    version = getattr(module, "__version__", None)
    if version is None:
        return "unknown"
    return str(version)


def load_symbol(dotted: str) -> tuple[str, Any]:
    """Import a dotted symbol from the running environment.

    Parameters
    ----------
    dotted : str
        Dotted path such as ``sklearn.model_selection.KFold``.

    Returns
    -------
    tuple of (str, object)
        Top-level package name and the resolved object.

    Raises
    ------
    LookupError
        If the path cannot be resolved.
    ImportError
        If the top-level package is missing.
    """
    parts = dotted.split(".")
    if len(parts) < 2 or not all(parts):
        raise LookupError(f"need a dotted symbol path, got {dotted!r}")
    importlib.import_module(parts[0])
    last_error: Exception | None = None
    for i in range(len(parts) - 1, 0, -1):
        modname = ".".join(parts[:i])
        try:
            module = importlib.import_module(modname)
        except ImportError as exc:
            last_error = exc
            continue
        obj: Any = module
        try:
            for part in parts[i:]:
                obj = getattr(obj, part)
        except AttributeError as exc:
            last_error = exc
            continue
        return parts[0], obj
    raise LookupError(f"cannot resolve {dotted!r}") from last_error


def symbol_card(dotted: str, obj: Any, version: str) -> str:
    """Render a markdown symbol card.

    Parameters
    ----------
    dotted : str
        Dotted path shown in the heading.
    obj : object
        Resolved symbol.
    version : str
        Installed package version.

    Returns
    -------
    str
        Markdown card.
    """
    try:
        signature = str(inspect.signature(obj))
    except (TypeError, ValueError):
        signature = "(unavailable)"
    doc = pydoc.render_doc(obj, renderer=pydoc.TextDoc())
    return (
        f"# `{dotted}`\n"
        f"\n"
        f"- package version: `{version}`\n"
        f"- signature: `{signature}`\n"
        f"\n"
        f"## Doc\n"
        f"\n"
        f"```\n"
        f"{doc.rstrip()}\n"
        f"```\n"
    )


def cache_path(root: Path, package: str, version: str, dotted: str) -> Path:
    """Return ``scratch/api/<lib>/<version>/<topic>.md`` under ``root``."""
    topic = dotted.replace(".", "_")
    return root / "scratch" / "api" / package / version / f"{topic}.md"


def get_symbol(dotted: str, *, root: Path | None = None) -> str:
    """Lookup ``dotted``, write the cache file, and return the card.

    Parameters
    ----------
    dotted : str
        Dotted symbol path.
    root : pathlib.Path or None, optional
        Workspace root for the cache (default: cwd).

    Returns
    -------
    str
        Markdown card (also written to disk).
    """
    workspace = Path.cwd() if root is None else root
    package, obj = load_symbol(dotted)
    version = package_version(package)
    card = symbol_card(dotted, obj, version)
    path = cache_path(workspace, package, version, dotted)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Always refresh so a stale card cannot outlive an env upgrade.
    path.write_text(card, encoding="utf-8")
    return card
