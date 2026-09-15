"""Tests for ``skore_skills cells run``."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from skore_skills.cli import cli

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_notebook.py"


def test_cells_run_digest_and_dest(tmp_path: Path) -> None:
    """CLI digest includes markdown, stdout, last-expr, and errors; dest matches."""
    dest = tmp_path / "out.md"
    result = CliRunner().invoke(cli, ["cells", "run", str(FIXTURE), str(dest)])
    assert result.exit_code == 0, result.output
    assert "Title" in result.output
    assert "hello" in result.output
    assert "2 + 2" in result.output
    assert "ValueError" in result.output
    assert dest.is_file()
    assert dest.read_text(encoding="utf-8") == result.output


def test_cells_run_missing_file() -> None:
    """Missing source exits non-zero."""
    result = CliRunner().invoke(cli, ["cells", "run", "no-such-notebook.py"])
    assert result.exit_code != 0
