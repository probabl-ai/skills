"""Tests for ``skore-skills review consent``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.review_consent import review_consent


def _write(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_missing_report_stops(tmp_path: Path) -> None:
    payload = review_consent(tmp_path, "01_baseline")

    assert payload == {
        "stem": "01_baseline",
        "action": "stop",
        "reason": "report_html_missing",
    }


def test_first_audit_asks(tmp_path: Path) -> None:
    stem = "01_baseline"
    _write(tmp_path / "scratch" / "results" / stem / "report.html")

    payload = review_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "ask",
        "reason": "first_audit",
        "choices": ["review", "skip", "stop"],
    }


def test_existing_digest_proceeds(tmp_path: Path) -> None:
    stem = "01_baseline"
    _write(tmp_path / "scratch" / "results" / stem / "report.html")
    _write(tmp_path / "scratch" / "audit" / stem / "audit.md", "## Checks summary\n")

    payload = review_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "proceed",
        "reason": "digest_present",
    }
    assert "choices" not in payload


def test_empty_stem_raises() -> None:
    with pytest.raises(ValueError, match="stem is required"):
        review_consent(Path("."), "  ")


def test_cli_prints_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stem = "01_baseline"
    _write(tmp_path / "scratch" / "results" / stem / "report.html")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["review", "consent", "--stem", stem])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["action"] == "ask"


def test_cli_requires_stem() -> None:
    result = CliRunner().invoke(cli, ["review", "consent"])

    assert result.exit_code != 0


def test_cli_rejects_blank_stem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank stem is a usage error, not an ask."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["review", "consent", "--stem", "  "])
    assert result.exit_code != 0
    assert "stem is required" in result.output
