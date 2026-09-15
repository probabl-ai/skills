"""Run ruff check --fix then format on workspace defaults or given paths."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable, Sequence
from importlib.resources import files
from pathlib import Path

SKIP_DIR_NAMES = (".pixi", ".venv", "venv", "node_modules")
DEFAULT_DIRS = ("src", "experiments", "audit")
RUFF_MISSING = (
    "ruff is not installed in this interpreter. "
    "Install it with the project env manager (see python-env-manager), "
    "e.g. `pixi add --feature dev ruff`."
)


def initialize_style(root: Path) -> bool:
    """Copy the packaged ``ruff.toml`` when the workspace has none."""
    destination = root / "ruff.toml"
    if destination.exists():
        return False
    template = files("skore_skills").joinpath("data/ruff.toml")
    destination.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
    return True


def default_targets(root: Path) -> list[Path]:
    """Return existing default globs, skipping vendored directory names."""
    targets: list[Path] = []
    for name in DEFAULT_DIRS:
        path = root / name
        if path.is_dir() and path.name not in SKIP_DIR_NAMES:
            targets.append(path)
    eda = root / "data" / "eda.py"
    if eda.is_file():
        targets.append(eda)
    targets.extend(path for path in sorted(root.glob("*.py")) if path.is_file())
    return targets


def ruff_argv(*args: str, targets: list[Path]) -> list[str]:
    """Build ``python -m ruff`` argv with skip excludes."""
    cmd = [sys.executable, "-m", "ruff", *args]
    for name in SKIP_DIR_NAMES:
        cmd.extend(["--exclude", name])
    cmd.extend(str(path) for path in targets)
    return cmd


def ruff_is_installed() -> bool:
    """Return True if ``python -m ruff --version`` succeeds."""
    completed = subprocess.run(
        [sys.executable, "-m", "ruff", "--version"],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def run_style(
    root: Path,
    paths: Sequence[Path],
    *,
    warn: Callable[[str], None] | None = None,
) -> int:
    """Run ruff check --fix then format.

    Parameters
    ----------
    root : pathlib.Path
        Workspace root (used for defaults and ruff.toml presence).
    paths : sequence of pathlib.Path
        Explicit paths; empty means default globs.
    warn : callable or None, optional
        Called with a warning string (no ruff.toml on defaults).

    Returns
    -------
    int
        Combined ruff exit code (last non-zero, else 0).
    """
    if not ruff_is_installed():
        raise FileNotFoundError(RUFF_MISSING)
    explicit = [path if path.is_absolute() else root / path for path in paths]
    targets = explicit if explicit else default_targets(root)
    if not targets:
        return 0
    if warn is not None and not explicit and not (root / "ruff.toml").is_file():
        warn("no ruff.toml at project root; running ruff with its defaults")
    check = subprocess.run(ruff_argv("check", "--fix", targets=targets), check=False)
    fmt = subprocess.run(ruff_argv("format", targets=targets), check=False)
    if check.returncode:
        return check.returncode
    return fmt.returncode
