"""Tests for ``skore-skills audit finding``."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from skore_skills.audit_finding import CLEAN, UNAVAILABLE, audit_finding
from skore_skills.cli import cli

DIGEST = """\
## Checks summary

Out[0]:
Checks summary: 1 issue(s), 2 tip(s), 3 passed, 10 not applicable, 0 skipped, 0 ignored.
Issues:
- [SKD002] Potential underfitting. Read more about this here: https://docs.skore.probabl.ai/c/SKD002.
Tips:
- [SKD006] Coefficient interpretation. Read more about this here: https://docs.skore.probabl.ai/c/SKD006.
- [SKD012] Useless features. Read more about this here: https://docs.skore.probabl.ai/c/SKD012.
Passed:
- [SKD001] Potential overfitting

## Metrics summary

              dummyregressor_mean  dummyregressor_std
metric
score                0.000000e+00            0.000000
rmse                 1.414214e+00            0.000000
mae                  1.200000e+00            0.000000
"""


def test_parses_issues_tips_and_metric(tmp_path: Path) -> None:
    path = tmp_path / "audit.md"
    path.write_text(DIGEST, encoding="utf-8")
    payload = audit_finding(path)
    assert payload["action"] == "proceed"
    assert payload["issues"] == ["SKD002"]
    assert payload["tips"] == ["SKD006", "SKD012"]
    assert payload["finding"].startswith(
        "1 issue(s), 2 tip(s) — SKD002 (issue), SKD006 (tip), SKD012 (tip)"
    )
    assert "RMSE 1.414214e+00" in payload["finding"]


def test_clean_digest(tmp_path: Path) -> None:
    path = tmp_path / "audit.md"
    path.write_text(
        "## Checks summary\nPassed:\n- [SKD001] Potential overfitting\n",
        encoding="utf-8",
    )
    payload = audit_finding(path)
    assert payload["finding"] == CLEAN
    assert payload["issues"] == []
    assert payload["tips"] == []


def test_missing_digest(tmp_path: Path) -> None:
    payload = audit_finding(tmp_path / "missing.md")
    assert payload["action"] == "stop"
    assert payload["finding"] == UNAVAILABLE


def test_error_digest(tmp_path: Path) -> None:
    path = tmp_path / "audit.md"
    path.write_text("**error:** cells run failed\n", encoding="utf-8")
    payload = audit_finding(path)
    assert payload["action"] == "stop"
    assert payload["finding"] == UNAVAILABLE


def test_cli_path_argument(tmp_path: Path) -> None:
    path = tmp_path / "digest.md"
    path.write_text(DIGEST, encoding="utf-8")
    result = CliRunner().invoke(cli, ["audit", "finding", str(path)])
    assert result.exit_code == 0
    assert json.loads(result.output)["tips"] == ["SKD006", "SKD012"]


def test_cli_stem_and_missing_args(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    digest = tmp_path / "scratch" / "audit" / "01_x" / "audit.md"
    digest.parent.mkdir(parents=True)
    digest.write_text(DIGEST, encoding="utf-8")
    result = CliRunner().invoke(cli, ["audit", "finding", "--stem", "01_x"])
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["issues"] == ["SKD002"]

    missing = CliRunner().invoke(cli, ["audit", "finding"])
    assert missing.exit_code == 2

    absent = CliRunner().invoke(cli, ["audit", "finding", "--stem", "nope"])
    assert absent.exit_code == 1
    assert json.loads(absent.output)["finding"] == UNAVAILABLE


def test_blank_line_inside_a_bullet_list_keeps_both_codes(tmp_path: Path) -> None:
    """A blank line between issue bullets does not end the list."""
    path = tmp_path / "audit.md"
    path.write_text(
        "Issues:\n- [SKD002] first\n\n- [SKD003] second\n\nTips:\n",
        encoding="utf-8",
    )
    payload = audit_finding(path)
    assert payload["issues"] == ["SKD002", "SKD003"]
