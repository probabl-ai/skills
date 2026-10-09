"""Shipped user artifacts must not document the skills framework."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CATALOG = json.loads((REPO / ".catalog.json").read_text(encoding="utf-8"))
SKILL_IDS = tuple(skill["id"] for skill in CATALOG["skills"])

RESULT_EMBED = re.compile(r"<!--\s*results-embed:\s*[A-Za-z0-9_-]+\s*-->")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
CELL_MARKER = re.compile(r"^#\s*%%")
HASH_COMMENT = re.compile(r"^#\s?(?P<body>.*)$")

BANNED = (
    re.compile(r"skore_skills"),
    re.compile(r"python\s+-m"),
    re.compile(r"cells\s+run", re.I),
    re.compile(r"site\s+build", re.I),
    re.compile(r"notebook\s+convert", re.I),
    re.compile(r"marker is durable", re.I),
    re.compile(r"scratch/results"),
    *(
        re.compile(rf"(?<![\w-]){re.escape(skill_id)}(?![\w-])")
        for skill_id in SKILL_IDS
    ),
)


def _template_paths() -> list[Path]:
    paths = [
        REPO / "src" / "skore_skills" / "data" / "experiment_design.md",
        REPO / "src" / "skore_skills" / "data" / "JOURNAL.md",
    ]
    paths.extend(
        sorted((REPO / "src" / "skore_skills" / "templates").glob("readme_*.md"))
    )
    for folder in sorted((REPO / "skills").glob("*/templates")):
        paths.extend(
            path for path in sorted(folder.glob("*")) if path.suffix in {".py", ".md"}
        )
    return paths


def _hits(text: str) -> list[str]:
    found: list[str] = []
    for pattern in BANNED:
        match = pattern.search(text)
        if match:
            found.append(match.group(0))
    return found


def _python_comment_bodies(text: str) -> Iterator[str]:
    for line in text.splitlines():
        stripped = line.lstrip()
        if CELL_MARKER.match(stripped):
            continue
        match = HASH_COMMENT.match(stripped)
        if match:
            yield match.group("body")


@pytest.mark.parametrize(
    "path", _template_paths(), ids=lambda path: str(path.relative_to(REPO))
)
def test_user_bound_templates_are_data_science_prose(path: Path) -> None:
    """Notebook/markdown templates omit CLI, skill ids, and HTML authoring hints."""
    text = path.read_text(encoding="utf-8")
    leftover = [
        comment
        for comment in HTML_COMMENT.findall(text)
        if RESULT_EMBED.fullmatch(comment.strip()) is None
    ]
    assert leftover == [], f"{path}: unexpected HTML comments {leftover!r}"

    scanned = "\n".join(_python_comment_bodies(text)) if path.suffix == ".py" else text
    scanned = RESULT_EMBED.sub("", scanned)
    hits = _hits(scanned)
    assert hits == [], f"{path}: banned phrases in user-facing prose {hits!r}"
