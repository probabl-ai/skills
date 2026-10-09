"""Tests for ``skore_skills notebook convert``."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from skore_skills import notebook as notebook_mod
from skore_skills.cli import cli

INLINE = "%matplotlib inline"


@pytest.fixture(autouse=True)
def _ipywidgets_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Happy-path converts assume the notebook kernel package is present."""
    if notebook_mod.ipywidgets is None:
        monkeypatch.setattr(notebook_mod, "ipywidgets", object())


def _stub_nbformat(write=None) -> SimpleNamespace:
    """nbformat stand-in with ``v4.new_code_cell`` for the inline setup."""

    def _write(nb: object, dest: object) -> None:
        Path(dest).write_text("nb", encoding="utf-8")

    return SimpleNamespace(
        write=write or _write,
        v4=SimpleNamespace(
            new_code_cell=lambda source: {
                "cell_type": "code",
                "source": source,
                "outputs": [],
            }
        ),
    )


def test_notebook_convert_writes_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Executed notebooks store cell outputs next to the percent source."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1 + 1\n", encoding="utf-8")
    payload = {"cells": [{"outputs": []}]}

    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(
        notebook_mod,
        "nbformat",
        _stub_nbformat(),
    )

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            self.notebook = notebook
            self.resources = kwargs.get("resources")

        def execute(self) -> object:
            assert payload["cells"][0]["source"] == INLINE
            payload["cells"][1]["outputs"] = [{"output_type": "execute_result"}]
            return self.notebook

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src)])
    assert result.exit_code == 0, result.output
    dest = tmp_path / "data_analysis.ipynb"
    assert dest.is_file()
    assert len(payload["cells"]) == 1
    assert payload["cells"][0]["outputs"]


def test_notebook_convert_strips_inline_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Execute sees ``%matplotlib inline``; the written notebook does not."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1 + 1\n", encoding="utf-8")
    payload = {"cells": [{"cell_type": "code", "source": "1 + 1", "outputs": []}]}
    seen: list[str] = []

    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(notebook_mod, "nbformat", _stub_nbformat())

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            cells = notebook["cells"]
            seen.append(cells[0]["source"])

        def execute(self) -> object:
            return None

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src)])
    assert result.exit_code == 0, result.output
    assert seen == [INLINE]
    assert [c.get("source") for c in payload["cells"]] == ["1 + 1"]


def test_notebook_convert_missing_src(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing source exits non-zero."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", "no-such.py"])
    assert result.exit_code != 0


def test_notebook_convert_import_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing jupytext/nbclient is a Click error, not a traceback."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    monkeypatch.setattr(notebook_mod, "jupytext", None)
    monkeypatch.setattr(notebook_mod, "nbformat", None)
    monkeypatch.setattr(notebook_mod, "NotebookClient", None)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src)])
    assert result.exit_code != 0
    assert "jupytext" in result.output


def test_notebook_convert_missing_ipywidgets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing ipywidgets is a Click error that names the package."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    monkeypatch.setattr(notebook_mod, "jupytext", SimpleNamespace(read=lambda path: {}))
    monkeypatch.setattr(notebook_mod, "nbformat", _stub_nbformat())
    monkeypatch.setattr(notebook_mod, "NotebookClient", object())
    monkeypatch.setattr(notebook_mod, "ipywidgets", None)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src)])
    assert result.exit_code != 0
    assert "ipywidgets" in result.output
    assert "jupytext" not in result.output


def test_notebook_convert_out_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--out`` writes the notebook to a chosen path."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    dest = tmp_path / "out" / "custom.ipynb"
    payload = {"cells": [{"outputs": []}]}
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(
        notebook_mod,
        "nbformat",
        _stub_nbformat(
            write=lambda nb, path: Path(path).write_text("nb", encoding="utf-8")
        ),
    )

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            self.notebook = notebook

        def execute(self) -> object:
            return self.notebook

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli, ["notebook", "convert", str(src), "--out", str(dest)]
    )
    assert result.exit_code == 0, result.output
    assert dest.is_file()


