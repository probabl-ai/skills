"""Tests for ``skore_skills env detect`` / ``env add``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.env import agent_plan, install_argv, load_stack_policy

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "envs"


@pytest.mark.parametrize(
    ("name", "manager"),
    [
        ("pixi", "pixi"),
        ("uv", "uv"),
        ("poetry", "poetry"),
        ("hatch", "hatch"),
        ("conda", "conda"),
        ("pip-venv", "pip-venv"),
        ("none", "none"),
    ],
)
def test_env_detect_each_manager(
    name: str, manager: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each fixture maps to the documented manager (or none)."""
    monkeypatch.chdir(FIXTURES / name)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == manager
    assert payload["ambiguous"] is False


def test_env_detect_ambiguous(monkeypatch: pytest.MonkeyPatch) -> None:
    """pixi.toml + conda env is ambiguous: JSON flag and non-zero exit."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ambiguous"] is True
    assert payload["env_manager"] is None
    assert payload["managers"] == ["pixi", "conda"]


def test_env_add_pixi_never_pip(monkeypatch: pytest.MonkeyPatch) -> None:
    """``env add`` on a pixi fixture prints ``pixi add``, never ``pip install``."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "pixi add skrub"
    assert "pip install" not in result.output


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("uv", "uv add pandas"),
        ("poetry", "poetry add pandas"),
        ("conda", "conda install -c conda-forge pandas"),
        ("pip-venv", "pip install pandas"),
    ],
)
def test_env_add_command_per_manager(
    fixture: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Print-only add matches the env-manager command table."""
    monkeypatch.chdir(FIXTURES / fixture)
    result = CliRunner().invoke(cli, ["env", "add", "pandas"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == expected


def test_env_add_hatch_prints_edit_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    """Hatch has no add command; print an edit hint and never pip."""
    monkeypatch.chdir(FIXTURES / "hatch")
    result = CliRunner().invoke(cli, ["env", "add", "pandas"])
    assert result.exit_code == 0, result.output
    assert "edit pyproject.toml" in result.output
    assert "pip install" not in result.output
    executed = CliRunner().invoke(cli, ["env", "add", "--execute", "pandas"])
    assert executed.exit_code != 0
    assert "pip install" not in executed.output


def test_env_add_forbidden_substitute(monkeypatch: pytest.MonkeyPatch) -> None:
    """Known substitutes are refused using python-stack.json."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "xgboost"])
    assert result.exit_code != 0
    assert "HistGradientBoosting" in result.output
    policy = load_stack_policy()
    assert "xgboost" in policy["forbidden_substitutes"]
    assert "scikit-learn" in policy["mandatory"]


def test_env_add_ambiguous_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not install into an ambiguous workspace."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "multiple env managers" in result.output


def test_env_add_none_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nothing detected: do not invent pip."""
    monkeypatch.chdir(FIXTURES / "none")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "no env manager" in result.output
    assert "pip install" not in result.output


def test_env_add_requires_package() -> None:
    """``env add`` without packages is usage error."""
    result = CliRunner().invoke(cli, ["env", "add"])
    assert result.exit_code != 0


def test_env_add_execute_runs_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``--execute`` runs the printed command."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "--execute", "skrub"])
    assert result.exit_code == 0, result.output
    assert seen == [["pixi", "add", "skrub"]]
    assert result.output.strip() == "pixi add skrub"


def test_install_argv_unknown_manager() -> None:
    """Unknown manager names are a programming error."""
    with pytest.raises(ValueError, match="unknown manager"):
        install_argv("pants", ["x"])


def test_add_packages_empty_list(tmp_path: Path) -> None:
    """Library callers still get a usage error for an empty package list."""
    from skore_skills.env import add_packages

    text, code = add_packages(tmp_path, [])
    assert code == 2
    assert "at least one package" in text


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("pixi", "pixi add --feature agent ipython pyright"),
        ("uv", "uv add --group agent ipython pyright"),
        ("poetry", "poetry add --group agent ipython pyright"),
    ],
)
def test_env_agent_prints_plan(
    fixture: str,
    expected: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Supported managers get deterministic agent-feature plans."""
    _write_agent_workspace(tmp_path, fixture)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "agent"])
    assert result.exit_code == 0, result.output
    assert expected in result.output
    assert "write pyrightconfig.json" in result.output
    assert "pyright --version" in result.output


