"""Tests for ``skore_skills git ignore-merge`` and ``git end-turn``."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.git import (
    RESOLVED_DOTFILES_PREFIX,
    RESOLVED_REVIEW_PREFIX,
    list_ambiguous_dotfiles,
    list_review_paths,
    merge_gitignore,
    run_end_turn,
    run_review,
)
from skore_skills.policy import set_policy_value

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(root: Path) -> None:
    _git(root, "init")


def _write(path: Path, text: str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # ``newline="\n"`` keeps byte counts stable: Windows text mode would
    # otherwise turn each ``\n`` into ``\r\n``.
    path.write_text(text, encoding="utf-8", newline="\n")


def test_end_turn_no_repo_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing ``.git`` skips without nagging."""
    monkeypatch.chdir(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "data_analysis"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] == "no_repo"
    assert payload["skill"] == "persist-ml-git"


def test_end_turn_unanswered_skips(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unanswered autocommit never asks persist."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / "src" / "pkg" / "data.py")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] == "unanswered"


def test_end_turn_off_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``off`` skips even when the tree is dirty."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "off")
    _write(tmp_path / "src" / "pkg" / "data.py")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] == "off"


def test_end_turn_on_invokes_persist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``on`` plus a dirty tree names ``persist-ml-git`` and does not commit."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "src" / "pkg" / "data.py")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "invoke"
    assert payload["reason"] == "persist"
    assert payload["skill"] == "persist-ml-git"
    assert "src/pkg/data.py" in payload["staged"]
    head = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
    assert head.returncode != 0


def test_end_turn_ambiguous_invokes_resolve(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Unknown hidden files still invoke persist to ask the user."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    CliRunner().invoke(cli, ["git", "ignore-merge"])
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "src" / "pkg" / "data.py")
    _write(tmp_path / ".python-version", "3.12\n")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "data_analysis"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "invoke"
    assert payload["reason"] == "resolve-dotfiles"
    assert ".python-version" in payload["ambiguous_dotfiles"]


def test_end_turn_clean_skips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A clean tree with autocommit on is a skip."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    CliRunner().invoke(cli, ["git", "ignore-merge"])
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    _git(tmp_path, "add", "--", ".gitignore")
    _git(tmp_path, "commit", "-m", "ignore")
    set_policy_value(tmp_path, "git.autocommit", "on")
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "setup"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] in {"clean", "nothing_to_commit"}


def test_ignore_merge_additive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Existing ignore lines are kept; packaged patterns are appended."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".gitignore", "custom-keep/\n")
    result = CliRunner().invoke(cli, ["git", "ignore-merge"])
    assert result.exit_code == 0, result.output
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "custom-keep/" in text
    assert "scratch/" in text
    assert "_build/" in text
    assert "html/" in text
    assert ".*" in text
    payload = json.loads(result.output)
    assert payload["action"] == "ready"


def test_merge_gitignore_is_idempotent(tmp_path: Path) -> None:
    """A second merge adds no duplicate patterns."""
    first = merge_gitignore(tmp_path)
    second = merge_gitignore(tmp_path)
    assert first
    assert second == []


def test_ignore_merge_ambiguous_dotfile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``ignore-merge`` reports unknown hidden paths and exits 2."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".python-version", "3.12\n")
    result = CliRunner().invoke(cli, ["git", "ignore-merge"])
    assert result.exit_code == 2, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "resolve-dotfiles"
    assert ".python-version" in payload["ambiguous_dotfiles"]