def test_notebook_convert_execute_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kernel failures surface as a Click error."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: {"cells": []})
    )

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            pass

        def execute(self) -> object:
            raise RuntimeError("kernel died")

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)
    monkeypatch.setattr(
        notebook_mod, "nbformat", _stub_nbformat(write=lambda *_a: None)
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src)])
    assert result.exit_code != 0
    assert "kernel died" in result.output


def test_notebook_convert_uses_script_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Kernel resources.path is the directory that contains SRC."""
    src = tmp_path / "data_analysis" / "data_analysis.py"
    src.parent.mkdir()
    src.write_text("# %%\n1\n", encoding="utf-8")
    payload = {"cells": [{"outputs": []}]}
    seen: list[object] = []
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(
        notebook_mod,
        "nbformat",
        _stub_nbformat(),
    )

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            seen.append(kwargs.get("resources"))

        def execute(self) -> object:
            return None

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src)])
    assert result.exit_code == 0, result.output
    assert seen
    resources = seen[0]
    assert isinstance(resources, dict)
    assert resources["metadata"]["path"] == str(src.parent.resolve())


def test_notebook_convert_html(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``--html`` writes ``<stem>.nb.html`` next to the source."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    payload = {"cells": [{"outputs": []}]}
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(
        notebook_mod,
        "nbformat",
        _stub_nbformat(),
    )

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            pass

        def execute(self) -> object:
            return None

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)
    monkeypatch.setattr(
        notebook_mod,
        "to_html",
        lambda ipynb, dest: (
            dest.write_text("<html>nb</html>", encoding="utf-8") or dest
        ),
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src), "--html"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "data_analysis.ipynb").is_file()
    assert (tmp_path / "data_analysis.nb.html").read_text(encoding="utf-8") == (
        "<html>nb</html>"
    )


def test_notebook_convert_writes_digest_from_same_execution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--digest`` renders outputs without starting a second execution."""
    src = tmp_path / "audit.py"
    src.write_text("# %% [markdown]\n# ## Checks\n# %%\n1 + 1\n", encoding="utf-8")
    payload = {
        "cells": [
            {"cell_type": "markdown", "source": "## Checks", "outputs": []},
            {"cell_type": "code", "source": "1 + 1", "outputs": []},
        ]
    }
    executions = 0
    written: dict[str, object] = {}
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )

    def write(notebook: object, dest: object) -> None:
        written["notebook"] = notebook
        Path(dest).write_text("nb", encoding="utf-8")

    monkeypatch.setattr(notebook_mod, "nbformat", _stub_nbformat(write=write))

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            self.notebook = notebook

        def execute(self) -> object:
            nonlocal executions
            executions += 1
            payload["cells"][2]["outputs"] = [
                {
                    "output_type": "execute_result",
                    "data": {"text/plain": "2"},
                }
            ]
            return self.notebook

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)
    digest = tmp_path / "scratch" / "audit.md"
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(
        cli,
        ["notebook", "convert", str(src), "--digest", str(digest)],
    )
    assert result.exit_code == 0, result.output
    assert executions == 1
    text = digest.read_text(encoding="utf-8")
    assert "## Checks" in text
    assert "**output:**\n```\n2\n```" in text
    metadata = written["notebook"]["metadata"]  # type: ignore[index]
    assert metadata["skore_skills"]["source_sha256"] == (
        notebook_mod.source_fingerprint(src)
    )


def test_render_digest_covers_streams_errors_and_blank_cells(tmp_path: Path) -> None:
    """Stream, error, and empty cells are part of the audit digest."""
    src = tmp_path / "audit.py"
    src.write_text("# %%\n", encoding="utf-8")
    text = notebook_mod.render_digest(
        src,
        {
            "cells": [
                {
                    "cell_type": "code",
                    "source": "   ",
                    "outputs": [
                        {"output_type": "stream", "name": "stderr", "text": "warn\n"},
                        {"output_type": "execute_result", "data": "2"},
                        {"output_type": "display_data", "data": {}},
                        {
                            "output_type": "error",
                            "ename": "ValueError",
                            "evalue": "bad",
                        },
                        {"output_type": "unknown"},
                    ],
                }
            ]
        },
    )
    assert "**stderr:**" in text
    assert "warn" in text
    assert "**error:** `ValueError: bad`" in text
    assert "**output:**" not in text
    assert "```python" not in text


