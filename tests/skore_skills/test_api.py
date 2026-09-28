"""Tests for ``skore_skills api get`` / ``api version``."""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.api import load_symbol
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


def test_api_get_dynamic_eval_in_mode_method(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Classes with ``__getattr__`` and ``_eval_in_mode`` expose mode methods."""
    module = types.ModuleType("dynmode_probe")

    class Probe:
        def __getattr__(self, name: str) -> object:
            raise AttributeError(name)

        def _eval_in_mode(self, mode: str, environment: dict) -> None:
            return None

    module.Probe = Probe
    monkeypatch.setitem(sys.modules, "dynmode_probe", module)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["api", "get", "dynmode_probe.Probe.fit"])
    assert result.exit_code == 0, result.output
    assert "environment" in result.output
    assert "env-dict" in result.output
    caches = list((tmp_path / "scratch" / "api").rglob("*.md"))
    assert len(caches) == 1


def test_api_get_getattr_without_eval_in_mode_still_fails() -> None:
    """``__getattr__`` alone does not synthesize a method."""
    module = types.ModuleType("dynmode_getattr_only")

    class Probe:
        def __getattr__(self, name: str) -> object:
            raise AttributeError(name)

    module.Probe = Probe
    sys.modules["dynmode_getattr_only"] = module
    try:
        with pytest.raises(LookupError, match="cannot resolve"):
            load_symbol("dynmode_getattr_only.Probe.fit")
    finally:
        del sys.modules["dynmode_getattr_only"]


def test_api_get_real_estimator_fit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Real class methods still resolve through ``getattr``."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["api", "get", "sklearn.dummy.DummyRegressor.fit"])
    assert result.exit_code == 0, result.output
    assert "DummyRegressor" in result.output or "fit" in result.output


def test_api_get_missing_method_on_real_class(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown methods on ordinary classes still fail."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli, ["api", "get", "sklearn.model_selection.KFold.not_a_method"]
    )
    assert result.exit_code != 0
    assert not (tmp_path / "scratch" / "api").exists()


def test_api_get_skrub_learner_fit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``SkrubLearner.fit`` is a dynamic DataOp-mode method."""
    pytest.importorskip("skrub")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["api", "get", "skrub.SkrubLearner.fit"])
    assert result.exit_code == 0, result.output
    assert "environment" in result.output
    assert "env-dict" in result.output


def test_symbol_card_unavailable_signature() -> None:
    """Objects without a signature still render a card."""
    from skore_skills.api import symbol_card

    card = symbol_card("example.thing", 1, "1.2.3")
    assert "- signature: `(unavailable)`" in card
    assert "example.thing" in card
    assert "1.2.3" in card