def test_env_agent_refuses_without_manager(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Agent install never invents a manager for an empty project."""
    monkeypatch.chdir(FIXTURES / "none")
    result = CliRunner().invoke(cli, ["env", "agent", "--execute"])
    assert result.exit_code != 0
    assert "no env manager" in result.output


def test_env_agent_execute_writes_pyright_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Execution runs the plan and renders the packaged config."""
    (tmp_path / "pixi.toml").write_text(
        """
[dependencies]
[feature.dev.dependencies]
pytest = "*"
[feature.agent.dependencies]
ipython = "*"
[environments]
lsp = { features = ["default", "dev", "agent"] }
""",
        encoding="utf-8",
    )
    seen: list[tuple[str, ...]] = []

    def fake_run(argv: tuple[str, ...], **kwargs: Any) -> Any:
        seen.append(tuple(argv))

        class Result:
            returncode = 0

        return Result()

    from skore_skills import env as env_mod

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "agent", "--execute"])
    assert result.exit_code == 0, result.output
    assert seen[0] == ("pixi", "add", "--feature", "agent", "ipython", "pyright")
    payload = json.loads((tmp_path / "pyrightconfig.json").read_text(encoding="utf-8"))
    assert payload["pythonPath"] == ".pixi/envs/lsp/bin/python"


def test_write_pyright_config_escapes_windows_paths(tmp_path: Path) -> None:
    """Backslashes in interpreter paths must produce valid JSON."""
    from skore_skills.env import _write_pyright_config

    windows_path = r"C:\Users\runner\hatch-lsp\Scripts\python.exe"
    _write_pyright_config(tmp_path, windows_path)
    payload = json.loads((tmp_path / "pyrightconfig.json").read_text(encoding="utf-8"))
    assert payload["pythonPath"] == windows_path


def _write_agent_workspace(root: Path, manager: str) -> None:
    """Write a minimal valid declarative agent layout."""
    if manager == "pixi":
        (root / "pixi.toml").write_text(
            """
[dependencies]
[feature.dev.dependencies]
pytest = "*"
[feature.agent.dependencies]
ipython = "*"
[environments]
lsp = { features = ["default", "dev", "agent"] }
""",
            encoding="utf-8",
        )
        python_path = ".pixi/envs/lsp/bin/python"
    elif manager == "uv":
        (root / "pyproject.toml").write_text(
            """
[tool.uv]
[dependency-groups]
dev = ["pytest"]
agent = ["ipython", "pyright"]
""",
            encoding="utf-8",
        )
        (root / "uv.lock").touch()
        python_path = ".venv/bin/python"
    else:
        (root / "pyproject.toml").write_text(
            """
[tool.poetry]
[tool.poetry.group.dev.dependencies]
pytest = "*"
[tool.poetry.group.agent.dependencies]
ipython = "*"
pyright = "*"
""",
            encoding="utf-8",
        )
        python_path = ".venv/bin/python"
    (root / "pyrightconfig.json").write_text(
        json.dumps({"pythonPath": python_path}),
        encoding="utf-8",
    )