def test_notebook_convert_html_import_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing nbconvert is a Click error when ``--html`` is set."""
    src = tmp_path / "data_analysis.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    payload = {"cells": [{"outputs": []}]}
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(
        notebook_mod,
        "nbformat",
        _stub_nbformat(),
    )

    class FakeClient:
        def __init__(
            self, notebook: object, timeout: int, kernel_name: str, **kwargs: object
        ) -> None:
            pass

        def execute(self) -> object:
            return None

    monkeypatch.setattr(notebook_mod, "NotebookClient", FakeClient)

    def fake_html(src: Path, out: Path) -> Path:
        raise ImportError(notebook_mod.MISSING_NBCONVERT)

    monkeypatch.setattr(notebook_mod, "to_html", fake_html)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "convert", str(src), "--html"])
    assert result.exit_code != 0
    assert "nbconvert" in result.output


def test_notebook_to_html_writes_self_contained_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Executed notebooks render with the Lab template and embedded images."""
    import sys
    from types import ModuleType

    src = tmp_path / "eda.ipynb"
    src.write_text("{}", encoding="utf-8")
    dest = tmp_path / "eda.nb.html"
    seen: dict[str, object] = {}

    class FakeExporter:
        def __init__(
            self,
            *,
            template_name: str,
            template_file: str,
        ) -> None:
            seen["template_name"] = template_name
            seen["template_file"] = template_file
            self.embed_images = False

        def from_filename(self, path: str) -> tuple[str, dict[str, object]]:
            seen["path"] = path
            seen["embed_images"] = self.embed_images
            return "<html>notebook</html>", {}

    module = ModuleType("nbconvert")
    module.HTMLExporter = FakeExporter  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "nbconvert", module)
    written = notebook_mod.to_html(src, dest)
    assert written == dest
    assert dest.read_text(encoding="utf-8") == "<html>notebook</html>"
    assert seen == {
        "template_name": "lab",
        "template_file": str(notebook_mod.TEMPLATE_DIR / "skore_notebook.html.j2"),
        "path": str(src),
        "embed_images": True,
    }


def test_notebook_to_html_missing_src(tmp_path: Path) -> None:
    """Missing notebook is FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        notebook_mod.to_html(tmp_path / "missing.ipynb", tmp_path / "out.html")


def test_notebook_to_html_import_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing nbconvert is ImportError."""
    import sys

    src = tmp_path / "eda.ipynb"
    src.write_text("{}", encoding="utf-8")
    monkeypatch.setitem(sys.modules, "nbconvert", None)  # type: ignore[arg-type]
    with pytest.raises(ImportError, match="nbconvert"):
        notebook_mod.to_html(src, tmp_path / "out.html")


def test_convert_raises_when_source_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``convert`` reports a missing percent-format source."""
    monkeypatch.setattr(notebook_mod, "jupytext", object())
    monkeypatch.setattr(notebook_mod, "nbformat", object())
    monkeypatch.setattr(notebook_mod, "NotebookClient", object())
    with pytest.raises(FileNotFoundError, match="notebook source not found"):
        notebook_mod.convert(tmp_path / "missing.py")


def test_notebook_fill_writes_empty_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Fill stores the source fingerprint and does not keep cell outputs."""
    src = tmp_path / "experiment.py"
    src.write_text("# %%\nreport\n", encoding="utf-8")
    payload = {
        "cells": [
            {
                "cell_type": "code",
                "source": "report",
                "outputs": [{"output_type": "execute_result"}],
                "execution_count": 1,
            },
            {"cell_type": "markdown", "source": "# Title"},
        ],
        "metadata": {},
    }
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(notebook_mod, "nbformat", _stub_nbformat())

    def fail_client(*args: object, **kwargs: object) -> None:
        raise AssertionError(args, kwargs)

    monkeypatch.setattr(notebook_mod, "NotebookClient", fail_client)
    monkeypatch.setattr(notebook_mod, "ipywidgets", None)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "fill", str(src)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "experiment.ipynb").is_file()
    assert payload["cells"][0]["outputs"] == []
    assert payload["cells"][0]["execution_count"] is None
    assert "outputs" not in payload["cells"][1]
    assert payload["metadata"]["skore_skills"]["source_sha256"] == (
        notebook_mod.source_fingerprint(src)
    )


