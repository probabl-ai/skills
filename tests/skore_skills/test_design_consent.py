"""Tests for ``skore-skills design consent``."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.cli import cli
from skore_skills.design_consent import design_approve, design_consent


def _write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _note(root: Path, stem: str, state: str) -> None:
    _write(
        root / "journal" / f"{stem}.md",
        "## Question / hypothesis\n\n"
        "Does a richer feature set beat the baseline?\n\n"
        "## Method\n\n"
        "- **Files touched:** `src/pkg/features.py`\n"
        "- **Change versus baseline:** add rolling aggregates\n\n"
        "## Risks / things that could invalidate the result\n\n"
        "- the rolling window may leak future rows\n\n"
        "## Status\n\n"
        f"- **State:** {state}\n- **Approved by user on:** n/a\n",
    )


def test_planned_asks_for_approval(tmp_path: Path) -> None:
    stem = "05_new_model"
    _note(tmp_path, stem, "planned")

    payload = design_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "ask",
        "reason": "first_approval",
        "choices": ["approve", "modify", "stop"],
        "context": {
            "note": f"journal/{stem}.md",
            "question": "Does a richer feature set beat the baseline?",
            "source": "",
            "files_touched": "`src/pkg/features.py`",
            "change": "add rolling aggregates",
            "risks": ["the rolling window may leak future rows"],
        },
    }


def test_approved_is_proceed(tmp_path: Path) -> None:
    stem = "01_baseline"
    _note(tmp_path, stem, "approved")

    payload = design_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "proceed",
        "reason": "approved",
    }
    assert "choices" not in payload
    assert "context" not in payload


def test_ask_context_is_empty_on_an_unpopulated_note(tmp_path: Path) -> None:
    stem = "06_shell"
    _write(
        tmp_path / "journal" / f"{stem}.md",
        "## Question / hypothesis\n\n<!-- One sentence. -->\n\n"
        "## Status\n\n- **State:** planned\n",
    )

    payload = design_consent(tmp_path, stem)

    assert payload["action"] == "ask"
    assert payload["context"] == {
        "note": f"journal/{stem}.md",
        "question": "",
        "source": "",
        "files_touched": "",
        "change": "",
        "risks": [],
    }


@pytest.mark.parametrize("state", ["running", "done"])
def test_running_and_done_are_proceed(tmp_path: Path, state: str) -> None:
    stem = "02_next"
    _note(tmp_path, stem, state)

    payload = design_consent(tmp_path, stem)

    assert payload["action"] == "proceed"
    assert payload["reason"] == state


def test_missing_design_is_stop(tmp_path: Path) -> None:
    payload = design_consent(tmp_path, "09_missing")

    assert payload == {
        "stem": "09_missing",
        "action": "stop",
        "reason": "missing_design",
    }


def test_abandoned_is_stop(tmp_path: Path) -> None:
    stem = "03_old"
    _note(tmp_path, stem, "abandoned — paper's required dep was non-trivial")

    payload = design_consent(tmp_path, stem)

    assert payload == {
        "stem": stem,
        "action": "stop",
        "reason": "abandoned",
    }


def test_empty_stem_raises() -> None:
    with pytest.raises(ValueError, match="stem is required"):
        design_consent(Path("."), "  ")


def test_cli_prints_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stem = "05_new_model"
    _note(tmp_path, stem, "planned")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["design", "consent", "--stem", stem])

    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["action"] == "ask"


def test_cli_requires_stem() -> None:
    result = CliRunner().invoke(cli, ["design", "consent"])

    assert result.exit_code == 2
    assert "Missing option" in result.output


def test_cli_rejects_blank_stem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank stem is a usage error."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["design", "consent", "--stem", "  "])
    assert result.exit_code != 0
    assert "stem is required" in result.output


def test_missing_or_blank_state_asks(tmp_path: Path) -> None:
    """No State line, or a State that strips to nothing, is still first approval."""
    stem = "05_new_model"
    _write(tmp_path / "journal" / f"{stem}.md", "# note\n\nno status yet\n")
    assert design_consent(tmp_path, stem)["reason"] == "first_approval"

    _write(tmp_path / "journal" / f"{stem}.md", "- **State:** `\n")
    assert design_consent(tmp_path, stem)["reason"] == "first_approval"


def test_design_approve_stamps_today(tmp_path: Path) -> None:
    """A planned note records approval with the injected date."""
    stem = "05_new_model"
    _note(tmp_path, stem, "planned")

    payload = design_approve(tmp_path, stem, today=date(2026, 10, 6))

    assert payload == {
        "action": "approved",
        "stem": stem,
        "state": "approved",
        "approved_on": "2026-10-06",
    }
    text = (tmp_path / "journal" / f"{stem}.md").read_text(encoding="utf-8")
    assert "- **State:** approved\n" in text
    assert "- **Approved by user on:** 2026-10-06\n" in text
    assert "Does a richer feature set beat the baseline?" in text
    assert design_consent(tmp_path, stem)["action"] == "proceed"


def test_design_approve_accepts_a_blank_state(tmp_path: Path) -> None:
    """A blank State still awaiting approval can be stamped."""
    stem = "05_new_model"
    _write(
        tmp_path / "journal" / f"{stem}.md",
        "## Status\n\n- **State:**\n- **Approved by user on:** n/a\n",
    )

    payload = design_approve(tmp_path, stem, today=date(2026, 10, 6))

    assert payload["approved_on"] == "2026-10-06"
    text = (tmp_path / "journal" / f"{stem}.md").read_text(encoding="utf-8")
    assert "- **State:** approved\n" in text


@pytest.mark.parametrize(
    "state",
    ["approved", "running", "done", "abandoned — kept reason", "draft"],
)
def test_design_approve_refuses_to_overwrite(tmp_path: Path, state: str) -> None:
    """A note that is not awaiting approval keeps its existing date."""
    stem = "01_baseline"
    _note(tmp_path, stem, state)
    path = tmp_path / "journal" / f"{stem}.md"
    before = path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="design note state is"):
        design_approve(tmp_path, stem, today=date(2026, 10, 6))

    assert path.read_text(encoding="utf-8") == before


def test_design_approve_requires_the_note(tmp_path: Path) -> None:
    """A missing design note is an error."""
    with pytest.raises(ValueError, match="design note is missing"):
        design_approve(tmp_path, "09_missing", today=date(2026, 10, 6))


def test_design_approve_requires_both_status_lines(tmp_path: Path) -> None:
    """Approval needs a State line and an Approved by user on line."""
    stem = "05_new_model"
    path = tmp_path / "journal" / f"{stem}.md"
    _write(path, "## Status\n\n- **Approved by user on:** n/a\n")
    with pytest.raises(ValueError, match="missing State"):
        design_approve(tmp_path, stem, today=date(2026, 10, 6))

    _write(path, "## Status\n\n- **State:** planned\n")
    before = path.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="missing Approved by user on"):
        design_approve(tmp_path, stem, today=date(2026, 10, 6))
    assert path.read_text(encoding="utf-8") == before


def test_design_approve_rejects_a_blank_stem() -> None:
    """A blank stem is an error."""
    with pytest.raises(ValueError, match="stem is required"):
        design_approve(Path("."), "  ")


def test_design_approve_cli_prints_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The CLI stamps the note and prints the approval date."""
    stem = "05_new_model"
    _note(tmp_path, stem, "planned")
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(cli, ["design", "approve", "--stem", stem])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["action"] == "approved"
    assert payload["approved_on"] == date.today().isoformat()
    text = (tmp_path / "journal" / f"{stem}.md").read_text(encoding="utf-8")
    assert f"- **Approved by user on:** {payload['approved_on']}\n" in text


def test_design_approve_cli_requires_stem() -> None:
    """Omitting --stem is a usage error."""
    result = CliRunner().invoke(cli, ["design", "approve"])

    assert result.exit_code == 2
    assert "Missing option" in result.output


def test_design_approve_cli_rejects_blank_stem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A blank stem is a usage error."""
    monkeypatch.chdir(tmp_path)
    result = CliRunner().invoke(cli, ["design", "approve", "--stem", "  "])
    assert result.exit_code != 0
    assert "stem is required" in result.output
