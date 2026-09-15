"""Tests for ``.skore`` workspace-section policy helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.policy import (
    empty_policy,
    save_policy,
    set_policy_value,
)
from skore_skills.workspace import snapshot


def test_status_merges_policy_file(tmp_path: Path) -> None:
    """Saved policy appears under ``status`` and overrides inferred stage."""
    policy = empty_policy()
    policy["env_manager"] = "pixi"
    policy["loop"]["stage"] = "audit"
    save_policy(tmp_path, policy)
    payload = snapshot(tmp_path)
    assert payload["policy"]["env_manager"] == "pixi"
    assert payload["loop_stage"] == "audit"


def test_policy_set_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``policy set`` writes JSON the next ``status`` call can read."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["policy", "set", "git.autocommit", "off"])
    assert result.exit_code == 0, result.output
    saved = json.loads((tmp_path / ".skore").read_text())
    assert saved["workspace"]["git"]["autocommit"] == "off"
    status = CliRunner().invoke(cli, ["status"])
    assert json.loads(status.output)["policy"]["git"]["autocommit"] == "off"


def test_policy_set_rejects_unknown_key(tmp_path: Path) -> None:
    """Unknown keys fail before writing."""
    with pytest.raises(ValueError, match="unknown policy key"):
        set_policy_value(tmp_path, "not-a-key", "x")


def test_save_policy_merges_existing_hub_keys(tmp_path: Path) -> None:
    """Unknown top-level keys survive a workspace write."""
    (tmp_path / ".skore").write_text(
        json.dumps({"api_key": "secret-token", "hub_uri": "https://hub.example"})
        + "\n",
        encoding="utf-8",
    )
    policy = empty_policy()
    policy["env_manager"] = "pixi"
    save_policy(tmp_path, policy)
    saved = json.loads((tmp_path / ".skore").read_text(encoding="utf-8"))
    assert saved["api_key"] == "secret-token"
    assert saved["hub_uri"] == "https://hub.example"
    assert saved["workspace"]["env_manager"] == "pixi"
    payload = snapshot(tmp_path)
    dumped = json.dumps(payload)
    assert "secret-token" not in dumped
    assert "api_key" not in dumped
    assert payload["policy"]["env_manager"] == "pixi"


def test_save_policy_rejects_skore_directory(tmp_path: Path) -> None:
    """A ``.skore`` directory is not a JSON file."""
    (tmp_path / ".skore").mkdir()
    with pytest.raises(ValueError, match="directory"):
        save_policy(tmp_path, empty_policy())


def test_load_legacy_flat_workspace_json(tmp_path: Path) -> None:
    """One-release read of leftover ``.skore-workspace.json``."""
    (tmp_path / ".skore-workspace.json").write_text(
        json.dumps({"env_manager": "uv", "git": {"autocommit": "on"}}) + "\n",
        encoding="utf-8",
    )
    assert snapshot(tmp_path)["policy"]["env_manager"] == "uv"
    assert snapshot(tmp_path)["policy"]["git"]["autocommit"] == "on"


def test_infer_evaluate_then_audit(tmp_path: Path) -> None:
    """Smoke without audit is evaluate; reports present becomes audit."""
    (tmp_path / "src").mkdir()
    (tmp_path / "journal").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "eda.md").write_text("# eda\n", encoding="utf-8")
    (tmp_path / "journal" / "01_baseline.md").write_text("# n\n", encoding="utf-8")
    smoke = tmp_path / "tests" / "smoke"
    smoke.mkdir(parents=True)
    (smoke / "test_01_baseline.py").write_text("# smoke\n", encoding="utf-8")
    assert snapshot(tmp_path)["loop_stage"] == "evaluate"
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "01_baseline").mkdir()
    assert snapshot(tmp_path)["loop_stage"] == "audit"
    audit = tmp_path / "audit"
    audit.mkdir()
    (audit / "01_baseline.py").write_text("# audit\n", encoding="utf-8")
    assert snapshot(tmp_path)["loop_stage"] == "backlog"
