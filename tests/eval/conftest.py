from __future__ import annotations

import os
from pathlib import Path

import pytest

from tests.eval.harness import (
    DEFAULT_JUDGE_MODEL,
    DEFAULT_PASS_RATIO,
    EVAL_RESULTS,
    case_node_id,
    ensure_transcript_dirs,
    load_eval_cases,
    new_run_id,
)
from tests.eval.tiers import (
    DEFAULT_TIER_MODELS,
    TIER_MODES,
    TIERS,
    models_for_skill,
    parse_tier_models,
    skill_tier,
    split_model_list,
)

VALID_MODES = ("with", "without", "both")


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("skill_eval", "Skill evaluations (DeepEval)")
    group.addoption(
        "--skill-model",
        action="append",
        default=None,
        help=(
            "Target model under test (LiteLLM name, repeatable). "
            "Overrides SKILL_EVAL_MODELS and the tier table."
        ),
    )
    group.addoption(
        "--skill-tier",
        default=None,
        choices=TIER_MODES,
        help=(
            "assigned: each skill on its own tier model; "
            "all: every skill x all three models; "
            "small|medium|big: only skills assigned to that tier. "
            "Overrides SKILL_EVAL_TIER. Ignored when --skill-model or "
            "SKILL_EVAL_MODELS is set."
        ),
    )
    group.addoption(
        "--skill-judge-model",
        default=None,
        help=(
            "Judge model (Jev or a GEval-compatible LiteLLM name). "
            "Overrides SKILL_EVAL_JUDGE_MODEL. "
            f"Default: {DEFAULT_JUDGE_MODEL}."
        ),
    )
    group.addoption(
        "--skill-mode",
        default=None,
        choices=VALID_MODES,
        help=(
            "with: SKILL.md as system prompt; without: empty system; "
            "both: parametrise each case. Overrides SKILL_EVAL_MODE."
        ),
    )
    group.addoption(
        "--skill-pass-ratio",
        default=None,
        help=(
            "Must-do GEval threshold in [0, 1] (diagnostic only; does not "
            "fail the node). Must-NOT stays all-or-nothing. "
            "Overrides SKILL_EVAL_PASS_RATIO. "
            f"Default: {DEFAULT_PASS_RATIO}."
        ),
    )


def pytest_configure(config: pytest.Config) -> None:
    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "YES")
    os.environ.setdefault("DEEPEVAL_UPDATE_WARNING_OPT_OUT", "YES")
    os.environ.setdefault("DEEPEVAL_DISABLE_TIMEOUTS", "YES")
    os.environ.setdefault("SKILL_EVAL_RUN_ID", new_run_id())
    config.addinivalue_line(
        "markers",
        "eval: LLM-backed skill evaluations (opt-in; requires provider API keys)",
    )
    _load_dotenv(config)
    EVAL_RESULTS.clear()
    ensure_transcript_dirs()


@pytest.fixture(scope="session")
def eval_run_id() -> str:
    run_id = os.environ.get("SKILL_EVAL_RUN_ID") or new_run_id()
    ensure_transcript_dirs(run_id)
    return run_id


def _load_dotenv(config: pytest.Config) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = Path(str(config.rootpath)) / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)


def _override_models(config: pytest.Config) -> list[str] | None:
    """CLI --skill-model or SKILL_EVAL_MODELS, else None (use the tier table)."""
    cli = config.getoption("--skill-model")
    if cli:
        return list(cli)
    env = os.environ.get("SKILL_EVAL_MODELS", "").strip()
    if env:
        return split_model_list(env)
    return None


def _tier_models() -> dict[str, str]:
    values = {
        name: os.environ.get(f"SKILL_EVAL_TIER_{name.upper()}", "").strip()
        or DEFAULT_TIER_MODELS[name]
        for name in TIERS
    }
    try:
        return parse_tier_models(values)
    except ValueError as exc:
        raise pytest.UsageError(str(exc)) from exc


def _tier_mode(config: pytest.Config) -> str:
    raw = config.getoption("--skill-tier") or os.environ.get(
        "SKILL_EVAL_TIER", "assigned"
    )
    if raw not in TIER_MODES:
        raise pytest.UsageError(
            f"skill tier must be one of {TIER_MODES}, got {raw!r}"
        )
    return raw


def _judge_model(config: pytest.Config) -> str:
    cli = config.getoption("--skill-judge-model")
    if cli:
        return str(cli)
    return os.environ.get("SKILL_EVAL_JUDGE_MODEL", DEFAULT_JUDGE_MODEL)


def _modes(config: pytest.Config) -> list[str]:
    raw = config.getoption("--skill-mode") or os.environ.get(
        "SKILL_EVAL_MODE", "with"
    )
    if raw not in VALID_MODES:
        raise pytest.UsageError(
            f"skill mode must be one of {VALID_MODES}, got {raw!r}"
        )
    return ["with", "without"] if raw == "both" else [raw]


