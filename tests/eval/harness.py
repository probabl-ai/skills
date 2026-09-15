"""Load skill-creator evals.json cases and generate a single-turn response."""

from __future__ import annotations

import json
import os
import re
import time
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"
TRANSCRIPT_DIR = REPO_ROOT / ".transcripts"

DEFAULT_TARGET_MODEL = "openrouter/deepseek/deepseek-v4.1-flash"
DEFAULT_JUDGE_MODEL = "openrouter/deepseek/deepseek-v4.1-flash"
DEFAULT_PASS_RATIO = 0.7
MUST_NOT_PREFIX = "The response does NOT"
NO_TOOLS_NOTE = (
    "Harness note: this is a single-turn evaluation. You have no tools this "
    "turn - no shell, no file reads, no scratch scripts. Treat the workspace "
    "state described above as already verified. Do not emit tool calls or "
    "wait for results; give your complete final answer in this message, "
    "filling any checklist from the information given. Put the complete "
    "deliverable in the assistant message, not only in a thinking channel."
)

_PROVIDER_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "azure": "AZURE_API_KEY",
    "gemini": "GOOGLE_API_KEY",
    "vertex_ai": "GOOGLE_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
}


@dataclass(frozen=True)
class EvalCase:
    skill_name: str
    skill_md_path: Path
    case_id: int | str
    title: str
    prompt: str
    expectations: tuple[str, ...]
    tools: bool = False
    sandbox: tuple[dict[str, Any], ...] = ()
    expect_files: tuple[str, ...] = ()
    expect_reads: tuple[str, ...] = ()
    expect_cli: tuple[str, ...] = ()

    @property
    def must_do(self) -> tuple[str, ...]:
        return split_expectations(self.expectations)[0]

    @property
    def must_not(self) -> tuple[str, ...]:
        return split_expectations(self.expectations)[1]


