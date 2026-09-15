"""CLI helpers for ``skore_skills status``."""

from __future__ import annotations

import json
from pathlib import Path

from skore_skills.workspace import format_status_text, snapshot


def render_status(root: Path, fmt: str) -> str:
    """Serialize the workspace snapshot as JSON or text."""
    payload = snapshot(root)
    if fmt == "text":
        return format_status_text(payload)
    return json.dumps(payload, indent=2) + "\n"
