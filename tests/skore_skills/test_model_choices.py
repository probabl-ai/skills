"""Tests for ``skore-skills model choices``."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.model_choices import model_choices


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ids(payload: dict[str, object]) -> list[str]:
    choices = payload["choices"]
    assert isinstance(choices, list)
    return [choice["id"] for choice in choices]


def _lock(
    root: Path, *, baseline: str = "seasonal_naive", note: str = "last week"
) -> None:
    _write(
        root / "journal" / "JOURNAL.md",
        "## Modeling decisions\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        "| Status | locked |\n"
        f"| Baseline | {baseline} |\n"
        f"| Baseline note | {note} |\n",
    )


def test_unlocked_modeling_decisions_stop(tmp_path: Path) -> None:
    payload = model_choices(tmp_path)

    assert payload["action"] == "stop"
    assert payload["reason"] == "modeling_decisions_unlocked"
    assert payload["modeling_decisions"] == "missing"
    assert "choices" not in payload


def test_first_model_choice_is_the_locked_baseline(tmp_path: Path) -> None:
    _lock(tmp_path)

    payload = model_choices(tmp_path)

    assert _ids(payload) == ["baseline", "discuss"]
    assert payload["choices"][0]["reason"] == (
        "locked baseline is seasonal_naive: last week"
    )
    assert payload["model_stems"] == []
    assert payload["data_analysis"] == "missing"
    assert payload["backlog"] == []


def test_existing_experiment_suppresses_first_model_choices(tmp_path: Path) -> None:
    _lock(tmp_path)
    _write(tmp_path / "experiments" / "01_model.py", "# model\n")
    _write(tmp_path / "experiments" / "__init__.py")

    payload = model_choices(tmp_path)

    assert _ids(payload) == ["discuss"]
    assert payload["model_stems"] == ["01_model"]


def test_history_run_counts_as_a_prior_model(tmp_path: Path) -> None:
    _write(
        tmp_path / "journal" / "JOURNAL.md",
        "## Modeling decisions\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        "| Status | locked |\n"
        "| Baseline | dummy |\n"
        "| Baseline note | global mean |\n\n"
        "## History\n\n"
        "| Stem | Intent | Status | Headline result | Report | Design note |\n"
        "|---|---|---|---|---|---|\n"
        "| `01_old` | baseline | done | score | n/a | note |\n"
        "| `02_plan` | next | planned | n/a | n/a | note |\n\n"
        "## Backlog\n",
    )

    payload = model_choices(tmp_path)

    assert _ids(payload) == ["discuss"]
    assert payload["model_stems"] == ["01_old"]


def test_present_eda_enables_proposal_but_skipped_does_not(tmp_path: Path) -> None:
    _lock(tmp_path)
    _write(tmp_path / "data_analysis" / "data_analysis.md", "# report\n")
    assert _ids(model_choices(tmp_path)) == [
        "baseline",
        "eda_proposal",
        "discuss",
    ]

    (tmp_path / "data_analysis" / "data_analysis.md").unlink()
    _write(
        tmp_path / "journal" / "JOURNAL.md",
        "## Modeling decisions\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        "| Status | locked |\n"
        "| Baseline | logistic |\n"
        "| Baseline note | class probabilities |\n\n"
        "## Data understanding\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        "| Status | skipped — 2026-09-21 |\n",
    )
    assert _ids(model_choices(tmp_path)) == ["baseline", "discuss"]


def test_real_backlog_rows_are_returned_and_malformed_rows_ignored(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path / "journal" / "JOURNAL.md",
        "## Modeling decisions\n\n"
        "| Variable | Value |\n"
        "|---|---|\n"
        "| Status | locked |\n"
        "| Baseline | dummy |\n"
        "| Baseline note | global mean |\n\n"
        "## History\n\n"
        "| Stem | Intent | Status | Headline result | Report | Design note |\n"
        "|---|---|---|---|---|---|\n\n"
        "## Backlog\n\n"
        "| # | Item | Source |\n"
        "|---|---|---|\n"
        "| B1 | try robust scaling | `user` |\n"
        "| nope | malformed identifier | user |\n"
        "| B2 |  | user |\n"
        "| <!-- B3 --> | <!-- example --> | <!-- user --> |\n",
    )

    payload = model_choices(tmp_path)

    assert _ids(payload) == [
        "baseline",
        "backlog",
        "discuss",
    ]
    assert payload["backlog"] == [
        {"id": "B1", "item": "try robust scaling", "source": "user"}
    ]


def test_cli_prints_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["model", "choices"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "stop"
    assert payload["reason"] == "modeling_decisions_unlocked"


def test_cli_rejects_unknown_model_subcommand() -> None:
    result = CliRunner().invoke(cli, ["model", "unknown"])

    assert result.exit_code == 2
    assert "No such command" in result.output
