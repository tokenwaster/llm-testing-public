"""Claude subscription usage-limit handling.

When the 5-hour / daily / weekly cap is hit, the CLI adapter must flag it as a
distinct non-retryable `usage_limit` error, and the runner must abandon the
current task UNSCORED and raise UsageLimitReached (so run_model can pause the
run cleanly and a re-run after the reset fills the gap) — never retry the wall
or write a fake zero.
"""
import json
from types import SimpleNamespace

import pytest

from harness import adapters
from harness.adapters import AdapterError, ClaudeCLIAdapter, _detect_usage_limit
from harness.runner import TaskRunner, UsageLimitReached



def test_detect_real_session_limit_message():
    ok, reset, hint = _detect_usage_limit(
        "claude CLI failed (exit 1): You've hit your session limit "
        "∙ resets 2:50am (America/Chicago)")
    assert ok
    assert reset is None
    assert hint == "resets 2:50am (America/Chicago)"


def test_detect_classic_format_with_epoch():
    ok, reset, hint = _detect_usage_limit("Claude AI usage limit reached|1730000000")
    assert ok and reset == 1730000000.0


def test_detect_ms_epoch_normalised_to_seconds():
    ok, reset, _ = _detect_usage_limit("usage limit reached|1730000000000")
    assert ok and reset == 1730000000.0


def test_detect_prose_variants_without_epoch():
    for msg in ["You've reached your usage limit for now",
                "5-hour limit — try again later",
                "Weekly limit reached"]:
        ok, reset, _ = _detect_usage_limit(msg)
        assert ok and reset is None, msg


def test_ordinary_error_is_not_a_limit():
    ok, reset, hint = _detect_usage_limit("claude CLI failed: connection reset")
    assert not ok and reset is None and hint == ""



def test_parse_result_raises_usage_limit():
    event = {"is_error": True,
             "result": "Claude AI usage limit reached|1730000000"}
    with pytest.raises(AdapterError) as ei:
        ClaudeCLIAdapter._parse_result(None, event, 0.0)
    assert ei.value.kind == "usage_limit"
    assert ei.value.retryable is False
    assert ei.value.reset_at == 1730000000.0


def test_parse_result_raises_on_real_session_limit():
    event = {"is_error": True,
             "result": "You've hit your session limit ∙ resets 2:50am (America/Chicago)"}
    with pytest.raises(AdapterError) as ei:
        ClaudeCLIAdapter._parse_result(None, event, 0.0)
    assert ei.value.kind == "usage_limit" and ei.value.retryable is False
    assert "2:50am" in ei.value.reset_hint


def test_parse_result_other_failure_stays_retryable_api():
    with pytest.raises(AdapterError) as ei:
        ClaudeCLIAdapter._parse_result(None, {"is_error": True,
                                              "result": "some transient boom"}, 0.0)
    assert ei.value.kind == "api" and ei.value.retryable is True



class _LimitAdapter:
    def __init__(self, reset_at):
        self.reset_at = reset_at
        self.calls = 0

    def chat(self, *a, **k):
        self.calls += 1
        raise AdapterError("Claude subscription usage limit reached",
                           kind="usage_limit", retryable=False,
                           reset_at=self.reset_at)


class _FlakyAdapter:
    def __init__(self):
        self.calls = 0

    def chat(self, *a, **k):
        self.calls += 1
        raise AdapterError("boom", kind="timeout", retryable=True)


def _runner(tmp_path, adapter):
    r = TaskRunner.__new__(TaskRunner)
    r.run_dir = tmp_path
    r.model = SimpleNamespace(name="claude-x")
    r.adapter = adapter
    r.cancel = None
    return r


def test_chat_with_retries_raises_usage_limit_without_retrying(tmp_path):
    adapter = _LimitAdapter(reset_at=1730000000.0)
    r = _runner(tmp_path, adapter)
    task = SimpleNamespace(max_retries=3, timeout_s=10)
    with pytest.raises(UsageLimitReached) as ei:
        r._chat_with_retries(tmp_path, task, [{"role": "user", "content": "hi"}],
                             "sys", None, [])
    assert ei.value.reset_at == 1730000000.0
    assert adapter.calls == 1


