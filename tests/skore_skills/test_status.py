"""Tests for ``skore_skills status`` and ``check workspace``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.workspace import STATUS_KEYS, snapshot


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_status_empty_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty tree reports ``env_manager=none`` and no ``src/``."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["status", "--format", "json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert list(payload) == list(STATUS_KEYS)
    assert payload["env_manager"] == "none"
    assert payload["has_src"] is False
    assert payload["package"] is None
    assert payload["eda"] == "missing"
    assert payload["git"] is False
    assert payload["last_history_stem"] is None
    assert payload["loop_stage"] == "setup"
    assert payload["policy"]["git"]["autocommit"] == "ask"


def test_status_text_format(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``--format text`` is parseable key: value lines."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["status", "--format", "text"])
    assert result.exit_code == 0, result.output
    assert result.output.startswith("package: None")
    assert "env_manager: none" in result.output


def test_status_organized_fixture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A tree with organize-like layout fills the frozen keys."""
    _write(tmp_path / "pyproject.toml", '[project]\nname = "demo-pkg"\n')
    _write(tmp_path / "pixi.toml", '[workspace]\nname = "demo"\n')
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True)
    (tmp_path / "experiments").mkdir()
    (tmp_path / "journal").mkdir()
    _write(tmp_path / "journal" / "JOURNAL.md", "# placeholder\n")
    _write(tmp_path / "journal" / "01_baseline.md", "# note\n")
    (tmp_path / "tests").mkdir()
    _write(tmp_path / "data" / "eda.md", "# eda\n")
    _write(tmp_path / "ruff.toml", 'target-version = "py311"\n')
    (tmp_path / ".git").mkdir()
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["status"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload == {
        "package": "demo-pkg",
        "env_manager": "pixi",
        "has_src": True,
        "has_experiments": True,
        "has_journal": True,
        "has_tests": True,
        "eda": "present",
        "ruff_toml": True,
        "git": True,
        "last_history_stem": "01_baseline",
        "policy": {
            "env_manager": None,
            "package": None,
            "tabular": None,
            "skore_mode": None,
            "git": {"autocommit": "ask"},
            "loop": {"stage": None, "stem": None},
        },
        "loop_stage": "implement",
    }


@pytest.mark.parametrize(
    ("files", "dirs", "toml", "expected"),
    [
        ({"pixi.lock": ""}, (), None, "pixi"),
        ({"uv.lock": ""}, (), None, "uv"),
        (
            {},
            (),
            "[tool.uv]\ndev-dependencies = []\n",
            "uv",
        ),
        ({"poetry.lock": ""}, (), None, "poetry"),
        ({}, (), '[tool.poetry]\nname = "x"\n', "poetry"),
        ({"hatch.toml": ""}, (), None, "hatch"),
        ({}, (), "[tool.hatch.build]\n", "hatch"),
        ({"environment.yml": "name: x\n"}, (), None, "conda"),
        ({"environment.yaml": "name: x\n"}, (), None, "conda"),
        ({"requirements.txt": "click\n"}, (".venv",), None, "pip-venv"),
        ({"requirements.txt": "click\n"}, ("venv",), None, "pip-venv"),
    ],
)
def test_status_each_manager_signal(
    tmp_path: Path,
    files: dict[str, str],
    dirs: tuple[str, ...],
    toml: str | None,
    expected: str,
) -> None:
    """Each documented manager signal is detected from the filesystem."""
    for name, body in files.items():
        _write(tmp_path / name, body)
    for name in dirs:
        (tmp_path / name).mkdir()
    if toml is not None:
        _write(tmp_path / "pyproject.toml", toml)
    assert snapshot(tmp_path)["env_manager"] == expected


def test_status_pyproject_without_tool_is_not_a_manager(tmp_path: Path) -> None:
    """``[project]`` alone does not imply an env manager."""
    _write(tmp_path / "pyproject.toml", '[project]\nname = "solo"\n')
    assert snapshot(tmp_path)["env_manager"] == "none"
    assert snapshot(tmp_path)["package"] == "solo"


def test_status_package_from_src_dir(tmp_path: Path) -> None:
    """Without ``[project].name``, the first ``src/`` directory is used."""
    (tmp_path / "src" / "fromsrc").mkdir(parents=True)
    assert snapshot(tmp_path)["package"] == "fromsrc"


def test_check_workspace_exit_codes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Exit 1 if ``src/`` is missing **and** ``journal/`` is missing.

    Either directory alone is enough to count as scaffolded.
    """
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    empty = runner.invoke(cli, ["check", "workspace", "--format", "json"])
    assert empty.exit_code == 1
    assert json.loads(empty.output) == {"scaffolded": False}

    (tmp_path / "src").mkdir()
    with_src = runner.invoke(cli, ["check", "workspace"])
    assert with_src.exit_code == 0
    assert json.loads(with_src.output) == {"scaffolded": True}

    (tmp_path / "src").rmdir()
    (tmp_path / "journal").mkdir()
    with_journal = runner.invoke(cli, ["check", "workspace", "--format", "text"])
    assert with_journal.exit_code == 0
    assert with_journal.output == "scaffolded\n"


def test_check_workspace_empty_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty dir text format still exits 1."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["check", "workspace", "--format", "text"])
    assert result.exit_code == 1
    assert result.output == "not scaffolded\n"
