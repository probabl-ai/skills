"""Compute the read-only board of stored project choices."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skore_skills.frame import _LABELS, frame_show
from skore_skills.workspace import snapshot

_SKORE_MODES = frozenset({"local", "hub", "mlflow"})
_TIME_CELLS = frozenset({"horizon", "gap", "time_role"})


def _installed(skills: dict[str, bool | None], skill_id: str) -> bool:
    return skills.get(skill_id) is True


def _framing_rows(source: dict[str, Any]) -> list[dict[str, str]]:
    deployment = source.get("deployment")
    validation = source.get("validation")
    rows: list[dict[str, str]] = []
    for label, key in _LABELS:
        if key in {"status", "revised_on"}:
            continue
        if key in _TIME_CELLS and deployment != "time":
            continue
        if key == "generalize_to" and deployment != "groups":
            continue
        if key == "folds" and validation != "cv":
            continue
        value = source.get(key)
        if not isinstance(value, str):
            continue
        text = value.strip()
        if not text or text == "n/a":
            continue
        rows.append(
            {
                "id": key,
                "label": label,
                "value": text,
                "skill": "frame-ml-problem",
            }
        )
    return rows


def _framing(
    root: Path, status: dict[str, Any]
) -> tuple[list[dict[str, str]], str | None]:
    skills = status["skills"]
    if status["modeling_decisions"] == "missing" or not _installed(
        skills, "frame-ml-problem"
    ):
        return [], "not framed yet"
    shown = frame_show(root)
    source = shown["decisions"] if "decisions" in shown else shown.get("context") or {}
    return _framing_rows(source), None


def review_choices(root: Path) -> dict[str, Any]:
    """Return the stored-choice board for ``root``.

    Read-only. Does not write ``.skore`` or the journal.
    """
    status = snapshot(root)
    policy = status["policy"]
    skills = status["skills"]
    changeable: list[dict[str, Any]] = []
    not_offered: list[dict[str, Any]] = []

    mode = policy.get("skore_mode")
    if mode not in _SKORE_MODES:
        not_offered.append(
            {
                "id": "skore_mode",
                "value": None,
                "reason": (
                    "not chosen yet; the first choice happens when a report is stored"
                ),
            }
        )
    elif _installed(skills, "sync-ml-reports"):
        changeable.append(
            {"id": "skore_mode", "value": mode, "skill": "sync-ml-reports"}
        )
    else:
        not_offered.append(
            {
                "id": "skore_mode",
                "value": mode,
                "reason": "sync-ml-reports is not installed",
            }
        )

    notebooks_site = {"notebooks": policy.get("notebooks"), "site": policy.get("site")}
    if _installed(skills, "export-ml-project"):
        changeable.append(
            {
                "id": "notebooks_site",
                "value": notebooks_site,
                "skill": "export-ml-project",
            }
        )
    else:
        not_offered.append(
            {
                "id": "notebooks_site",
                "value": notebooks_site,
                "reason": "export-ml-project is not installed",
            }
        )

    autocommit = policy.get("git", {}).get("autocommit")
    if _installed(skills, "setup-git"):
        changeable.append(
            {"id": "git_autocommit", "value": autocommit, "skill": "setup-git"}
        )
    else:
        not_offered.append(
            {
                "id": "git_autocommit",
                "value": autocommit,
                "reason": "setup-git is not installed",
            }
        )

    managed = policy.get("env", {}).get("managed")
    if _installed(skills, "setup-python-env"):
        changeable.append(
            {"id": "env_managed", "value": managed, "skill": "setup-python-env"}
        )
    else:
        not_offered.append(
            {
                "id": "env_managed",
                "value": managed,
                "reason": "setup-python-env is not installed",
            }
        )

    data_analysis = status["data_analysis"]
    if _installed(skills, "explore-ml-data"):
        changeable.append(
            {
                "id": "data_analysis",
                "value": data_analysis,
                "action": "rerun" if data_analysis == "present" else "run_or_skip",
                "skill": "explore-ml-data",
            }
        )
    else:
        not_offered.append(
            {
                "id": "data_analysis",
                "value": data_analysis,
                "reason": "explore-ml-data is not installed",
            }
        )

    framing, framing_reason = _framing(root, status)
    return {
        "read_only": [
            {
                "id": "package",
                "value": policy.get("package"),
                "reason": "an existing tree is not renamed",
            },
            {
                "id": "env_manager",
                "value": policy.get("env_manager"),
                "mismatch": status["mismatch"],
                "reason": "switching would leave two lockfiles",
            },
            {
                "id": "tabular",
                "value": policy.get("tabular"),
                "reason": "analysis and pipeline code already import one library",
            },
            {
                "id": "loop",
                "value": status["loop_stage"],
                "stem": policy.get("loop", {}).get("stem"),
                "reason": "it follows the files",
            },
        ],
        "changeable": changeable,
        "not_offered": not_offered,
        "framing": framing,
        "framing_reason": framing_reason,
    }


def render_review_choices(root: Path) -> str:
    """Serialize the stored-choice board as JSON."""
    return json.dumps(review_choices(root), indent=2) + "\n"
