"""Read the modeling-decisions block and the next gate."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_SECTION = re.compile(
    r"^## Modeling decisions\s*\n(.*?)(?=^## |\Z)",
    re.MULTILINE | re.DOTALL,
)
_QUANTITY = re.compile(r"^(?P<value>\d+(?:\.\d+)?)\s+(?P<unit>[A-Za-z]+)$")
_FOLDS = re.compile(r"^[1-9]\d*$")

_LABELS = (
    ("Status", "status"),
    ("Revised on", "revised_on"),
    ("Prediction goal", "prediction_goal"),
    ("Deployment", "deployment"),
    ("Horizon", "horizon"),
    ("Gap", "gap"),
    ("Generalize to", "generalize_to"),
    ("Known at predict", "known_at_predict"),
    ("Time role", "time_role"),
    ("Metric role", "metric_role"),
    ("Metric", "metric"),
    ("Baseline", "baseline"),
    ("Baseline note", "baseline_note"),
    ("Validation", "validation"),
    ("Folds", "folds"),
)
_BY_LABEL = dict(_LABELS)

_REFERENCES = {
    "prediction_goal": "references/prediction-goal.md",
    "deployment": "references/deployment.md",
    "horizon": "references/horizon-gap.md",
    "gap": "references/horizon-gap.md",
    "time_role": "references/deployment.md",
    "generalize_to": "references/generalize-to.md",
    "known_at_predict": "references/generalize-to.md",
    "metric_role": "references/metric-role.md",
    "metric": "references/metric-role.md",
    "baseline": "references/baseline.md",
    "baseline_note": "references/baseline.md",
    "validation": "references/validation.md",
    "folds": "references/validation.md",
}

_GOALS = (
    "probabilities",
    "point_labels",
    "intervals",
    "point_predictions",
)
_FALLBACK = "references/fallback.md"
_SUPPORTED_TASKS = frozenset({"", "none", "classification", "regression"})
_CONFIRM = ["lock", "modify", "stop"]
_REVISE = ["modify", "keep", "stop"]


def _cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def _empty(value: str) -> bool:
    text = value.strip()
    if not text:
        return True
    return text.startswith("<") and text.endswith(">")


def _section_text(root: Path) -> str:
    path = root / "journal" / "JOURNAL.md"
    if not path.is_file():
        return ""
    match = _SECTION.search(path.read_text(encoding="utf-8"))
    return match.group(1) if match else ""


def _raw_rows(root: Path) -> dict[str, str]:
    rows = {key: "" for _, key in _LABELS}
    for line in _section_text(root).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) != 2 or cells[0] in {"Variable", "---"}:
            continue
        if set(cells[1]) <= {"-", ":"} and set(cells[0]) <= {"-", ":"}:
            continue
        key = _BY_LABEL.get(cells[0])
        if key is None or _empty(cells[1]):
            continue
        rows[key] = cells[1].strip()
    return rows


def modeling_decisions_state(root: Path) -> str:
    """Return ``missing``, ``draft``, or ``locked`` for the journal block."""
    status = _raw_rows(root)["status"].split()
    token = status[0].lower().rstrip(".,;:") if status else ""
    if token in {"draft", "locked"}:
        return token
    return "missing"


def _recorded_task(root: Path) -> str:
    path = root / "scratch" / "data_analysis" / "extras.json"
    if not path.is_file():
        return ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    task = payload.get("task") if isinstance(payload, dict) else None
    return task.strip() if isinstance(task, str) else ""


def _goal_candidates(root: Path) -> list[str]:
    task = _recorded_task(root)
    if task == "classification":
        goals = ["probabilities", "point_labels"]
    elif task == "regression":
        goals = ["intervals", "point_predictions"]
    else:
        goals = list(_GOALS)
    goals.append("uncovered")
    return goals


def _metric_candidates(goal: str) -> list[str]:
    if goal == "probabilities":
        return ["proper_score", "ranking", "imposed"]
    if goal == "point_labels":
        return ["thresholded", "ranking", "imposed"]
    if goal == "intervals":
        return ["proper_score", "imposed"]
    if goal == "point_predictions":
        return ["point_error", "imposed"]
    return ["imposed", "proper_score", "ranking", "thresholded", "point_error"]


def _baseline_candidates(rows: dict[str, str]) -> list[str]:
    candidates: list[str] = []
    if rows["deployment"] == "time":
        candidates.append("seasonal_naive")
    known = rows["known_at_predict"]
    if known and known != "n/a":
        candidates.append("group_mean")
    if rows["prediction_goal"] == "probabilities":
        candidates.append("logistic")
    candidates.extend(["production", "dummy"])
    return candidates


def _candidates(root: Path, key: str, rows: dict[str, str]) -> list[str] | None:
    if key == "prediction_goal":
        return _goal_candidates(root)
    if key == "deployment":
        return ["iid", "time", "groups"]
    if key == "time_role":
        return ["sort_key", "covariate"]
    if key == "metric_role":
        return _metric_candidates(rows["prediction_goal"])
    if key == "baseline":
        return _baseline_candidates(rows)
    if key == "validation":
        return ["cv", "holdout"]
    return None


def _quantity(value: str) -> tuple[float, str] | None:
    match = _QUANTITY.fullmatch(value.strip())
    if match is None:
        return None
    return float(match.group("value")), match.group("unit").lower()


def _number(value: float) -> int | float:
    return int(value) if value.is_integer() else value


def _inapplicable(rows: dict[str, str], key: str) -> bool:
    if rows["prediction_goal"] == "uncovered":
        return key not in {"prediction_goal", "metric", "baseline_note"}
    deployment = rows["deployment"]
    if key in {"horizon", "gap", "time_role"}:
        return deployment in {"iid", "groups"}
    if key == "generalize_to":
        return deployment in {"iid", "time"}
    if key == "folds":
        return rows["validation"] == "holdout"
    return False


def _valid(root: Path, key: str, rows: dict[str, str]) -> bool:
    value = rows[key]
    if _inapplicable(rows, key):
        return True
    if not value:
        return False
    if key in {"horizon", "gap"}:
        return _quantity(value) is not None
    if key == "folds":
        return _FOLDS.fullmatch(value) is not None and int(value) >= 2
    if key == "generalize_to":
        return value != "n/a"
    allowed = _candidates(root, key, rows)
    if allowed is None:
        return True
    return value in allowed


def _required(rows: dict[str, str]) -> list[str]:
    if rows["prediction_goal"] == "uncovered":
        return ["prediction_goal", "metric", "baseline_note"]
    keys = ["prediction_goal", "deployment"]
    deployment = rows["deployment"]
    if deployment == "time":
        keys.extend(["horizon", "gap", "time_role"])
    elif deployment == "groups":
        keys.append("generalize_to")
    keys.extend(
        [
            "known_at_predict",
            "metric_role",
            "metric",
            "baseline",
            "baseline_note",
            "validation",
        ]
    )
    if rows["validation"] == "cv":
        keys.append("folds")
    return keys


def _effective(rows: dict[str, str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for _, key in _LABELS:
        if key in {"status", "revised_on"}:
            continue
        if _inapplicable(rows, key) and not rows[key]:
            values[key] = "n/a"
        else:
            values[key] = rows[key]
    return values


def _note_names(note: str) -> set[str]:
    return {part for part in re.split(r"[\s,]+", note.strip()) if part}


def _conflict(rows: dict[str, str]) -> str:
    if rows["prediction_goal"] == "uncovered":
        return ""
    if rows["deployment"] == "time":
        horizon = _quantity(rows["horizon"])
        gap = _quantity(rows["gap"])
        if horizon and gap:
            if horizon[1] != gap[1]:
                return "gap_unit_mismatch"
            if gap[0] < horizon[0]:
                return "gap_shorter_than_horizon"
    generalize = rows["generalize_to"]
    if (
        rows["baseline"] == "group_mean"
        and generalize not in {"", "n/a"}
        and (
            rows["baseline_note"].strip() == generalize
            or generalize in _note_names(rows["baseline_note"])
        )
    ):
        return "group_mean_on_generalize_to"
    return ""


def _translation(rows: dict[str, str]) -> dict[str, Any] | None:
    if rows["prediction_goal"] == "uncovered":
        return None
    effective = _effective(rows)
    gap = _quantity(effective["gap"]) if effective["deployment"] == "time" else None
    holdout = effective["validation"] == "holdout"
    splitter = None
    pattern = None
    scheme = None
    groups = None
    if not holdout and effective["deployment"] == "time":
        pattern, scheme = "B", "date_time"
    elif not holdout and effective["deployment"] == "groups":
        splitter, pattern = "GroupKFold", "B"
        groups = effective["generalize_to"]
    elif not holdout:
        splitter, pattern = "KFold", "A"
    folds = effective["folds"]
    return {
        "splitter": splitter,
        "pattern": pattern,
        "scheme": scheme,
        "n_splits": None if holdout or not folds.isdigit() else int(folds),
        "gap": None if gap is None else _number(gap[0]),
        "gap_unit": None if gap is None else gap[1],
        "groups": groups,
        "report": "EstimatorReport" if holdout else None,
        "metric": effective["metric"],
    }


def _ask(
    reason: str,
    rows: dict[str, str],
    *,
    missing: list[str] | None = None,
    candidates: list[str] | None = None,
    reference: str | None = None,
    choices: list[str] | None = None,
    full: bool = False,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"action": "ask", "reason": reason}
    if missing is not None:
        payload["missing"] = missing
    if candidates is not None:
        payload["candidates"] = candidates
    if reference is not None:
        payload["reference"] = reference
    if choices is not None:
        payload["choices"] = choices
    if full:
        context = _effective(rows)
    else:
        context = {
            key: value
            for key, value in rows.items()
            if value and key not in {"status", "revised_on"}
        }
    payload["context"] = context
    return payload


def frame_show(root: Path, *, revise: bool = False) -> dict[str, Any]:
    """Return the modeling-decisions gate for ``root``.

    Filesystem only: ``journal/JOURNAL.md`` and, when present,
    ``scratch/data_analysis/extras.json``. Does not write either file.
    """
    journal = root / "journal"
    if not journal.is_dir() or not (journal / "JOURNAL.md").is_file():
        return {"action": "stop", "reason": "missing_scaffold"}

    rows = _raw_rows(root)
    recorded = _recorded_task(root)
    if recorded not in _SUPPORTED_TASKS and not rows["prediction_goal"]:
        payload = _ask("uncovered", rows, reference=_FALLBACK)
        payload["context"] = {"task": recorded}
        return payload

    locked = rows["status"].split()[:1] == ["locked"]
    complete = all(_valid(root, key, rows) for key in _required(rows))
    if revise and locked and complete and not _conflict(rows):
        return _ask("revise", rows, choices=list(_REVISE), full=True)

    for key in _required(rows):
        if _valid(root, key, rows):
            continue
        reference = _REFERENCES[key]
        if rows["prediction_goal"] == "uncovered":
            reference = _FALLBACK
        payload = _ask(
            "missing_keys",
            rows,
            missing=[key],
            reference=reference,
        )
        candidates = _candidates(root, key, rows)
        if candidates is not None:
            payload["candidates"] = candidates
        return payload

    conflict = _conflict(rows)
    if conflict in {"gap_shorter_than_horizon", "gap_unit_mismatch"}:
        return _ask(
            conflict,
            rows,
            missing=["gap"],
            reference=_REFERENCES["gap"],
            full=True,
        )
    if conflict:
        return _ask(
            conflict,
            rows,
            missing=["baseline"],
            candidates=_baseline_candidates(rows),
            reference=_REFERENCES["baseline"],
            full=True,
        )

    if modeling_decisions_state(root) == "locked":
        return {
            "action": "proceed",
            "reason": "locked",
            "decisions": _effective(rows),
            "translation": _translation(rows),
        }
    return _ask("confirm_lock", rows, choices=list(_CONFIRM), full=True)


def render_frame_show(root: Path, *, revise: bool = False) -> str:
    """Serialize the modeling-decisions gate as JSON."""
    return json.dumps(frame_show(root, revise=revise), indent=2) + "\n"
