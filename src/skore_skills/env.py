"""Detect the project env manager and emit install commands."""

from __future__ import annotations

import json
import shlex
import subprocess
import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

from skore_skills.workspace import MANAGER_ORDER, manager_evidence, package_name

HATCH_ADD_HINT = (
    "hatch has no universal add command; edit pyproject.toml "
    "[project] dependencies or [tool.hatch.envs.<env>.dependencies], "
    "then `hatch run`"
)
NO_MANAGER = "no env manager detected; record one before installing packages"
AMBIGUOUS = "multiple env managers are visible; do not pick automatically"
UNSUPPORTED_CHECK = (
    "{manager} agent layout check is not supported; "
    "see setup-python-env/references/per_manager_footguns.md"
)
AGENT_PACKAGES = ("ipython", "pyright")


@dataclass(frozen=True)
class AgentPlan:
    """Commands and interpreter path for an agent-feature install."""

    manager: str
    install: tuple[tuple[str, ...], ...]
    verify: tuple[tuple[str, ...], ...]
    python_path: str


def load_stack_policy() -> dict[str, Any]:
    """Load packaged ``python-stack.json`` policy."""
    path = files("skore_skills").joinpath("data/python-stack.json")
    return json.loads(path.read_text(encoding="utf-8"))


def detect(root: Path) -> dict[str, Any]:
    """Return detection JSON for ``root``.

    When two or more managers are visible, ``ambiguous`` is true and
    ``env_manager`` is null — the CLI must not pick a winner.
    """
    evidence = manager_evidence(root)
    managers = [name for name in MANAGER_ORDER if name in evidence]
    ambiguous = len(managers) > 1
    if not managers:
        env_manager: str | None = "none"
    elif ambiguous:
        env_manager = None
    else:
        env_manager = managers[0]
    return {
        "env_manager": env_manager,
        "managers": managers,
        "evidence": evidence,
        "ambiguous": ambiguous,
    }


def forbidden_reason(package: str) -> str | None:
    """Return a refusal message if ``package`` is a known substitute."""
    policy = load_stack_policy()
    substitutes = policy["forbidden_substitutes"]
    key = package.strip().lower().split("[", 1)[0]
    message = substitutes.get(key)
    if isinstance(message, str):
        return message
    return None


def install_argv(manager: str, packages: list[str]) -> list[str] | None:
    """Return the manager-specific add command, or None for hatch."""
    commands: dict[str, list[str]] = {
        "pixi": ["pixi", "add", *packages],
        "uv": ["uv", "add", *packages],
        "poetry": ["poetry", "add", *packages],
        "conda": ["conda", "install", "-c", "conda-forge", *packages],
        "pip-venv": ["pip", "install", *packages],
    }
    if manager == "hatch":
        return None
    if manager not in commands:
        raise ValueError(f"unknown manager {manager!r}")
    return commands[manager]


def add_packages(
    root: Path,
    packages: list[str],
    *,
    execute: bool = False,
) -> tuple[str, int]:
    """Build (or run) install commands for ``packages``.

    Default is print-only. Never emits ``pip install`` for pixi.
    """
    if not packages:
        return "need at least one package\n", 2
    for name in packages:
        reason = forbidden_reason(name)
        if reason is not None:
            return reason + "\n", 1
    payload = detect(root)
    if payload["ambiguous"]:
        return AMBIGUOUS + "\n", 1
    manager = payload["env_manager"]
    if manager in {None, "none"}:
        return NO_MANAGER + "\n", 1
    argv = install_argv(str(manager), packages)
    if argv is None:
        text = HATCH_ADD_HINT + "\n"
        if execute:
            return text + "refusing --execute for hatch (no add command)\n", 1
        return text, 0
    rendered = " ".join(argv) + "\n"
    if not execute:
        return rendered, 0
    completed = subprocess.run(argv, check=False)
    return rendered, completed.returncode


def _poetry_groups(root: Path) -> list[str]:
    """Return Poetry dependency groups declared in either supported format."""
    data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    groups = set(data.get("dependency-groups", {}))
    poetry = data.get("tool", {}).get("poetry", {})
    if isinstance(poetry, dict):
        legacy = poetry.get("group", {})
        if isinstance(legacy, dict):
            groups.update(legacy)
    groups.add("agent")
    return sorted(str(group) for group in groups)


