#!/usr/bin/env python3
"""Bump the package version across every declaring source.

Increments the semver ``major``, ``minor``, or ``patch`` component and
writes the new version consistently to ``catalog.json``, ``pixi.toml``,
``.claude-plugin/plugin.json``, ``.claude-plugin/marketplace.json``, and
``.cursor-plugin/plugin.json``.

The script refuses to run when those sources disagree; run
``check_versions.py`` first to diagnose drift.

Usage
-----
    python tools/bump_version.py major
    python tools/bump_version.py minor --dry-run
    python tools/bump_version.py patch

Exits 0 on success, 1 on error. Does not create git commits or tags.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Allow importing sibling maintenance scripts when invoked as a file path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_versions import check, collect_versions  # noqa: E402

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

VERSION_FILES: tuple[str, ...] = (
    "catalog.json",
    "pixi.toml",
    ".claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/plugin.json",
)


def bump_version(current: str, component: str) -> str:
    """Return the next version after bumping ``component``.

    Parameters
    ----------
    current : str
        Current semver string ``X.Y.Z``.
    component : str
        One of ``"major"``, ``"minor"``, or ``"patch"``.

    Returns
    -------
    str
        The bumped semver string.

    Raises
    ------
    ValueError
        If ``current`` is not a valid ``X.Y.Z`` string or ``component`` is
        unknown.
    """
    match = SEMVER_RE.match(current)
    if not match:
        raise ValueError(f"current version {current!r} is not valid semver X.Y.Z")

    major, minor, patch = (int(part) for part in match.groups())
    if component == "major":
        return f"{major + 1}.0.0"
    if component == "minor":
        return f"{major}.{minor + 1}.0"
    if component == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"unknown component {component!r}")


def replacement_patterns(current: str, new: str, relative_path: str) -> tuple[str, str]:
    """Return the old/new search strings for a version source file.

    Parameters
    ----------
    current : str
        Version string currently declared in the file.
    new : str
        Version string to write.
    relative_path : str
        Repository-relative path to the file being updated.

    Returns
    -------
    tuple[str, str]
        ``(old_fragment, new_fragment)`` suitable for a single in-place
        string replacement.
    """
    if relative_path == "pixi.toml":
        return f'version = "{current}"', f'version = "{new}"'
    return f'"version": "{current}"', f'"version": "{new}"'


def apply_bump(repo_root: Path, current: str, new: str, dry_run: bool) -> list[str]:
    """Write the bumped version to every declaring source.

    Parameters
    ----------
    repo_root : pathlib.Path
        Path to the repository root.
    current : str
        Current consistent version across all sources.
    new : str
        Target version after the bump.
    dry_run : bool
        When True, report planned changes without writing files.

    Returns
    -------
    list[str]
        Human-readable error messages; empty when every file was updated
        (or would be updated in dry-run mode).
    """
    errors: list[str] = []

    for relative in VERSION_FILES:
        path = repo_root / relative
        old_fragment, new_fragment = replacement_patterns(current, new, relative)
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{relative}: could not read file ({exc})")
            continue

        count = text.count(old_fragment)
        if count == 0:
            errors.append(
                f"{relative}: expected exactly one occurrence of {old_fragment!r}, found 0"
            )
            continue
        if count > 1:
            errors.append(
                f"{relative}: expected exactly one occurrence of {old_fragment!r}, "
                f"found {count}"
            )
            continue

        if dry_run:
            print(f"  would update {relative}")
            continue

        path.write_text(text.replace(old_fragment, new_fragment, 1), encoding="utf-8")

    return errors


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    summary = (__doc__ or "").splitlines()[0] if __doc__ else ""
    parser = argparse.ArgumentParser(description=summary)
    parser.add_argument(
        "component",
        choices=("major", "minor", "patch"),
        help="Semver component to increment.",
    )
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_root,
        help="Path to the repository root (default: %(default)s).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned bump without writing any files.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()
    repo_root = args.repo_root.resolve()

    consistency_errors = check(repo_root)
    if consistency_errors:
        print("version bump aborted:", file=sys.stderr)
        for err in consistency_errors:
            print(f"::error::{err}", file=sys.stderr)
        return 1

    versions, read_errors = collect_versions(repo_root)
    if read_errors:
        print("version bump aborted:", file=sys.stderr)
        for err in read_errors:
            print(f"::error::{err}", file=sys.stderr)
        return 1

    current = next(iter(versions.values()))
    try:
        new = bump_version(current, args.component)
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"Dry run — would bump {current} -> {new}:")
    else:
        print(f"Bumping {current} -> {new}:")

    update_errors = apply_bump(repo_root, current, new, args.dry_run)
    if update_errors:
        print("version bump failed:", file=sys.stderr)
        for err in update_errors:
            print(f"::error::{err}", file=sys.stderr)
        return 1

    if args.dry_run:
        print(f"OK — dry run complete; no files were modified.")
    else:
        print(f"Bumped version {current} -> {new} across {len(VERSION_FILES)} sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
