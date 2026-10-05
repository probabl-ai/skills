"""Tests for loop artifacts, loop locator, and loop notebooks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.loop import (
    MISSING_LOCATOR,
    loop_artifacts,
    loop_locator,
    loop_notebooks,
)


def _touch(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_artifacts_smoke_missing(tmp_path: Path) -> None:
    payload = loop_artifacts(tmp_path, "01_x")
    assert payload["action"] == "stop"
    assert payload["reason"] == "smoke_missing"


def test_artifacts_evaluate_incomplete(tmp_path: Path) -> None:
    _touch(tmp_path / "tests" / "smoke" / "test_01_x.py")
    _touch(tmp_path / "experiments" / "01_x.py")
    payload = loop_artifacts(tmp_path, "01_x")
    assert payload["action"] == "evaluate_incomplete"
    assert payload["files"]["experiment"] is True


def test_artifacts_audit_then_record(tmp_path: Path) -> None:
    stem = "01_x"
    _touch(tmp_path / "tests" / "smoke" / f"test_{stem}.py")
    _touch(tmp_path / "scratch" / "results" / stem / "report.html")
    payload = loop_artifacts(tmp_path, stem)
    assert payload["action"] == "audit"
    _touch(tmp_path / "scratch" / "audit" / stem / "audit.md")
    payload = loop_artifacts(tmp_path, stem)
    assert payload["action"] == "record"


def test_empty_stem_raises() -> None:
    with pytest.raises(ValueError, match="stem is required"):
        loop_artifacts(Path("."), " ")
    with pytest.raises(ValueError, match="stem is required"):
        loop_locator(Path("."), " ")
    with pytest.raises(ValueError, match="stem is required"):
        loop_notebooks(Path("."), " ")


def test_locator_file_then_audit_then_missing(tmp_path: Path) -> None:
    stem = "01_x"
    assert loop_locator(tmp_path, stem)["locator"] == MISSING_LOCATOR
    audit = tmp_path / "audit" / f"{stem}.py"
    _touch(
        audit,
        "# %% [markdown]\n# ## Persisted report\n#\n"
        "# local workspace: [reports/](../reports/) · id: abc\n",
    )
    scraped = loop_locator(tmp_path, stem)
    assert scraped["reason"] == "audit"
    assert "id: abc" in scraped["locator"]
    _touch(
        tmp_path / "scratch" / "results" / stem / "locator.txt",
        "hub · id: from-file\n",
    )
    from_file = loop_locator(tmp_path, stem)
    assert from_file["reason"] == "file"
    assert from_file["locator"] == "hub · id: from-file"


def test_locator_ignores_placeholder_audit_cell(tmp_path: Path) -> None:
    stem = "01_x"
    _touch(
        tmp_path / "audit" / f"{stem}.py",
        "# %% [markdown]\n# ## Persisted report\n#\n# <REPORT_LOCATOR>\n",
    )
    payload = loop_locator(tmp_path, stem)
    assert payload["reason"] == "missing"
    assert payload["locator"] == MISSING_LOCATOR


def test_cli_artifacts_and_locator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    missing = CliRunner().invoke(cli, ["loop", "artifacts", "--stem", "01_x"])
    assert missing.exit_code == 1
    assert json.loads(missing.output)["action"] == "stop"

    _touch(tmp_path / "tests" / "smoke" / "test_01_x.py")
    _touch(tmp_path / "scratch" / "results" / "01_x" / "report.html")
    ready = CliRunner().invoke(cli, ["loop", "artifacts", "--stem", "01_x"])
    assert ready.exit_code == 0
    assert json.loads(ready.output)["action"] == "audit"

    loc = CliRunner().invoke(cli, ["loop", "locator", "--stem", "01_x"])
    assert loc.exit_code == 0
    assert json.loads(loc.output)["locator"] == MISSING_LOCATOR

    no_stem = CliRunner().invoke(cli, ["loop", "artifacts"])
    assert no_stem.exit_code == 2


def test_locator_without_persisted_cell_is_missing(tmp_path: Path) -> None:
    """An audit file that never records a locator does not invent one."""
    stem = "01_x"
    _touch(tmp_path / "audit" / f"{stem}.py", "# %%\nprint('no locator')\n")
    payload = loop_locator(tmp_path, stem)
    assert payload["reason"] == "missing"
    assert payload["locator"] == MISSING_LOCATOR


def test_cli_rejects_blank_stem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank stem is a usage error for the loop commands."""
    monkeypatch.chdir(tmp_path)
    artifacts = CliRunner().invoke(cli, ["loop", "artifacts", "--stem", "  "])
    locator = CliRunner().invoke(cli, ["loop", "locator", "--stem", "  "])
    notebooks = CliRunner().invoke(cli, ["loop", "notebooks", "--stem", "  "])
    assert artifacts.exit_code != 0
    assert locator.exit_code != 0
    assert notebooks.exit_code != 0
    assert "stem is required" in artifacts.output
    assert "stem is required" in locator.output
    assert "stem is required" in notebooks.output


