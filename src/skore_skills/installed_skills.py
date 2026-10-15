"""Detect skills installed by ``skore skills install``.

Source of truth is the same as skore-cli: ``.skore-skill.json``
sidecars under harness skill directories, plus each target's
``.catalog.json`` for the id universe. The released catalog is only
the fallback universe (available ids), never proof of install.

Targets are discovered from those artifacts rather than from a copy
of skore-cli's agent registry, so a new harness needs no change here.
"""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any

SIDECAR = ".skore-skill.json"
LOCAL_CATALOG = ".catalog.json"

# skore-cli installs into ``<dot-dir>/skills`` or
# ``<dot-dir>/<sub>/skills`` for every harness it supports, so match
# the artifacts it writes at those two depths instead of naming any
# harness.
SKILL_DIR_PATTERNS = (
    f".*/skills/*/{SIDECAR}",
    f".*/*/skills/*/{SIDECAR}",
    f".*/skills/{LOCAL_CATALOG}",
    f".*/*/skills/{LOCAL_CATALOG}",
)


def _skill_targets(root: Path, home: Path) -> list[Path]:
    """Return install targets discovered from skore-cli's own artifacts."""
    seen: set[Path] = set()
    targets: list[Path] = []
    for base in (root, home):
        for pattern in SKILL_DIR_PATTERNS:
            try:
                matches = sorted(base.glob(pattern))
            except OSError:
                continue
            for match in matches:
                # sidecar: <target>/<id>/<file>; catalog: <target>/<file>
                target = match.parent.parent if match.name == SIDECAR else match.parent
                resolved = target.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                targets.append(resolved)
    return targets


def _sidecar_ids(target: Path) -> set[str]:
    names: set[str] = set()
    if not target.is_dir():
        return names
    for child in target.iterdir():
        if not child.is_dir():
            continue
        sidecar = child / SIDECAR
        if not sidecar.is_file():
            continue
        try:
            data = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("id"), str):
            names.add(data["id"])
    return names


def _ids_from_catalog_data(data: Any) -> set[str]:
    names: set[str] = set()
    if not isinstance(data, dict):
        return names
    sources = data.get("sources")
    if isinstance(sources, dict):
        for entry in sources.values():
            names.update(_ids_from_catalog_data(entry))
        return names
    skills = data.get("skills")
    if isinstance(skills, list):
        for item in skills:
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                names.add(item["id"])
    return names


def _catalog_ids(target: Path) -> set[str]:
    path = target / LOCAL_CATALOG
    if not path.is_file():
        return set()
    try:
        return _ids_from_catalog_data(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return set()


def _released_skill_ids() -> set[str]:
    packaged = files("skore_skills").joinpath("data/catalog.json")
    if packaged.is_file():
        try:
            return _ids_from_catalog_data(
                json.loads(packaged.read_text(encoding="utf-8"))
            )
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    for parent in Path(__file__).resolve().parents:
        candidate = parent / ".catalog.json"
        if candidate.is_file():
            try:
                return _ids_from_catalog_data(
                    json.loads(candidate.read_text(encoding="utf-8"))
                )
            except (OSError, json.JSONDecodeError):
                continue
    return set()


def installed_skills(root: Path, *, home: Path | None = None) -> dict[str, bool | None]:
    """Return catalog skill ids mapped to install flags for ``root``.

    ``True`` / ``False`` when a catalog universe is known. ``None``
    when neither a target catalog, a sidecar, nor the released
    catalog can be read.
    """
    home_root = home if home is not None else Path.home()
    installed: set[str] = set()
    universe: set[str] = set()
    for target in _skill_targets(root, home_root):
        sidecars = _sidecar_ids(target)
        installed.update(sidecars)
        universe.update(_catalog_ids(target))
        universe.update(sidecars)

    if not universe:
        universe = _released_skill_ids()
    if not universe:
        return {}
    return {name: name in installed for name in sorted(universe)}
