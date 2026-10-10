"""Run ruff check --fix then format on workspace defaults or given paths."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

SKIP_DIR_NAMES = (".pixi", ".venv", "venv", "node_modules")
DEFAULT_DIRS = ("src", "experiments", "audit", "data_analysis")
RUFF_MISSING = (
    "ruff is not installed in this interpreter. "
    "Install it with the project env manager "
    "(python -m skore_skills env add --feature agent ruff)."
)
RUFF_PYPROJECT_TABLE = """\
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "D"]

[tool.ruff.lint.per-file-ignores]
"experiments/**" = ["E402", "B018", "D100", "D103"]
"audit/**" = ["E402", "B018", "D100", "D103"]
"data_analysis/**" = ["E402", "B018", "D100", "D103"]

[tool.ruff.lint.pydocstyle]
convention = "numpy"

[tool.ruff.format]
docstring-code-format = true
"""


def ruff_configured(root: Path) -> bool:
    """Return True if ruff.toml or ``[tool.ruff]`` exists."""
    if (root / "ruff.toml").is_file():
        return True
    path = root / "pyproject.toml"
    return path.is_file() and "[tool.ruff" in path.read_text(encoding="utf-8")


def ensure_ruff_in_pyproject(path: Path) -> bool:
    """Append ``[tool.ruff]`` to ``path`` when missing. Return True if written."""
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if "[tool.ruff" in text:
        return False
    path.write_text(text.rstrip() + "\n\n" + RUFF_PYPROJECT_TABLE, encoding="utf-8")
    return True


def initialize_style(root: Path) -> bool:
    """Ensure ``[tool.ruff]`` in pyproject.toml when no ruff config exists."""
    if ruff_configured(root):
        return False
    path = root / "pyproject.toml"
    if not path.is_file():
        path.write_text(RUFF_PYPROJECT_TABLE, encoding="utf-8")
        return True
    return ensure_ruff_in_pyproject(path)


def default_targets(root: Path) -> list[Path]:
    """Return existing default globs, skipping vendored directory names."""
    targets: list[Path] = []
    for name in DEFAULT_DIRS:
        path = root / name
        if path.is_dir() and path.name not in SKIP_DIR_NAMES:
            targets.append(path)
    targets.extend(path for path in sorted(root.glob("*.py")) if path.is_file())
    return targets


def ruff_candidates() -> list[Path]:
    """Return ``ruff`` paths owned by this interpreter, first preferred.

    Unix and Windows venvs keep the binary next to ``python``. A conda or
    pixi prefix on Windows keeps ``python.exe`` in the prefix root and
    ``ruff.exe`` in ``Scripts``.
    """
    executable = Path(sys.executable)
    names = ("ruff.exe", "ruff") if sys.platform == "win32" else ("ruff",)
    candidates = [executable.with_name(name) for name in names]
    if sys.platform == "win32":
        candidates.append(executable.parent / "Scripts" / "ruff.exe")
    return candidates


def ruff_executable() -> Path:
    """Return the ``ruff`` binary for this interpreter.

    Conda-forge ships that binary and no importable ``ruff`` module.
    The PyPI wheel ships both. ``python -m ruff`` only works for the wheel.
    """
    candidates = ruff_candidates()
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return candidates[0]


def ruff_argv(*args: str, targets: list[Path]) -> list[str]:
    """Build a ``ruff`` argv with skip excludes."""
    cmd = [str(ruff_executable()), *args]
    for name in SKIP_DIR_NAMES:
        cmd.extend(["--exclude", name])
    cmd.extend(str(path) for path in targets)
    return cmd


def ruff_is_installed() -> bool:
    """Return True if the sibling ``ruff`` binary runs ``--version``."""
    executable = ruff_executable()
    if not executable.is_file():
        return False
    completed = subprocess.run(
        [str(executable), "--version"],
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
    if warn is not None and not explicit and not ruff_configured(root):
        warn("no [tool.ruff] in pyproject.toml; running ruff with its defaults")
    check = subprocess.run(ruff_argv("check", "--fix", targets=targets), check=False)
    fmt = subprocess.run(ruff_argv("format", targets=targets), check=False)
    if check.returncode:
        return check.returncode
    return fmt.returncode
