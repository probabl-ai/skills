"""Deterministic check for the user-facing language prohibition."""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

from tests.eval.harness import MetricOutcome

REPO_ROOT = Path(__file__).resolve().parents[2]
LANGUAGE_MARK = "Put catalog skill ids, HITL"

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_FENCE = re.compile(r"^```")
_ALLOWED_G = frozenset({"G-REPORT-LOCATOR", "G-AUDIT-FINDING"})
_G_TOKEN = re.compile(r"\bG-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
_HITL = re.compile(r"\bHITL\b", re.IGNORECASE)
_WRAPPER = re.compile(r"python -m skore_skills")
_ENV_ADD = re.compile(r"\benv add\b")
_UNMANAGED = re.compile(r"(?:pixi add|uv add|pip install)\b")
_INTERNAL_CONTAINS = (
    "pre-flight",
    "preflight",
    "state at close",
    "post-close",
    "mechanical",
    "agent",
    "internal",
    "harness",
    "handoff",
    "sequence",
    "actions",
    "end of turn",
    "gate",
)
_INTERNAL_EXACT = frozenset({"run", "commands", "checklist"})


def is_language_prohibition(item: str) -> bool:
    """Return whether ``item`` is the shared user-facing language rule."""
    return LANGUAGE_MARK in item


def partition_language(items: Sequence[str]) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split the language rule out of the other Must-NOT expectations."""
    language = tuple(item for item in items if is_language_prohibition(item))
    rest = tuple(item for item in items if not is_language_prohibition(item))
    return language, rest


@lru_cache(maxsize=1)
def _catalog_ids() -> tuple[str, ...]:
    data = json.loads((REPO_ROOT / ".catalog.json").read_text(encoding="utf-8"))
    return tuple(
        str(skill["id"])
        for skill in data.get("skills") or []
        if isinstance(skill, dict) and skill.get("id")
    )


def _heading(line: str) -> tuple[int, str] | None:
    match = _HEADING.match(line)
    if match is None:
        return None
    return len(match.group(1)), match.group(2)


def _internal_heading(title: str) -> bool:
    normalized = re.sub(r"[*_`]", "", title).strip().rstrip(":").lower()
    if normalized in _INTERNAL_EXACT:
        return True
    return any(phrase in normalized for phrase in _INTERNAL_CONTAINS)


def user_facing_text(text: str) -> str:
    """Drop internal checklists and fenced wrapper commands."""
    lines = text.splitlines()
    kept: list[str] = []
    index = 0
    skip_level: int | None = None
    while index < len(lines):
        line = lines[index]
        if _FENCE.match(line):
            fence = [line]
            index += 1
            while index < len(lines) and not _FENCE.match(lines[index]):
                fence.append(lines[index])
                index += 1
            if index < len(lines):
                fence.append(lines[index])
                index += 1
            continue
        heading = _heading(line)
        if heading is not None:
            level, title = heading
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and _internal_heading(title):
                skip_level = level
                index += 1
                continue
        if skip_level is None and _plain_preflight(line):
            skip_level = 2
            index += 1
            continue
        if skip_level is None:
            kept.append(line)
        index += 1
    return "\n".join(kept)


def _unmanaged_line(line: str) -> bool:
    stripped = re.sub(r"^[\s\-*]+", "", line).strip("`")
    return _UNMANAGED.match(stripped) is not None


def _plain_preflight(line: str) -> bool:
    stripped = re.sub(r"^[\s\-*]+", "", line).strip().lower()
    return stripped.startswith(("pre-flight", "preflight"))


def _visible_prose(line: str) -> str:
    """Drop procedure names in code, bold, and parenthetical gate labels."""
    without_code = re.sub(r"`[^`]*`", " ", line)
    without_bold = re.sub(r"\*\*[^*]+\*\*", " ", without_code)
    without_parens = re.sub(r"\([^)]*\)", " ", without_bold)
    without_named_skill = re.sub(
        r"\bthe\s+[a-z0-9]+(?:-[a-z0-9]+)+\s+skill\b",
        " ",
        without_parens,
        flags=re.IGNORECASE,
    )
    without_status_gate = re.sub(
        r"(?:(?<=—)|(?<=–))\s*G-[A-Z0-9]+(?:-[A-Z0-9]+)*\b|\bG-[A-Z0-9]+(?:-[A-Z0-9]+)*\b(?=\s*\()",
        " ",
        without_named_skill,
    )
    if re.search(r"\bask\b", without_status_gate, flags=re.IGNORECASE) is None:
        without_status_gate = _G_TOKEN.sub(" ", without_status_gate)
    return re.sub(
        r"\b(?:design|post-smoke|first-[\w-]+|Evaluate)\s+HITL\b",
        " ",
        without_status_gate,
        flags=re.IGNORECASE,
    )


def _checklist_row(line: str) -> bool:
    return re.match(r"^\s*[-*]\s+\[[ xX~]\]", line) is not None


def _code_line(line: str) -> bool:
    """A comment or import is source, not the close narrative."""
    stripped = re.sub(r"^[\s\-*]+", "", line).strip()
    return stripped.startswith("#") or stripped.startswith(("import ", "from "))


def _gate_label(line: str) -> bool:
    """A heading or bullet whose label is only a ``G-*`` ask name."""
    stripped = re.sub(r"^[\s\-*]+", "", line).strip()
    stripped = re.sub(r"^\d+\.\s*", "", stripped)
    stripped = re.sub(r"^#{1,6}\s+", "", stripped)
    label = re.split(r"\s+[—–-]\s+|:|\s+→\s*", stripped, maxsplit=1)[0]
    label = re.sub(r"[*_`]", "", label).strip()
    return _G_TOKEN.fullmatch(label) is not None


def _command_record(line: str) -> bool:
    """A wrapper or ``env add`` line is the internal command record."""
    return _WRAPPER.search(line) is not None or _ENV_ADD.search(line) is not None


def language_violations(text: str) -> tuple[str, ...]:
    """Return forbidden tokens in the user-facing slice of ``text``."""
    found: list[str] = []
    seen: set[str] = set()
    ids = _catalog_ids()
    for line in user_facing_text(text).splitlines():
        if (
            _unmanaged_line(line)
            or _command_record(line)
            or _checklist_row(line)
            or _code_line(line)
            or _gate_label(line)
        ):
            continue
        prose = _visible_prose(re.sub(r"\s+#.*$", "", line))
        for skill_id in ids:
            if re.search(rf"(?<![\w-]){re.escape(skill_id)}(?![\w-])", prose):
                if skill_id not in seen:
                    found.append(skill_id)
                    seen.add(skill_id)
        match = _HITL.search(prose)
        if match is not None and match.group(0) not in seen:
            found.append(match.group(0))
            seen.add(match.group(0))
        for token in _G_TOKEN.findall(prose):
            if token not in _ALLOWED_G and token not in seen:
                found.append(token)
                seen.add(token)
    return tuple(found)


def score_user_facing_language(text: str) -> MetricOutcome:
    """Score the language rule without sending it to an LLM judge."""
    violations = language_violations(text)
    if violations:
        listed = ", ".join(violations)
        return MetricOutcome(
            name="must_not",
            score=0.0,
            threshold=1.0,
            reason=f"user-facing language: {listed}",
            passed=False,
        )
    return MetricOutcome(
        name="must_not",
        score=1.0,
        threshold=1.0,
        reason=(
            "user-facing language: no catalog id, HITL, G-* ask name, "
            "or wrapper CLI in the question or close"
        ),
        passed=True,
    )


def merge_must_not(
    language: MetricOutcome,
    judged: MetricOutcome | None,
) -> MetricOutcome:
    """Combine the deterministic language result with the other Must-NOT score."""
    if judged is None:
        return language
    if judged.reason.startswith("judge error:"):
        reason = judged.reason if language.passed else f"{judged.reason} | {language.reason}"
        return MetricOutcome(
            name="must_not",
            score=None,
            threshold=1.0,
            reason=reason,
            passed=False,
            evaluation_cost=judged.evaluation_cost,
        )
    passed = language.passed and judged.passed
    return MetricOutcome(
        name="must_not",
        score=1.0 if passed else 0.0,
        threshold=1.0,
        reason=f"{language.reason} | {judged.reason}",
        passed=passed,
        evaluation_cost=judged.evaluation_cost,
    )