def test_ignore_merge_keep_clears_ambiguity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``ignore-merge --keep`` drops a path from the ambiguous list."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".python-version", "3.12\n")
    result = CliRunner().invoke(
        cli, ["git", "ignore-merge", "--keep", ".python-version"]
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "ready"
    assert payload["ambiguous_dotfiles"] == []


def test_ignore_merge_keep_survives_second_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Keep exceptions in ``.gitignore`` stay decided without re-passing ``--keep``."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".python-version", "3.12\n")
    first = CliRunner().invoke(
        cli, ["git", "ignore-merge", "--keep", ".python-version"]
    )
    assert first.exit_code == 0, first.output
    second = CliRunner().invoke(cli, ["git", "ignore-merge"])
    assert second.exit_code == 0, second.output
    payload = json.loads(second.output)
    assert payload["action"] == "ready"
    assert payload["ambiguous_dotfiles"] == []


def test_ignore_merge_decide_clears_unkept(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--decide`` records ignored hidden paths so end-turn does not re-ask."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "src" / "pkg" / "data.py")
    _write(tmp_path / ".python-version", "3.12\n")
    result = CliRunner().invoke(cli, ["git", "ignore-merge", "--decide"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "ready"
    assert payload["ambiguous_dotfiles"] == []
    end = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "data_analysis"])
    assert end.exit_code == 0, end.output
    hook = json.loads(end.output)
    assert hook["reason"] != "resolve-dotfiles"
    assert hook["action"] == "invoke"
    assert hook["reason"] == "persist"


def test_ignore_merge_decide_still_reports_new_hidden(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A hidden path that appears after ``--decide`` is still ambiguous."""
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / ".python-version", "3.12\n")
    decided = CliRunner().invoke(cli, ["git", "ignore-merge", "--decide"])
    assert decided.exit_code == 0, decided.output
    _write(tmp_path / ".foo", "x\n")
    later = CliRunner().invoke(cli, ["git", "ignore-merge"])
    assert later.exit_code == 2, later.output
    payload = json.loads(later.output)
    assert payload["action"] == "resolve-dotfiles"
    assert ".foo" in payload["ambiguous_dotfiles"]
    assert ".python-version" not in payload["ambiguous_dotfiles"]


def _review_by_path(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    review = payload["review_paths"]
    assert isinstance(review, list)
    return {str(item["path"]): item for item in review}


def test_review_flags_large_file_and_fat_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A big file and a heavy directory are each one review entry."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.git.LARGE_FILE_BYTES", 8)
    monkeypatch.setattr("skore_skills.git.LARGE_DIR_COUNT", 3)
    _init_repo(tmp_path)
    _write(tmp_path / "blob.bin", "x" * 8)
    for name in ("a.txt", "b.txt", "c.txt"):
        _write(tmp_path / "bulk" / name, "x\n")
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 2, result.output
    paths = _review_by_path(json.loads(result.output))
    assert paths["blob.bin"]["kind"] == "large"
    assert paths["blob.bin"]["bytes"] == 8
    assert paths["bulk/"]["kind"] == "large"
    assert paths["bulk/"]["bytes"] == 6
    assert "bulk/a.txt" not in paths


def test_review_small_sample_csv_is_not_flagged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A small sample table stays committable without a question."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / "data" / "sample.csv", "a,b\n")
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "ready"
    assert payload["review_paths"] == []


def test_review_raw_and_dataset_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``data/raw/`` is one folder; a large table elsewhere stays a file."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.git.DATASET_MIN_BYTES", 4)
    _init_repo(tmp_path)
    _write(tmp_path / "data" / "sample.csv", "a\n")
    _write(tmp_path / "data" / "big.csv", "abcd")
    _write(tmp_path / "data" / "raw" / "tiny.csv", "x\n")
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 2, result.output
    paths = _review_by_path(json.loads(result.output))
    assert "data/sample.csv" not in paths
    assert "data/" not in paths
    assert paths["data/big.csv"]["kind"] == "dataset"
    assert paths["data/raw/"]["kind"] == "dataset"
    assert "data/raw/tiny.csv" not in paths


def test_review_artifact_folders(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Joblib siblings and a checkpoints directory collapse to folders."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / "weights" / "a.joblib", "x\n")
    _write(tmp_path / "weights" / "b.joblib", "y\n")
    _write(tmp_path / "checkpoints" / "note.txt", "x\n")
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 2, result.output
    paths = _review_by_path(json.loads(result.output))
    assert paths["weights/"]["kind"] == "artifact"
    assert paths["weights/"]["bytes"] == 4
    assert paths["checkpoints/"]["kind"] == "artifact"
    assert "weights/a.joblib" not in paths
    assert "checkpoints/note.txt" not in paths


def test_review_pkl_next_to_source_stays_a_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One model file beside source does not select the parent folder."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / "src" / "pkg" / "model.pkl", "x\n")
    _write(tmp_path / "src" / "pkg" / "data.py", "y\n")
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 2, result.output
    paths = _review_by_path(json.loads(result.output))
    assert set(paths) == {"src/pkg/model.pkl"}
    assert paths["src/pkg/model.pkl"]["kind"] == "artifact"
    decided = CliRunner().invoke(
        cli, ["git", "review-decide", "--ignore", "src/pkg/model.pkl"]
    )
    assert decided.exit_code == 0, decided.output
    lines = (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert lines.count("src/pkg/model.pkl") == 1
    assert "src/pkg/" not in lines


def test_review_one_large_file_does_not_select_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One large file under ``data/`` does not ignore the whole folder."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.git.LARGE_FILE_BYTES", 8)
    _init_repo(tmp_path)
    _write(tmp_path / "data" / "blob.bin", "x" * 8)
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 2, result.output
    paths = _review_by_path(json.loads(result.output))
    assert set(paths) == {"data/blob.bin"}
    assert paths["data/blob.bin"]["kind"] == "large"


def test_review_decide_ignore_folder_persists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ignoring a folder writes one directory pattern and is not re-asked."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "weights" / "a.joblib", "x\n")
    _write(tmp_path / "weights" / "b.joblib", "y\n")
    _write(tmp_path / "src" / "pkg" / "data.py")
    decided = CliRunner().invoke(cli, ["git", "review-decide", "--ignore", "weights/"])
    assert decided.exit_code == 0, decided.output
    lines = (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert lines.count("weights/") == 1
    assert any(
        line.startswith("# skore-skills resolved-review:") and "weights/" in line
        for line in lines
    )
    end = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "implement"])
    assert end.exit_code == 0, end.output
    payload = json.loads(end.output)
    assert payload["action"] == "invoke"
    assert payload["reason"] == "persist"
    assert payload["review_paths"] == []
    assert "src/pkg/data.py" in payload["staged"]
    assert all(not path.startswith("weights/") for path in payload["status"])


def test_review_decide_keep_persists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A kept file stays staged and is not asked again."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.git.LARGE_FILE_BYTES", 100)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "model.bin", "x" * 100)
    decided = CliRunner().invoke(cli, ["git", "review-decide", "--keep", "model.bin"])
    assert decided.exit_code == 0, decided.output
    lines = (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "model.bin" not in lines
    assert any("model.bin" in line for line in lines)
    end = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "implement"])
    assert end.exit_code == 0, end.output
    payload = json.loads(end.output)
    assert payload["reason"] == "persist"
    assert payload["review_paths"] == []
    assert "model.bin" in payload["staged"]


def test_review_decide_refuses_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``.env`` cannot be kept through the review decision."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / ".env", "TOKEN=1\n")
    result = CliRunner().invoke(cli, ["git", "review-decide", "--keep", ".env"])
    assert result.exit_code != 0
    assert "blocked" in result.output


def test_review_skips_ignored_mlruns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Packaged ignore rules hide ``mlruns/`` from review."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    CliRunner().invoke(cli, ["git", "ignore-merge"])
    _write(tmp_path / "mlruns" / "0" / "meta.yaml", "x\n")
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["review_paths"] == []
    assert all("mlruns" not in path for path in payload["status"])


def test_end_turn_omits_undecided_review_from_staged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Undecided review paths are invoked, and left out of ``staged``."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.git.LARGE_FILE_BYTES", 8)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / "src" / "pkg" / "data.py")
    _write(tmp_path / "blob.bin", "x" * 8)
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "implement"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "invoke"
    assert payload["reason"] == "resolve-review"
    assert "src/pkg/data.py" in payload["staged"]
    assert "blob.bin" not in payload["staged"]
    assert "blob.bin" in payload["status"]


def test_end_turn_off_beats_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Autocommit ``off`` skips before a review question."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.git.LARGE_FILE_BYTES", 8)
    _init_repo(tmp_path)
    set_policy_value(tmp_path, "git.autocommit", "off")
    _write(tmp_path / "blob.bin", "x" * 8)
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "implement"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "skip"
    assert payload["reason"] == "off"
    assert payload["review_paths"][0]["path"] == "blob.bin"


def test_end_turn_dotfiles_keep_review_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Hidden-path resolution still reports review paths in the same payload."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("skore_skills.git.LARGE_FILE_BYTES", 10_000)
    _init_repo(tmp_path)
    CliRunner().invoke(cli, ["git", "ignore-merge"])
    set_policy_value(tmp_path, "git.autocommit", "on")
    _write(tmp_path / ".python-version", "3.12\n")
    _write(tmp_path / "blob.bin", "x" * 10_000)
    result = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "data_analysis"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["reason"] == "resolve-dotfiles"
    assert ".python-version" in payload["ambiguous_dotfiles"]
    assert payload["review_paths"][0]["path"] == "blob.bin"
    assert "blob.bin" not in payload["staged"]


def test_review_notebook_when_present(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An ``.ipynb`` that git status shows is a notebook review path."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / "notes.ipynb", "{}\n")
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 2, result.output
    paths = _review_by_path(json.loads(result.output))
    assert paths["notes.ipynb"]["kind"] == "notebook"


def _failed_git(stderr: str = "fatal: not a git repository\n"):
    def fake_run(argv: list[str], **kwargs: object) -> object:
        return type(
            "Result",
            (),
            {"returncode": 128, "stdout": "", "stderr": stderr},
        )()

    return fake_run


def test_keep_absolute_directory_and_rejects_outside(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An absolute in-repo directory is kept; paths outside the root are refused."""
    monkeypatch.chdir(tmp_path)
    hidden = tmp_path / ".hidden"
    hidden.mkdir()
    _write(hidden / "note.txt", "x\n")
    kept = CliRunner().invoke(cli, ["git", "ignore-merge", "--keep", str(hidden)])
    assert kept.exit_code == 0, kept.output
    text = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "!.hidden/" in text
    assert "!.hidden/**" in text

    outside = CliRunner().invoke(
        cli, ["git", "ignore-merge", "--keep", str(tmp_path.parent / "nope")]
    )
    assert outside.exit_code != 0
    assert "outside workspace" in outside.output
    parent = CliRunner().invoke(cli, ["git", "ignore-merge", "--keep", "../nope"])
    assert parent.exit_code != 0
    assert "outside workspace" in parent.output


def test_gitignore_glob_exception_and_missing_root_are_settled(tmp_path: Path) -> None:
    """``!**`` counts as a decision, and a missing root has nothing to ask."""
    (tmp_path / ".gitignore").write_text("!.cache/**\n", encoding="utf-8")
    (tmp_path / ".cache").mkdir()
    assert list_ambiguous_dotfiles(tmp_path) == []
    assert list_ambiguous_dotfiles(tmp_path / "missing") == []


def test_decide_replaces_the_resolved_dotfile_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A second ``--decide`` rewrites the resolved line instead of duplicating it."""
    monkeypatch.chdir(tmp_path)
    quiet = CliRunner().invoke(cli, ["git", "ignore-merge", "--decide"])
    assert quiet.exit_code == 0, quiet.output
    assert RESOLVED_DOTFILES_PREFIX not in (tmp_path / ".gitignore").read_text(
        encoding="utf-8"
    )

    _write(tmp_path / ".extra", "a\n")
    first = CliRunner().invoke(cli, ["git", "ignore-merge", "--decide"])
    assert first.exit_code == 0, first.output
    _write(tmp_path / ".more", "b\n")
    second = CliRunner().invoke(cli, ["git", "ignore-merge", "--decide"])
    assert second.exit_code == 0, second.output
    lines = [
        line
        for line in (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.startswith(RESOLVED_DOTFILES_PREFIX)
    ]
    assert len(lines) == 1
    assert ".extra" in lines[0]
    assert ".more" in lines[0]


def test_porcelain_parses_renames_quotes_and_status_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Porcelain skips short rows, follows renames, and unquotes paths."""
    from skore_skills.git import _porcelain_paths, _run_git

    stdout = "\n".join(
        [
            " M",
            "R  old.py -> new.py",
            'A  "weird file.py"',
            "?? ok.py",
        ]
    )

    def fake_run(argv: list[str], **kwargs: object) -> object:
        return type(
            "Result",
            (),
            {"returncode": 0, "stdout": stdout, "stderr": ""},
        )()

    monkeypatch.setattr("skore_skills.git.subprocess.run", fake_run)
    assert _porcelain_paths(tmp_path) == ["new.py", "weird file.py", "ok.py"]

    monkeypatch.setattr("skore_skills.git.subprocess.run", _failed_git())
    with pytest.raises(ValueError, match="not a git repository"):
        _porcelain_paths(tmp_path)

    def missing_git(argv: list[str], **kwargs: object) -> object:
        raise FileNotFoundError

    monkeypatch.setattr("skore_skills.git.subprocess.run", missing_git)
    with pytest.raises(ValueError, match="not installed"):
        _run_git(tmp_path, "status")


def test_review_skips_missing_paths_and_unreadable_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Gone paths are dropped; an unreadable file is treated as empty."""
    assert list_review_paths(tmp_path, ["gone.pkl"]) == []
    _write(tmp_path / "locked.bin", "x" * 20)
    real_stat = Path.stat
    real_exists = Path.exists

    def exists(self: Path) -> bool:
        if self.name == "locked.bin":
            return True
        return real_exists(self)

    def stat(self: Path, *args: object, **kwargs: object):
        if self.name == "locked.bin":
            raise OSError("denied")
        return real_stat(self, *args, **kwargs)

    monkeypatch.setattr(Path, "exists", exists)
    monkeypatch.setattr(Path, "stat", stat)
    assert list_review_paths(tmp_path, ["locked.bin"]) == []


def test_review_html_notebook_and_mixed_folder(tmp_path: Path) -> None:
    """``.nb.html`` is a notebook, and a mixed folder keeps the dominant kind."""
    _write(tmp_path / "report.nb.html", "<p></p>\n")
    entries = list_review_paths(tmp_path, ["report.nb.html"])
    assert entries[0]["kind"] == "notebook"

    _write(tmp_path / "notes" / "model.pkl", "x\n")
    _write(tmp_path / "notes" / "view.ipynb", "{}\n")
    mixed = list_review_paths(tmp_path, ["notes/model.pkl", "notes/view.ipynb"])
    assert [item["path"] for item in mixed] == ["notes/"]
    assert mixed[0]["kind"] == "artifact"


def test_end_turn_rejects_unknown_stage(tmp_path: Path) -> None:
    """Library callers cannot invent a stage the CLI choice already rejects."""
    with pytest.raises(ValueError, match="stage must be one of"):
        run_end_turn(tmp_path, "audit")


def test_review_without_a_repo_is_ready(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """No ``.git`` means there is nothing to classify."""
    monkeypatch.chdir(tmp_path)
    payload, code = run_review(tmp_path)
    assert code == 0
    assert payload["reason"] == "no_repo"
    result = CliRunner().invoke(cli, ["git", "review"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["reason"] == "no_repo"


def test_git_commands_surface_status_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Review and end-turn turn a failing ``git status`` into a CLI error."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    monkeypatch.setattr("skore_skills.git.subprocess.run", _failed_git())
    review = CliRunner().invoke(cli, ["git", "review"])
    assert review.exit_code != 0
    assert "not a git repository" in review.output
    end = CliRunner().invoke(cli, ["git", "end-turn", "--stage", "implement"])
    assert end.exit_code != 0
    assert "not a git repository" in end.output


def test_review_decide_overlap_and_remaining_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A path cannot be kept and ignored, and leftover paths stay unresolved."""
    monkeypatch.chdir(tmp_path)
    _init_repo(tmp_path)
    _write(tmp_path / "a.pkl", "a\n")
    _write(tmp_path / "b.pkl", "b\n")
    empty = CliRunner().invoke(cli, ["git", "review-decide"])
    assert empty.exit_code == 2
    gitignore = tmp_path / ".gitignore"
    recorded = gitignore.read_text(encoding="utf-8") if gitignore.is_file() else ""
    assert RESOLVED_REVIEW_PREFIX not in recorded

    both = CliRunner().invoke(
        cli, ["git", "review-decide", "--keep", "a.pkl", "--ignore", "a.pkl"]
    )
    assert both.exit_code != 0
    assert "both keep and ignore" in both.output

    kept = CliRunner().invoke(cli, ["git", "review-decide", "--keep", "a.pkl"])
    assert kept.exit_code == 2
    payload = json.loads(kept.output)
    assert [item["path"] for item in payload["review_paths"]] == ["b.pkl"]

    ignored = CliRunner().invoke(cli, ["git", "review-decide", "--ignore", "b.pkl"])
    assert ignored.exit_code == 0, ignored.output
    lines = [
        line
        for line in (tmp_path / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.startswith(RESOLVED_REVIEW_PREFIX)
    ]
    assert len(lines) == 1
    assert "a.pkl" in lines[0]
    assert "b.pkl" in lines[0]
