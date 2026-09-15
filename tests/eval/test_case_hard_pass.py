from tests.eval.harness import MetricOutcome, case_hard_pass


def _must(*, passed: bool, reason: str = "") -> MetricOutcome:
    return MetricOutcome(
        name="must_not",
        score=1.0 if passed else 0.0,
        threshold=1.0,
        reason=reason,
        passed=passed,
    )


def _do(*, passed: bool, reason: str = "") -> MetricOutcome:
    return MetricOutcome(
        name="must_do",
        score=0.5 if not passed else 1.0,
        threshold=0.7,
        reason=reason,
        passed=passed,
    )


def test_must_do_fail_does_not_fail_the_node() -> None:
    hard, weak, judge_err = case_hard_pass(
        outcomes=[_do(passed=False), _must(passed=True)]
    )
    assert hard is True
    assert weak is True
    assert judge_err is False


def test_must_not_fail_fails_the_node() -> None:
    hard, weak, judge_err = case_hard_pass(
        outcomes=[_do(passed=True), _must(passed=False)]
    )
    assert hard is False
    assert weak is False
    assert judge_err is False


def test_must_not_judge_error_fails_the_node() -> None:
    hard, weak, judge_err = case_hard_pass(
        outcomes=[
            _do(passed=True),
            _must(passed=False, reason="judge error: timeout"),
        ]
    )
    assert hard is False
    assert judge_err is True


def test_must_do_judge_error_is_weak_not_fail() -> None:
    hard, weak, judge_err = case_hard_pass(
        outcomes=[
            _do(passed=False, reason="judge error: timeout"),
            _must(passed=True),
        ]
    )
    assert hard is True
    assert weak is True
    assert judge_err is False


def test_missing_files_fail_even_if_metrics_pass() -> None:
    hard, weak, judge_err = case_hard_pass(
        outcomes=[_do(passed=True), _must(passed=True)],
        missing_files=["scratch/api/skore/evaluate.md"],
    )
    assert hard is False
    assert weak is False
    assert judge_err is False


def test_missing_cli_fail_even_if_metrics_pass() -> None:
    hard, weak, judge_err = case_hard_pass(
        outcomes=[_do(passed=True), _must(passed=True)],
        missing_cli=["api get sklearn.model_selection.KFold"],
    )
    assert hard is False
    assert weak is False
    assert judge_err is False


def test_both_pass_is_clean() -> None:
    hard, weak, judge_err = case_hard_pass(
        outcomes=[_do(passed=True), _must(passed=True)]
    )
    assert (hard, weak, judge_err) == (True, False, False)
