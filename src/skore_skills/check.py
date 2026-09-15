"""CLI helpers for ``skore_skills check workspace``."""

from __future__ import annotations

import json
from pathlib import Path

from skore_skills.workspace import is_scaffolded


def render_workspace_check(root: Path, fmt: str) -> tuple[str, int]:
    """Return stdout and process exit code for a workspace check.

    Exit 1 when ``src/`` is missing **and** ``journal/`` is missing.
    """
    ok = is_scaffolded(root)
    code = 0 if ok else 1
    if fmt == "text":
        text = "scaffolded\n" if ok else "not scaffolded\n"
        return text, code
    return json.dumps({"scaffolded": ok}) + "\n", code
