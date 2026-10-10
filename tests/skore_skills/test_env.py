"""Tests for ``skore_skills env detect`` / ``env add``."""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from packaging.requirements import Requirement

from skore_skills.cli import cli
from skore_skills.env import _venv_bin, install_argv, load_stack_policy

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
    assert payload["mismatch"] is False


def test_env_detect_ambiguous(monkeypatch: pytest.MonkeyPatch) -> None:
    """pixi.toml + conda env is ambiguous: JSON flag and non-zero exit."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ambiguous"] is True
    assert payload["env_manager"] is None
    assert payload["managers"] == ["pixi", "conda"]


def test_status_reports_ambiguous_manager(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Status exposes the same ambiguity facts as env detect."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["status"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] is None
    assert payload["ambiguous"] is True
    assert payload["mismatch"] is False
    assert payload["managers"] == ["pixi", "conda"]


def test_reexec_in_dev_refuses_ambiguous_manager(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Library commands do not fall back to ambient Python when ambiguous."""
    from skore_skills import env as env_mod

    called = False

    def fake_run(*args: Any, **kwargs: Any) -> Any:
        nonlocal called
        called = True
        raise AssertionError("subprocess must not run")

    monkeypatch.delenv(env_mod.IN_DEV_ENV, raising=False)
    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    code = env_mod.reexec_in_dev(FIXTURES / "ambiguous", argv=["api", "version", "x"])
    assert code == 1
    assert called is False


def test_env_add_pixi_never_pip(monkeypatch: pytest.MonkeyPatch) -> None:
    """``env add`` on a pixi fixture prints ``pixi add``, never ``pip install``."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "pixi add skrub pydot graphviz"
    assert "pip install" not in result.output


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("uv", "uv add pandas"),
        ("poetry", "poetry add pandas"),
        (
            "conda",
            "conda install -n fixture-conda -c conda-forge pandas"
            " && conda install -n workspace-dev -c conda-forge pandas",
        ),
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


def test_env_add_hatch_writes_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hatch add inserts the package into pyproject.toml."""
    (tmp_path / "hatch.toml").write_text("# hatch\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "pandas"])
    assert result.exit_code == 0, result.output
    assert "updated pyproject.toml" in result.output
    assert "pip install" not in result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert '"pandas"' in text
    agent = CliRunner().invoke(cli, ["env", "add", "--feature", "agent", "optuna"])
    assert agent.exit_code == 0, agent.output
    agent_text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.hatch.envs.agent]" in agent_text
    assert "[tool.hatch.envs.dev]" in agent_text
    assert "extra-dependencies" in agent_text
    assert '"optuna"' in agent_text


def test_env_add_named_package_not_substituted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """User-named packages are added; no HistGradientBoosting swap."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "add", "xgboost"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "pixi add xgboost"
    assert "HistGradientBoosting" not in result.output
    policy = load_stack_policy()
    assert "forbidden_substitutes" not in policy
    assert "ruff" in policy["mandatory"]


def test_env_stack_prints_policy() -> None:
    """``env stack`` prints the packaged policy, including competing jobs."""
    result = CliRunner().invoke(cli, ["env", "stack"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["competing"]["tabular"] == ["pandas", "polars"]
    assert "pytest" in payload["stage"]
    assert payload == load_stack_policy()


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
    assert seen == [["pixi", "add", "skrub", "pydot", "graphviz"]]
    assert result.output.strip() == "pixi add skrub pydot graphviz"


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


def test_env_add_feature_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """``--feature`` / ``--group`` map onto pixi and uv/poetry flags."""
    monkeypatch.chdir(FIXTURES / "pixi")
    pixi = CliRunner().invoke(cli, ["env", "add", "--feature", "agent", "ruff"])
    assert pixi.exit_code == 0, pixi.output
    assert pixi.output.strip() == "pixi add --feature agent ruff"
    monkeypatch.chdir(FIXTURES / "uv")
    uv = CliRunner().invoke(cli, ["env", "add", "--group", "agent", "ruff"])
    assert uv.exit_code == 0, uv.output
    assert uv.output.strip() == "uv add --group agent ruff"


def test_env_add_refuses_when_unmanaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """User-managed workspaces never emit an install command."""
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code != 0
    assert "user-managed" in result.output
    assert "pixi add" not in result.output


def test_env_detect_recommended_uses_policy(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recorded ``env_manager`` leads the recommended list when none is visible."""
    from skore_skills.policy import empty_policy, save_policy

    policy = empty_policy()
    policy["env_manager"] = "uv"
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.env.shutil.which", lambda *_a, **_k: None)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "none"
    assert payload["recommended"][0] == "uv"
    assert payload["mismatch"] is False
    assert payload["managed"] is None


def _write_fake_skore(tmp_path: Path, *parts: str) -> Path:
    path = tmp_path.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    path.chmod(0o755)
    return path


def _patch_which(monkeypatch: pytest.MonkeyPatch, binary: Path | None) -> None:
    def which(name: str, path: str | None = None) -> str | None:
        if binary is not None and name in {"skore", "skore-cli"}:
            return str(binary)
        return None

    monkeypatch.setattr("skore_skills.env.shutil.which", which)


def test_env_detect_provenance_uv_when_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty root ranks ``uv`` from the ``skore`` install prefix."""
    binary = _write_fake_skore(tmp_path, "uv", "tools", "skore-cli", "bin", "skore")
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "none"
    assert payload["recommended"][0] == "uv"
    assert payload["provenance"]["manager"] == "uv"
    assert payload["mismatch"] is False


def test_env_detect_default_when_no_skore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Empty root with no ``skore`` on PATH keeps the packaged default."""
    monkeypatch.chdir(tmp_path)
    _patch_which(monkeypatch, None)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "none"
    assert payload["recommended"][0] == "pixi"
    assert payload["provenance"] == {"manager": None, "path": None}


def test_env_detect_policy_beats_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Recorded policy ranks above a pixi-looking ``skore`` prefix."""
    from skore_skills.policy import empty_policy, save_policy

    binary = _write_fake_skore(tmp_path, ".pixi", "bin", "skore")
    root = tmp_path / "project"
    root.mkdir()
    policy = empty_policy()
    policy["env_manager"] = "uv"
    save_policy(root, policy)
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["recommended"][0] == "uv"
    assert payload["provenance"]["manager"] == "pixi"
    assert payload["mismatch"] is False


def test_env_detect_manifest_beats_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A unique manifest wins over ``skore`` provenance."""
    binary = _write_fake_skore(tmp_path, "uv", "tools", "skore-cli", "bin", "skore")
    root = tmp_path / "project"
    root.mkdir()
    (root / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "pixi"
    assert payload["recommended"] == ["pixi"]
    assert payload["provenance"]["manager"] == "uv"
    assert payload["mismatch"] is False


def test_env_detect_policy_manifest_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Policy vs a different unique manifest is mismatch, not ambiguous."""
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env_manager"] = "uv"
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    _patch_which(monkeypatch, None)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "pixi"
    assert payload["ambiguous"] is False
    assert payload["mismatch"] is True
    assert payload["recommended"][0] == "uv"


def test_env_detect_ignores_pipx_provenance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A pipx ``skore`` install is too weak to rank a project manager."""
    binary = _write_fake_skore(
        tmp_path, ".local", "pipx", "venvs", "skore-cli", "bin", "skore"
    )
    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, binary)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["recommended"][0] == "pixi"
    assert payload["provenance"]["manager"] is None
    assert payload["provenance"]["path"] == str(binary.resolve())


