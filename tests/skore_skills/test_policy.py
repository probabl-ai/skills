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
    policy["loop"]["stage"] = "evaluate"
    save_policy(tmp_path, policy)
    payload = snapshot(tmp_path)
    assert payload["policy"]["env_manager"] == "pixi"
    assert payload["loop_stage"] == "evaluate"


def test_policy_set_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``policy set`` writes JSON the next ``status`` call can read."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["policy", "set", "git.autocommit", "off"])
    assert result.exit_code == 0, result.output
    saved = json.loads((tmp_path / ".skore").read_text())
    assert saved["workspace"]["git"]["autocommit"] == "off"
    status = CliRunner().invoke(cli, ["status"])
    assert json.loads(status.output)["policy"]["git"]["autocommit"] == "off"


def test_policy_set_env_managed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``env.managed`` accepts true/false aliases."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["policy", "set", "env.managed", "false"])
    assert result.exit_code == 0, result.output
    saved = json.loads((tmp_path / ".skore").read_text())
    assert saved["workspace"]["env"]["managed"] is False
    status = json.loads(CliRunner().invoke(cli, ["status"]).output)
    assert status["policy"]["env"]["managed"] is False
    again = CliRunner().invoke(cli, ["policy", "set", "env.managed", "yes"])
    assert again.exit_code == 0, again.output
    assert json.loads(again.output)["env"]["managed"] is True


def test_policy_set_rejects_invalid_managed(tmp_path: Path) -> None:
    """Managed accepts only boolean aliases."""
    with pytest.raises(ValueError, match="true or false"):
        set_policy_value(tmp_path, "env.managed", "maybe")


def test_policy_set_notebooks_and_site(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``notebooks`` and ``site`` persist as booleans."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["policy", "set", "notebooks", "true"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["notebooks"] is True
    again = CliRunner().invoke(cli, ["policy", "set", "site", "off"])
    assert again.exit_code == 0, again.output
    assert json.loads(again.output)["site"] is False
    with pytest.raises(ValueError, match="true or false"):
        set_policy_value(tmp_path, "site", "maybe")


def test_policy_set_rejects_invalid_autocommit(tmp_path: Path) -> None:
    """Autocommit accepts only ``off`` or ``on``."""
    with pytest.raises(ValueError, match="off or on"):
        set_policy_value(tmp_path, "git.autocommit", "maybe")


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


def test_infer_evaluate_until_audit_file(tmp_path: Path) -> None:
    """Smoke without an audit file is evaluate; audit file becomes backlog."""
    (tmp_path / "src").mkdir()
    (tmp_path / "journal").mkdir()
    (tmp_path / "data_analysis").mkdir()
    (tmp_path / "data_analysis" / "data_analysis.md").write_text(
        "# eda\n", encoding="utf-8"
    )
    (tmp_path / "journal" / "01_baseline.md").write_text("# n\n", encoding="utf-8")
    smoke = tmp_path / "tests" / "smoke"
    smoke.mkdir(parents=True)
    (smoke / "test_01_baseline.py").write_text("# smoke\n", encoding="utf-8")
    assert snapshot(tmp_path)["loop_stage"] == "evaluate"
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "01_baseline").mkdir()
    assert snapshot(tmp_path)["loop_stage"] == "evaluate"
    audit = tmp_path / "audit"
    audit.mkdir()
    (audit / "01_baseline.py").write_text("# audit\n", encoding="utf-8")
    assert snapshot(tmp_path)["loop_stage"] == "backlog"


def test_policy_set_rejects_audit_loop_stage(tmp_path: Path) -> None:
    """Audit is not a persistable loop stage."""
    with pytest.raises(ValueError, match="loop.stage must be one of"):
        set_policy_value(tmp_path, "loop.stage", "audit")


def test_policy_set_loop_keys(tmp_path: Path) -> None:
    """``loop.stage`` and ``loop.stem`` persist on the nested mapping."""
    policy = set_policy_value(tmp_path, "loop.stage", "implement")
    assert policy["loop"]["stage"] == "implement"
    policy = set_policy_value(tmp_path, "loop.stem", "01_baseline")
    assert policy["loop"]["stem"] == "01_baseline"


def test_policy_set_cli_rejects_unknown_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown keys fail at the CLI before a write."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["policy", "set", "nope", "x"])
    assert result.exit_code != 0
    assert "unknown policy key" in result.output
    assert not (tmp_path / ".skore").exists()


def test_load_policy_managed_string_aliases(tmp_path: Path) -> None:
    """String managed aliases fold to booleans."""
    from skore_skills.policy import load_policy

    (tmp_path / ".skore").write_text(
        json.dumps({"workspace": {"env": {"managed": "YES"}}}) + "\n",
        encoding="utf-8",
    )
    assert load_policy(tmp_path)["env"]["managed"] is True
    (tmp_path / ".skore").write_text(
        json.dumps({"workspace": {"env": {"managed": "Off"}}}) + "\n",
        encoding="utf-8",
    )
    assert load_policy(tmp_path)["env"]["managed"] is False


def test_load_policy_ignores_non_object_and_reads_flat_document(tmp_path: Path) -> None:
    """A JSON list is ignored; a flat ``.skore`` object is the workspace section."""
    from skore_skills.policy import load_policy

    (tmp_path / ".skore").write_text("[]\n", encoding="utf-8")
    assert load_policy(tmp_path) == empty_policy()
    (tmp_path / ".skore").write_text(
        json.dumps({"env_manager": "uv"}) + "\n", encoding="utf-8"
    )
    assert load_policy(tmp_path)["env_manager"] == "uv"


def test_load_legacy_nested_workspace_section(tmp_path: Path) -> None:
    """A leftover file may already nest keys under ``workspace``."""
    from skore_skills.policy import load_policy

    (tmp_path / ".skore-workspace.json").write_text(
        json.dumps({"workspace": {"package": "demo"}}) + "\n",
        encoding="utf-8",
    )
    assert load_policy(tmp_path)["package"] == "demo"


def test_load_policy_rejects_skore_directory(tmp_path: Path) -> None:
    """``.skore`` as a directory is not a policy file."""
    from skore_skills.policy import load_policy

    (tmp_path / ".skore").mkdir()
    with pytest.raises(ValueError, match="directory"):
        load_policy(tmp_path)
