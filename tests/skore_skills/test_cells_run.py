"""Tests for ``skore_skills cells run``."""

from __future__ import annotations

import importlib
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from click.testing import CliRunner

from skore_skills import cells
from skore_skills.cli import cli
from skore_skills.env import IN_DEV_ENV

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_notebook.py"


def test_cells_run_digest_and_dest(tmp_path: Path) -> None:
    """CLI digest includes markdown, stdout, last-expr, and errors; dest matches."""
    dest = tmp_path / "out.md"
    result = CliRunner().invoke(cli, ["cells", "run", str(FIXTURE), str(dest)])
    assert result.exit_code == 0, result.output
    assert "Title" in result.output
    assert "hello" in result.output
    assert "2 + 2" in result.output
    assert "ValueError" in result.output
    assert dest.is_file()
    assert dest.read_text(encoding="utf-8") == result.output


def test_cells_run_hides_the_editor_marker(tmp_path: Path, monkeypatch) -> None:
    """skore renders through rich's jupyter path when VSCODE_PID is visible.

    InteractiveShell also sets ``sys.ps1``, so skore reads the runner as
    notebook-like and writes displays through ``rich.jupyter.display``,
    which re-enters the redirected stdout and recurses until the process
    hangs. Cells must never see the marker.
    """
    monkeypatch.setenv("VSCODE_PID", "4321")
    importlib.reload(cells)
    assert "VSCODE_PID" not in os.environ

    src = tmp_path / "nb.py"
    src.write_text(
        '# %%\nimport os\nprint(os.environ.get("VSCODE_PID"))\n',
        encoding="utf-8",
    )
    dest = tmp_path / "out.md"
    cells.run(src, dest)

    assert "None" in dest.read_text(encoding="utf-8")


def test_cells_run_checks_summarize_does_not_hang_under_vscode_pid(
    tmp_path: Path,
) -> None:
    """Issue 61: checks under ``run_cell`` plus ``VSCODE_PID`` must finish.

    A fresh subprocess imports ``cells`` before skore, matching Cursor's
    launch shape. In-process pytest can already have built skore's jupyter
    Console, so this path cannot be covered by ``cells.run`` in the test
    process.
    """
    src = tmp_path / "audit.py"
    src.write_text(
        textwrap.dedent(
            """\
            # %%
            import pandas as pd
            import skore
            from sklearn.dummy import DummyRegressor
            from sklearn.model_selection import KFold

            frame = pd.DataFrame(
                {
                    "x": list(range(30)),
                    "z": [float(i % 7) for i in range(30)],
                    "y": [float(i % 5) for i in range(30)],
                }
            )
            report = skore.evaluate(
                DummyRegressor(),
                frame[["x", "z"]],
                frame["y"],
                splitter=KFold(n_splits=2),
            )

            # %%
            checks = report.checks.summarize()
            html = checks._repr_html_()
            assert html.lstrip().startswith("<")
            checks

            # %%
            checks.frame()
            """
        ),
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["VSCODE_PID"] = "1"
    env[IN_DEV_ENV] = "1"
    completed = subprocess.run(
        [sys.executable, "-m", "skore_skills", "cells", "run", str(src)],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert "issue(s)" in completed.stdout
    assert "SKD" in completed.stdout
    assert " object at 0x" not in completed.stdout


def test_cells_imports_without_matplotlib_or_pandas() -> None:
    """Optional plotting and dataframe imports are skipped when absent."""
    import builtins
    import importlib

    real_import = builtins.__import__

    def guarded(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "matplotlib" or name.startswith("matplotlib."):
            raise ImportError(name)
        if name == "pandas" or name.startswith("pandas."):
            raise ImportError(name)
        return real_import(name, globals, locals, fromlist, level)

    builtins.__import__ = guarded
    try:
        importlib.reload(cells)
        assert cells.pd is None
    finally:
        builtins.__import__ = real_import
        importlib.reload(cells)


def test_cells_run_missing_file() -> None:
    """Missing source exits non-zero."""
    result = CliRunner().invoke(cli, ["cells", "run", "no-such-notebook.py"])
    assert result.exit_code != 0


def test_cells_run_skips_empty_cells_and_captures_stderr(tmp_path: Path) -> None:
    """An empty cell is not fenced, and stderr is its own section."""
    src = tmp_path / "notes.py"
    src.write_text(
        "# %%\n\n# %%\nimport sys\nsys.stderr.write('warn\\n')\n",
        encoding="utf-8",
    )
    dest = tmp_path / "out" / "digest.md"
    cells.run(src, dest)
    digest = dest.read_text(encoding="utf-8")
    assert "**stderr:**" in digest
    assert "warn" in digest
    empty = digest.split("## Cell 0:", maxsplit=1)[1].split("## Cell 1:", maxsplit=1)[0]
    assert "```python" not in empty


def test_cells_run_records_an_execution_result(tmp_path, monkeypatch) -> None:
    """A cell result object is rendered under ``**output:**``."""

    class Result:
        result = 4
        success = True
        error_in_exec = None

    class Shell:
        def run_cell(self, body: str, store_history: bool = False) -> Result:
            return Result()

    src = tmp_path / "expr.py"
    src.write_text("# %%\n2 + 2\n", encoding="utf-8")
    monkeypatch.setattr(cells, "make_shell", lambda: Shell())
    dest = tmp_path / "digest.md"
    cells.run(src, dest)
    digest = dest.read_text(encoding="utf-8")
    assert "**output:**" in digest
    assert "4" in digest


def test_cells_main_usage_and_dest(tmp_path: Path, capsys) -> None:
    """``main`` rejects the wrong argument count and writes an optional dest."""
    assert cells.main([]) == 2
    assert "src.py" in capsys.readouterr().err

    src = tmp_path / "notes.py"
    src.write_text("# %%\nprint('hi')\n", encoding="utf-8")
    dest = tmp_path / "nested" / "out.md"
    assert cells.main([str(src), str(dest)]) == 0
    assert dest.is_file()
    assert "hi" in dest.read_text(encoding="utf-8")
    assert "hi" in capsys.readouterr().out