def test_env_detect_pixi_from_pyproject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``[tool.pixi]`` in pyproject.toml is pixi evidence."""
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pixi.workspace]\nchannels = ["conda-forge"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "detect"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["env_manager"] == "pixi"
    assert "pyproject.toml:[tool.pixi]" in payload["evidence"]["pixi"]


def test_env_init_pixi_writes_agent_tables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pixi init merges ``[tool.pixi]`` and agent packages into pyproject."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.pixi" in text
    assert "ipykernel" in text
    assert "ipython" in text
    assert "skore-skills" not in text
    assert 'dev = { features = ["default", "agent"]' in text
    assert 'agent = { features = ["agent"]' in text
    assert 'default = { features = ["default"]' in text
    assert "[tool.ruff]" in text
    assert not (tmp_path / "pixi.toml").exists()
    assert not (tmp_path / "src").exists()
    second = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert second.exit_code != 0
    assert "already present" in second.output


def test_env_init_uv_writes_dependency_groups(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """uv init writes PEP 735 agent groups."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "uv"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.uv]" in text
    assert "ipykernel" in text
    assert "skore-skills" not in text


def test_env_init_hatch_writes_dev_extra_dependencies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hatch init keeps agent tools-only and extends default via ``dev``."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "hatch"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.hatch.envs.agent]" in text
    assert "[tool.hatch.envs.dev]" in text
    assert "extra-dependencies" in text
    assert "skore-skills" not in text


@pytest.mark.parametrize("manager", ["poetry", "pip-venv"])
def test_env_init_agent_tools_do_not_list_skore_skills(
    manager: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Generated agent dependencies never own ``skore-skills``."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", manager])
    assert result.exit_code == 0, result.output
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    requirements = tmp_path / "requirements.txt"
    generated = pyproject
    if requirements.is_file():
        generated += requirements.read_text(encoding="utf-8")
    assert "skore-skills" not in generated


def test_env_init_refuses_manager_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--manager`` must match an already-detected manager."""
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "uv"])
    assert result.exit_code != 0
    assert "does not match" in result.output


def test_env_init_refuses_pixi_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Refuse to add ``[tool.pixi]`` when ``pixi.toml`` already exists."""
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert result.exit_code != 0
    assert "pixi.toml already exists" in result.output


def test_env_init_refuses_ambiguous_manifests(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Init never chooses or mutates one manager in an ambiguous root."""
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    conda = tmp_path / "environment.yml"
    conda.write_text("name: existing\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "conda"])
    assert result.exit_code != 0
    assert "multiple env managers" in result.output
    assert conda.read_text(encoding="utf-8") == "name: existing\n"
    assert not (tmp_path / "environment-agent.yml").exists()


def test_env_init_refuses_when_unmanaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Init is skipped when the user opted out of env management."""
    from skore_skills.policy import empty_policy, save_policy

    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert result.exit_code != 0
    assert "user-managed" in result.output


def test_env_init_conda_writes_yaml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Conda init writes sidecar YAML, not pyproject manager tables."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "conda"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "environment.yml").is_file()
    agent = (tmp_path / "environment-agent.yml").read_text(encoding="utf-8")
    assert "ipykernel" in agent
    assert "ipython" in agent
    assert "skore-skills" not in agent
    dev = (tmp_path / "environment-dev.yml").read_text(encoding="utf-8")
    assert "name: workspace-dev" in dev
    assert "skore-skills" not in dev
    second = CliRunner().invoke(cli, ["env", "init", "--manager", "conda"])
    assert second.exit_code != 0


def test_env_init_requires_manager() -> None:
    """``env init`` without ``--manager`` is a usage error."""
    result = CliRunner().invoke(cli, ["env", "init"])
    assert result.exit_code != 0


def test_env_init_unknown_manager_library(tmp_path: Path) -> None:
    """Library callers still reject unknown manager names."""
    from skore_skills.env import init_environment

    text, code = init_environment(tmp_path, "pants")
    assert code == 2
    assert "unknown manager" in text


def test_env_agent_removed() -> None:
    """LSP agent install is no longer a CLI command."""
    result = CliRunner().invoke(cli, ["env", "agent"])
    assert result.exit_code != 0
    result_check = CliRunner().invoke(cli, ["env", "check"])
    assert result_check.exit_code != 0


@pytest.mark.parametrize(
    ("fixture", "expected"),
    [
        ("pixi", "pixi install -e dev"),
        ("uv", "uv sync --group agent"),
        ("poetry", "poetry install --with agent"),
        ("hatch", "hatch env create dev"),
        (
            "conda",
            "conda env create -f environment.yml"
            " && conda env create -f environment-agent.yml"
            " && conda env create -f environment-dev.yml",
        ),
        (
            "pip-venv",
            f"python -m venv .venv && {_venv_bin('pip')} install -r requirements.txt",
        ),
    ],
)
def test_env_sync_print(
    fixture: str, expected: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Print-only sync matches the post-init command table."""
    monkeypatch.chdir(FIXTURES / fixture)
    result = CliRunner().invoke(cli, ["env", "sync"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == expected


def test_env_sync_refuses_unmanaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sync refuses when env.managed is false."""
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "sync"])
    assert result.exit_code != 0
    assert "user-managed" in result.output


def test_env_sync_execute_runs_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``env sync --execute`` runs the printed argv."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "sync", "--execute"])
    assert result.exit_code == 0, result.output
    assert seen == [["pixi", "install", "-e", "dev"]]


@pytest.mark.parametrize(
    ("package", "scope", "feature"),
    [
        ("ruff", "agent", "agent"),
        ("skore", "default", None),
        ("skore-skills", "default", None),
        ("skrub", "default", None),
        ("pytest", "default", None),
        ("optuna", "ask", None),
        ("jupyterlab", "ask", None),
        ("jupytext", "agent", "agent"),
        ("nbclient", "agent", "agent"),
        ("ipywidgets", "agent", "agent"),
        ("nbconvert", "agent", "agent"),
        ("mkdocs-material", "agent", "agent"),
        ("pandas", "default", None),
        ("xgboost", "default", None),
        ("black", "default", None),
    ],
)
def test_env_route_scopes(package: str, scope: str, feature: str | None) -> None:
    """Stack policy maps packages onto default, agent, or ask."""
    result = CliRunner().invoke(cli, ["env", "route", package])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["scope"] == scope
    assert payload["feature"] == feature


