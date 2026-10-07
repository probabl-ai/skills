"""Tests for ``skore-skills eda stamp``."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.eda import eda_stamp


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _journal(status: str = "n/a") -> str:
    return (
        "# JOURNAL\n\n"
        "## Status\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        "| Last experiment | n/a |\n\n"
        "## Data understanding\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        f"| Status | {status} |\n"
        "| Summary | shape stays |\n"
        "| Report | [data_analysis/data_analysis.md]"
        "(../data_analysis/data_analysis.md) |\n\n"
        "## Modeling decisions\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        "| Status | locked |\n"
    )


def test_eda_stamp_done_rewrites_only_the_status_cell(tmp_path: Path) -> None:
    """``done`` records today's date and leaves summary and report."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal())

    payload = eda_stamp(tmp_path, "done", today=date(2026, 10, 6))

    assert payload == {
        "action": "stamped",
        "status": "done",
        "recorded_on": "2026-10-06",
    }
    text = path.read_text(encoding="utf-8")
    assert "| Status | done — 2026-10-06 |" in text
    assert "| Summary | shape stays |" in text
    assert "| Report | [data_analysis/data_analysis.md]" in text
    assert "| Last experiment | n/a |" in text
    assert "| Status | locked |" in text


def test_eda_stamp_done_refreshes_the_date(tmp_path: Path) -> None:
    """A later ``done`` stamp replaces the previous recording date."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal("done — 2026-09-01"))

    payload = eda_stamp(tmp_path, "done", today=date(2026, 10, 6))

    assert payload["recorded_on"] == "2026-10-06"
    text = path.read_text(encoding="utf-8")
    assert "done — 2026-10-06" in text
    assert "2026-09-01" not in text


def test_eda_stamp_skipped_writes_the_status_cell(tmp_path: Path) -> None:
    """``skipped`` records today's date when no analysis file exists."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal())

    payload = eda_stamp(tmp_path, "skipped", today=date(2026, 10, 6))

    assert payload["status"] == "skipped"
    assert payload["recorded_on"] == "2026-10-06"
    text = path.read_text(encoding="utf-8")
    assert "| Status | skipped — 2026-10-06 |" in text
    assert "| Summary | shape stays |" in text


def test_eda_stamp_skipped_keeps_an_existing_date(tmp_path: Path) -> None:
    """A second skip does not replace an ISO date already on the row."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal())
    eda_stamp(tmp_path, "skipped", today=date(2026, 9, 18))
    before = path.read_text(encoding="utf-8")

    payload = eda_stamp(tmp_path, "skipped", today=date(2026, 10, 6))

    assert payload["recorded_on"] == "2026-09-18"
    assert path.read_text(encoding="utf-8") == before


def test_eda_stamp_skipped_replaces_an_invalid_date(tmp_path: Path) -> None:
    """A skip row without an ISO date is stamped."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal("skipped — 2026-13-01"))

    payload = eda_stamp(tmp_path, "skipped", today=date(2026, 10, 6))

    assert payload["recorded_on"] == "2026-10-06"
    assert "skipped — 2026-10-06" in path.read_text(encoding="utf-8")


def test_eda_stamp_skipped_refuses_a_present_analysis(tmp_path: Path) -> None:
    """A written analysis cannot be marked skipped."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal("done — 2026-09-01"))
    _write(tmp_path / "data_analysis" / "data_analysis.md", "# report\n")
    before = path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="data analysis is present"):
        eda_stamp(tmp_path, "skipped", today=date(2026, 10, 6))

    assert path.read_text(encoding="utf-8") == before


def test_eda_stamp_requires_the_journal(tmp_path: Path) -> None:
    """A missing journal is an error."""
    with pytest.raises(ValueError, match="journal is missing"):
        eda_stamp(tmp_path, "done", today=date(2026, 10, 6))


def test_eda_stamp_requires_the_section(tmp_path: Path) -> None:
    """A journal without Data understanding cannot be stamped."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, "# JOURNAL\n\n## History\n")
    before = path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="data understanding section is missing"):
        eda_stamp(tmp_path, "done", today=date(2026, 10, 6))

    assert path.read_text(encoding="utf-8") == before


def test_eda_stamp_requires_the_status_row(tmp_path: Path) -> None:
    """A Data understanding table without Status cannot be stamped."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(
        path,
        "# JOURNAL\n\n## Data understanding\n\n"
        "| Variable | Value |\n|---|---|\n| Summary | shape stays |\n",
    )
    before = path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="missing Status"):
        eda_stamp(tmp_path, "done", today=date(2026, 10, 6))

    assert path.read_text(encoding="utf-8") == before


def test_eda_stamp_rejects_an_unknown_status(tmp_path: Path) -> None:
    """Only done and skipped are status values."""
    with pytest.raises(ValueError, match="status must be done or skipped"):
        eda_stamp(tmp_path, "maybe", today=date(2026, 10, 6))


def test_eda_stamp_cli_prints_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI stamps Status and prints the recording date."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal())
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["eda", "stamp", "--status", "done"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["status"] == "done"
    assert payload["recorded_on"] == date.today().isoformat()
    assert f"done — {payload['recorded_on']}" in path.read_text(encoding="utf-8")


def test_eda_stamp_cli_rejects_a_bad_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unknown --status is a usage error and does not write."""
    path = tmp_path / "journal" / "JOURNAL.md"
    _write(path, _journal())
    before = path.read_text(encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["eda", "stamp", "--status", "maybe"])

    assert result.exit_code == 2
    assert path.read_text(encoding="utf-8") == before


def test_eda_stamp_cli_requires_the_journal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A missing journal is a usage error."""
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["eda", "stamp", "--status", "done"])

    assert result.exit_code != 0
    assert "journal is missing" in result.output


def test_eda_stamp_cli_requires_status() -> None:
    """Omitting --status is a usage error."""
    result = CliRunner().invoke(cli, ["eda", "stamp"])

    assert result.exit_code == 2
    assert "Missing option" in result.output
