"""Tests for ``skore-skills frame show``."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.frame import frame_show
from skore_skills.workspace import snapshot

_LABELS = (
    "Status",
    "Revised on",
    "Prediction goal",
    "Deployment",
    "Horizon",
    "Gap",
    "Generalize to",
    "Known at predict",
    "Time role",
    "Metric role",
    "Metric",
    "Baseline",
    "Baseline note",
    "Validation",
    "Folds",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _journal(root: Path, **values: str) -> None:
    lines = [
        "# JOURNAL",
        "",
        "## Modeling decisions",
        "",
        "| Variable | Value |",
        "|---|---|",
    ]
    lines.extend(f"| {label} | {values.get(label, '')} |" for label in _LABELS)
    lines.extend(["", "## History", ""])
    _write(root / "journal" / "JOURNAL.md", "\n".join(lines))


def _locked_iid(**overrides: str) -> dict[str, str]:
    rows = {
        "Status": "locked",
        "Revised on": "n/a",
        "Prediction goal": "point_predictions",
        "Deployment": "iid",
        "Horizon": "n/a",
        "Gap": "n/a",
        "Generalize to": "n/a",
        "Known at predict": "n/a",
        "Time role": "n/a",
        "Metric role": "point_error",
        "Metric": "MAE",
        "Baseline": "dummy",
        "Baseline note": "global mean",
        "Validation": "cv",
        "Folds": "5",
    }
    rows.update(overrides)
    return rows


def test_missing_scaffold(tmp_path: Path) -> None:
    assert frame_show(tmp_path) == {"action": "stop", "reason": "missing_scaffold"}


def test_missing_journal_file_is_stop(tmp_path: Path) -> None:
    (tmp_path / "journal").mkdir()

    assert frame_show(tmp_path)["reason"] == "missing_scaffold"


def test_first_key_uses_task_and_names_one_reference(tmp_path: Path) -> None:
    _journal(tmp_path)
    _write(
        tmp_path / "scratch" / "data_analysis" / "extras.json",
        json.dumps({"task": "classification"}) + "\n",
    )

    payload = frame_show(tmp_path)

    assert payload["action"] == "ask"
    assert payload["reason"] == "missing_keys"
    assert payload["missing"] == ["prediction_goal"]
    assert payload["candidates"] == ["probabilities", "point_labels", "uncovered"]
    assert payload["reference"] == "references/prediction-goal.md"
    assert "horizon-gap.md" not in payload["reference"]


def test_time_deployment_asks_horizon_without_a_menu(tmp_path: Path) -> None:
    _journal(
        tmp_path,
        **{
            "Status": "draft",
            "Prediction goal": "point_predictions",
            "Deployment": "time",
        },
    )

    payload = frame_show(tmp_path)

    assert payload["missing"] == ["horizon"]
    assert payload["reference"] == "references/horizon-gap.md"
    assert "candidates" not in payload


def test_complete_draft_asks_to_lock(tmp_path: Path) -> None:
    _journal(tmp_path, **_locked_iid(Status="draft"))

    payload = frame_show(tmp_path)

    assert payload["action"] == "ask"
    assert payload["reason"] == "confirm_lock"
    assert payload["choices"] == ["lock", "modify", "stop"]
    assert payload["context"]["metric"] == "MAE"
    assert payload["context"]["folds"] == "5"


def test_locked_iid_translates_to_kfold(tmp_path: Path) -> None:
    _journal(tmp_path, **_locked_iid())

    payload = frame_show(tmp_path)

    assert payload["action"] == "proceed"
    assert payload["reason"] == "locked"
    assert payload["translation"] == {
        "splitter": "KFold",
        "pattern": "A",
        "scheme": None,
        "n_splits": 5,
        "gap": None,
        "gap_unit": None,
        "groups": None,
        "report": None,
        "metric": "MAE",
    }


def test_locked_time_translates_to_a_date_splitter(tmp_path: Path) -> None:
    _journal(
        tmp_path,
        **_locked_iid(
            Deployment="time",
            Horizon="7 day",
            Gap="7 day",
            **{"Time role": "sort_key"},
            **{"Generalize to": "n/a"},
            Baseline="seasonal_naive",
            **{"Baseline note": "last observed week"},
            Folds="4",
        ),
    )

    payload = frame_show(tmp_path)

    assert payload["translation"]["splitter"] is None
    assert payload["translation"]["pattern"] == "B"
    assert payload["translation"]["scheme"] == "date_time"
    assert payload["translation"]["groups"] is None
    assert payload["translation"]["n_splits"] == 4
    assert payload["translation"]["gap"] == 7
    assert payload["translation"]["gap_unit"] == "day"


def test_locked_groups_translate_to_group_kfold(tmp_path: Path) -> None:
    _journal(
        tmp_path,
        **_locked_iid(
            Deployment="groups",
            **{"Generalize to": "store_id"},
            **{"Known at predict": "region"},
            Baseline="group_mean",
            **{"Baseline note": "region"},
        ),
    )

    payload = frame_show(tmp_path)

    assert payload["translation"]["splitter"] == "GroupKFold"
    assert payload["translation"]["pattern"] == "B"
    assert payload["translation"]["groups"] == "store_id"
    assert payload["translation"]["n_splits"] == 5


def test_holdout_translates_to_estimator_report(tmp_path: Path) -> None:
    _journal(tmp_path, **_locked_iid(Validation="holdout", Folds="n/a"))

    payload = frame_show(tmp_path)

    assert payload["translation"]["splitter"] is None
    assert payload["translation"]["report"] == "EstimatorReport"
    assert payload["translation"]["n_splits"] is None


def test_gap_shorter_than_horizon_does_not_proceed(tmp_path: Path) -> None:
    _journal(
        tmp_path,
        **_locked_iid(
            Deployment="time",
            Horizon="7 day",
            Gap="3 day",
            **{"Time role": "sort_key"},
            Baseline="seasonal_naive",
            **{"Baseline note": "last observed week"},
        ),
    )

    payload = frame_show(tmp_path)

    assert payload["action"] == "ask"
    assert payload["reason"] == "gap_shorter_than_horizon"
    assert payload["reference"] == "references/horizon-gap.md"


def test_mismatched_gap_units_ask_instead_of_converting(tmp_path: Path) -> None:
    _journal(
        tmp_path,
        **_locked_iid(
            Deployment="time",
            Horizon="7 day",
            Gap="24 hour",
            **{"Time role": "sort_key"},
            Baseline="seasonal_naive",
            **{"Baseline note": "last observed week"},
        ),
    )

    assert frame_show(tmp_path)["reason"] == "gap_unit_mismatch"


def test_group_mean_on_the_generalize_to_column_does_not_lock(tmp_path: Path) -> None:
    _journal(
        tmp_path,
        **_locked_iid(
            Deployment="groups",
            **{"Generalize to": "store_id"},
            **{"Known at predict": "store_id"},
            Baseline="group_mean",
            **{"Baseline note": "store_id"},
        ),
    )

    payload = frame_show(tmp_path)

    assert payload["action"] == "ask"
    assert payload["reason"] == "group_mean_on_generalize_to"
    assert "seasonal_naive" not in payload["candidates"]
    assert "group_mean" in payload["candidates"]


def test_iid_baseline_omits_seasonal_naive(tmp_path: Path) -> None:
    rows = _locked_iid(Status="draft")
    rows["Baseline"] = ""
    rows["Baseline note"] = ""
    _journal(tmp_path, **rows)

    payload = frame_show(tmp_path)

    assert payload["missing"] == ["baseline"]
    assert payload["candidates"] == ["production", "dummy"]
    assert payload["reference"] == "references/baseline.md"


def test_revise_asks_and_draft_blocks_proceed(tmp_path: Path) -> None:
    _journal(tmp_path, **_locked_iid())

    revise = frame_show(tmp_path, revise=True)

    assert revise["action"] == "ask"
    assert revise["reason"] == "revise"
    assert revise["choices"] == ["modify", "keep", "stop"]
    assert frame_show(tmp_path)["action"] == "proceed"

    _journal(tmp_path, **_locked_iid(Status="draft", **{"Revised on": "2026-09-25"}))

    assert frame_show(tmp_path)["reason"] == "confirm_lock"
    assert frame_show(tmp_path, revise=True)["reason"] == "confirm_lock"


def test_status_reads_the_block(tmp_path: Path) -> None:
    assert snapshot(tmp_path)["modeling_decisions"] == "missing"
    _journal(tmp_path, **_locked_iid(Status="draft"))
    assert snapshot(tmp_path)["modeling_decisions"] == "draft"
    _journal(tmp_path, **_locked_iid())
    assert snapshot(tmp_path)["modeling_decisions"] == "locked"


def test_unsupported_task_uses_the_fallback(tmp_path: Path) -> None:
    _journal(tmp_path)
    _write(
        tmp_path / "scratch" / "data_analysis" / "extras.json",
        json.dumps({"task": "clustering"}) + "\n",
    )

    payload = frame_show(tmp_path)

    assert payload["action"] == "ask"
    assert payload["reason"] == "uncovered"
    assert payload["reference"] == "references/fallback.md"
    assert payload["context"] == {"task": "clustering"}
    assert "candidates" not in payload


def test_uncovered_prose_locks_without_a_translation(tmp_path: Path) -> None:
    _journal(
        tmp_path,
        **{
            "Status": "draft",
            "Prediction goal": "uncovered",
            "Metric": "a clustering that matches the known segments",
            "Baseline note": "one cluster per site",
        },
    )

    draft = frame_show(tmp_path)

    assert draft["reason"] == "confirm_lock"
    assert draft["context"]["prediction_goal"] == "uncovered"

    _journal(
        tmp_path,
        **{
            "Status": "locked",
            "Prediction goal": "uncovered",
            "Metric": "a clustering that matches the known segments",
            "Baseline note": "one cluster per site",
        },
    )

    locked = frame_show(tmp_path)

    assert locked["action"] == "proceed"
    assert locked["translation"] is None


def test_cli_prints_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["frame", "show"])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["reason"] == "missing_scaffold"
