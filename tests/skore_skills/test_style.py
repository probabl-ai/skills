"""Tests for ``skore_skills style``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from skore_skills import style as style_mod
from skore_skills.cli import cli


def test_style_init_copies_packaged_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``style --init`` writes ``[tool.ruff]`` without requiring ruff."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["style", "--init"])
    assert result.exit_code == 0, result.output
    config = tmp_path / "pyproject.toml"
    assert config.is_file()
    assert 'target-version = "py312"' in config.read_text(encoding="utf-8")
    assert not (tmp_path / "ruff.toml").exists()


def test_style_init_preserves_existing_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Initialization never overwrites a workspace's Ruff policy."""
    config = tmp_path / "ruff.toml"
    config.write_text("line-length = 100\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["style", "--init"])
    assert result.exit_code == 0, result.output
    assert "already configured" in result.output
    assert config.read_text(encoding="utf-8") == "line-length = 100\n"


def test_style_missing_ruff(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing ruff exits non-zero with an env-manager install hint."""
    monkeypatch.chdir(tmp_path)

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 1
            stdout = ""
            stderr = "No module named ruff"

        if argv[-1:] == ["--version"] or (len(argv) >= 3 and argv[-1] == "--version"):
            return Result()
        raise AssertionError(f"unexpected argv {argv}")

    monkeypatch.setattr(style_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["style"])
    assert result.exit_code != 0
    assert "env add" in result.output


def test_style_default_globs_skip_vendored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Default targets include src/experiments and skip node_modules."""
    (tmp_path / "src").mkdir()
    (tmp_path / "experiments").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "pkg.py").write_text("x=1\n", encoding="utf-8")
    (tmp_path / "src" / "mod.py").write_text("x=1\n", encoding="utf-8")
    (tmp_path / "top.py").write_text("x=1\n", encoding="utf-8")
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.py").write_text(
        "x=1\n", encoding="utf-8"
    )
    (tmp_path / "audit").mkdir()
    monkeypatch.chdir(tmp_path)

    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 0

        if argv[-1] == "--version":
            return Result()
        seen.append(argv)
        return Result()

    monkeypatch.setattr(style_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["style"])
    assert result.exit_code == 0, result.output
    assert seen
    check_argv = seen[0]
    joined = " ".join(check_argv)
    assert str(tmp_path / "src") in check_argv
    assert str(tmp_path / "experiments") in check_argv
    assert str(tmp_path / "audit") in check_argv
    assert str(tmp_path / "data_analysis") in check_argv
    assert str(tmp_path / "top.py") in check_argv
    assert "node_modules" in joined  # exclude flag
    assert str(tmp_path / "node_modules") not in check_argv
    assert "no [tool.ruff]" in result.output


def test_style_given_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Explicit paths are forwarded instead of default globs."""
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "only.py"
    target.write_text("x=1\n", encoding="utf-8")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 0

        if argv[-1] == "--version":
            return Result()
        seen.append(argv)
        return Result()

    monkeypatch.setattr(style_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["style", "only.py"])
    assert result.exit_code == 0, result.output
    assert any(str(target) in argv for argv in seen)
    assert not any(str(tmp_path / "src") in argv for argv in seen)
    assert "no [tool.ruff]" not in result.output


def test_style_fixes_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Live ruff check --fix then format rewrites an easy unused import."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    messy = tmp_path / "src" / "messy.py"
    messy.write_text("import os\n\nx = 1\n", encoding="utf-8")
    result = CliRunner().invoke(cli, ["style"])
    assert result.exit_code == 0, result.output
    text = messy.read_text(encoding="utf-8")
    assert "import os" not in text
    assert "x = 1" in text


def test_style_empty_tree_is_ok(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No default targets is a successful no-op once ruff is present."""
    monkeypatch.chdir(tmp_path)

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 0

        if argv[-1] == "--version":
            return Result()
        raise AssertionError("ruff should not run without targets")

    monkeypatch.setattr(style_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["style"])
    assert result.exit_code == 0, result.output


def test_style_propagates_ruff_check_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failing ``ruff check`` exit code is returned even if format succeeds."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x=1\n", encoding="utf-8")
    calls = {"n": 0}

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 0

        if argv[-1] == "--version":
            return Result()
        calls["n"] += 1
        if "check" in argv:
            return type("R", (), {"returncode": 1})()
        return Result()

    monkeypatch.setattr(style_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["style"])
    assert result.exit_code == 1
    assert calls["n"] == 2


def test_style_init_appends_to_existing_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--init`` appends ``[tool.ruff]`` when pyproject.toml already exists."""
    config = tmp_path / "pyproject.toml"
    config.write_text('[project]\nname = "demo"\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["style", "--init"])
    assert result.exit_code == 0, result.output
    assert "wrote [tool.ruff]" in result.output
    text = config.read_text(encoding="utf-8")
    assert 'name = "demo"' in text
    assert "[tool.ruff]" in text
