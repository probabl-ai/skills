"""Tests for the stub ``skore_skills`` CLI."""

from __future__ import annotations

import subprocess
import sys

import pytest
from click.testing import CliRunner

from skore_skills import __version__
from skore_skills.cli import cli, main


def test_help_exits_zero() -> None:
    """``--help`` prints usage and exits 0."""
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Deterministic helpers" in result.output
    assert "python -m skore_skills" in result.output


def test_version_matches_package() -> None:
    """``--version`` reports the package ``__version__``."""
    result = CliRunner().invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output
    assert "skore-skills" in result.output


def test_unknown_subcommand_is_nonzero() -> None:
    """An unknown subcommand fails."""
    result = CliRunner().invoke(cli, ["not-a-command"])
    assert result.exit_code != 0


def test_main_help_raises_systemexit_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    """``main()`` with ``--help`` exits 0 via Click."""
    monkeypatch.setattr(sys, "argv", ["skore-skills", "--help"])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_module_help_subprocess() -> None:
    """``python -m skore_skills --help`` succeeds."""
    completed = subprocess.run(
        [sys.executable, "-m", "skore_skills", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "Deterministic helpers" in completed.stdout


def test_import_version() -> None:
    """The installed package exposes a version string."""
    assert __version__ == "0.7.0"