def agent_plan(
    root: Path,
    manager: str,
    *,
    project: str | None = None,
    requirements: Path | None = None,
) -> AgentPlan:
    """Build the manager-specific agent feature command plan."""
    if manager == "pixi":
        manifest = root / "pixi.toml"
        if not manifest.is_file():
            raise ValueError("pixi.toml not found at project root")
        text = manifest.read_text(encoding="utf-8")
        commands: list[tuple[str, ...]] = [
            ("pixi", "add", "--feature", "agent", *AGENT_PACKAGES)
        ]
        if not any(line.strip().startswith("lsp") for line in text.splitlines()):
            commands.append(
                (
                    "pixi",
                    "project",
                    "environment",
                    "add",
                    "lsp",
                    "--feature",
                    "default",
                    "--feature",
                    "dev",
                    "--feature",
                    "agent",
                )
            )
        commands.append(("pixi", "install", "-e", "lsp"))
        return AgentPlan(
            manager,
            tuple(commands),
            (
                ("pixi", "run", "-e", "agent", "ipython", "-c", "print('ok')"),
                ("pixi", "run", "-e", "agent", "pyright", "--version"),
            ),
            ".pixi/envs/lsp/bin/python",
        )
    if manager == "uv":
        if not (root / "pyproject.toml").is_file():
            raise ValueError("pyproject.toml not found at project root")
        return AgentPlan(
            manager,
            (
                ("uv", "add", "--group", "agent", *AGENT_PACKAGES),
                ("uv", "sync", "--all-groups"),
            ),
            (
                ("uv", "run", "--group", "agent", "python", "-c", "import IPython"),
                ("uv", "run", "--group", "agent", "pyright", "--version"),
            ),
            ".venv/bin/python",
        )
    if manager == "poetry":
        if not (root / "pyproject.toml").is_file():
            raise ValueError("pyproject.toml not found at project root")
        groups = ",".join(_poetry_groups(root))
        return AgentPlan(
            manager,
            (
                ("poetry", "config", "virtualenvs.in-project", "true"),
                ("poetry", "add", "--group", "agent", *AGENT_PACKAGES),
                ("poetry", "install", "--with", groups),
            ),
            (
                ("poetry", "run", "python", "-c", "import IPython"),
                ("poetry", "run", "pyright", "--version"),
            ),
            ".venv/bin/python",
        )
    if manager == "hatch":
        data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
        envs = data.get("tool", {}).get("hatch", {}).get("envs", {})
        if not isinstance(envs, dict) or not {"agent", "lsp"} <= set(envs):
            raise ValueError(
                "declare [tool.hatch.envs.agent] and [tool.hatch.envs.lsp] first"
            )
        return AgentPlan(
            manager,
            (("hatch", "env", "create", "agent"), ("hatch", "env", "create", "lsp")),
            (
                ("hatch", "run", "agent:python", "-c", "import IPython"),
                ("hatch", "run", "agent:pyright", "--version"),
            ),
            "<hatch-lsp>/bin/python",
        )
    if manager == "conda":
        project = project or package_name(root) or root.name
        for name in ("environment-agent.yml", "environment-lsp.yml"):
            if not (root / name).is_file():
                raise ValueError(f"{name} not found at project root")
        return AgentPlan(
            manager,
            (
                ("conda", "env", "create", "-f", "environment-agent.yml"),
                ("conda", "env", "create", "-f", "environment-lsp.yml"),
            ),
            (
                (
                    "conda",
                    "run",
                    "-n",
                    f"{project}-agent",
                    "python",
                    "-c",
                    "import IPython",
                ),
                ("conda", "run", "-n", f"{project}-agent", "pyright", "--version"),
            ),
            f"<conda-base>/envs/{project}-lsp/bin/python",
        )
    if manager == "pip-venv":
        requirements = requirements or Path("requirements.txt")
        req = root / requirements
        if not req.is_file():
            raise ValueError(f"requirements file not found: {requirements}")
        return AgentPlan(
            manager,
            (
                ("python3", "-m", "venv", ".venv-agent"),
                (".venv-agent/bin/python", "-m", "pip", "install", "--upgrade", "pip"),
                (
                    ".venv-agent/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(requirements),
                    *AGENT_PACKAGES,
                ),
                ("python3", "-m", "venv", ".venv-lsp"),
                (".venv-lsp/bin/python", "-m", "pip", "install", "--upgrade", "pip"),
                (
                    ".venv-lsp/bin/python",
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(requirements),
                    "ruff",
                    "pytest",
                    "jupyterlab",
                    "ipykernel",
                    *AGENT_PACKAGES,
                ),
            ),
            (
                (".venv-agent/bin/python", "-c", "import IPython"),
                (".venv-agent/bin/pyright", "--version"),
            ),
            ".venv-lsp/bin/python",
        )
    raise ValueError(f"unknown manager {manager!r}")


def _resolve_python_path(root: Path, plan: AgentPlan) -> str:
    """Resolve manager-specific absolute interpreter placeholders."""
    if plan.manager == "hatch":
        result = subprocess.run(
            ["hatch", "env", "find", "lsp"],
            check=False,
            capture_output=True,
            text=True,
            cwd=root,
        )
        if result.returncode:
            raise ValueError("hatch could not locate the lsp environment")
        # as_posix keeps JSON-safe separators; Path(str) on Windows would
        # otherwise turn "/tmp/..." into "\tmp\..." and break the config.
        return (Path(result.stdout.strip()) / "bin" / "python").as_posix()
    if plan.manager == "conda":
        result = subprocess.run(
            ["conda", "info", "--base"],
            check=False,
            capture_output=True,
            text=True,
            cwd=root,
        )
        if result.returncode:
            raise ValueError("conda could not report its base directory")
        return plan.python_path.replace("<conda-base>", result.stdout.strip())
    return plan.python_path