def test_chat_with_retries_still_retries_transient(tmp_path):
    adapter = _FlakyAdapter()
    r = _runner(tmp_path, adapter)
    task = SimpleNamespace(max_retries=2, timeout_s=10)
    orig = adapters
    import harness.runner as runner_mod
    runner_mod.time.sleep = lambda *_: None
    out = r._chat_with_retries(tmp_path, task, [{"role": "user", "content": "hi"}],
                               "sys", None, [])
    assert out is None
    assert adapter.calls == 3



class _SucceedThenLimit:
    """Succeeds on the first `succeed` calls, then hits the subscription cap."""
    def __init__(self, reset_at, succeed=1):
        self.reset_at = reset_at
        self.succeed = succeed
        self.calls = 0

    def chat(self, *a, **k):
        self.calls += 1
        if self.calls <= self.succeed:
            from harness.adapters import ChatResult
            return ChatResult(text="ANSWER: 4", total_ms=5.0, ttft_ms=1.0,
                              tokens_in=3, tokens_out=2, stop_reason="stop")
        raise AdapterError("Claude AI usage limit reached|1730000000",
                           kind="usage_limit", retryable=False,
                           reset_at=self.reset_at)


def test_run_model_drops_task_preserves_completed_and_annotates(tmp_path, monkeypatch):
    """A claude run whose 2nd task hits the cap: task 1 completes and is saved,
    task 2 leaves NO score.json, task 3 never starts, and the run manifest
    records the pause + reset time."""
    from harness import runner as R
    from harness.util import write_json, read_json

    run_dir = tmp_path / "run1"
    model = SimpleNamespace(name="claude-x", local=False, provider="claude-cli",
                            supports_tools=False, base_url="")

    def mk_task(tid):
        return SimpleNamespace(id=tid, tier=1, category="reasoning",
                               content_hash="h", max_retries=1, timeout_s=10,
                               setup_dir=None, scoring_type="answer",
                               scoring={"answer": "4", "match": "exact"},
                               prompt="What is 2+2?", max_turns=1)
    tasks = [mk_task("t1-done"), mk_task("t2-limit"), mk_task("t3-never")]

    run_dir.mkdir(parents=True)
    write_json(run_dir / "run.json", {"run_id": "run1", "finished": None,
                                      "models": ["claude-x"]})

    monkeypatch.setattr(R, "make_adapter",
                        lambda m: _SucceedThenLimit(reset_at=1730000000.0, succeed=1))
    logs = []
    R.run_model(run_dir, model, tasks, progress=logs.append, manage_memory=False)

    t1 = run_dir / "claude-x" / "t1-done"
    assert (t1 / "score.json").exists()
    assert not (run_dir / "claude-x" / "t2-limit" / "score.json").exists()
    assert not (run_dir / "claude-x" / "t3-never").exists()
    mani = read_json(run_dir / "run.json", {})
    assert mani["stopped_reason"] == "usage_limit"
    assert mani["reset_at"] == 1730000000.0
    assert "claude-x" in mani["stopped_models"]
    assert any("usage limit reached" in ln.lower() for ln in logs)



def test_resolves_the_answering_model_not_the_helper():
    mu = {"claude-haiku-4-5-20251001": {"outputTokens": 11, "costUSD": 0.00056},
          "claude-sonnet-4-6": {"outputTokens": 4, "costUSD": 0.0769}}
    assert adapters._resolve_served_model(mu, "sonnet") == "claude-sonnet-4-6"


def test_falls_back_to_the_priciest_when_the_alias_doesnt_match():
    mu = {"claude-haiku-4-5": {"costUSD": 0.001},
          "claude-opus-4-8": {"costUSD": 0.90}}
    assert adapters._resolve_served_model(mu, "mystery") == "claude-opus-4-8"


def test_single_entry_and_empty():
    assert adapters._resolve_served_model({"claude-fable-5": {}}, "x") == "claude-fable-5"
    assert adapters._resolve_served_model({}, "sonnet") is None
    assert adapters._resolve_served_model(None, "sonnet") is None



