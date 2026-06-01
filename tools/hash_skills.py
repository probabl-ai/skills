#!/usr/bin/env python3
"""Compute SHA-256 hashes for each skill in ``catalog.json``.

For every entry in the catalog's ``skills`` array, this script walks the
skill's ``path`` directory, hashes every file's relative path + content
into a single SHA-256 digest, and writes that digest back into the
entry's ``hash`` field.

A top-level ``catalog_hash`` is then computed over the sorted list of
``(id, hash)`` pairs, giving a stable aggregate fingerprint for the
whole catalog.

Usage
-----
    # Update catalog.json in place
    python tools/hash_skills.py

    # Check mode: exit non-zero if any hash is stale (no writes)
    python tools/hash_skills.py --check

    # Use a non-default catalog path
    python tools/hash_skills.py --catalog path/to/catalog.json

Notes
-----
- File path inside a skill is hashed as a POSIX path so digests are
  stable across operating systems.
- ``.DS_Store``, ``__pycache__/``, ``.pytest_cache/``, and ``*.pyc``
  files are skipped: they're build artefacts, not part of the skill.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Files / directory names that must never contribute to a skill hash.
EXCLUDED_NAMES = {".DS_Store", "__pycache__", ".pytest_cache", ".mypy_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def iter_skill_files(skill_dir: Path) -> list[Path]:
    """Return the sorted list of files contributing to a skill's hash.

    Parameters
    ----------
    skill_dir : pathlib.Path
        Directory of a single skill (e.g. ``skills/build-ml-pipeline``).

    Returns
    -------
    list[pathlib.Path]
        All non-excluded files under ``skill_dir``, sorted by their
        POSIX path relative to ``skill_dir`` so the order is stable
        across operating systems.
    """
    files: list[Path] = []
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_NAMES for part in path.relative_to(skill_dir).parts):
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        files.append(path)
    files.sort(key=lambda p: p.relative_to(skill_dir).as_posix())
    return files


def hash_skill(skill_dir: Path) -> str:
    """Compute the SHA-256 digest of a skill directory.

    The digest covers every non-excluded file: for each file we feed
    its POSIX-relative path, a NUL separator, its byte length, another
    NUL separator, its raw bytes, and a final newline into the hasher.
    This makes both renames and content edits affect the digest.

    Parameters
    ----------
    skill_dir : pathlib.Path
        Directory of a single skill.

    Returns
    -------
    str
        Hex-encoded SHA-256 digest of the skill's content.
    """
    hasher = hashlib.sha256()
    for path in iter_skill_files(skill_dir):
        rel = path.relative_to(skill_dir).as_posix().encode("utf-8")
        data = path.read_bytes()
        hasher.update(rel)
        hasher.update(b"\0")
        hasher.update(str(len(data)).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(data)
        hasher.update(b"\n")
    return hasher.hexdigest()


def aggregate_hash(skills: list[dict]) -> str:
    """Compute the aggregate catalog hash.

    Concatenates ``"<id>\\t<hash>\\n"`` for each skill (sorted by id)
    and hashes the result with SHA-256. The catalog hash therefore
    changes when any skill's content changes, when a skill is added or
    removed, or when a skill's id changes.

    Parameters
    ----------
    skills : list[dict]
        Skill entries from the catalog, each with ``id`` and ``hash``
        fields already populated.

    Returns
    -------
    str
        Hex-encoded SHA-256 digest summarising the whole catalog.
    """
    hasher = hashlib.sha256()
    for skill in sorted(skills, key=lambda s: s["id"]):
        line = f"{skill['id']}\t{skill['hash']}\n".encode("utf-8")
        hasher.update(line)
    return hasher.hexdigest()


def update_catalog(catalog_path: Path, check: bool) -> int:
    """Update or check skill hashes in ``catalog_path``.

    Parameters
    ----------
    catalog_path : pathlib.Path
        Path to the catalog JSON file.
    check : bool
        If True, do not write; exit non-zero when any hash is stale.

    Returns
    -------
    int
        Process exit code: 0 on success, 1 when ``--check`` finds a
        stale hash.
    """
    repo_root = catalog_path.parent
    with catalog_path.open(encoding="utf-8") as fh:
        catalog = json.load(fh)

    stale: list[str] = []
    for skill in catalog["skills"]:
        skill_dir = repo_root / skill["path"]
        if not skill_dir.is_dir():
            raise FileNotFoundError(
                f"Skill '{skill['id']}' points to missing path: {skill_dir}"
            )
        new_hash = hash_skill(skill_dir)
        if skill.get("hash") != new_hash:
            stale.append(skill["id"])
        skill["hash"] = new_hash

    new_catalog_hash = aggregate_hash(catalog["skills"])
    if catalog.get("catalog_hash") != new_catalog_hash:
        stale.append("<catalog_hash>")
    catalog["catalog_hash"] = new_catalog_hash

    if check:
        if stale:
            print("Stale hashes detected:", file=sys.stderr)
            for entry in stale:
                print(f"  - {entry}", file=sys.stderr)
            print(
                "Run `python tools/hash_skills.py` to refresh the catalog.",
                file=sys.stderr,
            )
            return 1
        print("All skill hashes are up to date.")
        return 0

    with catalog_path.open("w", encoding="utf-8") as fh:
        json.dump(catalog, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    if stale:
        print(f"Updated {len(stale)} stale hash(es) in {catalog_path.name}:")
        for entry in stale:
            print(f"  - {entry}")
    else:
        print(f"No changes; {catalog_path.name} was already up to date.")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    summary = (__doc__ or "").splitlines()[0] if __doc__ else ""
    parser = argparse.ArgumentParser(description=summary)
    default_catalog = Path(__file__).resolve().parent.parent / "catalog.json"
    parser.add_argument(
        "--catalog",
        type=Path,
        default=default_catalog,
        help="Path to catalog.json (default: %(default)s).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if any hash is stale; do not write.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()
    return update_catalog(args.catalog.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