def _write_pyright_config(root: Path, python_path: str) -> None:
    """Write the packaged pyright configuration with its interpreter path."""
    template = files("skore_skills").joinpath("templates/pyrightconfig.json")
    payload = json.loads(template.read_text(encoding="utf-8"))
    payload["pythonPath"] = python_path
    (root / "pyrightconfig.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


def install_agent_feature(
    root: Path,
    *,
    execute: bool = False,
    project: str | None = None,
    requirements: Path | None = None,
) -> tuple[str, int]:
    """Print or execute the detected manager's agent-feature plan."""
    payload = detect(root)
    if payload["ambiguous"]:
        return AMBIGUOUS + "\n", 1
    manager = payload["env_manager"]
    if manager in {None, "none"}:
        return NO_MANAGER + "\n", 1
    try:
        plan = agent_plan(
            root,
            str(manager),
            project=project,
            requirements=requirements,
        )
    except (OSError, tomllib.TOMLDecodeError, ValueError) as exc:
        return f"{exc}\n", 1

    lines = [shlex.join(command) for command in plan.install]
    lines.append(f"write pyrightconfig.json (pythonPath={plan.python_path})")
    lines.extend(shlex.join(command) for command in plan.verify)
    rendered = "\n".join(lines) + "\n"
    if not execute:
        return rendered, 0

    try:
        for command in plan.install:
            result = subprocess.run(command, check=False, cwd=root)
            if result.returncode:
                return rendered, result.returncode
        python_path = _resolve_python_path(root, plan)
        _write_pyright_config(root, python_path)
        for command in plan.verify:
            result = subprocess.run(command, check=False, cwd=root)
            if result.returncode:
                return rendered, result.returncode
    except (FileNotFoundError, ValueError) as exc:
        return rendered + f"{exc}\n", 1
    return rendered, 0


def _pyright_check(root: Path, expected: str) -> tuple[bool, str]:
    """Check the project pyright config and expected interpreter."""
    path = root / "pyrightconfig.json"
    if not path.is_file():
        return False, "pyrightconfig.json missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False, "pyrightconfig.json is invalid JSON"
    actual = payload.get("pythonPath")
    if actual != expected:
        return False, f"pythonPath is {actual!r}; expected {expected!r}"
    return True, f"pythonPath = {expected}"


def check_agent_feature(root: Path) -> tuple[str, int]:
    """Check agent-feature composition for pixi, uv, or Poetry."""
    payload = detect(root)
    if payload["ambiguous"]:
        return AMBIGUOUS + "\n", 1
    manager = payload["env_manager"]
    if manager in {None, "none"}:
        return NO_MANAGER + "\n", 1
    if manager not in {"pixi", "uv", "poetry"}:
        return UNSUPPORTED_CHECK.format(manager=manager) + "\n", 2

    failures: list[str] = []
    notes: list[str] = []
    try:
        if manager == "pixi":
            text = (root / "pixi.toml").read_text(encoding="utf-8")
            failures.extend(
                f"feature {feature!r} is not declared"
                for feature in ("dev", "agent")
                if f"[feature.{feature}" not in text
            )
            lsp_lines = [
                line for line in text.splitlines() if line.strip().startswith("lsp")
            ]
            if not lsp_lines or not all(
                f'"{feature}"' in lsp_lines[0]
                for feature in ("default", "dev", "agent")
            ):
                failures.append("lsp must include default, dev, and agent")
            expected = ".pixi/envs/lsp/bin/python"
        else:
            data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
            groups = set(data.get("dependency-groups", {}))
            if manager == "poetry":
                poetry = data.get("tool", {}).get("poetry", {})
                legacy = poetry.get("group", {}) if isinstance(poetry, dict) else {}
                if isinstance(legacy, dict):
                    groups.update(legacy)
            failures.extend(
                f"group {group!r} is not declared"
                for group in ("dev", "agent")
                if group not in groups
            )
            expected = ".venv/bin/python"
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return f"{exc}\n", 1

    ok, note = _pyright_check(root, expected)
    (notes if ok else failures).append(note)
    lines = [f"env agent check: {manager}"]
    lines.extend(f"[ok] {note}" for note in notes)
    lines.extend(f"[FAIL] {failure}" for failure in failures)
    lines.append("agent layout OK" if not failures else "agent layout has drift")
    return "\n".join(lines) + "\n", int(bool(failures))
