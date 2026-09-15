"""Dispatch tests for the eval harness ``run_skore_skills`` tool (no LLM)."""

from __future__ import annotations

from pathlib import Path

from tests.eval.sandbox import Sandbox, missing_cli, parse_cli_args


def test_status_runs_in_sandbox(tmp_path: Path) -> None:
    box = Sandbox(tmp_path)
    out = box.dispatch("run_skore_skills", {"args": ["status"]})
    assert "exit_code=0" in out
    assert "has_src" in out


def test_api_version_sklearn(tmp_path: Path) -> None:
    box = Sandbox(tmp_path)
    out = box.dispatch("run_skore_skills", {"args": ["api", "version", "sklearn"]})
    assert "exit_code=0" in out
    assert any(ch.isdigit() for ch in out)


def test_api_get_writes_cache_under_sandbox(tmp_path: Path) -> None:
    box = Sandbox(tmp_path)
    out = box.dispatch(
        "run_skore_skills",
        {"args": ["api", "get", "sklearn.model_selection.KFold"]},
    )
    assert "exit_code=0" in out
    caches = list((tmp_path / "scratch" / "api").rglob("*.md"))
    assert len(caches) == 1
    assert "KFold" in caches[0].read_text(encoding="utf-8")


def test_rejects_empty_args(tmp_path: Path) -> None:
    box = Sandbox(tmp_path)
    out = box.dispatch("run_skore_skills", {"args": []})
    assert out.startswith("error:")
    assert "non-empty" in out


def test_rejects_python_c(tmp_path: Path) -> None:
    box = Sandbox(tmp_path)
    out = box.dispatch("run_skore_skills", {"args": ["-c", "print(1)"]})
    assert out.startswith("error:")
    assert "python -c" in out


def test_rejects_posix_absolute_path(tmp_path: Path) -> None:
    box = Sandbox(tmp_path)
    out = box.dispatch("run_skore_skills", {"args": ["cells", "run", "/tmp/x.py"]})
    assert out.startswith("error:")
    assert "relative" in out


def test_rejects_windows_absolute_path(tmp_path: Path) -> None:
    box = Sandbox(tmp_path)
    out = box.dispatch(
        "run_skore_skills",
        {"args": ["cells", "run", r"C:\temp\x.py"]},
    )
    assert out.startswith("error:")
    assert "relative" in out


def test_parse_cli_args_from_json_string() -> None:
    assert parse_cli_args('["api", "version", "sklearn"]') == [
        "api",
        "version",
        "sklearn",
    ]


def test_missing_cli_matches_argv_substring() -> None:
    trace = [
        {
            "name": "run_skore_skills",
            "arguments": {"args": ["api", "get", "sklearn.model_selection.KFold"]},
        }
    ]
    assert missing_cli(trace, ["api get sklearn.model_selection.KFold"]) == []
    assert missing_cli(trace, ["style src/"]) == ["style src/"]
    assert missing_cli(
        [{"name": "run_python", "arguments": {"path": "scratch/x.py"}}],
        ["api get"],
    ) == ["api get"]
