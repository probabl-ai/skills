"""Package root.

Exposes `PROJECT_ROOT`: the absolute path to the project root,
derived from this file's location. Any module that needs to resolve
a project-relative path (data files, fixtures, configs) imports this
constant instead of hard-coding a CWD-relative string. This is what
lets experiment scripts run from any CWD without breaking.

This works because the package is installed in **editable** mode
(see `python-env-manager` § "Editable workspace package"); `__file__`
points back into the source tree at `<root>/src/<pkg>/__init__.py`,
so `parents[2]` is the project root.

If the workspace ever moves away from a `src/` layout, replace the
`parents[2]` walk with an upward search for an anchor file (e.g.
`pyproject.toml`).
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
