"""Tests for ``skore_skills scaffold``."""

from __future__ import annotations

import ast
import compileall
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli


def test_scaffold_tree_and_no_placeholders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scaffold substitutes ``<pkg>`` and matches the skill file set."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["scaffold", "--package", "demo_pkg"])
    assert result.exit_code == 0, result.output
    src = tmp_path / "src" / "demo_pkg"
    assert (src / "__init__.py").is_file()
    assert (src / "data.py").is_file()
    assert (src / "features.py").is_file()
    assert (src / "pipeline.py").is_file()
    assert (src / "evaluate.py").is_file()
    assert (tmp_path / "experiments" / "01_baseline.py").is_file()
    assert (tmp_path / "pyproject.toml").is_file()
    assert (tmp_path / ".gitignore").is_file()
    assert (tmp_path / "ruff.toml").is_file()
    assert (tmp_path / "journal" / "JOURNAL.md").is_file()
    journal = (tmp_path / "journal" / "JOURNAL.md").read_text(encoding="utf-8")
    assert "## History" in journal
    assert "## Backlog" in journal
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "demo-pkg"' in pyproject
    experiment = (tmp_path / "experiments" / "01_baseline.py").read_text(
        encoding="utf-8"
    )
    assert "from demo_pkg import PROJECT_ROOT" in experiment
    assert "<pkg>" not in experiment
    tree = ast.parse(experiment)
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"evaluate", "put"}
        for node in ast.walk(tree)
    )
    for path in tmp_path.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".toml", ".md"}:
            text = path.read_text(encoding="utf-8")
            assert "<pkg>" not in text
            assert "<SKORE_PROJECT_INIT>" not in text
    assert compileall.compile_dir(str(src), quiet=1)


def test_scaffold_refuses_without_force(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A second run on a complete layout exits non-zero unless ``--force``."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    first = runner.invoke(cli, ["scaffold", "--package", "demo_pkg"])
    assert first.exit_code == 0, first.output
    second = runner.invoke(cli, ["scaffold", "--package", "demo_pkg"])
    assert second.exit_code != 0
    assert "refusing" in second.output
    forced = runner.invoke(cli, ["scaffold", "--package", "demo_pkg", "--force"])
    assert forced.exit_code == 0, forced.output


def test_scaffold_requires_package() -> None:
    """A scaffold mode is mandatory."""
    result = CliRunner().invoke(cli, ["scaffold"])
    assert result.exit_code != 0
    assert "--package or --journal" in result.output


def test_scaffold_rejects_invalid_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hyphenated names are not importable package directories."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["scaffold", "--package", "demo-pkg"])
    assert result.exit_code != 0
    assert "identifier" in result.output


def test_scaffold_journal_index_and_design(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Journal mode initializes the index and a substituted design note."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli,
        ["scaffold", "--journal", "--stem", "02_target_transform"],
    )
    assert result.exit_code == 0, result.output
    journal = tmp_path / "journal" / "JOURNAL.md"
    design = tmp_path / "journal" / "02_target_transform.md"
    assert "## History" in journal.read_text(encoding="utf-8")
    assert design.read_text(encoding="utf-8").startswith("# 02_target_transform\n")


def test_scaffold_journal_preserves_index_and_refuses_existing_design(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Journal mode preserves the index and requires force for a design."""
    journal_dir = tmp_path / "journal"
    journal_dir.mkdir()
    index = journal_dir / "JOURNAL.md"
    index.write_text("# Existing\n", encoding="utf-8")
    design = journal_dir / "01_baseline.md"
    design.write_text("# Existing design\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli,
        ["scaffold", "--journal", "--stem", "01_baseline"],
    )
    assert result.exit_code != 0
    assert "refusing to overwrite" in result.output
    assert index.read_text(encoding="utf-8") == "# Existing\n"
    assert design.read_text(encoding="utf-8") == "# Existing design\n"
    forced = CliRunner().invoke(
        cli,
        ["scaffold", "--journal", "--stem", "01_baseline", "--force"],
    )
    assert forced.exit_code == 0, forced.output
    assert "## History" in index.read_text(encoding="utf-8")
    assert design.read_text(encoding="utf-8").startswith("# 01_baseline\n")


@pytest.mark.parametrize(
    "argv",
    [
        ["scaffold", "--journal", "--stem", "../bad"],
        ["scaffold", "--package", "demo", "--stem", "01_baseline"],
        ["scaffold", "--package", "demo", "--journal"],
    ],
)
def test_scaffold_journal_rejects_bad_modes(argv: list[str]) -> None:
    """Journal mode rejects unsafe stems and conflicting options."""
    result = CliRunner().invoke(cli, argv)
    assert result.exit_code != 0