def _policy(root: Path, *, notebooks: bool | None, site: bool | None = None) -> None:
    payload = {"workspace": {"notebooks": notebooks, "site": site}}
    (root / ".skore").write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_notebooks_policy_off(tmp_path: Path) -> None:
    stem = "01_x"
    _touch(tmp_path / "experiments" / f"{stem}.py")
    _touch(tmp_path / "scratch" / "results" / stem / "report.html")
    unset = loop_notebooks(tmp_path, stem)
    assert unset["action"] == "skip"
    assert unset["reason"] == "policy_off"
    assert unset["sources"] == []
    _policy(tmp_path, notebooks=False, site=True)
    off = loop_notebooks(tmp_path, stem)
    assert off["action"] == "skip"
    assert off["reason"] == "policy_off"
    assert off["html"] is True


def test_notebooks_not_evaluated(tmp_path: Path) -> None:
    stem = "01_x"
    _policy(tmp_path, notebooks=True, site=True)
    _touch(tmp_path / "experiments" / f"{stem}.py")
    payload = loop_notebooks(tmp_path, stem)
    assert payload["action"] == "skip"
    assert payload["reason"] == "not_evaluated"
    assert payload["sources"] == []


def test_notebooks_experiment_only(tmp_path: Path) -> None:
    stem = "01_x"
    _policy(tmp_path, notebooks=True, site=False)
    _touch(tmp_path / "experiments" / f"{stem}.py")
    _touch(tmp_path / "scratch" / "results" / stem / "report.html")
    missing = loop_notebooks(tmp_path, stem)
    assert missing["action"] == "convert"
    assert missing["reason"] == "notebook_missing"
    assert missing["html"] is False
    assert missing["sources"] == [f"experiments/{stem}.py"]
    _touch(tmp_path / "experiments" / f"{stem}.ipynb")
    present = loop_notebooks(tmp_path, stem)
    assert present["action"] == "skip"
    assert present["reason"] == "already_present"


def test_notebooks_experiment_and_audit_require_html(tmp_path: Path) -> None:
    stem = "01_x"
    _policy(tmp_path, notebooks=True, site=True)
    _touch(tmp_path / "experiments" / f"{stem}.py")
    _touch(tmp_path / "audit" / f"{stem}.py")
    _touch(tmp_path / "scratch" / "results" / stem / "report.html")
    both = loop_notebooks(tmp_path, stem)
    assert both["html"] is True
    assert both["sources"] == [
        f"experiments/{stem}.py",
        f"audit/{stem}.py",
    ]
    _touch(tmp_path / "experiments" / f"{stem}.ipynb")
    _touch(tmp_path / "audit" / f"{stem}.ipynb")
    html_missing = loop_notebooks(tmp_path, stem)
    assert html_missing["action"] == "convert"
    assert html_missing["sources"] == both["sources"]
    _touch(tmp_path / "experiments" / f"{stem}.nb.html")
    _touch(tmp_path / "audit" / f"{stem}.nb.html")
    done = loop_notebooks(tmp_path, stem)
    assert done["action"] == "skip"
    assert done["reason"] == "already_present"
    assert done["sources"] == []


def test_cli_notebooks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    stem = "01_x"
    _policy(tmp_path, notebooks=True, site=True)
    _touch(tmp_path / "experiments" / f"{stem}.py")
    _touch(tmp_path / "scratch" / "results" / stem / "report.html")
    due = CliRunner().invoke(cli, ["loop", "notebooks", "--stem", stem])
    assert due.exit_code == 0
    payload = json.loads(due.output)
    assert payload["action"] == "convert"
    assert payload["sources"] == [f"experiments/{stem}.py"]
    no_stem = CliRunner().invoke(cli, ["loop", "notebooks"])
    assert no_stem.exit_code == 2
