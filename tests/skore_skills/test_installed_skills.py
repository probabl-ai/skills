"""Tests for skill-install discovery beyond the status happy path."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skore_skills.installed_skills import (
    SIDECAR,
    _catalog_ids,
    _released_skill_ids,
    _sidecar_ids,
    installed_skills,
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_sidecar_scan_skips_files_bad_json_and_non_ids(tmp_path: Path) -> None:
    """Only a sidecar object with a string id counts as installed."""
    target = tmp_path / ".agents" / "skills"
    _write(target / "notes.txt", "not a skill dir\n")
    _write(target / "bare" / "SKILL.md", "# bare\n")
    _write(target / "broken" / SIDECAR, "{")
    _write(target / "numeric" / SIDECAR, json.dumps({"id": 1}) + "\n")
    _write(target / "setup-git" / SIDECAR, json.dumps({"id": "setup-git"}) + "\n")
    _write(
        target / ".catalog.json",
        json.dumps({"skills": [{"id": "setup-git"}, {"id": "setup-workspace"}]}) + "\n",
    )

    flags = installed_skills(tmp_path, home=tmp_path / "empty-home")

    assert flags == {"setup-git": True, "setup-workspace": False}


def test_catalog_errors_fall_through_to_the_next_file(tmp_path: Path) -> None:
    """A corrupt ``.catalog.json`` is skipped in favor of ``catalog.json``."""
    target = tmp_path / ".agents" / "skills"
    _write(target / ".catalog.json", "{")
    _write(
        target / "catalog.json",
        json.dumps({"skills": [{"id": "setup-git"}, "not-an-object"]}) + "\n",
    )
    _write(target / "setup-git" / SIDECAR, json.dumps({"id": "setup-git"}) + "\n")

    assert _catalog_ids(target) == {"setup-git"}
    flags = installed_skills(tmp_path, home=tmp_path / "empty-home")
    assert flags == {"setup-git": True}


def test_non_object_catalog_does_not_define_a_universe(tmp_path: Path) -> None:
    """A JSON list is not a catalog; sidecars still mark installs."""
    target = tmp_path / ".agents" / "skills"
    _write(target / ".catalog.json", "[]\n")
    _write(target / "setup-git" / SIDECAR, json.dumps({"id": "setup-git"}) + "\n")

    flags = installed_skills(tmp_path, home=tmp_path / "empty-home")

    assert flags == {"setup-git": True}


def test_missing_target_has_no_sidecars(tmp_path: Path) -> None:
    """A path that is not a directory contributes no install ids."""
    assert _sidecar_ids(tmp_path / "missing") == set()


def test_unreadable_skill_root_is_skipped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An unreadable project root does not hide a home install."""
    home = tmp_path / "home"
    target = home / ".agents" / "skills"
    _write(target / ".catalog.json", json.dumps({"skills": [{"id": "setup-git"}]}))
    _write(target / "setup-git" / SIDECAR, json.dumps({"id": "setup-git"}) + "\n")
    project = tmp_path / "project"
    project.mkdir()
    real_glob = Path.glob

    def glob(self: Path, pattern: str):
        if self == project:
            raise OSError("denied")
        return real_glob(self, pattern)

    monkeypatch.setattr(Path, "glob", glob)

    flags = installed_skills(project, home=home)

    assert flags == {"setup-git": True}


def test_released_ids_prefer_the_packaged_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A readable wheel catalog is the fallback universe."""
    from skore_skills import installed_skills as mod

    class Packaged:
        def is_file(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            return json.dumps({"skills": [{"id": "from-wheel"}]})

    class Root:
        def joinpath(self, name: str) -> Packaged:
            assert name == "data/catalog.json"
            return Packaged()

    monkeypatch.setattr(mod, "files", lambda package: Root())

    assert _released_skill_ids() == {"from-wheel"}


def test_released_ids_skip_unreadable_catalogs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Corrupt packaged and parent catalogs are skipped until one parses."""
    from skore_skills import installed_skills as mod

    class Packaged:
        def is_file(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            raise OSError("unreadable")

    class Root:
        def joinpath(self, name: str) -> Packaged:
            return Packaged()

    monkeypatch.setattr(mod, "files", lambda package: Root())
    module_file = Path(mod.__file__)
    real_resolve = Path.resolve

    def resolve(self: Path, *args: object, **kwargs: object) -> Path:
        if self == module_file:
            return tmp_path / "src" / "installed_skills.py"
        return real_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    _write(tmp_path / "src" / ".catalog.json", "{")
    _write(
        tmp_path / ".catalog.json",
        json.dumps({"skills": [{"id": "from-parent"}]}) + "\n",
    )

    assert _released_skill_ids() == {"from-parent"}


def test_released_ids_empty_when_every_catalog_is_corrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No readable catalog yields an empty id set."""
    from skore_skills import installed_skills as mod

    class Packaged:
        def is_file(self) -> bool:
            return True

        def read_text(self, encoding: str = "utf-8") -> str:
            return "{"

    class Root:
        def joinpath(self, name: str) -> Packaged:
            return Packaged()

    monkeypatch.setattr(mod, "files", lambda package: Root())
    module_file = Path(mod.__file__)
    real_resolve = Path.resolve

    def resolve(self: Path, *args: object, **kwargs: object) -> Path:
        if self == module_file:
            return tmp_path / "installed_skills.py"
        return real_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    _write(tmp_path / ".catalog.json", "{")

    assert _released_skill_ids() == set()
