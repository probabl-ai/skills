#!/usr/bin/env python3
"""Validate ``catalog.json`` against the on-disk ``skills/`` directory.

The validator enforces four invariants:

1. Every directory under ``skills/`` has a matching entry in
   ``catalog.json``'s ``skills`` array, and vice versa.
2. Every catalog entry's ``path`` resolves to a directory containing a
   ``SKILL.md`` file.
3. Every skill entry uses a known ``category`` and a permitted
   ``subcategory`` for that category (``null`` is required for
   categories that don't take a subcategory).
4. Every workflow's ``includes`` list references known skill ids.

Usage
-----
    python tools/validate_catalog.py

Exits 0 on success, 1 on the first error. Designed to be wired into
CI alongside ``hash_skills.py --check``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow-list: category -> set of permitted subcategories.
# An empty set means the category does not take a subcategory
# (entries under it must have ``"subcategory": null``).
CATEGORIES: dict[str, set[str]] = {
    "methodology": set(),
    "orchestration": {"dispatchers", "experiment-sourcing", "test-strategies"},
    "tooling": {"project-setup", "code-quality"},
    "reference": set(),
}


def validate(catalog_path: Path) -> list[str]:
    """Return a list of validation errors for ``catalog_path``.

    An empty list means the catalog is valid.

    Parameters
    ----------
    catalog_path : pathlib.Path
        Path to the catalog JSON file.

    Returns
    -------
    list[str]
        Human-readable error messages, one per problem detected.
    """
    repo_root = catalog_path.parent
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    errors: list[str] = []

    catalog_ids = {s["id"] for s in catalog["skills"]}
    skills_dir = repo_root / "skills"
    folder_ids = {p.name for p in skills_dir.iterdir() if p.is_dir()}

    missing_in_catalog = folder_ids - catalog_ids
    if missing_in_catalog:
        errors.append(
            f"skill folders without a catalog.json entry: {sorted(missing_in_catalog)}"
        )

    missing_folders = catalog_ids - folder_ids
    if missing_folders:
        errors.append(
            "catalog.json entries without a matching skills/ folder: "
            f"{sorted(missing_folders)}"
        )

    for skill in catalog["skills"]:
        sid = skill["id"]
        skill_path = repo_root / skill["path"]
        if not (skill_path / "SKILL.md").is_file():
            errors.append(f"{skill['path']}/SKILL.md is missing")

        cat = skill.get("category")
        sub = skill.get("subcategory")
        if cat not in CATEGORIES:
            errors.append(
                f"skill {sid!r} has unknown category {cat!r} "
                f"(allowed: {sorted(CATEGORIES)})"
            )
            continue
        allowed_subs = CATEGORIES[cat]
        if allowed_subs:
            if sub not in allowed_subs:
                errors.append(
                    f"skill {sid!r}: subcategory {sub!r} not allowed under "
                    f"category {cat!r} (allowed: {sorted(allowed_subs)})"
                )
        elif sub is not None:
            errors.append(
                f"skill {sid!r}: category {cat!r} takes no subcategory, "
                f"got {sub!r}"
            )

    for workflow in catalog.get("workflows", []):
        unknown = [s for s in workflow.get("includes", []) if s not in catalog_ids]
        if unknown:
            errors.append(
                f"workflow {workflow['id']!r} references unknown skill ids: {unknown}"
            )

    return errors


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
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()
    catalog_path = args.catalog.resolve()
    errors = validate(catalog_path)

    if errors:
        print("catalog validation failed:", file=sys.stderr)
        for err in errors:
            # ``::error::`` makes GitHub Actions surface it as an annotation
            # when run inside a workflow; harmless locally.
            print(f"::error::{err}", file=sys.stderr)
        return 1

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    print(
        f"OK \u2014 {len(catalog['skills'])} skills, "
        f"{len(catalog.get('workflows', []))} workflow(s); all categories valid."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