def test_env_route_named_booster_is_default() -> None:
    """Unknown named libraries route to default, not refuse."""
    result = CliRunner().invoke(cli, ["env", "route", "xgboost"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["scope"] == "default"
    assert payload["feature"] is None
    assert "HistGradientBoosting" not in result.output


def _pixi_editable_spec(root: Path, package: str) -> str:
    return f"{package} @ {root.resolve().as_uri()}"


def _assert_pixi_editable_spec(spec: str, *, root: Path, package: str) -> None:
    requirement = Requirement(spec)
    assert requirement.name == package
    assert requirement.url == root.resolve().as_uri()
    assert requirement.url.startswith("file:")


def test_env_add_editable_pixi(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Editable pixi add uses a PEP 508 ``file:`` URL, not ``--path .``."""
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-pkg"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "--editable"])
    assert result.exit_code == 0, result.output
    prefix = "pixi add --pypi --editable "
    assert result.output.startswith(prefix)
    spec = result.output.removeprefix(prefix).strip()
    _assert_pixi_editable_spec(spec, root=tmp_path, package="demo-pkg")
    assert "--path" not in result.output


def test_env_add_editable_pixi_execute(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--execute`` runs the pixi editable argv with a ``file:`` spec."""
    from skore_skills import env as env_mod

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-pkg"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "--editable", "--execute"])
    assert result.exit_code == 0, result.output
    spec = _pixi_editable_spec(tmp_path, "demo-pkg")
    assert seen[0] == ["pixi", "add", "--pypi", "--editable", spec]
    assert seen[1][:5] == ["pixi", "run", "-e", "dev", "python"]
    assert "demo_pkg" in seen[1][-1]
    assert len(seen) == 2
    _assert_pixi_editable_spec(spec, root=tmp_path, package="demo-pkg")


def test_env_add_editable_execute_fails_when_import_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A successful add that cannot be imported is still a failure."""
    from skore_skills import env as env_mod

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-pkg"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        if "import_module" in " ".join(argv):
            Result.returncode = 1
            Result.stderr = "ModuleNotFoundError: No module named 'demo_pkg'\n"
        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "--editable", "--execute"])
    assert result.exit_code != 0
    assert "No module named 'demo_pkg'" in result.output
    assert "pixi add --pypi --editable" in result.output


def test_env_add_editable_execute_stops_when_add_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed editable add does not run the import check."""
    from skore_skills import env as env_mod

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-pkg"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        if "import_module" in " ".join(argv):
            raise AssertionError("import check ran after a failed add")

        class Result:
            returncode = 1
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "--editable", "--execute"])
    assert result.exit_code != 0
    assert "pixi add --pypi --editable" in result.output


@pytest.mark.parametrize(
    ("files", "expected"),
    [
        ({"uv.lock": ""}, "uv add --editable ."),
        ({"poetry.lock": ""}, "poetry add --editable ."),
        (
            {"requirements.txt": "click\n", ".venv": None},
            "pip install -e .",
        ),
    ],
)
def test_env_add_editable_other_managers_print(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    files: dict[str, str | None],
    expected: str,
) -> None:
    """uv, poetry, and pip-venv already emit an editable argv."""
    for name, body in files.items():
        path = tmp_path / name
        if body is None:
            path.mkdir()
        else:
            path.write_text(body, encoding="utf-8")
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-pkg"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "--editable"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == expected


def test_env_add_editable_conda_refuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Conda has no editable add; do not emit pip -e."""
    (tmp_path / "environment.yml").write_text(
        "name: workspace\ndependencies: []\n", encoding="utf-8"
    )
    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "pkg"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "--editable"])
    assert result.exit_code != 0
    assert "not supported" in result.output
    assert not result.output.startswith("pip install")


def test_env_add_editable_requires_src(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Editable add waits for ``src/``."""
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "--editable"])
    assert result.exit_code != 0
    assert "has_src" in result.output


def test_env_add_conda_feature_agent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Agent-scope conda add targets the agent environment name."""
    (tmp_path / "environment.yml").write_text(
        "name: workspace\ndependencies: []\n", encoding="utf-8"
    )
    (tmp_path / "environment-agent.yml").write_text(
        "name: workspace-agent\ndependencies: []\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "--feature", "agent", "ruff"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == (
        "conda install -n workspace-agent -c conda-forge ruff"
        " && conda install -n workspace-dev -c conda-forge ruff"
    )


def test_env_add_conda_execute_mirrors_default_into_dev(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Conda emulates composition by updating default and dev."""
    from skore_skills import env as env_mod

    (tmp_path / "environment.yml").write_text(
        "name: workspace\ndependencies: []\n", encoding="utf-8"
    )
    (tmp_path / "environment-dev.yml").write_text(
        "name: workspace-dev\ndependencies: []\n", encoding="utf-8"
    )
    monkeypatch.chdir(tmp_path)
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "--execute", "skrub"])
    assert result.exit_code == 0, result.output
    assert seen == [
        [
            "conda",
            "install",
            "-n",
            "workspace",
            "-c",
            "conda-forge",
            "skrub",
            "pydot",
            "graphviz",
        ],
        [
            "conda",
            "install",
            "-n",
            "workspace-dev",
            "-c",
            "conda-forge",
            "skrub",
            "pydot",
            "graphviz",
        ],
    ]


def test_env_verify_print_pixi(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify checks bootstrap packages in composed ``dev``."""
    monkeypatch.chdir(FIXTURES / "pixi")
    result = CliRunner().invoke(cli, ["env", "verify"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is None
    assert payload["argv"][:5] == ["pixi", "run", "-e", "dev", "python"]
    snippet = payload["argv"][-1]
    assert "IPython" in snippet
    assert "skore" in snippet
    assert "skore_skills" in snippet
    assert "import ruff" not in snippet
    assert "with_name" in snippet
    assert "Scripts" in snippet


def test_agent_packages_exclude_transitive_skore_skills() -> None:
    """Agent tools and bootstrap import verification are distinct lists."""
    from skore_skills.env import AGENT_PACKAGES, BOOTSTRAP_PACKAGES

    assert AGENT_PACKAGES == ("ruff", "ipython", "ipykernel")
    assert BOOTSTRAP_PACKAGES == (
        "skore",
        "skore-skills",
        "ruff",
        "ipython",
        "ipykernel",
    )


def test_env_verify_execute_mocked(monkeypatch: pytest.MonkeyPatch) -> None:
    """``env verify --execute`` runs the printed argv."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0
            stdout = "SKORE_SKILLS_VERIFY []\n"
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "verify", "--execute"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["missing"] == []
    assert seen == [payload["argv"]]


def test_env_verify_execute_reports_only_failed_probes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A single failed probe is the only name in ``missing``."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 1
            stdout = 'SKORE_SKILLS_VERIFY ["ruff"]\n'
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "verify", "--execute"])
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert payload["missing"] == ["ruff"]


