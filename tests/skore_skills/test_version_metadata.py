"""Tests for the release version read by the Hatch metadata hook."""

from __future__ import annotations

from pathlib import Path

from hatch.metadata import version_from_root


def test_version_from_root_reads_version_file(tmp_path: Path) -> None:
    """A release build uses the tag written to ``VERSION.txt``."""
    (tmp_path / "VERSION.txt").write_text("1.2.3\n", encoding="utf-8")

    assert version_from_root(tmp_path, "0.0.0+unknown") == "1.2.3"


def test_version_from_root_uses_default_when_missing(tmp_path: Path) -> None:
    """A local checkout without ``VERSION.txt`` keeps the fallback version."""
    assert version_from_root(tmp_path, "0.0.0+unknown") == "0.0.0+unknown"
