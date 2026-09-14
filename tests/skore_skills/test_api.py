"""Tests for ``skore_skills api get`` / ``api version``."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli


def test_api_get_kfold(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``api get`` writes a KFold card under scratch/api."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["api", "get", "sklearn.model_selection.KFold"])
    assert result.exit_code == 0, result.output
    assert "n_splits" in result.output
    assert "KFold" in result.output
    caches = list((tmp_path / "scratch" / "api").rglob("*.md"))
    assert len(caches) == 1
    assert caches[0].read_text(encoding="utf-8") == result.output


def test_api_get_unknown_symbol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown dotted path exits non-zero and writes no cache."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli, ["api", "get", "sklearn.model_selection.NotARealEstimator"]
    )
    assert result.exit_code != 0
    assert not (tmp_path / "scratch" / "api").exists()


def test_api_get_missing_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing top-level package exits non-zero."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["api", "get", "definitely_not_installed.Foo"])
    assert result.exit_code != 0


def test_api_get_always_refreshes_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A second ``api get`` overwrites an existing cache file."""
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    first = runner.invoke(cli, ["api", "get", "sklearn.model_selection.KFold"])
    assert first.exit_code == 0, first.output
    caches = list((tmp_path / "scratch" / "api").rglob("*.md"))
    assert len(caches) == 1
    caches[0].write_text("stale", encoding="utf-8")
    second = runner.invoke(cli, ["api", "get", "sklearn.model_selection.KFold"])
    assert second.exit_code == 0, second.output
    assert caches[0].read_text(encoding="utf-8") == second.output
    assert "stale" not in second.output


def test_api_get_undotted_symbol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A bare package name is not a dotted symbol path."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["api", "get", "sklearn"])
    assert result.exit_code != 0
    assert not (tmp_path / "scratch" / "api").exists()


def test_api_version_sklearn() -> None:
    """``api version sklearn`` prints a version string."""
    result = CliRunner().invoke(cli, ["api", "version", "sklearn"])
    assert result.exit_code == 0
    assert result.output.strip()


def test_api_version_missing() -> None:
    """Missing package version lookup fails."""
    result = CliRunner().invoke(cli, ["api", "version", "definitely_not_installed"])
    assert result.exit_code != 0