def test_env_verify_execute_without_marker_did_not_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A composed env that never starts does not mark every package missing."""
    from skore_skills import env as env_mod
    from skore_skills.env import VERIFY_DID_NOT_RUN

    monkeypatch.chdir(FIXTURES / "pixi")

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 1
            stdout = ""
            stderr = "pixi failed\n"

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "verify", "--execute"])
    assert result.exit_code != 0
    payload, end = json.JSONDecoder().raw_decode(result.output)
    assert payload["ok"] is False
    assert payload["missing"] == []
    assert payload["error"] == VERIFY_DID_NOT_RUN
    assert "pixi failed" in result.output[end:]


def test_parse_verify_report_rejects_a_bad_payload() -> None:
    """Noise, invalid JSON, and a non-list payload are not a package list."""
    from skore_skills.env import VERIFY_MARKER, _parse_verify_report

    assert _parse_verify_report(f"{VERIFY_MARKER} []\nnoise\n") == []
    assert _parse_verify_report(f"{VERIFY_MARKER} not-json") is None
    assert _parse_verify_report(f"{VERIFY_MARKER} " + '{"no": "list"}') is None


def test_env_init_mentions_sync(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Init still prints next: and points at ``env sync``."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert result.exit_code == 0, result.output
    assert "next: pixi install -e dev" in result.output
    assert "run: python -m skore_skills env sync" in result.output


@pytest.mark.parametrize(
    ("fixture", "mode", "expected"),
    [
        ("pixi", "local", "pixi add skore"),
        ("pixi", "hub", "pixi add skore"),
        ("pixi", "mlflow", "pixi add skore mlflow>=3"),
        ("uv", "local", "uv add skore"),
        ("uv", "hub", "uv add skore[hub]"),
        ("uv", "mlflow", "uv add skore[mlflow] mlflow>=3"),
        ("poetry", "hub", "poetry add skore[hub]"),
        ("pip-venv", "hub", "pip install skore[hub]"),
        (
            "conda",
            "hub",
            "conda install -n fixture-conda -c conda-forge skore"
            " && conda install -n workspace-dev -c conda-forge skore",
        ),
        (
            "conda",
            "mlflow",
            "conda install -n fixture-conda -c conda-forge skore mlflow>=3"
            " && conda install -n workspace-dev -c conda-forge skore mlflow>=3",
        ),
    ],
)
def test_env_add_skore_manager_mode_matrix(
    fixture: str,
    mode: str,
    expected: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Skore uses conda packages for pixi/conda and PyPI elsewhere."""
    monkeypatch.chdir(FIXTURES / fixture)
    result = CliRunner().invoke(cli, ["env", "add-skore", "--mode", mode])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == expected


def test_env_add_skore_hatch_writes_pypi_requirement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hatch upgrades bootstrap Skore to the mode-specific requirement."""
    (tmp_path / "hatch.toml").write_text("# hatch\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    bootstrap = CliRunner().invoke(cli, ["env", "add-skore", "--mode", "local"])
    assert bootstrap.exit_code == 0, bootstrap.output
    result = CliRunner().invoke(cli, ["env", "add-skore", "--mode", "hub"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert '"skore[hub]"' in text
    assert '"skore"' not in text

    second = CliRunner().invoke(cli, ["env", "add-skore", "--mode", "hub"])
    assert second.exit_code == 0, second.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert text.count('"skore[hub]"') == 1


def test_env_add_skore_execute_runs_subprocess(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Managed ``--execute`` runs the resolved manager command."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(
        cli, ["env", "add-skore", "--mode", "mlflow", "--execute"]
    )
    assert result.exit_code == 0, result.output
    assert seen == [["pixi", "add", "skore", "mlflow>=3"]]


def test_env_add_skore_refuses_unmanaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skore install preserves the managed-environment gate."""
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli, ["env", "add-skore", "--mode", "local", "--execute"]
    )
    assert result.exit_code != 0
    assert "user-managed" in result.output