@pytest.mark.parametrize("manager", ["pixi", "uv", "poetry"])
def test_env_check_supported_manager(
    tmp_path: Path, manager: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Agent checks pass for valid pixi, uv, and Poetry declarations."""
    _write_agent_workspace(tmp_path, manager)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "check"])
    assert result.exit_code == 0, result.output
    assert "agent layout OK" in result.output


def test_env_check_detects_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing composition and config produce actionable failures."""
    (tmp_path / "pixi.toml").write_text("[dependencies]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "check"])
    assert result.exit_code == 1
    assert "agent layout has drift" in result.output
    assert "pyrightconfig.json missing" in result.output


@pytest.mark.parametrize("fixture", ["hatch", "conda", "pip-venv"])
def test_env_check_warns_for_manual_managers(
    fixture: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Managers without declarative checks return the documented code 2."""
    monkeypatch.chdir(FIXTURES / fixture)
    result = CliRunner().invoke(cli, ["env", "check"])
    assert result.exit_code == 2
    assert "not supported" in result.output


def test_agent_plan_requires_conda_manifests(tmp_path: Path) -> None:
    """Conda plans require explicit agent and LSP manifests."""
    with pytest.raises(ValueError, match="environment-agent.yml"):
        agent_plan(tmp_path, "conda", project="demo")


def test_agent_plan_manual_managers(tmp_path: Path) -> None:
    """Hatch, conda, and pip-venv plans preserve their explicit contracts."""
    (tmp_path / "pyproject.toml").write_text(
        """
[tool.hatch.envs.agent]
dependencies = ["ipython", "pyright"]
[tool.hatch.envs.lsp]
dependencies = ["ipython", "pyright"]
""",
        encoding="utf-8",
    )
    hatch = agent_plan(tmp_path, "hatch")
    assert hatch.python_path == "<hatch-lsp>/bin/python"

    (tmp_path / "environment-agent.yml").touch()
    (tmp_path / "environment-lsp.yml").touch()
    conda = agent_plan(tmp_path, "conda", project="demo")
    assert conda.python_path == "<conda-base>/envs/demo-lsp/bin/python"

    (tmp_path / "requirements-dev.txt").write_text("skore\n", encoding="utf-8")
    pip = agent_plan(tmp_path, "pip-venv", requirements=Path("requirements-dev.txt"))
    assert any("-r" in command for command in pip.install)
    assert pip.python_path == ".venv-lsp/bin/python"


def test_agent_plan_rejects_missing_or_unknown_inputs(tmp_path: Path) -> None:
    """Manager plans fail clearly when required inputs are absent."""
    with pytest.raises(ValueError, match="pixi.toml"):
        agent_plan(tmp_path, "pixi")
    with pytest.raises(ValueError, match="pyproject.toml"):
        agent_plan(tmp_path, "uv")
    with pytest.raises(ValueError, match="requirements file"):
        agent_plan(tmp_path, "pip-venv")
    with pytest.raises(ValueError, match="unknown manager"):
        agent_plan(tmp_path, "pants")


def test_env_agent_bad_argv() -> None:
    """Options that require values are Click usage errors."""
    result = CliRunner().invoke(cli, ["env", "agent", "--project"])
    assert result.exit_code == 2


def test_env_agent_execute_reports_command_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed manager command stops execution with its status."""
    _write_agent_workspace(tmp_path, "pixi")

    def fake_run(argv: tuple[str, ...], **kwargs: Any) -> Any:
        class Result:
            returncode = 7

        return Result()

    from skore_skills import env as env_mod

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "agent", "--execute"])
    assert result.exit_code == 7


@pytest.mark.parametrize(
    ("manager", "resolved"),
    [("hatch", "/tmp/hatch-lsp"), ("conda", "/tmp/conda")],
)
def test_env_agent_resolves_absolute_manager_paths(
    tmp_path: Path,
    manager: str,
    resolved: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Hatch and conda resolve their machine-local LSP interpreters."""
    if manager == "hatch":
        (tmp_path / "pyproject.toml").write_text(
            """
[tool.hatch.envs.agent]
dependencies = ["ipython", "pyright"]
[tool.hatch.envs.lsp]
dependencies = ["ipython", "pyright"]
""",
            encoding="utf-8",
        )
    else:
        (tmp_path / "environment.yml").touch()
        (tmp_path / "environment-agent.yml").touch()
        (tmp_path / "environment-lsp.yml").touch()

    def fake_run(argv: tuple[str, ...], **kwargs: Any) -> Any:
        class Result:
            returncode = 0
            stdout = resolved

        return Result()

    from skore_skills import env as env_mod

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "agent", "--execute", "--project", "demo"])
    assert result.exit_code == 0, result.output
    payload = json.loads((tmp_path / "pyrightconfig.json").read_text(encoding="utf-8"))
    if manager == "hatch":
        assert payload["pythonPath"] == "/tmp/hatch-lsp/bin/python"
    else:
        assert payload["pythonPath"] == "/tmp/conda/envs/demo-lsp/bin/python"


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("not-json", "invalid JSON"),
        (json.dumps({"pythonPath": "wrong"}), "expected"),
    ],
)
def test_env_check_rejects_bad_pyright_config(
    tmp_path: Path,
    body: str,
    message: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid or mismatched pyright configuration is drift."""
    _write_agent_workspace(tmp_path, "uv")
    (tmp_path / "pyrightconfig.json").write_text(body, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "check"])
    assert result.exit_code == 1
    assert message in result.output
