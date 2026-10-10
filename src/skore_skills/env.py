"""Detect the project env manager and emit install / init commands."""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from collections.abc import Sequence
from importlib.resources import files
from pathlib import Path
from typing import Any

from skore_skills.policy import load_policy
from skore_skills.style import RUFF_PYPROJECT_TABLE, ensure_ruff_in_pyproject
from skore_skills.workspace import (
    MANAGER_ORDER,
    manager_detection,
    package_name,
)

NO_MANAGER = "no env manager detected; record one before installing packages"
AMBIGUOUS = "multiple env managers are visible; do not pick automatically"
UNMANAGED = "environment is user-managed (env.managed is false); do not install"
PIXI_TOML_PRESENT = (
    "pixi.toml already exists; refuse to add [tool.pixi] to pyproject.toml"
)
INIT_EXISTS = "manager tables already present; pass --force to replace them"
INIT_MISMATCH = "detected manager {detected!r} does not match --manager {wanted!r}"
EDITABLE_UNSUPPORTED = (
    "editable install is not supported for {manager}; do not pip install -e ."
)
NO_SRC = "has_src is false; scaffold before editable install"
NO_PACKAGE = "no package name; scaffold src/ before editable install"
SYNC_HINT = "python -m skore_skills env sync"
AGENT_PACKAGES = ("ruff", "ipython", "ipykernel")
BOOTSTRAP_PACKAGES = ("skore", "skore-skills", *AGENT_PACKAGES)
IN_DEV_ENV = "SKORE_SKILLS_IN_DEV"
MISSING_SKORE_SKILLS = "No module named 'skore_skills'"
MISSING_SKORE_SKILLS_HINT = (
    "skore-skills is supplied by skore but is missing from the project "
    "dev environment.\n"
    "run: python -m skore_skills env add-skore --mode local --execute\n"
)
_IMPORT_NAMES = {
    "ipython": "IPython",
    "scikit-learn": "sklearn",
}
CONDA_GRAPHVIZ_MANAGERS = frozenset({"pixi", "conda"})
GRAPHVIZ_DOCS = "https://graphviz.org/download/"
GRAPHVIZ_REPAIR = (
    "Graphviz SVG rendering failed; repair or reinstall pydot and Graphviz "
    "with their existing package managers"
)
GRAPHVIZ_PROBE_SNIPPET = """\
import sys
import xml.etree.ElementTree as ET

try:
    import pydot

    graph = pydot.Dot("probe", graph_type="digraph")
    graph.add_edge(pydot.Edge("source", "target"))
    root = ET.fromstring(graph.create_svg())
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise RuntimeError("Graphviz returned non-SVG output")
except Exception as exc:
    print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
    sys.exit(1)
"""
WHICH_DOT_SNIPPET = "import shutil; print(shutil.which('dot') or '')"

_SKELETON = """\
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "workspace"
version = "0.1.0"
description = "ML experimentation workspace."
requires-python = ">=3.11"
dependencies = []

[tool.hatch.build.targets.wheel]
packages = ["src"]
"""

_PIXI_TABLE = """
[tool.pixi.workspace]
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "osx-arm64", "win-64"]

[tool.pixi.feature.agent.dependencies]
ruff = "*"
ipython = "*"
ipykernel = "*"

[tool.pixi.environments]
default = { features = ["default"], solve-group = "default" }
agent = { features = ["agent"], solve-group = "default" }
dev = { features = ["default", "agent"], solve-group = "default" }
"""

_UV_GROUPS = """
[tool.uv]

[dependency-groups]
agent = ["ruff", "ipython", "ipykernel"]
"""

_PIP_GROUPS = """
[dependency-groups]
agent = ["ruff", "ipython", "ipykernel"]
"""

_POETRY_GROUPS = """
[tool.poetry]
package-mode = false

[dependency-groups]
agent = ["ruff", "ipython", "ipykernel"]
"""

_HATCH_ENV = """
[tool.hatch.envs.default]

[tool.hatch.envs.agent]
dependencies = ["ruff", "ipython", "ipykernel"]

[tool.hatch.envs.dev]
extra-dependencies = ["ruff", "ipython", "ipykernel"]
"""

_CONDA_DEFAULT = """\
name: workspace
channels:
  - conda-forge
dependencies:
  - python>=3.11
"""

_CONDA_AGENT = """\
name: workspace-agent
channels:
  - conda-forge
dependencies:
  - python>=3.11
  - ruff
  - ipython
  - ipykernel
"""

_CONDA_DEV = """\
name: workspace-dev
channels:
  - conda-forge
dependencies:
  - python>=3.11
  - ruff
  - ipython
  - ipykernel
"""


def load_stack_policy() -> dict[str, Any]:
    """Load packaged ``python-stack.json`` policy."""
    path = files("skore_skills").joinpath("data/python-stack.json")
    return json.loads(path.read_text(encoding="utf-8"))