def _pass_ratio(config: pytest.Config) -> float:
    raw = config.getoption("--skill-pass-ratio")
    if raw is None:
        raw = os.environ.get("SKILL_EVAL_PASS_RATIO", DEFAULT_PASS_RATIO)
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise pytest.UsageError(
            f"skill pass ratio must be a float in [0, 1], got {raw!r}"
        ) from exc
    if not 0.0 <= value <= 1.0:
        raise pytest.UsageError(
            f"skill pass ratio must be in [0, 1], got {value}"
        )
    return value


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "eval_case" not in metafunc.fixturenames:
        return
    cases = load_eval_cases()
    modes = _modes(metafunc.config)
    override = _override_models(metafunc.config)
    if override is not None:
        params = [
            (case, model, mode)
            for case in cases
            for model in override
            for mode in modes
        ]
    else:
        tier_models = _tier_models()
        tier_mode = _tier_mode(metafunc.config)
        params = [
            (case, model, mode)
            for case in cases
            for model in models_for_skill(
                case.skill_name, tier_mode=tier_mode, tier_models=tier_models
            )
            for mode in modes
        ]
    metafunc.parametrize(
        "eval_case,target_model,skill_mode",
        params,
        ids=[
            case_node_id(case, mode=mode, model=model)
            for case, model, mode in params
        ],
    )


@pytest.fixture(scope="session")
def skill_judge_model(pytestconfig: pytest.Config) -> str:
    return _judge_model(pytestconfig)


@pytest.fixture(scope="session")
def skill_pass_ratio(pytestconfig: pytest.Config) -> float:
    return _pass_ratio(pytestconfig)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    workeroutput = getattr(session.config, "workeroutput", None)
    if workeroutput is not None:
        workeroutput["skill_eval_results"] = {
            mode: list(rows) for mode, rows in EVAL_RESULTS.items()
        }


def pytest_testnodedown(node, error) -> None:
    workeroutput = getattr(node, "workeroutput", None)
    if not workeroutput:
        return
    incoming = workeroutput.get("skill_eval_results") or {}
    for mode, rows in incoming.items():
        EVAL_RESULTS[mode].extend(rows)


def pytest_terminal_summary(
    terminalreporter, exitstatus: int, config: pytest.Config
) -> None:
    if getattr(config, "workerinput", None) is not None:
        return
    if not EVAL_RESULTS:
        return
    terminalreporter.write_sep("=", "skill-eval summary")
    counts: dict[str, tuple[int, int, int, int, int]] = {}
    for mode, rows in EVAL_RESULTS.items():
        passed = sum(
            1 for *_, ok, _err, skip, _weak in rows if ok and not skip
        )
        skipped = sum(1 for *_, _ok, _err, skip, _weak in rows if skip)
        weak = sum(
            1
            for *_, ok, _err, skip, must_do_weak in rows
            if ok and not skip and must_do_weak
        )
        errored = sum(
            1 for *_, _ok, err, skip, _weak in rows if err and not skip
        )
        total = len(rows)
        scored = total - skipped
        counts[mode] = (passed, scored, errored, skipped, weak)
        pct = (100 * passed / scored) if scored else 0
        line = f"  {mode:<8s} {passed}/{scored} ({pct:.0f}%)"
        if skipped:
            line += f"  {skipped} skipped"
        if weak:
            line += f"  {weak} must-do-weak"
        if errored:
            line += f"  {errored} judge-error"
        terminalreporter.write_line(line)
    if "with" in counts and "without" in counts:
        with_p, with_t, _, _, _ = counts["with"]
        without_p, without_t, _, _, _ = counts["without"]
        if with_t and without_t:
            delta_pp = (with_p / with_t - without_p / without_t) * 100
            terminalreporter.write_line(f"  delta    {delta_pp:+.0f}pp")

    by_tier: dict[str, list[bool]] = {name: [] for name in TIERS}
    for rows in EVAL_RESULTS.values():
        for skill, _case_id, _title, ok, _err, skip, _weak in rows:
            if skip:
                continue
            by_tier[skill_tier(skill)].append(ok)
    if any(by_tier.values()):
        terminalreporter.write_line("  by tier:")
        for name in TIERS:
            results = by_tier[name]
            if not results:
                continue
            passed = sum(results)
            total = len(results)
            pct = 100 * passed / total
            terminalreporter.write_line(
                f"    {name:<8s} {passed}/{total} ({pct:.0f}%)"
            )

    failed = [
        (mode, skill, case_id, title)
        for mode, rows in EVAL_RESULTS.items()
        for skill, case_id, title, ok, _err, skip, _weak in rows
        if not ok and not skip
    ]
    if failed:
        terminalreporter.write_line("  failed:")
        for mode, skill, case_id, title in failed:
            suffix = f" — {title}" if title else ""
            terminalreporter.write_line(
                f"    [{mode}] {skill} case {case_id}{suffix}"
            )

    weak_rows = [
        (mode, skill, case_id, title)
        for mode, rows in EVAL_RESULTS.items()
        for skill, case_id, title, ok, _err, skip, must_do_weak in rows
        if ok and not skip and must_do_weak
    ]
    if weak_rows:
        terminalreporter.write_line("  must-do-weak (not a fail):")
        for mode, skill, case_id, title in weak_rows:
            suffix = f" — {title}" if title else ""
            terminalreporter.write_line(
                f"    [{mode}] {skill} case {case_id}{suffix}"
            )
