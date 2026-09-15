"""Load and save workspace policy in the project ``.skore`` file.

Hub/agent keys owned by skore-cli stay at the top level. This module
only reads and writes the nested ``workspace`` section (merge-write).
skore-cli must also merge (see ``.spec/B03-skore-merge-write.md``) or
``skore agent`` will wipe the section.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

POLICY_FILENAME = ".skore"
LEGACY_POLICY_FILENAME = ".skore-workspace.json"
WORKSPACE_KEY = "workspace"

AUTOCOMMIT_VALUES = ("off", "ask", "on")
LOOP_STAGES = ("setup", "eda", "implement", "evaluate", "audit", "backlog")

POLICY_SET_KEYS = (
    "env_manager",
    "package",
    "tabular",
    "skore_mode",
    "git.autocommit",
    "loop.stage",
    "loop.stem",
)

_POLICY_FLAT_KEYS = frozenset(
    {"env_manager", "package", "tabular", "skore_mode", "git", "loop"}
)


def empty_policy() -> dict[str, Any]:
    """Return the default policy mapping."""
    return {
        "env_manager": None,
        "package": None,
        "tabular": None,
        "skore_mode": None,
        "git": {"autocommit": "ask"},
        "loop": {"stage": None, "stem": None},
    }


def policy_path(root: Path) -> Path:
    """Return the ``.skore`` path under ``root``."""
    return root / POLICY_FILENAME


def _merge_loaded(raw: Any) -> dict[str, Any]:
    data = empty_policy()
    if not isinstance(raw, dict):
        return data
    for key in ("env_manager", "package", "tabular", "skore_mode"):
        if key in raw:
            data[key] = raw[key]
    git = raw.get("git")
    if isinstance(git, dict) and "autocommit" in git:
        data["git"] = {"autocommit": git["autocommit"]}
    loop = raw.get("loop")
    if isinstance(loop, dict):
        merged = dict(data["loop"])
        if "stage" in loop:
            merged["stage"] = loop["stage"]
        if "stem" in loop:
            merged["stem"] = loop["stem"]
        data["loop"] = merged
    return data


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    return raw


def _load_document(root: Path) -> dict[str, Any]:
    path = policy_path(root)
    if path.is_dir():
        raise ValueError(".skore is a directory; expected a JSON file")
    doc = _read_json_object(path)
    return {} if doc is None else dict(doc)


def load_policy(root: Path) -> dict[str, Any]:
    """Read the ``workspace`` section, or defaults when missing.

    Also accepts a leftover flat ``.skore-workspace.json`` for one
    release when ``.skore`` has no ``workspace`` section.
    """
    path = policy_path(root)
    if path.is_dir():
        raise ValueError(".skore is a directory; expected a JSON file")
    doc = _read_json_object(path)
    if doc is not None:
        inner = doc.get(WORKSPACE_KEY)
        if isinstance(inner, dict):
            return _merge_loaded(inner)
        if _POLICY_FLAT_KEYS & doc.keys() and WORKSPACE_KEY not in doc:
            return _merge_loaded(doc)
    legacy = _read_json_object(root / LEGACY_POLICY_FILENAME)
    if legacy is not None:
        if isinstance(legacy.get(WORKSPACE_KEY), dict):
            return _merge_loaded(legacy[WORKSPACE_KEY])
        return _merge_loaded(legacy)
    return empty_policy()


def save_policy(root: Path, policy: dict[str, Any]) -> Path:
    """Merge ``policy`` into ``.skore`` under ``workspace``.

    Parameters
    ----------
    root : pathlib.Path
        Project root.
    policy : dict
        Workspace policy mapping (not hub credentials).

    Returns
    -------
    pathlib.Path
        Path written.

    Raises
    ------
    ValueError
        If ``.skore`` exists as a directory.
    """
    dest = policy_path(root)
    if dest.is_dir():
        raise ValueError(".skore is a directory; expected a JSON file")
    document = _load_document(root)
    document[WORKSPACE_KEY] = policy
    dest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return dest


def set_policy_value(root: Path, key: str, value: str) -> dict[str, Any]:
    """Update one dotted policy key and persist.

    Raises
    ------
    ValueError
        Unknown key or invalid enum.
    """
    if key not in POLICY_SET_KEYS:
        raise ValueError(f"unknown policy key: {key}")
    parsed: Any = None if value in {"", "null", "none"} else value
    if key == "git.autocommit" and parsed not in AUTOCOMMIT_VALUES:
        raise ValueError("git.autocommit must be off, ask, or on")
    if key == "loop.stage" and parsed is not None and parsed not in LOOP_STAGES:
        raise ValueError(f"loop.stage must be one of {', '.join(LOOP_STAGES)}")
    policy = load_policy(root)
    if key.startswith("git."):
        policy["git"][key.split(".", 1)[1]] = parsed
    elif key.startswith("loop."):
        policy["loop"][key.split(".", 1)[1]] = parsed
    else:
        policy[key] = parsed
    save_policy(root, policy)
    return policy


def infer_loop_stage(
    root: Path, policy: dict[str, Any], snapshot: dict[str, Any]
) -> str:
    """Return policy stage or a filesystem-derived stage."""
    recorded = policy.get("loop", {}).get("stage")
    if recorded in LOOP_STAGES:
        return str(recorded)
    if not snapshot.get("has_src") and not snapshot.get("has_journal"):
        return "setup"
    if snapshot.get("eda") != "present":
        return "eda"
    stem = policy.get("loop", {}).get("stem") or snapshot.get("last_history_stem")
    if not stem:
        return "implement"
    if not (root / "tests" / "smoke" / f"test_{stem}.py").is_file():
        return "implement"
    if not (root / "audit" / f"{stem}.py").is_file():
        reports = root / "reports"
        if reports.is_dir() and any(reports.iterdir()):
            return "audit"
        return "evaluate"
    return "backlog"
