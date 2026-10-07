"""Stamp the JOURNAL data-understanding status date."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

_SECTION = re.compile(
    r"^## Data understanding\s*\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
_STATUS_ROW = re.compile(
    r"^(?P<prefix>\s*\|\s*Status\s*\|\s*)(?P<value>.*?)(?P<suffix>\s*\|\s*)$",
    re.MULTILINE,
)
_KEPT_SKIP = re.compile(r"skipped — (?P<day>\d{4}-\d{2}-\d{2})\Z")
_STATUSES = frozenset({"done", "skipped"})


def _kept_skip(value: str) -> str | None:
    match = _KEPT_SKIP.fullmatch(value.strip())
    if match is None:
        return None
    day = match.group("day")
    try:
        date.fromisoformat(day)
    except ValueError:
        return None
    return day


def eda_stamp(root: Path, status: str, *, today: date | None = None) -> dict[str, Any]:
    """Stamp the data-understanding Status date.

    Writes only that cell in ``journal/JOURNAL.md``. ``done`` records
    ``today``. ``skipped`` records ``today`` when no analysis file
    exists, and keeps an existing ISO skip date.

    Raises
    ------
    ValueError
        When the journal, section, or status cannot be stamped.
    """
    if status not in _STATUSES:
        raise ValueError("status must be done or skipped")

    path = root / "journal" / "JOURNAL.md"
    if not path.is_file():
        raise ValueError("journal is missing")

    text = path.read_text(encoding="utf-8")
    section = _SECTION.search(text)
    if section is None:
        raise ValueError("data understanding section is missing")

    body = section.group(1)
    row = _STATUS_ROW.search(body)
    if row is None:
        raise ValueError("data understanding table is missing Status")

    recorded = (today or date.today()).isoformat()
    if status == "skipped":
        if (root / "data_analysis" / "data_analysis.md").is_file():
            raise ValueError("data analysis is present")
        kept = _kept_skip(row.group("value"))
        if kept is not None:
            return {
                "action": "stamped",
                "status": "skipped",
                "recorded_on": kept,
            }
        new_value = f"skipped — {recorded}"
    else:
        new_value = f"done — {recorded}"

    updated = (
        body[: row.start()]
        + f"{row.group('prefix')}{new_value}{row.group('suffix')}"
        + body[row.end() :]
    )
    path.write_text(
        text[: section.start(1)] + updated + text[section.end(1) :],
        encoding="utf-8",
    )
    return {"action": "stamped", "status": status, "recorded_on": recorded}


def render_eda_stamp(root: Path, status: str) -> str:
    """Stamp the data-understanding status and serialize it as JSON."""
    return json.dumps(eda_stamp(root, status), indent=2) + "\n"