_CONDA_PREFIX_MARKERS = (
    "miniconda",
    "miniconda3",
    "mambaforge",
    "micromamba",
    "anaconda",
    "anaconda3",
)


def _resolve_skore_binary() -> Path | None:
    """Return the real path of ``skore`` or ``skore-cli`` on PATH."""
    for name in ("skore", "skore-cli"):
        found = shutil.which(name)
        if found is None:
            continue
        path = Path(found)
        try:
            return path.resolve()
        except OSError:
            return path
    return None


def _manager_from_skore_path(path: Path) -> str | None:
    """Map a ``skore`` install path to a project manager, or None if weak."""
    parts = [part.lower() for part in path.parts]
    posix = path.as_posix().lower()
    if "pipx" in parts:
        return None
    if ".pixi" in parts or "/pixi/bin/" in posix:
        return "pixi"
    uv_tool = os.environ.get("UV_TOOL_DIR")
    if uv_tool:
        try:
            if path.resolve().is_relative_to(Path(uv_tool).resolve()):
                return "uv"
        except (OSError, ValueError):
            pass
    if "uv" in parts and "tools" in parts:
        return "uv"
    if "/uv/tools/" in posix:
        return "uv"
    parent = path.parent
    prefix = parent.parent if parent.name in {"bin", "Scripts"} else parent
    if (prefix / "conda-meta").is_dir():
        return "conda"
    if any(marker in parts for marker in _CONDA_PREFIX_MARKERS):
        return "conda"
    return None


def skore_cli_provenance() -> dict[str, str | None]:
    """Return how ``skore`` was installed, for ``recommended`` ranking only."""
    path = _resolve_skore_binary()
    if path is None:
        return {"manager": None, "path": None}
    return {"manager": _manager_from_skore_path(path), "path": str(path)}


def _recorded_manager(root: Path) -> str | None:
    recorded = load_policy(root).get("env_manager")
    if recorded in MANAGER_ORDER:
        return recorded
    return None


def _order_with_lead(lead: str | None) -> list[str]:
    order = list(MANAGER_ORDER)
    if lead in order:
        order.remove(lead)
        order.insert(0, lead)
    return order


def _recommended(
    root: Path,
    evidence: dict[str, list[str]],
    provenance_manager: str | None,
) -> list[str]:
    """Return manager names in ask order.

    Policy, then a unique manifest, then ``skore`` provenance, then
    ``MANAGER_ORDER``.
    """
    recorded = _recorded_manager(root)
    present = [name for name in MANAGER_ORDER if name in evidence]
    if recorded is not None:
        return _order_with_lead(recorded)
    if len(present) == 1:
        return present
    if present:
        return [name for name in MANAGER_ORDER if name in present]
    if provenance_manager in MANAGER_ORDER:
        return _order_with_lead(provenance_manager)
    return list(MANAGER_ORDER)


def detect(root: Path) -> dict[str, Any]:
    """Return detection JSON for ``root``.

    When two or more managers are visible, ``ambiguous`` is true and
    ``env_manager`` is null — the CLI must not pick a winner.
    ``recommended`` may still rank a recorded policy or ``skore``
    provenance; those do not change ``env_manager``.
    """
    manager = manager_detection(root)
    evidence = manager["evidence"]
    provenance = skore_cli_provenance()
    return {
        **manager,
        "recommended": _recommended(root, evidence, provenance["manager"]),
        "provenance": provenance,
        "managed": load_policy(root).get("env", {}).get("managed"),
    }


def forbidden_reason(package: str) -> str | None:
    """Return a refusal message if ``package`` is a known substitute."""
    policy = load_stack_policy()
    substitutes = policy.get("forbidden_substitutes") or {}
    key = package.strip().lower().split("[", 1)[0]
    message = substitutes.get(key)
    if isinstance(message, str):
        return message
    return None


def _package_key(package: str) -> str:
    return package.strip().lower().split("[", 1)[0]


def expand_display_packages(manager: str, packages: list[str]) -> list[str]:
    """Append pydot (and conda Graphviz) when ``skrub`` is among ``packages``."""
    if "skrub" not in {_package_key(name) for name in packages}:
        return packages
    extras = ["pydot"]
    if manager in CONDA_GRAPHVIZ_MANAGERS:
        extras.append("graphviz")
    seen = {_package_key(name) for name in packages}
    expanded = list(packages)
    for extra in extras:
        if extra not in seen:
            expanded.append(extra)
            seen.add(extra)
    return expanded


def _unmanaged(root: Path) -> bool:
    return load_policy(root).get("env", {}).get("managed") is False


