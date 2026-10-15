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
WORKSPACE_KEY = "workspace"

AUTOCOMMIT_VALUES = ("off", "on")
SNAPSHOT_VALUES = ("committed", "declined", "skipped")
LOOP_STAGES = (
    "setup",
    "data_analysis",
    "implement",
    "evaluate",
    "backlog",
)

SETUP_PIECES = ("env", "workspace", "editable", "git")
SETUP_VALUES = ("done", "declined")

POLICY_SET_KEYS = (
    "env_manager",
    "env.managed",
    "package",
    "tabular",
    "skore_mode",
    "notebooks",
    "site",
    "git.autocommit",
    "git.snapshot",
    "loop.stage",
    "loop.stem",
    "setup.env",
    "setup.workspace",
    "setup.editable",
    "setup.git",
)

MANAGED_TRUE = ("true", "on", "yes")
MANAGED_FALSE = ("false", "off", "no")
BOOL_KEYS = frozenset({"notebooks", "site"})


def empty_policy() -> dict[str, Any]:
    """Return the default policy mapping."""
    return {
        "env_manager": None,
        "package": None,
        "tabular": None,
        "skore_mode": None,
        "notebooks": None,
        "site": None,
        "env": {"managed": None},
        "git": {"autocommit": None, "snapshot": None},
        "loop": {"stage": None, "stem": None},
        "setup": dict.fromkeys(SETUP_PIECES),
    }


def policy_path(root: Path) -> Path:
    """Return the ``.skore`` path under ``root``."""
    return root / POLICY_FILENAME


def _merge_loaded(raw: Any) -> dict[str, Any]:
    data = empty_policy()
    if not isinstance(raw, dict):
        return data
    for key in (
        "env_manager",
        "package",
        "tabular",
        "skore_mode",
        "notebooks",
        "site",
    ):
        if key in raw:
            data[key] = raw[key]
    env = raw.get("env")
    if isinstance(env, dict) and "managed" in env:
        managed = env["managed"]
        if managed is True or managed is False:
            data["env"] = {"managed": managed}
        elif isinstance(managed, str) and managed.lower() in MANAGED_TRUE:
            data["env"] = {"managed": True}
        elif isinstance(managed, str) and managed.lower() in MANAGED_FALSE:
            data["env"] = {"managed": False}
    git = raw.get("git")
    if isinstance(git, dict):
        autocommit = git.get("autocommit")
        recorded = git.get("snapshot")
        data["git"] = {
            "autocommit": autocommit if autocommit in AUTOCOMMIT_VALUES else None,
            "snapshot": recorded if recorded in SNAPSHOT_VALUES else None,
        }
    loop = raw.get("loop")
    if isinstance(loop, dict):
        merged = dict(data["loop"])
        if "stage" in loop:
            merged["stage"] = loop["stage"]
        if "stem" in loop:
            merged["stem"] = loop["stem"]
        data["loop"] = merged
    setup = raw.get("setup")
    if isinstance(setup, dict):
        merged_setup = dict(data["setup"])
        for piece in SETUP_PIECES:
            value = setup.get(piece)
            if value in SETUP_VALUES:
                merged_setup[piece] = value
        data["setup"] = merged_setup
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
    """Read the ``workspace`` section, or defaults when missing."""
    path = policy_path(root)
    if path.is_dir():
        raise ValueError(".skore is a directory; expected a JSON file")
    doc = _read_json_object(path)
    if doc is not None:
        inner = doc.get(WORKSPACE_KEY)
        if isinstance(inner, dict):
            return _merge_loaded(inner)
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
    if (
        key == "git.autocommit"
        and parsed is not None
        and parsed not in AUTOCOMMIT_VALUES
    ):
        raise ValueError("git.autocommit must be off or on")
    if key == "git.snapshot" and parsed is not None and parsed not in SNAPSHOT_VALUES:
        raise ValueError("git.snapshot must be committed, declined, or skipped")
    if key == "loop.stage" and parsed is not None and parsed not in LOOP_STAGES:
        raise ValueError(f"loop.stage must be one of {', '.join(LOOP_STAGES)}")
    if key.startswith("setup.") and parsed is not None and parsed not in SETUP_VALUES:
        raise ValueError("setup piece must be done or declined")
    if key == "env.managed" and parsed is not None:
        lowered = str(parsed).lower()
        if lowered in MANAGED_TRUE:
            parsed = True
        elif lowered in MANAGED_FALSE:
            parsed = False
        else:
            raise ValueError("env.managed must be true or false")
    if key in BOOL_KEYS and parsed is not None:
        lowered = str(parsed).lower()
        if lowered in MANAGED_TRUE:
            parsed = True
        elif lowered in MANAGED_FALSE:
            parsed = False
        else:
            raise ValueError(f"{key} must be true or false")
    policy = load_policy(root)
    if key.startswith("setup."):
        policy["setup"][key.split(".", 1)[1]] = parsed
    elif key.startswith("git."):
        policy["git"][key.split(".", 1)[1]] = parsed
    elif key.startswith("loop."):
        policy["loop"][key.split(".", 1)[1]] = parsed
    elif key.startswith("env."):
        policy["env"][key.split(".", 1)[1]] = parsed
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
    if snapshot.get("data_analysis") not in {"present", "skipped"}:
        return "data_analysis"
    stem = policy.get("loop", {}).get("stem") or snapshot.get("last_history_stem")
    if not stem:
        return "implement"
    if not (root / "tests" / "smoke" / f"test_{stem}.py").is_file():
        return "implement"
    if not (root / "audit" / f"{stem}.py").is_file():
        return "evaluate"
    return "backlog"