def test_spiral_aborts_when_no_text_is_ever_emitted(monkeypatch):
    """Only thinking events, never an assistant message -> stop at the cutoff."""
    import harness.adapters as A

    class _FakeProc:
        returncode = None
        pid = 999_999_999
        def __init__(self): self.stdin = _Sink(); self.stdout = _ThinkForever()
        def poll(self): return None
        def kill(self): self.returncode = -9
        def wait(self, timeout=None): return -9

    class _Sink:
        def write(self, *_): pass
        def close(self): pass

    class _ThinkForever:
        def __iter__(self): return self
        def __next__(self):
            return '{"type":"system","subtype":"thinking_tokens"}\n'

    import subprocess as _sp
    monkeypatch.setattr(_sp, "Popen", lambda *a, **k: _FakeProc())
    monkeypatch.setattr(_sp, "run", lambda *a, **k: None)
    ticks = iter([0.0, 1000.0, 2000.0, 3000.0, 4000.0] * 50)
    monkeypatch.setattr(A, "now_ms", lambda: next(ticks))

    with pytest.raises(AdapterError) as ei:
        A._stream_claude_cli(["claude", "-p", "--output-format", "json"],
                             "hi", ".", timeout_s=9999, spiral_s=1)
    assert ei.value.kind == "rumination_spiral"
    assert ei.value.retryable is False


def test_stream_cmd_switches_to_stream_json():
    """The runner passes --output-format json; streaming needs stream-json +
    --verbose, or the CLI stays silent until it exits and we're blind again."""
    import subprocess as _sp
    captured = {}

    class _P:
        returncode = 0
        def __init__(self, cmd, **k):
            captured["cmd"] = cmd
            self.stdin = type("S", (), {"write": lambda *_: None,
                                        "close": lambda *_: None})()
            self.stdout = iter(['{"type":"result","subtype":"success",'
                                '"result":"hi","usage":{}}\n'])
        def poll(self): return 0
        def kill(self): pass
        def wait(self, timeout=None): return 0

    import harness.adapters as A
    _orig = _sp.Popen
    _sp.Popen = _P
    try:
        out = A._stream_claude_cli(["claude", "-p", "--output-format", "json"],
                                   "hi", ".", timeout_s=60, spiral_s=60)
    finally:
        _sp.Popen = _orig
    assert "stream-json" in captured["cmd"]
    assert "--verbose" in captured["cmd"]
    assert "json" not in [c for c in captured["cmd"] if c == "json"]
    assert out["result"] == "hi"


def test_terminate_tree_kills_spinning_grandchild():
    """The 'fan keeps roaring after the run' bug: `claude` spawns a tree of
    workers, and a plain proc.kill() (TerminateProcess on Windows) reaps ONLY
    the top process — a busy-looping grandchild survives and pegs a core.
    _terminate_tree must take out the whole subtree."""
    import ctypes
    import subprocess
    import sys
    import time

    from harness.adapters import _terminate_tree

    spin = "import time\nt=time.time()\nwhile time.time()-t < 20:\n    pass\n"
    parent_code = (
        "import subprocess,sys,time\n"
        f"c=subprocess.Popen([sys.executable,'-c',{spin!r}])\n"
        "print('GC',c.pid,flush=True)\n"
        "time.sleep(20)\n"
    )
    proc = subprocess.Popen([sys.executable, "-c", parent_code],
                            stdout=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        gc_pid = int(proc.stdout.readline().split()[1])
        time.sleep(0.5)
        _terminate_tree(proc)
        proc.wait(timeout=10)
        time.sleep(0.5)

        if sys.platform == "win32":
            h = ctypes.windll.kernel32.OpenProcess(0x1000, False, gc_pid)
            if h:
                code = ctypes.c_ulong()
                ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(code))
                ctypes.windll.kernel32.CloseHandle(h)
                if code.value == 259:
                    subprocess.run(["taskkill", "/F", "/PID", str(gc_pid)],
                                   capture_output=True)
                    pytest.fail("grandchild survived _terminate_tree")
        else:
            import os
            try:
                os.kill(gc_pid, 0)
                os.kill(gc_pid, 9)
                pytest.fail("grandchild survived _terminate_tree")
            except ProcessLookupError:
                pass
    finally:
        _terminate_tree(proc)
