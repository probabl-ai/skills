"""Jev decision-model adapter for skill evaluations."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping, Sequence
from typing import Any
from urllib.request import Request, urlopen

from tests.eval.harness import MetricOutcome, call_with_retries

JEV_DECISIONS_URL = "https://openrouter.ai/api/alpha/decisions"
JEV_DECISION_THRESHOLD = 0.5
JEV_TIMEOUT_SECONDS = 180.0

DecisionRequest = Callable[[str, Mapping[str, Any]], Mapping[str, Any]]


def is_jev_model(model: str) -> bool:
    """Return whether ``model`` names a TypeSafe Jev model."""
    return model.removeprefix("~").startswith("typesafe/jev-")


def _request_decisions(model: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    api_key = os.environ["OPENROUTER_API_KEY"]
    body = json.dumps({"model": model, **payload}).encode()
    request = Request(
        JEV_DECISIONS_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urlopen(request, timeout=JEV_TIMEOUT_SECONDS) as response:  # noqa: S310
        result = json.load(response)
    if not isinstance(result, dict):
        raise ValueError("Jev returned a non-object response")
    return result


def _question(expectation: str) -> dict[str, Any]:
    return {
        "type": "noul",
        "instructions": (
            "Considering only `actual_output`, does it satisfy this expectation "
            f"exactly?\n\n{expectation}"
        ),
        "criteria": {
            "true": "The actual output satisfies the expectation.",
            "false": "The actual output violates or fails to satisfy the expectation.",
        },
    }


def _error_outcomes(
    *,
    must_do: Sequence[str],
    must_not: Sequence[str],
    pass_ratio: float,
    reason: str,
) -> list[MetricOutcome]:
    outcomes = []
    if must_do:
        outcomes.append(
            MetricOutcome(
                name="must_do",
                score=None,
                threshold=pass_ratio,
                reason=f"judge error: {reason}",
                passed=False,
            )
        )
    if must_not:
        outcomes.append(
            MetricOutcome(
                name="must_not",
                score=None,
                threshold=1.0,
                reason=f"judge error: {reason}",
                passed=False,
            )
        )
    return outcomes


def _probability(answers: Mapping[str, Any], question_id: str) -> float:
    answer = answers.get(question_id)
    if not isinstance(answer, Mapping) or answer.get("type") != "noul":
        raise ValueError(f"missing or invalid Jev answer for {question_id!r}")
    value = answer.get("noul")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"invalid Jev probability for {question_id!r}")
    probability = float(value)
    if not 0.0 <= probability <= 1.0:
        raise ValueError(f"Jev probability outside [0, 1] for {question_id!r}")
    return probability


def _reason(
    label: str,
    items: Sequence[str],
    probabilities: Sequence[float],
) -> str:
    rows = []
    for item, probability in zip(items, probabilities, strict=True):
        verdict = "satisfied" if probability >= JEV_DECISION_THRESHOLD else "not satisfied"
        rows.append(f"{verdict} (p={probability:.3f}): {item}")
    return f"Jev {label} decisions at threshold {JEV_DECISION_THRESHOLD:.1f}: " + " | ".join(
        rows
    )


def judge_with_jev(
    *,
    model: str,
    actual_output: str,
    must_do: Sequence[str],
    must_not: Sequence[str],
    pass_ratio: float,
    request_decisions: DecisionRequest = _request_decisions,
) -> list[MetricOutcome]:
    """Evaluate expectations in one Jev Decisions API request."""
    questions = {
        **{f"must_do_{i}": _question(item) for i, item in enumerate(must_do)},
        **{f"must_not_{i}": _question(item) for i, item in enumerate(must_not)},
    }
    try:
        response = call_with_retries(
            lambda: request_decisions(
                model,
                {
                    "state": {"actual_output": actual_output},
                    "questions": questions,
                },
            )
        )
        answers = response.get("answers")
        if not isinstance(answers, Mapping):
            raise ValueError("Jev response has no answers object")
        do_probabilities = [
            _probability(answers, f"must_do_{i}") for i in range(len(must_do))
        ]
        not_probabilities = [
            _probability(answers, f"must_not_{i}") for i in range(len(must_not))
        ]
    except Exception as exc:  # noqa: BLE001 - normalize provider and schema errors
        return _error_outcomes(
            must_do=must_do,
            must_not=must_not,
            pass_ratio=pass_ratio,
            reason=str(exc),
        )

    usage = response.get("usage")
    cost = usage.get("cost") if isinstance(usage, Mapping) else None
    total_cost = float(cost) if isinstance(cost, (int, float)) else None
    question_count = len(questions)

    def group_cost(size: int) -> float | None:
        if total_cost is None or not question_count:
            return None
        return total_cost * size / question_count

    outcomes = []
    if must_do:
        score = sum(
            probability >= JEV_DECISION_THRESHOLD
            for probability in do_probabilities
        ) / len(must_do)
        outcomes.append(
            MetricOutcome(
                name="must_do",
                score=score,
                threshold=pass_ratio,
                reason=_reason("Must-do", must_do, do_probabilities),
                passed=score >= pass_ratio,
                evaluation_cost=group_cost(len(must_do)),
            )
        )
    if must_not:
        passed = all(
            probability >= JEV_DECISION_THRESHOLD
            for probability in not_probabilities
        )
        outcomes.append(
            MetricOutcome(
                name="must_not",
                score=float(passed),
                threshold=1.0,
                reason=_reason("Must-NOT", must_not, not_probabilities),
                passed=passed,
                evaluation_cost=group_cost(len(must_not)),
            )
        )
    return outcomes
