from types import SimpleNamespace

from tests.eval.harness import CONTENT_NUDGE, generate_response


def test_empty_completion_retries_with_reasoning_cap(monkeypatch) -> None:
    """An empty first answer is retried with a low reasoning cap."""
    calls: list[dict[str, object]] = []

    def fake_completion(**kwargs: object) -> SimpleNamespace:
        calls.append(kwargs)
        content = "" if len(calls) == 1 else "the answer"
        message = SimpleNamespace(
            content=content,
            reasoning_content="thought",
            tool_calls=None,
            role="assistant",
        )
        finish = "length" if len(calls) == 1 else "stop"
        choice = SimpleNamespace(message=message, finish_reason=finish)
        return SimpleNamespace(choices=[choice], usage=None)

    monkeypatch.setattr("tests.eval.harness._target_completion", fake_completion)
    result = generate_response(model="example", system="sys", user="hi")

    assert result.content == "the answer"
    assert result.finish_reason == "stop"
    assert "reasoning_effort" not in calls[0]
    assert "max_completion_tokens" not in calls[0]
    assert calls[1]["reasoning_effort"] == "low"
    assert calls[1]["max_completion_tokens"] == 16384
    messages = calls[1]["messages"]
    assert isinstance(messages, list)
    assert messages[-1] == {"role": "user", "content": CONTENT_NUDGE}