def split_expectations(
    expectations: Sequence[str],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return (must_do, must_not) using the prompts.md negation prefix."""
    must_do: list[str] = []
    must_not: list[str] = []
    for item in expectations:
        if item.startswith(MUST_NOT_PREFIX):
            must_not.append(item)
        else:
            must_do.append(item)
    return tuple(must_do), tuple(must_not)


def compose_user_prompt(prompt: str, *, tools: bool = False) -> str:
    from tests.eval.sandbox import TOOLS_NOTE

    note = TOOLS_NOTE if tools else NO_TOOLS_NOTE
    return f"{prompt.rstrip()}\n\n{note}"


def slugify(text: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug[:max_len].rstrip("-") or "untitled")


def litellm_model_name(model: str) -> str:
    """Accept bare Anthropic/OpenAI ids as well as provider-qualified LiteLLM names."""
    if "/" in model:
        return model
    if model.startswith("claude"):
        return f"anthropic/{model}"
    if model.startswith(("gpt-", "o1", "o3", "o4")):
        return f"openai/{model}"
    if model.startswith("gemini"):
        return f"gemini/{model}"
    return model


def required_api_key_env(model: str) -> str | None:
    provider = litellm_model_name(model).split("/", 1)[0]
    return _PROVIDER_ENV.get(provider)


def load_eval_cases() -> list[EvalCase]:
    cases: list[EvalCase] = []
    for evals_path in sorted(SKILLS_DIR.glob("*/evals/evals.json")):
        skill_dir = evals_path.parent.parent
        data = json.loads(evals_path.read_text(encoding="utf-8"))
        skill_name = data.get("skill_name") or skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        for raw in data.get("evals") or []:
            expectations = tuple(str(item) for item in (raw.get("expectations") or []))
            case_id = raw["id"]
            sandbox = tuple(
                item for item in (raw.get("sandbox") or []) if isinstance(item, dict)
            )
            expect_files = tuple(str(item) for item in (raw.get("expect_files") or []))
            expect_reads = tuple(str(item) for item in (raw.get("expect_reads") or []))
            expect_cli = tuple(str(item) for item in (raw.get("expect_cli") or []))
            cases.append(
                EvalCase(
                    skill_name=skill_name,
                    skill_md_path=skill_md,
                    case_id=case_id,
                    title=str(raw.get("title") or ""),
                    prompt=raw["prompt"],
                    expectations=expectations,
                    tools=bool(raw.get("tools")),
                    sandbox=sandbox,
                    expect_files=expect_files,
                    expect_reads=expect_reads,
                    expect_cli=expect_cli,
                )
            )
    return cases


EVAL_RESULTS: dict[
    str, list[tuple[str, object, str, bool, bool, bool, bool]]
] = defaultdict(list)


def record_eval_result(
    *,
    mode: str,
    case: EvalCase,
    passed: bool,
    judge_error: bool = False,
    skipped: bool = False,
    must_do_weak: bool = False,
) -> None:
    EVAL_RESULTS[mode].append(
        (
            case.skill_name,
            case.case_id,
            case.title,
            passed,
            judge_error,
            skipped,
            must_do_weak,
        )
    )


def require_keys(*models: str) -> None:
    missing: list[str] = []
    seen: set[str] = set()
    for model in models:
        env_name = required_api_key_env(model)
        if env_name and env_name not in seen and not os.environ.get(env_name):
            missing.append(env_name)
            seen.add(env_name)
    if missing:
        pytest.skip("missing API key(s): " + ", ".join(missing))


def case_node_id(case: EvalCase, *, mode: str, model: str) -> str:
    slug = slugify(case.title)
    return f"{case.skill_name}-case{case.case_id}-{slug}-{mode}-{_short_model(model)}"


def _short_model(model: str) -> str:
    return model.rsplit("/", 1)[-1].replace(":", "_")


@dataclass(frozen=True)
class MetricOutcome:
    name: str
    score: float | None
    threshold: float
    reason: str
    passed: bool
    evaluation_cost: float | None = None


def case_hard_pass(
    *,
    outcomes: Sequence[MetricOutcome],
    missing_files: Sequence[str] = (),
    missing_reads: Sequence[str] = (),
    missing_cli: Sequence[str] = (),
) -> tuple[bool, bool, bool]:
    """Return ``(hard_pass, must_do_weak, must_not_judge_error)``.

    Pytest fails only when ``hard_pass`` is false (Must-NOT miss,
    missing sandbox files/reads/cli, or a Must-NOT judge error).
    Must-do below threshold is ``must_do_weak`` and does not fail.
    """
    if missing_files or missing_reads or missing_cli:
        return False, False, False
    by_name = {item.name: item for item in outcomes}
    must_not = by_name.get("must_not")
    must_do = by_name.get("must_do")
    if must_not is not None and must_not.reason.startswith("judge error:"):
        return False, False, True
    if must_not is not None and not must_not.passed:
        return False, False, False
    weak = must_do is not None and not must_do.passed
    return True, weak, False


def format_eval_failure(
    *,
    case: EvalCase,
    target_model: str,
    skill_mode: str,
    actual: str,
    outcomes: Sequence[MetricOutcome],
    transcript: Path | None = None,
    extra: str = "",
) -> str:
    heading = f"{case.skill_name}  case {case.case_id}"
    if case.title:
        heading += f" — {case.title}"
    lines = [
        heading,
        f"mode: {skill_mode}  target: {target_model}",
    ]
    if outcomes:
        width = max(len(item.name) for item in outcomes)
        for item in outcomes:
            score_s = "n/a" if item.score is None else f"{item.score:.2f}"
            verdict = "ok" if item.passed else "FAIL"
            lines.append(
                f"{item.name:<{width}}  {score_s} (threshold {item.threshold:.2f})  {verdict}"
            )
        lines.append("")
        for item in outcomes:
            lines.append(f"{item.name} reason: {item.reason or '(no reason from judge)'}")
    else:
        lines.append("GEval: (not run)")
    if transcript is not None:
        lines.append(f"transcript: {transcript}")
        lines.append(f"transcript_md: {transcript.with_suffix('.md')}")
    if extra:
        lines += ["", extra]
    lines += ["", "Must do:"]
    if case.must_do:
        lines.extend(f"  - {item}" for item in case.must_do)
    else:
        lines.append("  (none)")
    lines += ["", "Must NOT:"]
    if case.must_not:
        lines.extend(f"  - {item}" for item in case.must_not)
    else:
        lines.append("  (none)")
    lines += ["", "--- Response ---", actual or "(empty)"]
    return "\n".join(lines)


@dataclass(frozen=True)
class GenerationResult:
    content: str
    reasoning: str
    finish_reason: str | None
    usage: dict[str, object] = field(default_factory=dict)
    tool_trace: list[dict[str, Any]] = field(default_factory=list)


def new_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_transcript_dirs(run_id: str | None = None) -> Path:
    """Create `.transcripts/` and, when ``run_id`` is set, `<run-id>/`.

    Per-skill directories are created lazily by ``write_transcript``.
    """
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    if run_id is None:
        return TRANSCRIPT_DIR
    session = TRANSCRIPT_DIR / run_id
    session.mkdir(parents=True, exist_ok=True)
    return session


def transcript_path(case: EvalCase, *, run_id: str, mode: str, model: str) -> Path:
    name = f"case{case.case_id}-{mode}-{_short_model(model)}.json"
    return TRANSCRIPT_DIR / run_id / case.skill_name / name


def write_transcript(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    path.with_suffix(".md").write_text(_format_transcript_md(payload), encoding="utf-8")
    return path


def _format_transcript_md(payload: dict) -> str:
    heading = f"{payload.get('skill', '')} case {payload.get('case_id', '')}"
    title = payload.get("title") or ""
    if title:
        heading += f" — {title}"
    lines = [
        f"# {heading}",
        "",
        f"- mode: {payload.get('mode')}",
        f"- tier: {payload.get('tier')}",
        f"- target: {payload.get('target_model')}",
        f"- judge: {payload.get('judge_model')}",
        f"- finish_reason: {payload.get('finish_reason')}",
        f"- judged_from: {payload.get('judged_from')}",
        f"- usage: {payload.get('usage')}",
    ]
    if "passed" in payload:
        lines.append(f"- passed: {payload.get('passed')}")
    if payload.get("skipped"):
        lines.append(f"- skipped: {payload.get('skip_reason')}")
    lines += ["", "## Prompt", "", str(payload.get("prompt") or "").rstrip(), ""]
    note = payload.get("harness_note")
    if note:
        lines += ["## Harness note", "", str(note).rstrip(), ""]
    user = payload.get("user")
    if user:
        lines += ["## User message", "", str(user).rstrip(), ""]
    tools_on = payload.get("tools")
    if tools_on:
        lines += ["## Tools", "", "enabled", ""]
        trace = payload.get("tool_trace") or []
        if trace:
            lines += ["## Tool trace", ""]
            for i, item in enumerate(trace, 1):
                args = item.get("arguments") or {}
                lines.append(f"{i}. `{item.get('name')}` {args}")
                result = str(item.get("result") or "")
                if len(result) > 800:
                    result = result[:800] + "\n…"
                lines += ["", "```", result, "```", ""]
        tree = payload.get("sandbox_tree") or []
        if tree:
            lines += ["## Sandbox tree", ""]
            lines.extend(f"- {name}" for name in tree)
            lines.append("")
    must_do = payload.get("must_do")
    must_not = payload.get("must_not")
    if must_do is None and must_not is None:
        must_do, must_not = split_expectations(payload.get("expectations") or [])
    lines += ["## Must do", ""]
    if must_do:
        lines.extend(f"- {item}" for item in must_do)
    else:
        lines.append("(none)")
    lines += ["", "## Must NOT", ""]
    if must_not:
        lines.extend(f"- {item}" for item in must_not)
    else:
        lines.append("(none)")
    lines += ["", "## Response", "", str(payload.get("content") or "").rstrip() or "(empty)", ""]
    reasoning = str(payload.get("reasoning") or "").rstrip()
    if reasoning:
        lines += ["## Reasoning", "", reasoning, ""]
    metrics = payload.get("metrics") or []
    if metrics:
        lines += ["## Metrics", ""]
        for metric in metrics:
            score = metric.get("score")
            score_s = "n/a" if score is None else f"{float(score):.2f}"
            threshold = metric.get("threshold")
            threshold_s = "" if threshold is None else f"{float(threshold):.2f}"
            verdict = "ok" if metric.get("passed") else "FAIL"
            cost = metric.get("evaluation_cost")
            cost_s = "" if cost is None else f"  cost: {cost}"
            lines += [
                f"### {metric.get('name')}",
                "",
                f"score: {score_s} (threshold {threshold_s})  {verdict}{cost_s}",
                "",
                str(metric.get("reason") or "(no reason from judge)"),
                "",
            ]
    elif payload.get("geval_reason") or payload.get("geval_score") is not None:
        score = payload.get("geval_score")
        score_s = "n/a" if score is None else f"{float(score):.2f}"
        lines += [
            "## Metrics",
            "",
            f"score: {score_s}",
            "",
            str(payload.get("geval_reason") or "(no reason from judge)"),
            "",
        ]
    return "\n".join(lines) + "\n"


_FENCE_RE = re.compile(r"```(?:[^\n`]*)\n.*?```", re.DOTALL)
_REASONING_TAIL_CHARS = 2000
FINAL_NUDGE = (
    "No more tools. Put the complete deliverable in the assistant "
    "message (not only in a thinking channel). Do not emit tool calls."
)
CONTENT_NUDGE = (
    "Put the complete deliverable in the assistant message "
    "(not only in a thinking channel)."
)

_DANGLING_CHECKBOX = re.compile(r"- \[[xX ]?(?!\])\s*$")
_NOW_WRITING = re.compile(
    r"^(now writing|let me now proceed|now proceeding)\b",
    re.IGNORECASE,
)


def died_mid_deliverable(content: str) -> str | None:
    """Return a skip reason if the visible answer clearly truncated.

    Used when the model started a checklist or announced a write and then
    stopped. A complete last line (including a finished ``- [x] …`` row)
    is not a skip.
    """
    text = (content or "").strip()
    if not text:
        return None
    if _DANGLING_CHECKBOX.search(text):
        return "visible answer truncated mid-checklist"
    last = next(
        (line.strip() for line in reversed(text.splitlines()) if line.strip()),
        "",
    )
    last_bare = last.rstrip(":").strip()
    if _NOW_WRITING.match(last_bare):
        return "visible answer stopped before the deliverable"
    if text.count("```") % 2 == 1:
        return "visible answer has an unclosed code fence"
    return None


def _is_xml_only(content: str) -> bool:
    from tests.eval.sandbox import is_tool_xml_only

    return is_tool_xml_only(content)


def visible_text(result: GenerationResult) -> tuple[str, str]:
    """Prefer assistant content; fall back to reasoning if content is empty.

    When only reasoning exists, prefer the last fenced code block plus a
    short tail so the judge scores the deliverable, not the monologue.
    Full reasoning stays on the transcript payload.
    """
    content = (result.content or "").strip()
    if content and not _is_xml_only(content):
        return content, "content"
    reasoning = (result.reasoning or "").strip()
    if not reasoning:
        return "", "empty"
    extracted = _reasoning_deliverable(reasoning)
    return extracted, "reasoning"


def _reasoning_deliverable(reasoning: str) -> str:
    fences = list(_FENCE_RE.finditer(reasoning))
    if not fences:
        return ""
    last = fences[-1]
    extracted = last.group(0)
    tail = reasoning[last.end() :].strip()
    if tail:
        extracted = extracted + "\n\n" + tail[:_REASONING_TAIL_CHARS]
    return extracted


TARGET_TRANSPORT_TIMEOUT = 600.0
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = (1.0, 3.0, 9.0)


def call_with_retries(fn, *, attempts: int = RETRY_ATTEMPTS):
    """Retry ``fn`` on transient failures with exponential backoff."""
    last_exc: BaseException | None = None
    for attempt in range(attempts):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — provider SDKs raise many types
            last_exc = exc
            if attempt >= attempts - 1:
                break
            delay = RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)]
            time.sleep(delay)
    assert last_exc is not None
    raise last_exc


def _usage_dict(response: Any) -> dict[str, object]:
    usage = getattr(response, "usage", None)
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "__dict__"):
        return {k: v for k, v in vars(usage).items() if not k.startswith("_")}
    return {}


def _merge_usage(left: Mapping[str, object], right: Mapping[str, object]) -> dict[str, object]:
    merged = dict(left)
    for key, value in right.items():
        if isinstance(value, (int, float)) and isinstance(merged.get(key), (int, float)):
            merged[key] = merged[key] + value  # type: ignore[operator]
        else:
            merged[key] = value
    return merged


def _assistant_message_dict(message: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "role": getattr(message, "role", None) or "assistant",
        "content": message.content or "",
    }
    tool_calls = getattr(message, "tool_calls", None) or []
    if tool_calls:
        payload["tool_calls"] = [
            {
                "id": getattr(tc, "id", "") or "",
                "type": "function",
                "function": {
                    "name": getattr(getattr(tc, "function", None), "name", "") or "",
                    "arguments": getattr(getattr(tc, "function", None), "arguments", "")
                    or "",
                },
            }
            for tc in tool_calls
        ]
    return payload


def generate_response(*, model: str, system: str, user: str) -> GenerationResult:
    """Call the target with no max_tokens cap so reasoning models can finish."""
    from litellm import completion

    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    def _once():
        return completion(
            model=litellm_model_name(model),
            messages=messages,
            temperature=0,
            timeout=TARGET_TRANSPORT_TIMEOUT,
        )

    response = call_with_retries(_once)
    choice = response.choices[0]
    message = choice.message
    content = message.content or ""
    reasoning = str(getattr(message, "reasoning_content", None) or "")
    finish = getattr(choice, "finish_reason", None)
    usage = _usage_dict(response)
    if not (content or "").strip():
        messages.append(_assistant_message_dict(message))
        messages.append({"role": "user", "content": CONTENT_NUDGE})
        response = call_with_retries(_once)
        usage = _merge_usage(usage, _usage_dict(response))
        choice = response.choices[0]
        message = choice.message
        content = message.content or ""
        reasoning = str(getattr(message, "reasoning_content", None) or "") or reasoning
        finish = getattr(choice, "finish_reason", None)
    return GenerationResult(
        content=content,
        reasoning=reasoning,
        finish_reason=finish,
        usage=usage,
    )


def generate_agent_response(
    *,
    model: str,
    system: str,
    user: str,
    sandbox: Any,
) -> GenerationResult:
    """Multi-turn LiteLLM tool loop against a temp workspace."""
    from litellm import completion

    from tests.eval.sandbox import (
        TOOL_LOOP_CAP,
        TOOL_SCHEMAS,
        is_tool_xml_only,
        parse_tool_arguments,
        parse_xml_tool_calls,
        strip_tool_xml,
    )

    messages: list[dict[str, Any]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})

    usage: dict[str, object] = {}
    tool_trace: list[dict[str, Any]] = []
    last_content = ""
    last_reasoning = ""
    last_finish: str | None = None
    last_prose = ""

    def _complete(*, use_tools: bool) -> Any:
        def _once() -> Any:
            kwargs: dict[str, Any] = {
                "model": litellm_model_name(model),
                "messages": messages,
                "temperature": 0,
                "timeout": TARGET_TRANSPORT_TIMEOUT,
            }
            if use_tools:
                kwargs["tools"] = TOOL_SCHEMAS
            return completion(**kwargs)

        return call_with_retries(_once)

    def _record(message: Any, finish: str | None) -> None:
        nonlocal last_content, last_reasoning, last_finish, last_prose
        last_content = message.content or ""
        last_reasoning = str(getattr(message, "reasoning_content", None) or "")
        last_finish = finish
        prose = strip_tool_xml(last_content)
        if prose:
            last_prose = prose

    def _dispatch_native(message: Any) -> None:
        messages.append(_assistant_message_dict(message))
        for tc in list(getattr(message, "tool_calls", None) or []):
            fn = getattr(tc, "function", None)
            name = getattr(fn, "name", "") or ""
            args = parse_tool_arguments(getattr(fn, "arguments", "") or "")
            result = sandbox.dispatch(name, args)
            tool_trace.append({"name": name, "arguments": args, "result": result[:4000]})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": getattr(tc, "id", "") or "",
                    "content": result,
                }
            )

    def _dispatch_xml(content: str, xml_calls: list[dict[str, Any]], step: int) -> None:
        messages.append({"role": "assistant", "content": content})
        for i, item in enumerate(xml_calls):
            name = str(item.get("name") or "")
            args = item.get("arguments") or {}
            result = sandbox.dispatch(name, args)
            tool_trace.append({"name": name, "arguments": args, "result": result[:4000]})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": f"xml-{step}-{i}",
                    "content": result,
                }
            )

    still_calling_tools = True
    for step in range(TOOL_LOOP_CAP):
        response = _complete(use_tools=True)
        usage = _merge_usage(usage, _usage_dict(response))
        choice = response.choices[0]
        message = choice.message
        _record(message, getattr(choice, "finish_reason", None))
        tool_calls = list(getattr(message, "tool_calls", None) or [])
        xml_calls = [] if tool_calls else parse_xml_tool_calls(last_content)
        if not tool_calls and not xml_calls:
            still_calling_tools = False
            break
        if tool_calls:
            _dispatch_native(message)
        else:
            _dispatch_xml(last_content, xml_calls, step)
        last_finish = "tool_calls"

    if still_calling_tools or is_tool_xml_only(last_content) or not strip_tool_xml(
        last_content
    ):
        if last_prose and is_tool_xml_only(last_content):
            last_content = last_prose
            last_finish = "stop"
        else:
            for _nudge in range(2):
                if _nudge:
                    messages.append(
                        {"role": "assistant", "content": last_content or ""}
                    )
                    messages.append({"role": "user", "content": FINAL_NUDGE})
                response = _complete(use_tools=False)
                usage = _merge_usage(usage, _usage_dict(response))
                choice = response.choices[0]
                message = choice.message
                _record(message, getattr(choice, "finish_reason", None))
                prose = strip_tool_xml(last_content)
                if prose:
                    last_content = prose
                    last_finish = "stop"
                    break
                if last_prose:
                    last_content = last_prose
                    last_finish = "stop"
                    break
            else:
                last_content = last_prose or strip_tool_xml(last_content) or last_content
    else:
        last_content = strip_tool_xml(last_content) or last_content

    return GenerationResult(
        content=last_content,
        reasoning=last_reasoning,
        finish_reason=last_finish,
        usage=usage,
        tool_trace=tool_trace,
    )
