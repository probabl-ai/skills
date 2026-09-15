"""Read-only filesystem snapshot of an ML workspace.

Detection copies the python-env-manager table (files at the project
root only). Ambient PATH managers are ignored.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from skore_skills.policy import infer_loop_stage, load_policy

# First-signal-wins order from python-env-manager § Detection.
MANAGER_ORDER = ("pixi", "uv", "poetry", "hatch", "conda", "pip-venv")

STATUS_KEYS = (
    "package",
    "env_manager",
    "has_src",
    "has_experiments",
    "has_journal",
    "has_tests",
    "eda",
    "ruff_toml",
    "git",
    "last_history_stem",
    "policy",
    "loop_stage",
)


def load_pyproject(root: Path) -> dict[str, Any]:
    """Parse ``pyproject.toml`` if present."""
    path = root / "pyproject.toml"
    if not path.is_file():
        return {}
    return tomllib.loads(path.read_text(encoding="utf-8"))


def manager_evidence(root: Path) -> dict[str, list[str]]:
    """Return visible env-manager signals at ``root``.

    Parameters
    ----------
    root : pathlib.Path
        Project root.

    Returns
    -------
    dict
        Mapping of manager name to evidence filenames / sections.
    """
    evidence: dict[str, list[str]] = {}
    pixi_files = [
        name for name in ("pixi.toml", "pixi.lock") if (root / name).is_file()
    ]
    if pixi_files:
        evidence["pixi"] = pixi_files

    pyproject = load_pyproject(root)
    tools = pyproject.get("tool", {}) if isinstance(pyproject.get("tool"), dict) else {}

    uv_bits: list[str] = []
    if (root / "uv.lock").is_file():
        uv_bits.append("uv.lock")
    if "uv" in tools:
        uv_bits.append("pyproject.toml:[tool.uv]")
    if uv_bits:
        evidence["uv"] = uv_bits

    poetry_bits: list[str] = []
    if (root / "poetry.lock").is_file():
        poetry_bits.append("poetry.lock")
    if "poetry" in tools:
        poetry_bits.append("pyproject.toml:[tool.poetry]")
    if poetry_bits:
        evidence["poetry"] = poetry_bits

    hatch_bits: list[str] = []
    if (root / "hatch.toml").is_file():
        hatch_bits.append("hatch.toml")
    if "hatch" in tools:
        hatch_bits.append("pyproject.toml:[tool.hatch]")
    if hatch_bits:
        evidence["hatch"] = hatch_bits

    conda_files = [
        name
        for name in ("environment.yml", "environment.yaml")
        if (root / name).is_file()
    ]
    if conda_files:
        evidence["conda"] = conda_files

    venv_dir = None
    for name in (".venv", "venv"):
        if (root / name).is_dir():
            venv_dir = name
            break
    if (root / "requirements.txt").is_file() and venv_dir is not None:
        evidence["pip-venv"] = ["requirements.txt", venv_dir]

    return evidence


def first_manager(evidence: dict[str, list[str]]) -> str:
    """Return the first manager in table order, or ``none``."""
    for name in MANAGER_ORDER:
        if name in evidence:
            return name
    return "none"


def package_name(root: Path) -> str | None:
    """Return ``[project].name`` or the first ``src/`` package directory."""
    pyproject = load_pyproject(root)
    project = pyproject.get("project")
    if isinstance(project, dict):
        name = project.get("name")
        if isinstance(name, str) and name:
            return name
    src = root / "src"
    if src.is_dir():
        dirs = sorted(path.name for path in src.iterdir() if path.is_dir())
        if dirs:
            return dirs[0]
    return None


def last_history_stem(root: Path) -> str | None:
    """Stem of the last ``journal/*.md`` note, excluding ``JOURNAL.md``."""
    journal = root / "journal"
    if not journal.is_dir():
        return None
    notes = sorted(
        path
        for path in journal.glob("*.md")
        if path.name != "JOURNAL.md" and path.is_file()
    )
    if not notes:
        return None
    return notes[-1].stem


def is_scaffolded(root: Path) -> bool:
    """Return True if ``src/`` or ``journal/`` exists.

    Fail closed when both are missing (empty / unorganized tree).
    """
    return (root / "src").is_dir() or (root / "journal").is_dir()


def snapshot(root: Path) -> dict[str, Any]:
    """Return the frozen ``status`` mapping for ``root``."""
    evidence = manager_evidence(root)
    payload: dict[str, Any] = {
        "package": package_name(root),
        "env_manager": first_manager(evidence),
        "has_src": (root / "src").is_dir(),
        "has_experiments": (root / "experiments").is_dir(),
        "has_journal": (root / "journal").is_dir(),
        "has_tests": (root / "tests").is_dir(),
        "eda": "present" if (root / "data" / "eda.md").is_file() else "missing",
        "ruff_toml": (root / "ruff.toml").is_file(),
        "git": (root / ".git").exists(),
        "last_history_stem": last_history_stem(root),
    }
    policy = load_policy(root)
    payload["policy"] = policy
    payload["loop_stage"] = infer_loop_stage(root, policy, payload)
    return payload


def format_status_text(payload: dict[str, Any]) -> str:
    """Render ``payload`` as one key: value line per frozen key."""
    lines = [f"{key}: {payload[key]}" for key in STATUS_KEYS]
    return "\n".join(lines) + "\n"
