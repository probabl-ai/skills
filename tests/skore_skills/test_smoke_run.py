"""Tests for ``skore-skills smoke run``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.smoke import run_smoke


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _payload(output: str) -> dict[str, object]:
    start = output.rfind("{")
    assert start != -1, output
    return json.loads(output[start:])


def test_missing_file_is_stop(tmp_path: Path) -> None:
    payload, code = run_smoke(tmp_path, "01_baseline")
    assert code == 1
    assert payload["action"] == "stop"
    assert payload["reason"] == "smoke_missing"


def test_empty_stem_raises() -> None:
    with pytest.raises(ValueError, match="stem is required"):
        run_smoke(Path("."), "  ")


def test_green_pytest_is_proceed(tmp_path: Path) -> None:
    _write(
        tmp_path / "tests" / "smoke" / "test_01_ok.py",
        "def test_ok():\n    assert True\n",
    )
    payload, code = run_smoke(tmp_path, "01_ok")
    assert code == 0
    assert payload["action"] == "proceed"
    assert payload["reason"] == "green"
    assert payload["exit_code"] == 0


def test_red_pytest_is_stop(tmp_path: Path) -> None:
    _write(
        tmp_path / "tests" / "smoke" / "test_01_bad.py",
        "def test_bad():\n    assert False\n",
    )
    payload, code = run_smoke(tmp_path, "01_bad")
    assert code != 0
    assert payload["action"] == "stop"
    assert payload["reason"] == "red"


def test_cli_missing_stem() -> None:
    result = CliRunner().invoke(cli, ["smoke", "run"])
    assert result.exit_code == 2


def test_cli_prints_json_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["smoke", "run", "--stem", "01_x"])
    assert result.exit_code == 1
    payload = _payload(result.output)
    assert payload["action"] == "stop"
    assert payload["reason"] == "smoke_missing"


def test_cli_green(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    _write(
        tmp_path / "tests" / "smoke" / "test_01_ok.py",
        "def test_ok():\n    assert True\n",
    )
    result = CliRunner().invoke(cli, ["smoke", "run", "--stem", "01_ok"])
    assert result.exit_code == 0, result.output
    payload = _payload(result.output)
    assert payload["action"] == "proceed"


def test_cli_rejects_blank_stem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank stem is a usage error before pytest starts."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["smoke", "run", "--stem", "  "])
    assert result.exit_code != 0
    assert "stem is required" in result.output


def test_rel_keeps_paths_outside_the_workspace(tmp_path: Path) -> None:
    """A smoke path that is not under the root is reported as given."""
    from skore_skills.smoke import _rel

    outside = tmp_path.parent / "elsewhere.py"
    assert _rel(tmp_path, outside) == outside.as_posix()
