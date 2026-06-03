#!/usr/bin/env python3
"""Check that the package version agrees across every declaring source.

The repository ships its version in several files that are maintained by
hand. This script reads each one and fails if they disagree, so a release
bump can never leave one source lagging behind another.

Sources checked
---------------
1. ``catalog.json``                 -> top-level ``version``.
2. ``pixi.toml``                    -> ``[workspace] version``.
3. ``.claude-plugin/plugin.json``   -> ``version``.
4. ``.claude-plugin/marketplace.json`` -> each ``plugins[].version``.
5. ``.cursor-plugin/plugin.json``   -> ``version``.

Usage
-----
    python tools/check_versions.py

Exits 0 when every source reports the same version, 1 otherwise.
Designed to be wired into CI alongside ``hash_skills.py --check`` and
``validate_catalog.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path


def collect_versions(repo_root: Path) -> tuple[dict[str, str], list[str]]:
    """Collect the declared version from every known source.

    Parameters
    ----------
    repo_root : pathlib.Path
        Path to the repository root containing the version sources.

    Returns
    -------
    versions : dict[str, str]
        Mapping of ``"<source label>"`` to the version string found there.
    errors : list[str]
        Human-readable messages for sources that could not be read or that
        are missing the expected version field.
    """
    versions: dict[str, str] = {}
    errors: list[str] = []

    catalog_path = repo_root / "catalog.json"
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        versions["catalog.json"] = catalog["version"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        errors.append(f"catalog.json: could not read version ({exc})")

    pixi_path = repo_root / "pixi.toml"
    try:
        pixi = tomllib.loads(pixi_path.read_text(encoding="utf-8"))
        versions["pixi.toml"] = pixi["workspace"]["version"]
    except (OSError, tomllib.TOMLDecodeError, KeyError) as exc:
        errors.append(f"pixi.toml: could not read [workspace] version ({exc})")

    plugin_path = repo_root / ".claude-plugin" / "plugin.json"
    try:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        versions[".claude-plugin/plugin.json"] = plugin["version"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        errors.append(f".claude-plugin/plugin.json: could not read version ({exc})")

    cursor_plugin_path = repo_root / ".cursor-plugin" / "plugin.json"
    try:
        cursor_plugin = json.loads(cursor_plugin_path.read_text(encoding="utf-8"))
        versions[".cursor-plugin/plugin.json"] = cursor_plugin["version"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        errors.append(f".cursor-plugin/plugin.json: could not read version ({exc})")

    marketplace_path = repo_root / ".claude-plugin" / "marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        for plugin_entry in marketplace["plugins"]:
            label = f".claude-plugin/marketplace.json (plugin {plugin_entry['name']!r})"
            versions[label] = plugin_entry["version"]
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        errors.append(
            f".claude-plugin/marketplace.json: could not read plugin version ({exc})"
        )

    return versions, errors


def check(repo_root: Path) -> list[str]:
    """Return a list of version-consistency errors for ``repo_root``.

    An empty list means every source declares the same version.

    Parameters
    ----------
    repo_root : pathlib.Path
        Path to the repository root containing the version sources.

    Returns
    -------
    list[str]
        Human-readable error messages, one per problem detected.
    """
    versions, errors = collect_versions(repo_root)

    distinct = set(versions.values())
    if len(distinct) > 1:
        detail = ", ".join(
            f"{source} -> {version}" for source, version in sorted(versions.items())
        )
        errors.append(f"version mismatch across sources: {detail}")

    return errors


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    summary = (__doc__ or "").splitlines()[0] if __doc__ else ""
    parser = argparse.ArgumentParser(description=summary)
    default_root = Path(__file__).resolve().parent.parent
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=default_root,
        help="Path to the repository root (default: %(default)s).",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = parse_args()
    repo_root = args.repo_root.resolve()
    errors = check(repo_root)

    if errors:
        print("version consistency check failed:", file=sys.stderr)
        for err in errors:
            # ``::error::`` makes GitHub Actions surface it as an annotation
            # when run inside a workflow; harmless locally.
            print(f"::error::{err}", file=sys.stderr)
        return 1

    versions, _ = collect_versions(repo_root)
    version = next(iter(versions.values()), "<none>")
    print(f"OK \u2014 version {version} consistent across {len(versions)} sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