@pytest.mark.parametrize("fixture", ["none", "ambiguous"])
def test_env_add_skore_refuses_unresolved_manager(
    fixture: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skore source is never selected without one manifest manager."""
    monkeypatch.chdir(FIXTURES / fixture)
    result = CliRunner().invoke(cli, ["env", "add-skore", "--mode", "local"])
    assert result.exit_code != 0


def test_env_add_skore_rejects_invalid_mode() -> None:
    """The CLI rejects an unknown Skore mode."""
    result = CliRunner().invoke(cli, ["env", "add-skore", "--mode", "remote"])
    assert result.exit_code != 0


def test_env_add_skore_omitted_mode_defaults_to_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Omitting ``--mode`` installs plain Skore when no destination is stored."""
    (tmp_path / "pixi.toml").write_text(
        '[workspace]\nname = "demo"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add-skore"])
    assert result.exit_code == 0, result.output
    assert "mlflow" not in result.output
    assert "skore" in result.output


def test_env_add_skore_omitted_mode_uses_recorded_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Omitting ``--mode`` follows a recorded MLflow destination."""
    (tmp_path / "pixi.toml").write_text(
        '[workspace]\nname = "demo"\n',
        encoding="utf-8",
    )
    (tmp_path / ".skore").write_text(
        json.dumps({"workspace": {"skore_mode": "mlflow"}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add-skore"])
    assert result.exit_code == 0, result.output
    assert "mlflow>=3" in result.output


def test_env_add_skore_refuses_local_over_recorded_hub(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--mode local`` does not replace a recorded Hub destination."""
    (tmp_path / "pixi.toml").write_text(
        '[workspace]\nname = "demo"\n',
        encoding="utf-8",
    )
    (tmp_path / ".skore").write_text(
        json.dumps({"workspace": {"skore_mode": "hub"}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add-skore", "--mode", "local"])
    assert result.exit_code != 0
    assert "refusing --mode local" in result.output


def test_env_add_skore_explicit_mode_overrides_recorded_local(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An explicit non-local mode still names that destination."""
    (tmp_path / "uv.lock").write_text("", encoding="utf-8")
    (tmp_path / ".skore").write_text(
        json.dumps({"workspace": {"skore_mode": "local"}}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add-skore", "--mode", "hub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "uv add skore[hub]"


def test_add_skore_rejects_invalid_mode_library(tmp_path: Path) -> None:
    """Library callers receive a usage error for an unknown mode."""
    from skore_skills.env import add_skore

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    text, code = add_skore(tmp_path, "remote")
    assert code == 2
    assert "unknown skore mode" in text


@pytest.mark.parametrize(
    ("manager", "expected"),
    [
        ("pixi", ["pixi", "run", "-e", "dev", "python"]),
        ("uv", ["uv", "run", "--group", "agent", "python"]),
        ("poetry", ["poetry", "run", "python"]),
        ("hatch", ["hatch", "run", "dev:python"]),
        ("conda", ["conda", "run", "-n", "workspace-dev", "python"]),
        ("pip-venv", [_venv_bin("python")]),
    ],
)
def test_dev_run_argv_per_manager(
    manager: str, expected: list[str], tmp_path: Path
) -> None:
    """Composed-dev launcher matches the manager table."""
    from skore_skills.env import dev_run_argv

    if manager == "conda":
        (tmp_path / "environment-dev.yml").write_text(
            "name: workspace-dev\ndependencies: []\n", encoding="utf-8"
        )
    assert dev_run_argv(manager, root=tmp_path) == expected


def test_dev_run_argv_unknown_manager(tmp_path: Path) -> None:
    """Unknown managers are a programming error."""
    from skore_skills.env import dev_run_argv

    with pytest.raises(ValueError, match="unknown manager"):
        dev_run_argv("pants", root=tmp_path)


def test_api_get_reexecs_into_dev(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Library-touching commands re-enter the composed pixi ``dev`` env."""
    from skore_skills import env as env_mod
    from skore_skills.env import IN_DEV_ENV

    monkeypatch.chdir(FIXTURES / "pixi")
    monkeypatch.delenv(IN_DEV_ENV, raising=False)
    seen: list[list[str]] = []
    captured: dict[str, Any] = {}

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)
        captured.update(kwargs)

        class Result:
            returncode = 0
            stdout = "# card\n"
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["api", "get", "skrub.TableReport"])
    assert result.exit_code == 0, result.output
    assert seen == [
        [
            "pixi",
            "run",
            "-e",
            "dev",
            "python",
            "-m",
            "skore_skills",
            "api",
            "get",
            "skrub.TableReport",
        ]
    ]
    assert captured["env"][IN_DEV_ENV] == "1"
    assert result.output == "# card\n"


def test_style_reexecs_into_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    """``style`` re-enters composed ``dev`` with the original flags."""
    from skore_skills import env as env_mod
    from skore_skills.env import IN_DEV_ENV

    monkeypatch.chdir(FIXTURES / "pixi")
    monkeypatch.delenv(IN_DEV_ENV, raising=False)
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["style", "--init"])
    assert result.exit_code == 0, result.output
    assert seen[0][:8] == [
        "pixi",
        "run",
        "-e",
        "dev",
        "python",
        "-m",
        "skore_skills",
        "style",
    ]
    assert "--init" in seen[0]


def test_cells_run_reexecs_into_dev(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``cells run`` re-enters composed ``dev``."""
    from skore_skills import env as env_mod
    from skore_skills.env import IN_DEV_ENV

    src = tmp_path / "nb.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(IN_DEV_ENV, raising=False)
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0
            stdout = "# digest\n"
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["cells", "run", str(src)])
    assert result.exit_code == 0, result.output
    assert seen[0][:8] == [
        "pixi",
        "run",
        "-e",
        "dev",
        "python",
        "-m",
        "skore_skills",
        "cells",
    ]
    assert result.output == "# digest\n"


def test_api_get_skips_reexec_when_already_in_dev(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """``SKORE_SKILLS_IN_DEV`` prevents a second dispatch."""
    from skore_skills import env as env_mod
    from skore_skills.env import IN_DEV_ENV, reexec_in_dev

    monkeypatch.chdir(FIXTURES / "pixi")
    monkeypatch.setenv(IN_DEV_ENV, "1")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(argv)

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    assert reexec_in_dev(FIXTURES / "pixi", argv=["api", "get", "x"]) is None
    assert seen == []


def test_api_get_skips_reexec_when_unmanaged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """User-managed workspaces keep the running interpreter."""
    from skore_skills.env import IN_DEV_ENV, reexec_in_dev
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.delenv(IN_DEV_ENV, raising=False)
    assert reexec_in_dev(tmp_path, argv=["api", "get", "x"]) is None


def test_reexec_skips_when_no_manager(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No env manager means the current interpreter stays in-process."""
    from skore_skills.env import IN_DEV_ENV, reexec_in_dev

    monkeypatch.delenv(IN_DEV_ENV, raising=False)
    assert reexec_in_dev(tmp_path, argv=["api", "get", "x"]) is None


def test_reexec_hints_when_skore_skills_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing wheel in ``dev`` points at ``env sync``."""
    from skore_skills import env as env_mod
    from skore_skills.env import IN_DEV_ENV, MISSING_SKORE_SKILLS_HINT, reexec_in_dev

    monkeypatch.chdir(FIXTURES / "pixi")
    monkeypatch.delenv(IN_DEV_ENV, raising=False)

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 1
            stdout = ""
            stderr = "ModuleNotFoundError: No module named 'skore_skills'\n"

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    stdout = io.StringIO()
    stderr = io.StringIO()
    monkeypatch.setattr(env_mod.sys, "stdout", stdout)
    monkeypatch.setattr(env_mod.sys, "stderr", stderr)
    code = reexec_in_dev(FIXTURES / "pixi", argv=["api", "get", "x"])
    assert code == 1
    assert MISSING_SKORE_SKILLS_HINT in stderr.getvalue()
    assert "env add-skore --mode local --execute" in stderr.getvalue()
    assert "env sync" not in stderr.getvalue()


def test_env_add_skrub_uv_adds_pydot_not_graphviz(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pip-based managers get pydot; Graphviz is not a PyPI package here."""
    monkeypatch.chdir(FIXTURES / "uv")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "uv add skrub pydot"
    assert "graphviz" not in result.output


def test_env_add_skrub_pip_adds_pydot_not_graphviz(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """pip-venv follows the same pydot-only expansion as uv."""
    monkeypatch.chdir(FIXTURES / "pip-venv")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "pip install skrub pydot"
    assert "graphviz" not in result.output


def test_env_add_skrub_poetry_adds_pydot_not_graphviz(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Poetry gets pydot but leaves the native Graphviz install to the OS."""
    monkeypatch.chdir(FIXTURES / "poetry")
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    assert result.output.strip() == "poetry add skrub pydot"
    assert "graphviz" not in result.output


def test_env_add_skrub_hatch_writes_pydot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hatch records pydot next to skrub; not graphviz."""
    (tmp_path / "hatch.toml").write_text("# hatch\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["env", "add", "skrub"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert '"skrub"' in text
    assert '"pydot"' in text
    assert "graphviz" not in text


def _graphviz_run(
    seen: list[list[str]],
    *,
    which: str | None = "/usr/bin/dot",
    probe: int = 0,
    probe_error: str = "RuntimeError: Graphviz returned non-SVG output\n",
) -> Any:
    """Return a subprocess.run stand-in for ``env graphviz`` probes."""
    from skore_skills.env import GRAPHVIZ_PROBE_SNIPPET, WHICH_DOT_SNIPPET

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(list(argv))
        snippet = argv[-1] if argv else ""

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        if snippet == WHICH_DOT_SNIPPET:
            Result.stdout = (which or "") + "\n"
            Result.returncode = 0
        elif snippet == GRAPHVIZ_PROBE_SNIPPET:
            Result.returncode = probe
            Result.stderr = probe_error if probe else ""
        return Result()

    return fake_run


def test_env_graphviz_pixi_missing_dot_prints_conda_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pixi without ``dot`` reports action conda and the add command."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []
    monkeypatch.setattr(env_mod.subprocess, "run", _graphviz_run(seen, which=None))
    result = CliRunner().invoke(cli, ["env", "graphviz"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "conda"
    assert payload["dot"] is None
    assert payload["command"] == ["pixi", "add", "graphviz"]
    assert payload["ok"] is None
    assert payload["instructions"] is None
    assert not any(argv[-1:] == [env_mod.GRAPHVIZ_PROBE_SNIPPET] for argv in seen)


def test_env_graphviz_pixi_execute_adds_then_probes_svg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Managed pixi ``--execute`` installs Graphviz then verifies SVG."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []
    which_hits = {"n": 0}

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(list(argv))
        snippet = argv[-1] if argv else ""

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        if snippet == env_mod.WHICH_DOT_SNIPPET:
            which_hits["n"] += 1
            Result.stdout = ("" if which_hits["n"] == 1 else "/pixi/env/bin/dot") + "\n"
        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dot"] == "/pixi/env/bin/dot"
    assert payload["ok"] is True
    assert ["pixi", "add", "graphviz"] in seen
    assert any(argv[-1] == env_mod.GRAPHVIZ_PROBE_SNIPPET for argv in seen)


def test_env_graphviz_dot_present_execute_only_probes_svg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An existing Graphviz is verified without reinstalling or mutating it."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []
    monkeypatch.setattr(
        env_mod.subprocess, "run", _graphviz_run(seen, which="/usr/bin/dot")
    )
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dot"] == "/usr/bin/dot"
    assert payload["ok"] is True
    assert payload["instructions"] is None
    assert payload["command"] is None
    assert ["pixi", "add", "graphviz"] not in seen
    assert any(argv[-1] == env_mod.GRAPHVIZ_PROBE_SNIPPET for argv in seen)
    assert all("dot -c" not in " ".join(argv) for argv in seen)


def test_env_graphviz_uv_missing_dot_refuses_os_execute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pip-based managers never ``env add graphviz``; ``--execute`` cannot brew."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "uv")
    seen: list[list[str]] = []
    monkeypatch.setattr(env_mod.subprocess, "run", _graphviz_run(seen, which=None))
    printed = CliRunner().invoke(cli, ["env", "graphviz"])
    assert printed.exit_code == 0, printed.output
    payload = json.loads(printed.output)
    assert payload["action"] == "system"
    assert payload["command"] is None
    assert payload["ok"] is None
    assert "graphviz.org/download" in payload["instructions"]
    executed = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert executed.exit_code != 0
    assert not any("brew" in " ".join(argv) for argv in seen)
    assert not any(argv[:2] == ["uv", "add"] for argv in seen)


def test_env_graphviz_uv_dot_present_probes_svg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Homebrew Graphviz already on PATH is verified without cache writes."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "uv")
    seen: list[list[str]] = []
    monkeypatch.setattr(
        env_mod.subprocess,
        "run",
        _graphviz_run(seen, which="/opt/homebrew/bin/dot"),
    )
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["dot"] == "/opt/homebrew/bin/dot"
    assert any(argv[-1] == env_mod.GRAPHVIZ_PROBE_SNIPPET for argv in seen)
    assert not any(argv[:2] == ["uv", "add"] for argv in seen)
    assert all("dot -c" not in " ".join(argv) for argv in seen)


def test_env_graphviz_svg_probe_failure_prints_repair_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An unregistered plugin gets one in-env ``dot -c``, never sudo."""
    from skore_skills import env as env_mod
    from skore_skills.env import GRAPHVIZ_REPAIR

    monkeypatch.chdir(FIXTURES / "uv")
    seen: list[list[str]] = []
    plugin_error = (
        'Format: "svg" not recognized. No formats found.\n'
        'Perhaps "dot -c" needs to be run (with installer\'s privileges) '
        "to register the plugins?\n"
    )
    monkeypatch.setattr(
        env_mod.subprocess,
        "run",
        _graphviz_run(seen, which="/usr/bin/dot", probe=1, probe_error=plugin_error),
    )
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code != 0
    assert GRAPHVIZ_REPAIR in result.output
    assert "not recognized" in result.output
    assert '"ok": false' in result.output
    assert "brew install" not in result.output
    registrations = [argv for argv in seen if argv[-2:] == ["dot", "-c"]]
    assert len(registrations) == 1
    assert registrations[0][:3] == ["uv", "run", "--group"]
    assert not any(argv and argv[0] == "sudo" for argv in seen)
    probes = [argv for argv in seen if argv[-1] == env_mod.GRAPHVIZ_PROBE_SNIPPET]
    assert len(probes) == 2


def test_env_graphviz_does_not_reprobe_when_registration_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed ``dot -c`` is not followed by a second SVG probe."""
    from skore_skills import env as env_mod
    from skore_skills.env import (
        GRAPHVIZ_PROBE_SNIPPET,
        GRAPHVIZ_REPAIR,
        WHICH_DOT_SNIPPET,
    )

    monkeypatch.chdir(FIXTURES / "uv")
    seen: list[list[str]] = []
    plugin_error = 'Format: "svg" not recognized.\nPerhaps "dot -c" needs to be run\n'

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(list(argv))

        class Result:
            returncode = 0
            stdout = ""
            stderr = ""

        if argv[-1:] == [WHICH_DOT_SNIPPET]:
            Result.stdout = "/usr/bin/dot\n"
        elif argv[-1:] == [GRAPHVIZ_PROBE_SNIPPET]:
            Result.returncode = 1
            Result.stderr = plugin_error
        elif argv[-2:] == ["dot", "-c"]:
            Result.returncode = 1
        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code != 0
    assert GRAPHVIZ_REPAIR in result.output
    assert any(argv[-2:] == ["dot", "-c"] for argv in seen)
    probes = [argv for argv in seen if argv[-1:] == [GRAPHVIZ_PROBE_SNIPPET]]
    assert len(probes) == 1


def test_dev_command_argv_pip_venv_uses_the_venv_binary(tmp_path: Path) -> None:
    """Graphviz registration in a venv calls that venv's ``dot``."""
    from skore_skills.env import _dev_command_argv

    argv = _dev_command_argv("pip-venv", tmp_path, ["dot", "-c"])
    python = Path(_venv_bin("python"))
    dot = python.with_name(f"dot{python.suffix}")
    assert argv == [str(dot), "-c"]


def test_script_name_adds_exe_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Windows script names gain ``.exe``; an existing suffix is kept."""
    from skore_skills import env as env_mod

    monkeypatch.setattr(env_mod.os, "name", "nt")
    assert env_mod._script_name("dot") == "dot.exe"
    assert env_mod._script_name("dot.exe") == "dot.exe"


def test_env_graphviz_missing_pydot_prints_probe_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The SVG probe preserves a concise pydot import failure."""
    from skore_skills import env as env_mod
    from skore_skills.env import GRAPHVIZ_REPAIR

    monkeypatch.chdir(FIXTURES / "uv")
    seen: list[list[str]] = []
    error = "ModuleNotFoundError: No module named 'pydot'\n"
    monkeypatch.setattr(
        env_mod.subprocess,
        "run",
        _graphviz_run(seen, probe=1, probe_error=error),
    )
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code != 0
    assert error.strip() in result.output
    assert GRAPHVIZ_REPAIR in result.output
    assert all("dot -c" not in " ".join(argv) for argv in seen)


def test_env_graphviz_unmanaged_prints_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unmanaged workspaces still get print-only Graphviz JSON."""
    from skore_skills import env as env_mod
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    seen: list[list[str]] = []
    monkeypatch.setattr(env_mod.subprocess, "run", _graphviz_run(seen, which=None))
    printed = CliRunner().invoke(cli, ["env", "graphviz"])
    assert printed.exit_code == 0, printed.output
    payload = json.loads(printed.output)
    assert payload["action"] == "conda"
    assert payload["command"] == ["pixi", "add", "graphviz"]
    executed = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert executed.exit_code != 0
    assert "user-managed" in executed.output
    assert ["pixi", "add", "graphviz"] not in seen


def test_skore_path_maps_uv_tool_dir_and_conda(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Provenance recognizes uv tool dirs and conda prefixes, not arbitrary bins."""
    import os

    from skore_skills.env import _manager_from_skore_path, _resolve_skore_binary

    uv_tool = tmp_path / "custom-tools"
    binary = _write_fake_skore(uv_tool, "skore")
    monkeypatch.setenv("UV_TOOL_DIR", str(uv_tool))
    assert _manager_from_skore_path(binary) == "uv"

    conda_bin = _write_fake_skore(tmp_path, "env", "bin", "skore")
    (tmp_path / "env" / "conda-meta").mkdir()
    assert _manager_from_skore_path(conda_bin) == "conda"
    marker = _write_fake_skore(tmp_path, "miniconda3", "bin", "skore")
    assert _manager_from_skore_path(marker) == "conda"
    other = _write_fake_skore(tmp_path, "usr", "local", "bin", "skore")
    assert _manager_from_skore_path(other) is None

    root = tmp_path / "project"
    root.mkdir()
    monkeypatch.chdir(root)
    _patch_which(monkeypatch, marker)
    detected = json.loads(CliRunner().invoke(cli, ["env", "detect"]).output)
    assert detected["provenance"]["manager"] == "conda"
    assert detected["recommended"][0] == "conda"

    real_resolve = Path.resolve

    def resolve(self: Path, *args: object, **kwargs: object) -> Path:
        if self == Path(os.environ["UV_TOOL_DIR"]):
            raise OSError("missing tool dir")
        if self == other:
            raise OSError("broken link")
        return real_resolve(self, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", resolve)
    monkeypatch.setenv("UV_TOOL_DIR", str(tmp_path / "missing-uv-tools"))
    assert _manager_from_skore_path(other) is None
    _patch_which(monkeypatch, other)
    assert _resolve_skore_binary() == other


def test_forbidden_substitute_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """A string substitute is refused; a non-string entry is ignored."""
    from skore_skills.env import forbidden_reason

    policy = load_stack_policy()
    policy["forbidden_substitutes"] = {"black": "use ruff instead", "flake8": ["no"]}
    monkeypatch.setattr("skore_skills.env.load_stack_policy", lambda: policy)
    assert forbidden_reason("flake8") is None
    monkeypatch.chdir(FIXTURES / "pixi")
    routed = CliRunner().invoke(cli, ["env", "route", "black"])
    assert routed.exit_code == 1
    assert routed.output.strip() == "use ruff instead"
    added = CliRunner().invoke(cli, ["env", "add", "black"])
    assert added.exit_code == 1
    assert added.output.strip() == "use ruff instead"


def test_conda_yaml_without_a_name_uses_the_default(tmp_path: Path) -> None:
    """A yaml with no ``name:`` line falls back to the workspace env name."""
    from skore_skills.env import conda_env_name

    (tmp_path / "environment.yml").write_text("dependencies: []\n", encoding="utf-8")
    (tmp_path / "environment-dev.yml").write_text("channels: []\n", encoding="utf-8")
    assert conda_env_name(tmp_path) == "workspace"
    assert conda_env_name(tmp_path, feature="dev") == "workspace-dev"


def test_manager_commands_reject_unknown_names() -> None:
    """Sync, install, and Skore requirements refuse an unknown manager."""
    from skore_skills.env import skore_requirements, sync_argv

    with pytest.raises(ValueError, match="unknown manager"):
        sync_argv("npm")
    assert install_argv("hatch", ["pandas"]) is None
    with pytest.raises(ValueError, match="unknown manager"):
        skore_requirements("npm", "local")


def test_windows_venv_pip_uses_scripts() -> None:
    """pip-venv sync on Windows calls ``Scripts/pip.exe``."""
    import os
    from pathlib import PurePosixPath

    from skore_skills import env as env_mod

    original_name = os.name
    original_path = env_mod.Path
    os.name = "nt"
    env_mod.Path = PurePosixPath  # type: ignore[misc]
    try:
        pip = env_mod.sync_argv("pip-venv")[1][0]
    finally:
        os.name = original_name
        env_mod.Path = original_path
    assert pip == ".venv/Scripts/pip.exe"


def test_env_sync_execute_stops_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """A failing sync command stops the rest of the chain."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "conda")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(list(argv))

        class Result:
            returncode = 0 if len(seen) == 1 else 4

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "sync", "--execute"])
    assert result.exit_code == 4
    assert len(seen) == 2


def test_hatch_toml_edits_cover_quotes_and_missing_lists() -> None:
    """Hatch edits ignore brackets inside strings and create a missing list."""
    from skore_skills.env import (
        _insert_into_deps_list,
        _replace_hatch_skore_requirement,
    )

    quoted = "[project]\ndependencies = ['a]b']\n"
    inserted, changed = _insert_into_deps_list(quoted, "pandas", header="[project]")
    assert changed is True
    assert "'a]b'" in inserted
    assert '"pandas"' in inserted

    trailing = '[project]\ndependencies = ["skore",]\n'
    inserted, changed = _insert_into_deps_list(trailing, "pandas", header="[project]")
    assert changed is True
    assert '"skore", "pandas"' in inserted

    escaped = '[project]\ndependencies = ["say \\"hi\\""]\n'
    inserted, changed = _insert_into_deps_list(escaped, "pandas", header="[project]")
    assert changed is True
    assert 'say \\"hi\\"' in inserted

    assert _insert_into_deps_list("no header\n", "pandas", header="[project]") == (
        "no header\n",
        False,
    )
    created, changed = _insert_into_deps_list("[project]", "pandas", header="[project]")
    assert changed is True
    assert created == '[project]\ndependencies = ["pandas"]'
    unclosed = "[project]\ndependencies = [\n"
    assert _insert_into_deps_list(unclosed, "pandas", header="[project]") == (
        unclosed,
        False,
    )
    assert _replace_hatch_skore_requirement("name = 'x'\n", "skore[hub]")[1] is False
    assert (
        _replace_hatch_skore_requirement("[project]\nname = 'x'\n", "skore[hub]")[1]
        is False
    )
    assert (
        _replace_hatch_skore_requirement("[project]\ndependencies = [\n", "skore[hub]")[
            1
        ]
        is False
    )


def test_hatch_feature_adds_a_missing_dev_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Agent-only Hatch metadata grows a dev env, then refuses a duplicate."""
    (tmp_path / "hatch.toml").write_text("# hatch\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "workspace"\ndependencies = []\n\n'
        '[tool.hatch.envs.agent]\ndependencies = ["ruff"]\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    added = CliRunner().invoke(cli, ["env", "add", "--feature", "agent", "optuna"])
    assert added.exit_code == 0, added.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.hatch.envs.dev]" in text
    assert text.count('"optuna"') == 2
    again = CliRunner().invoke(cli, ["env", "add", "--feature", "agent", "optuna"])
    assert again.exit_code == 0, again.output
    assert "already lists optuna" in again.output


def test_env_add_hatch_execute_syncs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--execute`` on Hatch writes the table and runs ``hatch env create``."""
    from skore_skills import env as env_mod

    (tmp_path / "hatch.toml").write_text("# hatch\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(list(argv))

        class Result:
            returncode = 0

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "add", "pandas", "--execute"])
    assert result.exit_code == 0, result.output
    assert seen == [["hatch", "env", "create", "dev"]]
    assert "hatch env create dev" in result.output


def test_graphviz_instructions_follow_the_platform(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Graphviz instructions cover common OS package managers and PATH refresh."""
    from skore_skills import env as env_mod
    from skore_skills.env import system_graphviz_instructions

    monkeypatch.setattr(env_mod.sys, "platform", "darwin")
    assert system_graphviz_instructions().startswith("brew install graphviz")
    monkeypatch.setattr(env_mod.sys, "platform", "linux")
    monkeypatch.setattr(
        env_mod.platform,
        "freedesktop_os_release",
        lambda: {"ID": "ubuntu", "ID_LIKE": "debian"},
    )
    assert system_graphviz_instructions().startswith("sudo apt-get install graphviz")
    monkeypatch.setattr(
        env_mod.platform,
        "freedesktop_os_release",
        lambda: {"ID": "fedora"},
    )
    assert system_graphviz_instructions().startswith("sudo dnf install graphviz")
    monkeypatch.setattr(
        env_mod.platform,
        "freedesktop_os_release",
        lambda: {"ID": "arch"},
    )
    assert system_graphviz_instructions().startswith("sudo pacman -S graphviz")
    monkeypatch.setattr(
        env_mod.platform,
        "freedesktop_os_release",
        lambda: {"ID": "opensuse-tumbleweed", "ID_LIKE": "suse"},
    )
    assert system_graphviz_instructions().startswith("sudo zypper install graphviz")

    def missing_release() -> dict[str, str]:
        raise OSError

    monkeypatch.setattr(env_mod.platform, "freedesktop_os_release", missing_release)
    assert system_graphviz_instructions().startswith(
        "install Graphviz with your system"
    )
    monkeypatch.setattr(env_mod.sys, "platform", "win32")
    windows = system_graphviz_instructions()
    assert windows.startswith("winget install")
    assert "Restart the terminal or IDE" in windows
    monkeypatch.setattr(env_mod.sys, "platform", "freebsd")
    assert "system package manager" in system_graphviz_instructions()


def test_env_graphviz_refuses_ambiguous_and_missing_managers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Graphviz status does not pick a manager when detection cannot."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    ambiguous = CliRunner().invoke(cli, ["env", "graphviz"])
    assert ambiguous.exit_code != 0
    assert "multiple env managers" in ambiguous.output
    monkeypatch.chdir(FIXTURES / "none")
    missing = CliRunner().invoke(cli, ["env", "graphviz"])
    assert missing.exit_code != 0
    assert "no env manager" in missing.output


def test_env_graphviz_which_failure_is_missing_dot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failing composed-env probe is the same as ``dot`` being absent."""
    from skore_skills import env as env_mod
    from skore_skills.env import WHICH_DOT_SNIPPET

    monkeypatch.chdir(FIXTURES / "pixi")

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        class Result:
            returncode = 1 if argv and argv[-1] == WHICH_DOT_SNIPPET else 0
            stdout = ""
            stderr = "boom\n"

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "graphviz"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["dot"] is None
    assert payload["command"] == ["pixi", "add", "graphviz"]


def test_env_graphviz_conda_execute_installs_both_envs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Conda Graphviz install targets the default env and the dev env."""
    from skore_skills import env as env_mod

    monkeypatch.chdir(FIXTURES / "conda")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(list(argv))

        class Result:
            returncode = 0
            stdout = "\n"
            stderr = ""

        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code == 1
    installs = [argv for argv in seen if argv[:2] == ["conda", "install"]]
    assert installs == [
        [
            "conda",
            "install",
            "-n",
            "fixture-conda",
            "-c",
            "conda-forge",
            "graphviz",
        ],
        ["conda", "install", "-n", "workspace-dev", "-c", "conda-forge", "graphviz"],
    ]


def test_env_graphviz_execute_stops_when_install_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A failed conda Graphviz install stops before the SVG probe."""
    from skore_skills import env as env_mod
    from skore_skills.env import GRAPHVIZ_PROBE_SNIPPET, WHICH_DOT_SNIPPET

    monkeypatch.chdir(FIXTURES / "pixi")
    seen: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> Any:
        seen.append(list(argv))

        class Result:
            returncode = 0
            stdout = "\n"
            stderr = ""

        snippet = argv[-1] if argv else ""
        if snippet == WHICH_DOT_SNIPPET:
            Result.returncode = 0
        elif snippet != GRAPHVIZ_PROBE_SNIPPET:
            Result.returncode = 7
        return Result()

    monkeypatch.setattr(env_mod.subprocess, "run", fake_run)
    result = CliRunner().invoke(cli, ["env", "graphviz", "--execute"])
    assert result.exit_code == 7
    assert all(argv[-1] != GRAPHVIZ_PROBE_SNIPPET for argv in seen)


def test_editable_refuses_unmanaged_and_unnamed_package(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Editable install stops when the env is unmanaged or the package is unnamed."""
    from skore_skills.policy import empty_policy, save_policy

    (tmp_path / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    (tmp_path / "src" / "demo_pkg").mkdir(parents=True)
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo-pkg"\n', encoding="utf-8"
    )
    policy = empty_policy()
    policy["env"]["managed"] = False
    save_policy(tmp_path, policy)
    monkeypatch.chdir(tmp_path)
    unmanaged = CliRunner().invoke(cli, ["env", "add", "--editable"])
    assert unmanaged.exit_code != 0
    assert "user-managed" in unmanaged.output

    bare = tmp_path / "bare"
    bare.mkdir()
    (bare / "pixi.toml").write_text("[workspace]\n", encoding="utf-8")
    (bare / "src").mkdir()
    (bare / "pyproject.toml").write_text("[project]\nversion = '0.1.0'\n")
    monkeypatch.chdir(bare)
    unnamed = CliRunner().invoke(cli, ["env", "add", "--editable"])
    assert unnamed.exit_code != 0
    assert "no package name" in unnamed.output


def test_env_verify_refuses_an_ambiguous_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify does not import-check an ambiguous workspace."""
    monkeypatch.chdir(FIXTURES / "ambiguous")
    result = CliRunner().invoke(cli, ["env", "verify"])
    assert result.exit_code != 0
    payload = json.loads(result.output)
    assert payload["ok"] is False
    assert "multiple env managers" in payload["error"]


def test_env_init_force_keeps_existing_tables(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--force`` does not rewrite manager tables that are already present."""
    monkeypatch.chdir(tmp_path)
    first = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi"])
    assert first.exit_code == 0, first.output
    text = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    forced = CliRunner().invoke(cli, ["env", "init", "--manager", "pixi", "--force"])
    assert forced.exit_code != 0
    assert "already present" in forced.output
    assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == text