def _ready_manager(root: Path) -> tuple[str | None, str | None]:
    """Return ``(manager, error)``. Error is set when add/sync/verify must stop."""
    if _unmanaged(root):
        return None, UNMANAGED
    payload = detect(root)
    if payload["ambiguous"]:
        return None, AMBIGUOUS
    manager = payload["env_manager"]
    if manager in {None, "none"}:
        return None, NO_MANAGER
    return str(manager), None


def _yaml_name(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("name:"):
            return stripped.split(":", 1)[1].strip().strip("\"'")
    return None


def conda_env_name(root: Path, *, feature: str | None = None) -> str | None:
    """Return the conda env name from YAML, or None if no yaml is present."""
    default_path = root / "environment.yml"
    agent_path = root / "environment-agent.yml"
    dev_path = root / "environment-dev.yml"
    if (
        not default_path.is_file()
        and not agent_path.is_file()
        and not dev_path.is_file()
    ):
        return None
    if feature == "dev":
        return _yaml_name(dev_path) or "workspace-dev"
    if feature:
        return _yaml_name(agent_path) or "workspace-agent"
    return _yaml_name(default_path) or "workspace"


def _venv_bin(name: str) -> str:
    if os.name == "nt":
        exe = name if name.endswith(".exe") else f"{name}.exe"
        return str(Path(".venv") / "Scripts" / exe)
    return str(Path(".venv") / "bin" / name)


def _render_argvs(argvs: list[list[str]]) -> str:
    return " && ".join(" ".join(argv) for argv in argvs)


def _run_argvs(argvs: list[list[str]], *, cwd: Path) -> int:
    code = 0
    for argv in argvs:
        completed = subprocess.run(argv, check=False, cwd=cwd)
        code = completed.returncode
        if code:
            return code
    return code


def sync_argv(manager: str) -> list[list[str]]:
    """Return the bootstrap install/sync command(s) for ``manager``."""
    commands: dict[str, list[list[str]]] = {
        "pixi": [["pixi", "install", "-e", "dev"]],
        "uv": [["uv", "sync", "--group", "agent"]],
        "poetry": [["poetry", "install", "--with", "agent"]],
        "hatch": [["hatch", "env", "create", "dev"]],
        "conda": [
            ["conda", "env", "create", "-f", "environment.yml"],
            ["conda", "env", "create", "-f", "environment-agent.yml"],
            ["conda", "env", "create", "-f", "environment-dev.yml"],
        ],
        "pip-venv": [
            ["python", "-m", "venv", ".venv"],
            [_venv_bin("pip"), "install", "-r", "requirements.txt"],
        ],
    }
    if manager not in commands:
        raise ValueError(f"unknown manager {manager!r}")
    return commands[manager]


def install_argv(
    manager: str,
    packages: list[str],
    *,
    feature: str | None = None,
    root: Path | None = None,
) -> list[str] | None:
    """Return the manager-specific add command, or None when hatch writes TOML."""
    extra: list[str] = []
    if feature:
        if manager == "pixi":
            extra = ["--feature", feature]
        elif manager in {"uv", "poetry"}:
            extra = ["--group", feature]
    conda: list[str] = ["conda", "install"]
    if root is not None:
        env_name = conda_env_name(root, feature=feature)
        if env_name is not None:
            conda.extend(["-n", env_name])
    conda.extend(["-c", "conda-forge", *packages])
    commands: dict[str, list[str]] = {
        "pixi": ["pixi", "add", *extra, *packages],
        "uv": ["uv", "add", *extra, *packages],
        "poetry": ["poetry", "add", *extra, *packages],
        "conda": conda,
        "pip-venv": ["pip", "install", *packages],
    }
    if manager == "hatch":
        return None
    if manager not in commands:
        raise ValueError(f"unknown manager {manager!r}")
    return commands[manager]


def skore_requirements(manager: str, mode: str) -> list[str]:
    """Return manager-aware requirements for a Skore project mode."""
    if manager not in MANAGER_ORDER:
        raise ValueError(f"unknown manager {manager!r}")
    if mode not in {"local", "hub", "mlflow"}:
        raise ValueError(f"unknown skore mode {mode!r}")
    if manager in {"pixi", "conda"}:
        packages = ["skore"]
    else:
        packages = {
            "local": ["skore"],
            "hub": ["skore[hub]"],
            "mlflow": ["skore[mlflow]"],
        }[mode]
    if mode == "mlflow":
        packages.append("mlflow>=3")
    return packages


def editable_argv(manager: str, package: str, *, root: Path) -> list[str] | None:
    """Return the editable-install argv, or None if unsupported."""
    pixi_spec = f"{package} @ {root.resolve().as_uri()}"
    commands: dict[str, list[str]] = {
        "pixi": [
            "pixi",
            "add",
            "--pypi",
            "--editable",
            pixi_spec,
        ],
        "uv": ["uv", "add", "--editable", "."],
        "poetry": ["poetry", "add", "--editable", "."],
        "pip-venv": ["pip", "install", "-e", "."],
    }
    return commands.get(manager)


def _import_name(package: str) -> str:
    key = _package_key(package)
    return _IMPORT_NAMES.get(key, key.replace("-", "_"))


def dev_run_argv(manager: str, *, root: Path) -> list[str]:
    """Return argv that runs python in the composed env (default + agent)."""
    if manager == "pixi":
        return ["pixi", "run", "-e", "dev", "python"]
    if manager == "uv":
        return ["uv", "run", "--group", "agent", "python"]
    if manager == "poetry":
        return ["poetry", "run", "python"]
    if manager == "hatch":
        return ["hatch", "run", "dev:python"]
    if manager == "conda":
        env_name = conda_env_name(root, feature="dev") or "workspace-dev"
        return ["conda", "run", "-n", env_name, "python"]
    if manager == "pip-venv":
        return [_venv_bin("python")]
    raise ValueError(f"unknown manager {manager!r}")


VERIFY_MARKER = "SKORE_SKILLS_VERIFY"
VERIFY_DID_NOT_RUN = "composed environment did not run the check"


def verify_argv(manager: str, packages: Sequence[str], *, root: Path) -> list[str]:
    """Return the composed-dev check for ``packages``.

    Python packages are imported. ``ruff`` is the executable beside that
    environment's interpreter, not ``import ruff``.
    """
    checks = [
        {
            "package": name,
            "module": None if _package_key(name) == "ruff" else _import_name(name),
        }
        for name in packages
    ]
    snippet = (
        "import importlib, json, sys\n"
        "from pathlib import Path\n"
        f"checks = json.loads({json.dumps(json.dumps(checks))})\n"
        "missing = []\n"
        "for item in checks:\n"
        "    module = item['module']\n"
        "    package = item['package']\n"
        "    if module is None:\n"
        "        executable = Path(sys.executable)\n"
        "        names = ('ruff.exe', 'ruff') if sys.platform == 'win32' else "
        "('ruff',)\n"
        "        candidates = [executable.with_name(name) for name in names]\n"
        "        if sys.platform == 'win32':\n"
        "            candidates.append(executable.parent / 'Scripts' / 'ruff.exe')\n"
        "        if not any(path.is_file() for path in candidates):\n"
        "            missing.append(package)\n"
        "        continue\n"
        "    try:\n"
        "        importlib.import_module(module)\n"
        "    except Exception:\n"
        "        missing.append(package)\n"
        f"print({VERIFY_MARKER!r} + ' ' + json.dumps(missing))\n"
        "raise SystemExit(1 if missing else 0)\n"
    )
    return [*dev_run_argv(manager, root=root), "-c", snippet]


def _parse_verify_report(stdout: str) -> list[str] | None:
    """Return missing package names, or None if the check did not run."""
    prefix = VERIFY_MARKER + " "
    for line in reversed(stdout.splitlines()):
        if not line.startswith(prefix):
            continue
        try:
            data = json.loads(line[len(prefix) :])
        except json.JSONDecodeError:
            return None
        if isinstance(data, list) and all(isinstance(item, str) for item in data):
            return data
        return None
    return None


def reexec_in_dev(root: Path, argv: Sequence[str] | None = None) -> int | None:
    """Re-run this CLI in the composed dev env.

    Returns the child exit code when a managed manager is present and
    this process is not already inside that env. Returns ``None`` to
    keep running in-process.
    """
    if os.environ.get(IN_DEV_ENV):
        return None
    if _unmanaged(root):
        return None
    payload = detect(root)
    if payload["ambiguous"]:
        sys.stderr.write(AMBIGUOUS + "\n")
        return 1
    manager = payload["env_manager"]
    if manager in {None, "none"}:
        return None
    rest = list(argv) if argv is not None else sys.argv[1:]
    child = [
        *dev_run_argv(str(manager), root=root),
        "-m",
        "skore_skills",
        *rest,
    ]
    env = os.environ.copy()
    env[IN_DEV_ENV] = "1"
    completed = subprocess.run(
        child,
        check=False,
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(completed.stdout)
    sys.stderr.write(completed.stderr)
    if completed.returncode and MISSING_SKORE_SKILLS in (completed.stderr or ""):
        sys.stderr.write(MISSING_SKORE_SKILLS_HINT)
    return completed.returncode


def route_package(package: str) -> dict[str, Any]:
    """Return default/agent/ask/refuse routing for ``package``."""
    key = _package_key(package)
    reason = forbidden_reason(key)
    if reason is not None:
        return {"scope": "refuse", "feature": None, "message": reason}
    policy = load_stack_policy()
    mandatory = {_package_key(name) for name in policy["mandatory"]}
    if key in mandatory:
        return {"scope": "agent", "feature": "agent", "message": None}
    export = {_package_key(name) for name in policy.get("export") or []}
    if key in export:
        return {"scope": "agent", "feature": "agent", "message": None}
    optional = {_package_key(name) for name in policy["optional"]}
    if key in optional - mandatory:
        return {"scope": "ask", "feature": None, "message": None}
    return {"scope": "default", "feature": None, "message": None}


def _toml_list_close(text: str, start: int) -> int:
    """Return the closing bracket, ignoring brackets inside strings."""
    quote: str | None = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if escaped:
            escaped = False
        elif char == "\\" and quote == '"':
            escaped = True
        elif char in {'"', "'"}:
            quote = None if quote == char else char if quote is None else quote
        elif char == "]" and quote is None:
            return index
    return -1


def _insert_into_deps_list(
    text: str, pkg: str, *, header: str, key: str = "dependencies"
) -> tuple[str, bool]:
    """Insert ``pkg`` into ``key = [...]`` after ``header``."""
    start = text.find(header)
    if start < 0:
        return text, False
    search = text[start:]
    match = re.search(rf"{re.escape(key)}\s*=\s*\[", search)
    if match is None:
        newline = text.find("\n", start)
        if newline < 0:
            newline = len(text)
        insert = f'\n{key} = ["{pkg}"]'
        return text[:newline] + insert + text[newline:], True
    list_open = start + match.end()
    list_close = _toml_list_close(text, list_open)
    if list_close < 0:
        return text, False
    body = text[list_open:list_close]
    if re.search(rf'["\']{re.escape(pkg)}["\']', body):
        return text, False
    stripped = body.strip()
    addition = f'"{pkg}"'
    if not stripped:
        new_body = addition
    elif stripped.endswith(","):
        new_body = f"{stripped} {addition}"
    else:
        new_body = f"{stripped}, {addition}"
    return text[:list_open] + new_body + text[list_close:], True


def _replace_hatch_skore_requirement(text: str, requirement: str) -> tuple[str, bool]:
    """Replace an existing Skore requirement in ``[project]``."""
    start = text.find("[project]")
    if start < 0:
        return text, False
    match = re.search(r"dependencies\s*=\s*\[", text[start:])
    if match is None:
        return text, False
    list_open = start + match.end()
    list_close = _toml_list_close(text, list_open)
    if list_close < 0:
        return text, False
    body = text[list_open:list_close]
    pattern = r'(["\'])skore(?:\[[^"\']+\])?\1'
    current = re.search(pattern, body)
    if current is None:
        return text, False
    quoted = f'"{requirement}"'
    if current.group(0) == quoted:
        return text, False
    body = re.sub(pattern, quoted, body, count=1)
    return text[:list_open] + body + text[list_close:], True


def _hatch_add(root: Path, packages: list[str], *, feature: str | None) -> str:
    path = _ensure_pyproject(root)
    text = path.read_text(encoding="utf-8")
    if feature:
        if "[tool.hatch.envs.agent]" not in text:
            text = text.rstrip() + "\n" + _HATCH_ENV.strip() + "\n"
        elif "[tool.hatch.envs.dev]" not in text:
            text = text.rstrip() + "\n[tool.hatch.envs.dev]\n"
        changed = False
        for pkg in packages:
            text, inserted_agent = _insert_into_deps_list(
                text, pkg, header="[tool.hatch.envs.agent]"
            )
            text, inserted_dev = _insert_into_deps_list(
                text,
                pkg,
                header="[tool.hatch.envs.dev]",
                key="extra-dependencies",
            )
            changed = changed or inserted_agent or inserted_dev
        path.write_text(text, encoding="utf-8")
        if changed:
            return f"updated {path.name}\n"
        return f"{path.name} already lists {', '.join(packages)}\n"
    header = "[project]"
    changed = False
    for pkg in packages:
        if _package_key(pkg) == "skore":
            text, replaced = _replace_hatch_skore_requirement(text, pkg)
            if replaced:
                changed = True
                continue
        text, inserted = _insert_into_deps_list(text, pkg, header=header)
        changed = changed or inserted
    path.write_text(text, encoding="utf-8")
    if changed:
        return f"updated {path.name}\n"
    return f"{path.name} already lists {', '.join(packages)}\n"


def add_packages(
    root: Path,
    packages: list[str],
    *,
    execute: bool = False,
    feature: str | None = None,
    editable: bool = False,
) -> tuple[str, int]:
    """Build (or run) install commands for ``packages``.

    Default is print-only. Never emits ``pip install`` for pixi.
    """
    if editable:
        return add_editable(root, execute=execute)
    if not packages:
        return "need at least one package\n", 2
    manager, error = _ready_manager(root)
    if error is not None:
        return error + "\n", 1
    assert manager is not None
    packages = expand_display_packages(manager, packages)
    for name in packages:
        reason = forbidden_reason(name)
        if reason is not None:
            return reason + "\n", 1
    if manager == "hatch":
        text = _hatch_add(root, packages, feature=feature)
        if not execute:
            return text, 0
        argvs = sync_argv("hatch")
        rendered = text + _render_argvs(argvs) + "\n"
        return rendered, _run_argvs(argvs, cwd=root)
    argv = install_argv(manager, packages, feature=feature, root=root)
    if argv is None:
        return "need at least one package\n", 2
    argvs = [argv]
    if manager == "conda":
        dev_argv = install_argv("conda", packages, feature="dev", root=root)
        assert dev_argv is not None
        if dev_argv != argv:
            argvs.append(dev_argv)
    rendered = _render_argvs(argvs) + "\n"
    if not execute:
        return rendered, 0
    return rendered, _run_argvs(argvs, cwd=root)


def system_graphviz_instructions() -> str:
    """Return OS-specific Graphviz install lines. Never a pip command."""
    if sys.platform == "darwin":
        install = "brew install graphviz"
    elif sys.platform.startswith("linux"):
        try:
            release = platform.freedesktop_os_release()
        except OSError:
            release = {}
        distro = " ".join((release.get("ID", ""), release.get("ID_LIKE", ""))).lower()
        if any(name in distro for name in ("debian", "ubuntu")):
            install = "sudo apt-get install graphviz"
        elif any(name in distro for name in ("fedora", "rhel", "centos")):
            install = "sudo dnf install graphviz"
        elif "arch" in distro:
            install = "sudo pacman -S graphviz"
        elif any(name in distro for name in ("suse", "opensuse")):
            install = "sudo zypper install graphviz"
        else:
            install = "install Graphviz with your system package manager"
    elif sys.platform == "win32":
        install = "winget install Graphviz.Graphviz"
    else:
        install = "install Graphviz with your system package manager"
    return (
        f"{install}\n"
        "Restart the terminal or IDE after installation if `dot` is not on PATH.\n"
        f"Graphviz installation instructions -> {GRAPHVIZ_DOCS}"
    )


def _which_dot(manager: str, root: Path) -> str | None:
    """Return ``dot`` as seen inside the composed env, not the outer PATH."""
    argv = [*dev_run_argv(manager, root=root), "-c", WHICH_DOT_SNIPPET]
    completed = subprocess.run(
        argv,
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        return None
    lines = (completed.stdout or "").strip().splitlines()
    if not lines:
        return None
    path = lines[-1].strip()
    return path or None


def _graphviz_probe_argv(manager: str, root: Path) -> list[str]:
    return [*dev_run_argv(manager, root=root), "-c", GRAPHVIZ_PROBE_SNIPPET]


def _conda_graphviz_argvs(manager: str, root: Path) -> list[list[str]]:
    argv = install_argv(manager, ["graphviz"], root=root)
    assert argv is not None
    argvs = [argv]
    if manager == "conda":
        dev_argv = install_argv("conda", ["graphviz"], feature="dev", root=root)
        assert dev_argv is not None
        if dev_argv != argv:
            argvs.append(dev_argv)
    return argvs


def graphviz_status(root: Path) -> tuple[dict[str, Any], int]:
    """Return how to get ``dot`` on the composed-env PATH.

    Print-only even when ``env.managed`` is false so the skill can
    show the manager or OS line. ``ensure_graphviz(..., execute=True)``
    still refuses to install or run the SVG probe while unmanaged.
    """
    detected = detect(root)
    manager = detected["env_manager"]
    payload: dict[str, Any] = {
        "ok": None,
        "dot": None,
        "manager": manager,
        "action": None,
        "command": None,
        "instructions": None,
        "managed": detected.get("managed"),
    }
    if detected["ambiguous"]:
        payload["error"] = AMBIGUOUS
        return payload, 1
    if manager in {None, "none"}:
        payload["error"] = NO_MANAGER
        return payload, 1
    payload["dot"] = _which_dot(str(manager), root)
    if manager in CONDA_GRAPHVIZ_MANAGERS:
        payload["action"] = "conda"
        if payload["dot"] is None:
            payload["command"] = _conda_graphviz_argvs(str(manager), root)[0]
        else:
            payload["command"] = None
    else:
        payload["action"] = "system"
        payload["command"] = None
        if payload["dot"] is None:
            payload["instructions"] = system_graphviz_instructions()
    return payload, 0


def _plugins_unregistered(stderr: str) -> bool:
    """Return True when ``dot`` asked for ``dot -c`` to register plugins."""
    lowered = stderr.lower()
    return "not recognized" in lowered and "dot -c" in lowered


def _dev_command_argv(manager: str, root: Path, command: list[str]) -> list[str]:
    """Return argv that runs ``command`` inside the composed env."""
    argv = dev_run_argv(manager, root=root)
    if manager == "pip-venv":
        python = Path(argv[-1])
        tool = command[0]
        if os.name == "nt" and not tool.endswith(".exe"):
            tool = f"{tool}.exe"
        return [str(python.with_name(tool)), *command[1:]]
    return [*argv[:-1], *command]


def _probe_graphviz(manager: str, root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        _graphviz_probe_argv(manager, root),
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )


def _graphviz_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2) + "\n"


def ensure_graphviz(root: Path, *, execute: bool = False) -> tuple[str, int]:
    """Print JSON; optionally install conda Graphviz and verify SVG rendering."""
    payload, code = graphviz_status(root)
    if code or not execute:
        return _graphviz_json(payload), code
    if _unmanaged(root):
        return _graphviz_json(payload) + UNMANAGED + "\n", 1
    manager = payload["manager"]
    assert manager is not None
    if payload["action"] == "conda" and payload["command"] is not None:
        run_code = _run_argvs(_conda_graphviz_argvs(manager, root), cwd=root)
        if run_code:
            payload["ok"] = False
            return _graphviz_json(payload), run_code
        payload["dot"] = _which_dot(manager, root)
        payload["command"] = None
    if not payload["dot"]:
        payload["ok"] = False
        return _graphviz_json(payload), 1
    completed = _probe_graphviz(manager, root)
    if completed.returncode and _plugins_unregistered(completed.stderr or ""):
        registered = subprocess.run(
            _dev_command_argv(manager, root, ["dot", "-c"]),
            check=False,
            cwd=root,
            capture_output=True,
            text=True,
        )
        if registered.returncode == 0:
            completed = _probe_graphviz(manager, root)
    if completed.returncode:
        sys.stderr.write(completed.stderr or "")
        payload["ok"] = False
        return _graphviz_json(payload) + GRAPHVIZ_REPAIR + "\n", completed.returncode
    payload["ok"] = True
    return _graphviz_json(payload), 0


def resolve_add_skore_mode(root: Path, mode: str | None) -> str:
    """Return the Skore install mode for ``root``.

    An omitted ``mode`` uses a recorded ``hub`` or ``mlflow``
    destination and otherwise ``local``. An explicit mode is an
    override, except ``local`` while ``hub`` or ``mlflow`` is recorded.

    Raises
    ------
    ValueError
        When ``--mode local`` would replace a recorded hub or MLflow
        destination.
    """
    recorded = load_policy(root).get("skore_mode")
    if mode == "local" and recorded in {"hub", "mlflow"}:
        raise ValueError(f"recorded destination is {recorded}; refusing --mode local")
    if mode is None:
        if recorded in {"hub", "mlflow"}:
            return recorded
        return "local"
    return mode


def add_skore(
    root: Path,
    mode: str,
    *,
    execute: bool = False,
) -> tuple[str, int]:
    """Print or run the manager-aware Skore install command."""
    manager, error = _ready_manager(root)
    if error is not None:
        return error + "\n", 1
    assert manager is not None
    try:
        packages = skore_requirements(manager, mode)
    except ValueError as exc:
        return str(exc) + "\n", 2
    return add_packages(root, packages, execute=execute)


def add_editable(root: Path, *, execute: bool = False) -> tuple[str, int]:
    """Print or run the editable install for ``src/<pkg>/``."""
    manager, error = _ready_manager(root)
    if error is not None:
        return error + "\n", 1
    if not (root / "src").is_dir():
        return NO_SRC + "\n", 1
    name = package_name(root)
    if not name:
        return NO_PACKAGE + "\n", 1
    assert manager is not None
    argv = editable_argv(manager, name, root=root)
    if argv is None:
        return EDITABLE_UNSUPPORTED.format(manager=manager) + "\n", 1
    rendered = " ".join(argv) + "\n"
    if not execute:
        return rendered, 0
    code = _run_argvs([argv], cwd=root)
    if code:
        return rendered, code
    module = _import_name(name)
    snippet = (
        "import importlib, sys\n"
        "try:\n"
        f"    importlib.import_module({module!r})\n"
        "except Exception as exc:\n"
        "    print(f'{type(exc).__name__}: {exc}', file=sys.stderr)\n"
        "    sys.exit(1)\n"
    )
    completed = subprocess.run(
        [*dev_run_argv(manager, root=root), "-c", snippet],
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if completed.returncode:
        sys.stderr.write(completed.stderr or completed.stdout or "")
        return rendered, completed.returncode
    return rendered, 0


def sync_environment(root: Path, *, execute: bool = False) -> tuple[str, int]:
    """Print or run the post-init install/sync command."""
    manager, error = _ready_manager(root)
    if error is not None:
        return error + "\n", 1
    assert manager is not None
    argvs = sync_argv(manager)
    rendered = _render_argvs(argvs) + "\n"
    if not execute:
        return rendered, 0
    return rendered, _run_argvs(argvs, cwd=root)


def verify_environment(
    root: Path,
    packages: list[str] | None = None,
    *,
    execute: bool = False,
) -> tuple[dict[str, Any], int]:
    """Print a composed-dev import check. ``--execute`` runs it.

    ``missing`` lists only probes that failed. A composed env that never
    starts leaves ``missing`` empty and sets ``error``.
    """
    names = list(packages) if packages else list(BOOTSTRAP_PACKAGES)
    manager, error = _ready_manager(root)
    payload: dict[str, Any] = {
        "ok": False,
        "missing": [],
        "argv": [],
    }
    if error is not None:
        payload["error"] = error
        return payload, 1
    assert manager is not None
    argv = verify_argv(manager, names, root=root)
    payload["argv"] = argv
    payload["ok"] = None
    if not execute:
        return payload, 0
    completed = subprocess.run(
        argv,
        check=False,
        cwd=root,
        capture_output=True,
        text=True,
    )
    if completed.stderr:
        sys.stderr.write(completed.stderr)
    missing = _parse_verify_report(completed.stdout or "")
    if missing is None:
        payload["ok"] = False
        payload["error"] = VERIFY_DID_NOT_RUN
        return payload, 1
    payload["missing"] = missing
    payload["ok"] = not missing
    return payload, 0 if not missing else 1


def _followup(follow: str) -> str:
    return f"next: {follow}\nrun: {SYNC_HINT}\n"


def _ensure_pyproject(root: Path) -> Path:
    path = root / "pyproject.toml"
    if not path.is_file():
        path.write_text(_SKELETON + "\n" + RUFF_PYPROJECT_TABLE, encoding="utf-8")
    else:
        ensure_ruff_in_pyproject(path)
    return path


def _append_if_missing(path: Path, marker: str, block: str, *, force: bool) -> bool:
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if marker in text and not force:
        return False
    if marker in text and force:
        # Keep existing file; caller treats False as already-present.
        return False
    path.write_text(text.rstrip() + "\n" + block.strip() + "\n", encoding="utf-8")
    return True


def init_environment(
    root: Path,
    manager: str,
    *,
    force: bool = False,
) -> tuple[str, int]:
    """Write manager + agent tables. Does not create ``src/`` or install."""
    if manager not in MANAGER_ORDER:
        return f"unknown manager {manager!r}\n", 2
    if _unmanaged(root):
        return UNMANAGED + "\n", 1
    payload = detect(root)
    if payload["ambiguous"]:
        return AMBIGUOUS + "\n", 1
    detected = payload["env_manager"]
    if detected not in {None, "none", manager}:
        return INIT_MISMATCH.format(detected=detected, wanted=manager) + "\n", 1
    if manager == "pixi" and (root / "pixi.toml").is_file():
        return PIXI_TOML_PRESENT + "\n", 1

    written: list[str] = []
    if manager == "conda":
        default = root / "environment.yml"
        agent = root / "environment-agent.yml"
        dev = root / "environment-dev.yml"
        if default.is_file() and not force:
            return INIT_EXISTS + "\n", 1
        default.write_text(_CONDA_DEFAULT, encoding="utf-8")
        agent.write_text(_CONDA_AGENT, encoding="utf-8")
        dev.write_text(_CONDA_DEV, encoding="utf-8")
        written.extend(
            ["environment.yml", "environment-agent.yml", "environment-dev.yml"]
        )
        follow = _render_argvs(sync_argv("conda"))
        return "wrote " + ", ".join(written) + "\n" + _followup(follow), 0

    path = _ensure_pyproject(root)
    if manager == "pixi":
        added = _append_if_missing(path, "[tool.pixi", _PIXI_TABLE, force=force)
        follow = _render_argvs(sync_argv("pixi"))
    elif manager == "uv":
        added = _append_if_missing(path, "[tool.uv]", _UV_GROUPS, force=force)
        follow = _render_argvs(sync_argv("uv"))
    elif manager == "poetry":
        added = _append_if_missing(path, "[tool.poetry]", _POETRY_GROUPS, force=force)
        follow = _render_argvs(sync_argv("poetry"))
    elif manager == "hatch":
        added = _append_if_missing(
            path, "[tool.hatch.envs.agent]", _HATCH_ENV, force=force
        )
        follow = _render_argvs(sync_argv("hatch"))
    else:
        added = _append_if_missing(
            path, "[dependency-groups]", _PIP_GROUPS, force=force
        )
        req = root / "requirements.txt"
        if not req.is_file() or force:
            req.write_text("ruff\nipython\nipykernel\n", encoding="utf-8")
            added = True
        follow = _render_argvs(sync_argv("pip-venv"))
    if not added:
        return INIT_EXISTS + "\n", 1
    return f"updated {path.name}\n" + _followup(follow), 0
