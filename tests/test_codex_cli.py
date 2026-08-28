"""codex-cli provider: the ChatGPT subscription avenue, built like claude-cli."""
import pytest

from harness import adapters, apicost, budget
from harness.adapters import AdapterError, CodexCLIAdapter
from harness.registry import Model


def _model(**kw):
    base = dict(name="codex-cli-gpt-5.6-sol", provider="codex-cli",
                model="gpt-5.6-sol", local=False, stream=False,
                supports_tools=False, max_tokens=65536, temperature=None)
    base.update(kw)
    return Model(**base)


def _adapter(**kw):
    a = CodexCLIAdapter.__new__(CodexCLIAdapter)
    a.model = _model(**kw)
    return a


def test_parse_collects_agent_messages_and_usage():
    data = {"_texts": ["I'll work it out.", "ANSWER: 42"], "_commands_run": 0,
            "_first_text_ms": 120.0, "_error": None,
            "usage": {"input_tokens": 22384, "cached_input_tokens": 9984,
                      "cache_write_input_tokens": 0, "output_tokens": 374,
                      "reasoning_output_tokens": 84}}
    r = _adapter()._parse_result(data, 900.0)
    assert r.text == "I'll work it out.\n\nANSWER: 42"
    assert r.tokens_in == 22384 and r.tokens_out == 374
    assert r.reasoning_tokens == 84 and r.cache_read_tokens == 9984
    assert r.first_text_ms == 120.0 and r.stop_reason == "end_turn"


def test_output_budget_is_enforced_post_hoc_like_claude():
    data = {"_texts": ["x" * 4000], "_commands_run": 0, "_first_text_ms": 1.0,
            "_error": None, "usage": {"input_tokens": 10, "output_tokens": 900}}
    r = _adapter(max_tokens=500)._parse_result(data, 1.0)
    assert r.over_cap_tokens == 900 and r.tokens_out == 500
    assert r.stop_reason == "length" and len(r.text) < 4000


def test_usage_limit_wording_pauses_the_model():
    data = {"_texts": [], "_commands_run": 0, "_first_text_ms": None,
            "usage": None, "_error": "You've hit your usage limit. Limit resets Tue 9:00"}
    with pytest.raises(AdapterError) as ei:
        _adapter()._parse_result(data, 1.0)
    assert ei.value.kind == "usage_limit" and not ei.value.retryable


def test_other_errors_stay_retryable_api():
    data = {"_texts": [], "_commands_run": 0, "_first_text_ms": None,
            "usage": None, "_error": "stream disconnected"}
    with pytest.raises(AdapterError) as ei:
        _adapter()._parse_result(data, 1.0)
    assert ei.value.kind == "api" and ei.value.retryable


def test_a_command_that_executed_fails_the_text_only_attempt(monkeypatch):
    monkeypatch.setattr(adapters, "_codex_exe", lambda: "codex.exe")
    monkeypatch.setattr(adapters, "_stream_codex_cli",
                        lambda cmd, prompt, cwd, t: {
                            "_texts": ["1337"], "_commands_run": 1,
                            "_first_text_ms": 5.0, "_error": None,
                            "usage": {"input_tokens": 1, "output_tokens": 1}})
    with pytest.raises(AdapterError) as ei:
        _adapter().chat([{"role": "user", "content": "compute"}], timeout_s=5)
    assert ei.value.kind == "tool_use" and not ei.value.retryable


def test_text_only_command_line_locks_the_sandbox_down(monkeypatch):
    seen = {}
    monkeypatch.setattr(adapters, "_codex_exe", lambda: "codex.exe")

    def fake(cmd, prompt, cwd, t):
        seen["cmd"], seen["prompt"] = cmd, prompt
        return {"_texts": ["ok"], "_commands_run": 0, "_first_text_ms": 1.0,
                "_error": None, "usage": {"input_tokens": 1, "output_tokens": 1}}
    monkeypatch.setattr(adapters, "_stream_codex_cli", fake)
    _adapter(effort="high").chat([{"role": "user", "content": "hi"}],
                                 system="be brief", timeout_s=5)
    cmd = seen["cmd"]
    assert cmd[1:3] == ["exec", "--json"]
    assert "--ignore-user-config" in cmd and "--ephemeral" in cmd
    assert cmd[cmd.index("-s") + 1] == "read-only"
    assert cmd[cmd.index("-m") + 1] == "gpt-5.6-sol"
    assert 'model_reasoning_effort="high"' in cmd
    assert 'shell_environment_policy.inherit="none"' in cmd
    assert 'web_search="disabled"' in cmd
    for feat in ("browser_use", "computer_use", "apps", "multi_agent"):
        assert feat in cmd
    assert cmd[-1] == "-", "the prompt goes over stdin (213k-char ledgers)"
    assert seen["prompt"].startswith("be brief\n\nhi")


def test_registry_treats_codex_as_a_subscription_cli():
    m = _model()
    assert m.is_cli and m.effort_settable and not m.sampling_settable
    assert "minimal" in m.effort_levels and "max" not in m.effort_levels
    assert "Codex CLI" in m.unsettable_reason
    assert apicost.PROVIDER_AVENUE["codex-cli"] == "cli"
    assert apicost._usable(m)
    assert "codex-cli" in budget.NO_BALANCE_API
    assert adapters.ADAPTERS["codex-cli"] is CodexCLIAdapter


def test_effort_is_validated_against_the_codex_levels():
    from harness.validate import validate_models
    bad = _model(effort="max", source_file="x.yaml")
    msgs = validate_models([bad])
    assert any("not a level the CLI accepts (codex-cli)" in m for m in msgs)
    assert not validate_models([_model(effort="xhigh", source_file="x.yaml")])


def test_the_bundled_exe_is_found_when_not_on_path(monkeypatch, tmp_path):
    import shutil
    exe_dir = tmp_path / "OpenAI" / "Codex" / "bin" / "abc123"
    exe_dir.mkdir(parents=True)
    (exe_dir / "codex.exe").write_bytes(b"")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("CODEX_EXE", raising=False)
    monkeypatch.setattr(shutil, "which", lambda n: None)
    assert adapters._codex_exe() == str(exe_dir / "codex.exe")


def test_blocked_command_attempts_are_counted_not_hidden():
    """sol tried to run code on ctx-014 several times (the sandbox blocked
    each one) and answered from reasoning; the cell must say so."""
    data = {"_texts": ["ANSWER: 1"], "_commands_run": 0, "_commands_blocked": 4,
            "_first_text_ms": 1.0, "_error": None,
            "usage": {"input_tokens": 232427, "output_tokens": 2970}}
    r = _adapter()._parse_result(data, 1.0)
    assert r.tool_attempts == 4