def test_notebook_fill_out_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``--out`` writes the notebook and clears outputs on a cell object."""
    src = tmp_path / "experiment.py"
    src.write_text("# %%\nreport\n", encoding="utf-8")
    dest = tmp_path / "out" / "custom.ipynb"

    class _Cell:
        def __init__(self) -> None:
            self.cell_type = "code"
            self.outputs = [{"output_type": "execute_result"}]
            self.execution_count = 2

        def get(self, key: str, default: object = None) -> object:
            return getattr(self, key, default)

    code = _Cell()
    payload = SimpleNamespace(
        cells=[code, {"cell_type": "markdown", "source": "# Title"}],
        metadata={},
    )
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(notebook_mod, "nbformat", _stub_nbformat())
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "fill", str(src), "--out", str(dest)])
    assert result.exit_code == 0, result.output
    assert dest.is_file()
    assert code.outputs == []
    assert code.execution_count is None
    assert "outputs" not in payload.cells[1]


def test_notebook_fill_unexpected_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failure while reading the source is a Click error."""
    src = tmp_path / "experiment.py"
    src.write_text("# %%\n1\n", encoding="utf-8")

    def fail(path: Path) -> None:
        raise RuntimeError("fill broke")

    monkeypatch.setattr(notebook_mod, "jupytext", SimpleNamespace(read=fail))
    monkeypatch.setattr(notebook_mod, "nbformat", _stub_nbformat())
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "fill", str(src)])
    assert result.exit_code != 0
    assert "fill broke" in result.output


def test_notebook_fill_html(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """``--html`` renders the output-free notebook."""
    src = tmp_path / "audit.py"
    src.write_text("# %%\nchecks\n", encoding="utf-8")
    payload = {"cells": [{"cell_type": "code", "source": "checks"}], "metadata": {}}
    monkeypatch.setattr(
        notebook_mod, "jupytext", SimpleNamespace(read=lambda path: payload)
    )
    monkeypatch.setattr(notebook_mod, "nbformat", _stub_nbformat())
    monkeypatch.setattr(
        notebook_mod,
        "to_html",
        lambda ipynb, dest: (
            dest.write_text("<html>source</html>", encoding="utf-8") or dest
        ),
    )
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "fill", str(src), "--html"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "audit.nb.html").read_text(encoding="utf-8") == (
        "<html>source</html>"
    )


def test_notebook_fill_import_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Missing jupytext is a Click error and does not mention nbclient."""
    src = tmp_path / "experiment.py"
    src.write_text("# %%\n1\n", encoding="utf-8")
    monkeypatch.setattr(notebook_mod, "jupytext", None)
    monkeypatch.setattr(notebook_mod, "nbformat", None)
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["notebook", "fill", str(src)])
    assert result.exit_code != 0
    assert "jupytext" in result.output
    assert "nbclient" not in result.output


def test_fill_raises_when_source_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """``fill`` reports a missing percent-format source."""
    monkeypatch.setattr(notebook_mod, "jupytext", object())
    monkeypatch.setattr(notebook_mod, "nbformat", object())
    with pytest.raises(FileNotFoundError, match="notebook source not found"):
        notebook_mod.fill(tmp_path / "missing.py")
