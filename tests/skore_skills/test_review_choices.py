"""Tests for ``skore-skills review choices``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.installed_skills import SIDECAR
from skore_skills.review_choices import review_choices

_OWNERS = (
    "sync-ml-reports",
    "export-ml-project",
    "setup-git",
    "setup-python-env",
    "explore-ml-data",
    "frame-ml-problem",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _install(root: Path, *names: str) -> None:
    target = root / ".agents" / "skills"
    skills = [{"id": name} for name in names]
    _write(
        target / ".catalog.json",
        json.dumps({"skills": skills}) + "\n",
    )
    for name in names:
        _write(target / name / SIDECAR, json.dumps({"id": name}) + "\n")


def _isolate_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home = tmp_path / "isolated-home"
    home.mkdir()
    monkeypatch.setattr("skore_skills.installed_skills.Path.home", lambda: home)


def _journal(root: Path) -> None:
    _write(
        root / "journal" / "JOURNAL.md",
        "\n".join(
            [
                "# JOURNAL",
                "",
                "## Modeling decisions",
                "",
                "| Variable | Value |",
                "|---|---|",
                "| Status | locked |",
                "| Revised on | n/a |",
                "| Prediction goal | point_predictions |",
                "| Deployment | iid |",
                "| Horizon | 7 day |",
                "| Gap | n/a |",
                "| Generalize to | n/a |",
                "| Known at predict | n/a |",
                "| Time role | n/a |",
                "| Metric role | point_error |",
                "| Metric | MAE |",
                "| Baseline | dummy |",
                "| Baseline note | global mean |",
                "| Validation | cv |",
                "| Folds | 5 |",
                "",
                "## History",
                "",
            ]
        ),
    )


def _ids(rows: object) -> list[str]:
    assert isinstance(rows, list)
    return [row["id"] for row in rows]


def test_review_choices_board_filters_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Installed owners are offered; inapplicable framing cells are not."""
    _isolate_home(tmp_path, monkeypatch)
    _install(tmp_path, *_OWNERS)
    _write(tmp_path / "data_analysis" / "data_analysis.md", "# report\n")
    _journal(tmp_path)
    _write(
        tmp_path / ".skore",
        json.dumps(
            {
                "workspace": {
                    "package": "load_forecast",
                    "skore_mode": "local",
                    "notebooks": True,
                    "site": False,
                    "env_manager": "pixi",
                    "git": {"autocommit": "on"},
                    "env": {"managed": True},
                }
            }
        )
        + "\n",
    )
    before = (tmp_path / "journal" / "JOURNAL.md").read_text(encoding="utf-8")

    payload = review_choices(tmp_path)

    assert _ids(payload["read_only"]) == [
        "package",
        "env_manager",
        "tabular",
        "loop",
    ]
    assert payload["read_only"][0]["value"] == "load_forecast"
    assert _ids(payload["changeable"]) == [
        "skore_mode",
        "notebooks_site",
        "git_autocommit",
        "env_managed",
        "data_analysis",
    ]
    analysis = payload["changeable"][-1]
    assert analysis["action"] == "rerun"
    assert analysis["skill"] == "explore-ml-data"
    assert "horizon" not in _ids(payload["framing"])
    assert "metric" in _ids(payload["framing"])
    assert payload["framing_reason"] is None
    assert (tmp_path / "journal" / "JOURNAL.md").read_text(encoding="utf-8") == before


def test_unset_mode_and_missing_frame_are_not_offered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unset destination and a missing frame stay off the menu."""
    _isolate_home(tmp_path, monkeypatch)
    _install(tmp_path, "sync-ml-reports")

    payload = review_choices(tmp_path)

    assert "skore_mode" not in _ids(payload["changeable"])
    skipped = {row["id"]: row for row in payload["not_offered"]}
    assert "not chosen yet" in skipped["skore_mode"]["reason"]
    assert payload["framing"] == []
    assert payload["framing_reason"] == "not framed yet"


def test_holdout_frame_does_not_offer_folds(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Folds stay off the board when validation is not cross-validation."""
    _isolate_home(tmp_path, monkeypatch)
    _install(tmp_path, "frame-ml-problem")
    _journal(tmp_path)
    path = tmp_path / "journal" / "JOURNAL.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("| Validation | cv |", "| Validation | holdout |")
    text = text.replace("| Folds | 5 |", "| Folds | n/a |")
    path.write_text(text, encoding="utf-8")

    payload = review_choices(tmp_path)

    assert "folds" not in _ids(payload["framing"])
    assert "metric" in _ids(payload["framing"])


def test_recorded_mode_without_sync_is_not_offered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A stored destination is not changeable when its skill is absent."""
    _isolate_home(tmp_path, monkeypatch)
    _write(
        tmp_path / ".skore",
        json.dumps({"workspace": {"skore_mode": "hub"}}) + "\n",
    )

    payload = review_choices(tmp_path)

    assert "skore_mode" not in _ids(payload["changeable"])
    skipped = {row["id"]: row for row in payload["not_offered"]}
    assert skipped["skore_mode"]["reason"] == "sync-ml-reports is not installed"


def test_framing_rows_skip_non_text_values() -> None:
    """A non-text cell is not a row the user can reopen."""
    from skore_skills.review_choices import _framing_rows

    rows = _framing_rows(
        {
            "deployment": "iid",
            "validation": "cv",
            "metric": 1,
            "folds": "5",
        }
    )

    assert "metric" not in _ids(rows)
    assert "folds" in _ids(rows)


def test_review_choices_cli_bad_argv_and_directory_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown argv fails, and a ``.skore`` directory is a usage error."""
    _isolate_home(tmp_path, monkeypatch)
    monkeypatch.chdir(tmp_path)
    unknown = CliRunner().invoke(cli, ["review", "choices", "--stem", "01"])
    assert unknown.exit_code != 0

    (tmp_path / ".skore").mkdir()
    failed = CliRunner().invoke(cli, ["review", "choices"])
    assert failed.exit_code != 0
    assert ".skore is a directory" in failed.output
