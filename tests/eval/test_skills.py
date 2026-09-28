from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.models import LiteLLMModel
from deepeval.test_case import LLMTestCase, SingleTurnParams

from tests.eval.harness import (
    EvalCase,
    MetricOutcome,
    NO_TOOLS_NOTE,
    call_with_retries,
    case_hard_pass,
    compose_user_prompt,
    died_mid_deliverable,
    format_eval_failure,
    generate_agent_response,
    generate_response,
    litellm_model_name,
    record_eval_result,
    require_keys,
    transcript_path,
    visible_text,
    write_transcript,
)
from tests.eval.jev import is_jev_model, judge_with_jev
from tests.eval.language import (
    merge_must_not,
    partition_language,
    score_user_facing_language,
)
from tests.eval.sandbox import (
    TOOLS_NOTE,
    Sandbox,
    missing_cli,
    missing_reads,
    missing_tools,
)
from tests.eval.tiers import skill_tier


def _judge_model(skill_judge_model: str) -> LiteLLMModel:
    return LiteLLMModel(model=litellm_model_name(skill_judge_model))


def _must_do_metric(items: Sequence[str], *, judge: LiteLLMModel, pass_ratio: float) -> GEval:
    return GEval(
        name="must_do",
        evaluation_steps=[
            "Read the actual output only. Do not reward implied intent.",
            *(f"The actual output must satisfy this expectation: {item}" for item in items),
            "Score = 10 x (fraction of the expectations above that are met), rounded to the nearest integer.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
        rubric=[
            Rubric(
                score_range=(0, 0),
                expected_outcome="None of the Must-do expectations are met.",
            ),
            Rubric(
                score_range=(1, 4),
                expected_outcome="Fewer than half of the Must-do expectations are met.",
            ),
            Rubric(
                score_range=(5, 7),
                expected_outcome="Most Must-do expectations are met, with several misses.",
            ),
            Rubric(
                score_range=(8, 9),
                expected_outcome=(
                    "Almost all Must-do expectations are met; only minor misses remain."
                ),
            ),
            Rubric(
                score_range=(10, 10),
                expected_outcome="Every Must-do expectation is met.",
            ),
        ],
        threshold=pass_ratio,
        strict_mode=False,
        model=judge,
    )


def _must_not_metric(items: Sequence[str], *, judge: LiteLLMModel) -> GEval:
    return GEval(
        name="must_not",
        evaluation_steps=[
            "Read the actual output only. Do not reward implied intent.",
            *(f"The actual output must satisfy this prohibition: {item}" for item in items),
            "Score 1.0 only if every prohibition above is respected; otherwise score 0.0.",
        ],
        evaluation_params=[SingleTurnParams.ACTUAL_OUTPUT],
        threshold=1.0,
        strict_mode=True,
        model=judge,
    )


def _run_metric(metric: GEval, test_case: LLMTestCase) -> MetricOutcome:
    try:
        call_with_retries(lambda: metric.measure(test_case))
    except Exception as exc:
        if type(exc).__name__ == "MissingTestCaseParamsError":
            return MetricOutcome(
                name=metric.name,
                score=None,
                threshold=float(metric.threshold),
                reason=str(exc),
                passed=False,
            )
        return MetricOutcome(
            name=metric.name,
            score=None,
            threshold=float(metric.threshold),
            reason=f"judge error: {exc}",
            passed=False,
        )
    score = metric.score
    threshold = float(metric.threshold)
    # GEval.success can be False even when score meets threshold
    # (non-strict must-do). Trust the numeric score.
    passed = score is not None and float(score) >= threshold
    cost = getattr(metric, "evaluation_cost", None)
    return MetricOutcome(
        name=metric.name,
        score=None if score is None else float(score),
        threshold=threshold,
        reason=str(metric.reason or ""),
        passed=passed,
        evaluation_cost=None if cost is None else float(cost),
    )


def _outcomes_payload(outcomes: Sequence[MetricOutcome]) -> list[dict]:
    return [
        {
            "name": item.name,
            "score": item.score,
            "threshold": item.threshold,
            "reason": item.reason,
            "passed": item.passed,
            "evaluation_cost": item.evaluation_cost,
        }
        for item in outcomes
    ]


@pytest.mark.eval
def test_skill_case(
    eval_case: EvalCase,
    target_model: str,
    skill_mode: str,
    skill_judge_model: str,
    skill_pass_ratio: float,
    eval_run_id: str,
) -> None:
    require_keys(target_model, skill_judge_model)

    if skill_mode == "with":
        if not eval_case.skill_md_path.is_file():
            pytest.skip(f"SKILL.md not found at {eval_case.skill_md_path}")
        system = eval_case.skill_md_path.read_text(encoding="utf-8")
    else:
        system = ""

    user = compose_user_prompt(eval_case.prompt, tools=eval_case.tools)
    path = transcript_path(
        eval_case, run_id=eval_run_id, mode=skill_mode, model=target_model
    )
    payload: dict = {
        "skill": eval_case.skill_name,
        "case_id": eval_case.case_id,
        "title": eval_case.title,
        "mode": skill_mode,
        "tier": skill_tier(eval_case.skill_name),
        "target_model": target_model,
        "judge_model": skill_judge_model,
        "pass_ratio": skill_pass_ratio,
        "prompt": eval_case.prompt,
        "tools": eval_case.tools,
        "harness_note": TOOLS_NOTE if eval_case.tools else NO_TOOLS_NOTE,
        "user": user,
        "expectations": list(eval_case.expectations),
        "must_do": list(eval_case.must_do),
        "must_not": list(eval_case.must_not),
    }

    missing_files: list[str] = []
    missing_reads_list: list[str] = []
    missing_cli_list: list[str] = []
    missing_tools_list: list[str] = []
    if eval_case.tools:
        with TemporaryDirectory(prefix="skill-eval-") as tmp:
            box = Sandbox(Path(tmp))
            box.seed(list(eval_case.sandbox))
            result = generate_agent_response(
                model=target_model,
                system=system,
                user=user,
                sandbox=box,
            )
            missing_files = box.expect_ok(list(eval_case.expect_files))
            missing_reads_list = missing_reads(
                result.tool_trace, list(eval_case.expect_reads)
            )
            missing_cli_list = missing_cli(
                result.tool_trace, list(eval_case.expect_cli)
            )
            missing_tools_list = missing_tools(
                result.tool_trace, list(eval_case.expect_tools)
            )
            payload["sandbox_tree"] = box.list_tree()
    else:
        result = generate_response(
            model=target_model,
            system=system,
            user=user,
        )
    actual, source = visible_text(result)
    skip_reason = died_mid_deliverable(result.content or "")
    if eval_case.tools and result.tool_trace:
        used = "\n".join(
            f"- {item.get('name')} {item.get('arguments')}"
            for item in result.tool_trace
        )
        tree = payload.get("sandbox_tree") or []
        tree_s = "\n".join(f"- {name}" for name in tree)
        actual = (
            f"{actual}\n\n## Harness: tools used\n{used}\n\n"
            f"## Harness: sandbox files\n{tree_s}"
        )
    payload.update(
        {
            "content": result.content,
            "reasoning": result.reasoning,
            "finish_reason": result.finish_reason,
            "usage": result.usage,
            "judged_from": source,
            "tool_trace": result.tool_trace,
            "missing_files": missing_files,
            "missing_reads": missing_reads_list,
            "missing_cli": missing_cli_list,
            "missing_tools": missing_tools_list,
            "skipped": bool(skip_reason),
            "skip_reason": skip_reason,
        }
    )
    write_transcript(path, payload)

    if skip_reason:
        record_eval_result(
            mode=skill_mode, case=eval_case, passed=False, skipped=True
        )
        pytest.skip(skip_reason)

    if not actual:
        record_eval_result(mode=skill_mode, case=eval_case, passed=False)
        pytest.fail(
            format_eval_failure(
                case=eval_case,
                target_model=target_model,
                skill_mode=skill_mode,
                actual="",
                outcomes=(),
                transcript=path,
                extra="The model returned neither content nor reasoning_content.",
            ),
            pytrace=False,
        )

    if not eval_case.expectations:
        passed = (
            not missing_files
            and not missing_reads_list
            and not missing_cli_list
            and not missing_tools_list
        )
        record_eval_result(mode=skill_mode, case=eval_case, passed=passed)
        payload["passed"] = passed
        payload["metrics"] = []
        write_transcript(path, payload)
        if not passed:
            extra_bits = []
            if missing_files:
                extra_bits.append(
                    "Missing expected sandbox files: " + ", ".join(missing_files)
                )
            if missing_reads_list:
                extra_bits.append(
                    "Missing expected read_file paths: "
                    + ", ".join(missing_reads_list)
                )
            if missing_cli_list:
                extra_bits.append(
                    "Missing expected run_skore_skills argv: "
                    + ", ".join(missing_cli_list)
                )
            if missing_tools_list:
                extra_bits.append(
                    "Missing expected tools: " + ", ".join(missing_tools_list)
                )
            pytest.fail(
                format_eval_failure(
                    case=eval_case,
                    target_model=target_model,
                    skill_mode=skill_mode,
                    actual=actual,
                    outcomes=(),
                    transcript=path,
                    extra=" ".join(extra_bits),
                ),
                pytrace=False,
            )
        return

    language_items, other_must_not = partition_language(eval_case.must_not)
    outcomes: list[MetricOutcome]
    if is_jev_model(skill_judge_model):
        outcomes = judge_with_jev(
            model=skill_judge_model,
            actual_output=actual,
            must_do=eval_case.must_do,
            must_not=other_must_not,
            pass_ratio=skill_pass_ratio,
        )
    else:
        test_case = LLMTestCase(input=eval_case.prompt, actual_output=actual)
        judge = _judge_model(skill_judge_model)
        outcomes = []
        if eval_case.must_do:
            outcomes.append(
                _run_metric(
                    _must_do_metric(
                        eval_case.must_do, judge=judge, pass_ratio=skill_pass_ratio
                    ),
                    test_case,
                )
            )
        if other_must_not:
            outcomes.append(
                _run_metric(
                    _must_not_metric(other_must_not, judge=judge), test_case
                )
            )
    if language_items:
        judged_not = next((item for item in outcomes if item.name == "must_not"), None)
        others = [item for item in outcomes if item.name != "must_not"]
        outcomes = others + [
            merge_must_not(score_user_facing_language(actual), judged_not)
        ]

    payload["metrics"] = _outcomes_payload(outcomes)
    hard_pass, must_do_weak, must_not_judge_error = case_hard_pass(
        outcomes=outcomes,
        missing_files=missing_files,
        missing_reads=missing_reads_list,
        missing_cli=missing_cli_list,
        missing_tools=missing_tools_list,
    )
    payload["passed"] = hard_pass
    payload["must_do_weak"] = must_do_weak
    write_transcript(path, payload)

    extra_bits = []
    if missing_files:
        extra_bits.append(
            "Missing expected sandbox files: " + ", ".join(missing_files)
        )
    if missing_reads_list:
        extra_bits.append(
            "Missing expected read_file paths: " + ", ".join(missing_reads_list)
        )
    if missing_cli_list:
        extra_bits.append(
            "Missing expected run_skore_skills argv: " + ", ".join(missing_cli_list)
        )
    if missing_tools_list:
        extra_bits.append(
            "Missing expected tools: " + ", ".join(missing_tools_list)
        )
    extra = " ".join(extra_bits)

    if hard_pass:
        record_eval_result(
            mode=skill_mode,
            case=eval_case,
            passed=True,
            must_do_weak=must_do_weak,
        )
        return

    record_eval_result(
        mode=skill_mode,
        case=eval_case,
        passed=False,
        judge_error=must_not_judge_error,
    )
    pytest.fail(
        format_eval_failure(
            case=eval_case,
            target_model=target_model,
            skill_mode=skill_mode,
            actual=actual,
            outcomes=outcomes,
            transcript=path,
            extra=extra,
        ),
        pytrace=False,
    )
