"""Hatchling hook that sets the package version from ``VERSION.txt``."""

from __future__ import annotations

from pathlib import Path

try:
    from hatchling.metadata.plugin.interface import MetadataHookInterface
except ImportError:  # pragma: no cover - present when Hatch builds the package
    MetadataHookInterface = object  # type: ignore[misc,assignment]


def version_from_root(root: Path, default: str) -> str:
    """Return the stripped ``VERSION.txt`` text, or ``default`` when absent.

    Parameters
    ----------
    root : pathlib.Path
        Project root that may contain ``VERSION.txt``.
    default : str
        Version used for a local checkout that has not been released.

    Returns
    -------
    str
        The release version or ``default``.
    """
    try:
        return (Path(root) / "VERSION.txt").read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return default


class MetadataHook(MetadataHookInterface):
    """Set ``version`` from the file written by the release workflow."""

    def update(self, metadata: dict) -> None:
        """Write the release version into the package metadata."""
        metadata["version"] = version_from_root(
            Path(self.root), self.config["version-default"]
        )
