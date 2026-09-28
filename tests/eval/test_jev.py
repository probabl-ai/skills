from __future__ import annotations

from typing import Any

import pytest

from tests.eval.harness import DEFAULT_JUDGE_MODEL, required_api_key_env
from tests.eval.jev import is_jev_model, judge_with_jev


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("~typesafe/jev-latest", True),
        ("typesafe/jev-1.13", True),
        ("openrouter/deepseek/deepseek-v4.1-flash", False),
    ],
)
def test_is_jev_model(model: str, expected: bool) -> None:
    assert is_jev_model(model) is expected


def test_jev_is_default_and_uses_openrouter_key() -> None:
    assert DEFAULT_JUDGE_MODEL == "~typesafe/jev-latest"
    assert required_api_key_env(DEFAULT_JUDGE_MODEL) == "OPENROUTER_API_KEY"
    assert required_api_key_env("typesafe/jev-1.13") == "OPENROUTER_API_KEY"


def test_judge_with_jev_builds_questions_and_maps_outcomes() -> None:
    captured: dict[str, Any] = {}

    def request(model: str, payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(model=model, payload=payload)
        return {
            "answers": {
                "must_do_0": {"type": "noul", "noul": 0.91},
                "must_do_1": {"type": "noul", "noul": 0.49},
                "must_not_0": {"type": "noul", "noul": 0.2},
            },
            "usage": {"cost": 0.012},
        }

    outcomes = judge_with_jev(
        model="~typesafe/jev-latest",
        actual_output="The evaluated answer",
        must_do=("Includes a summary.", "Includes a command."),
        must_not=("The response does NOT invent results.",),
        pass_ratio=0.7,
        request_decisions=request,
    )

    assert captured["model"] == "~typesafe/jev-latest"
    payload = captured["payload"]
    assert payload["state"] == {"actual_output": "The evaluated answer"}
    assert set(payload["questions"]) == {
        "must_do_0",
        "must_do_1",
        "must_not_0",
    }
    assert "Includes a summary." in payload["questions"]["must_do_0"]["instructions"]

    must_do, must_not = outcomes
    assert must_do.name == "must_do"
    assert must_do.score == 0.5
    assert must_do.passed is False
    assert must_do.evaluation_cost == pytest.approx(0.008)
    assert "p=0.490" in must_do.reason
    assert must_not.name == "must_not"
    assert must_not.score == 0.0
    assert must_not.passed is False
    assert must_not.evaluation_cost == pytest.approx(0.004)


def test_judge_with_jev_accepts_probability_at_threshold() -> None:
    def request(model: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "answers": {
                "must_do_0": {"type": "noul", "noul": 0.5},
                "must_not_0": {"type": "noul", "noul": 0.5},
            }
        }

    outcomes = judge_with_jev(
        model="typesafe/jev-1.13",
        actual_output="answer",
        must_do=("Does the work.",),
        must_not=("The response does NOT leak a secret.",),
        pass_ratio=1.0,
        request_decisions=request,
    )

    assert [(outcome.name, outcome.score, outcome.passed) for outcome in outcomes] == [
        ("must_do", 1.0, True),
        ("must_not", 1.0, True),
    ]


def test_judge_with_jev_turns_invalid_response_into_judge_errors() -> None:
    def request(model: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"answers": {"must_do_0": {"type": "choice", "choice": "yes"}}}

    outcomes = judge_with_jev(
        model="typesafe/jev-1.13",
        actual_output="answer",
        must_do=("Does the work.",),
        must_not=("The response does NOT leak a secret.",),
        pass_ratio=0.7,
        request_decisions=request,
    )

    assert [outcome.name for outcome in outcomes] == ["must_do", "must_not"]
    assert all(outcome.score is None for outcome in outcomes)
    assert all(outcome.reason.startswith("judge error:") for outcome in outcomes)
