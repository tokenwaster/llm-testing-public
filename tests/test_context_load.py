"""Local models must load with full GPU offload and a batch-sized context.

Two bugs made gemma-4-31b crawl at 8 tok/s on a 32GB card with VRAM to spare:
  1. `lms load` defaulted to "auto" GPU offload, which left layers on the CPU
     even with GBs free — 17% GPU util. Forcing "--gpu max" -> 82% util, 57 tok/s.
  2. One 128k-context task made the whole run load a 205k window (37GB), so even
     "--gpu max" couldn't fit it and it spilled. Grouping tasks by the context
     they need keeps the short ones in a window that fits, so only the genuine
     long-context tasks pay the cost.
"""

from harness import lmstudio
from harness.runner import (_bucket_offload, context_buckets, _ctx_bucket,
                            load_plan)

_SMALL_FP = {"weights_gb": 5.0, "kv_fixed_gb": 0.1, "kv_per_tok_gb": 4e-05}
_BIG_FP = {"weights_gb": 18.7, "kv_fixed_gb": 1.68, "kv_per_tok_gb": 8.2e-05}


def test_load_plan_coalesces_a_small_model_to_one_load():
    m = _M()
    tasks = [_T("short", 200), _T("mid", 40000), _T("long", 128000)]
    plan = load_plan(m, tasks, _SMALL_FP, 32607)
    assert len(plan) == 1
    ctx, off, g = plan[0]
    assert off == "max" and len(g) == 3


def test_load_plan_keeps_overflow_separate_on_a_big_model():
    m = _M()
    tasks = [_T("short", 200), _T("big", 180000)]
    plan = load_plan(m, tasks, _BIG_FP, 32607)
    by_off = {off: g for _c, off, g in plan}
    assert set(by_off) == {"max", "auto"}
    assert [t.id for t in by_off["max"]] == ["short"]
    assert [t.id for t in by_off["auto"]] == ["big"]


def test_load_plan_all_auto_and_uncoalesced_when_unmeasurable():
    m = _M()
    tasks = [_T("a", 200), _T("b", 120000)]
    plan = load_plan(m, tasks, None, None)
    assert all(off == "auto" for _c, off, _g in plan)

_FP = {"weights_gb": 18.7, "kv_fixed_gb": 1.68, "kv_per_tok_gb": 8.192e-05}


def test_offload_is_max_when_it_fits():
    assert _bucket_offload(_FP, 49152, 32607) == "max"


def test_offload_is_auto_when_it_overflows():
    assert _bucket_offload(_FP, 212992, 32607) == "auto"


def test_offload_defaults_to_auto_when_unmeasurable():
    assert _bucket_offload(_FP, 49152, None) == "auto"
    assert _bucket_offload(None, 49152, 32607) == "auto"


class _M:
    def __init__(self, max_tokens=32768, context_length=0):
        self.max_tokens = max_tokens
        self.context_length = context_length


class _T:
    def __init__(self, tid, prompt_tokens):
        self.id = tid
        self.prompt = "x" * (prompt_tokens * 3)



def test_short_tasks_share_one_small_bucket():
    m = _M()
    tasks = [_T(f"t{i}", 200) for i in range(10)]
    buckets = context_buckets(m, tasks)
    assert len(buckets) == 1
    ctx, group = buckets[0]
    assert len(group) == 10
    assert ctx == 49152


def test_a_long_context_task_gets_its_own_larger_bucket():
    m = _M()
    tasks = [_T("short", 200), _T("long", 128000)]
    buckets = context_buckets(m, tasks)
    assert len(buckets) == 2
    assert buckets[0][0] < buckets[1][0]
    assert buckets[0][1][0].id == "short"
    assert buckets[1][1][0].id == "long"
    assert buckets[1][0] > 160000


def test_every_task_lands_in_exactly_one_bucket():
    m = _M()
    tasks = [_T(f"t{i}", n) for i, n in enumerate([200, 300, 16000, 32000, 64000, 128000])]
    ids = [t.id for _c, g in context_buckets(m, tasks) for t in g]
    assert sorted(ids) == sorted(t.id for t in tasks)
    assert len(ids) == len(set(ids))


def test_yaml_context_cap_bounds_every_bucket():
    m = _M(context_length=65536)
    tasks = [_T("huge", 200000)]
    ctx, _g = context_buckets(m, tasks)[0]
    assert ctx == 65536


def test_bucket_rounds_up_to_16k_chunks():
    assert _ctx_bucket(1) == 16384
    assert _ctx_bucket(16384) == 16384
    assert _ctx_bucket(16385) == 32768
    assert _ctx_bucket(50000) == 65536



def test_load_model_forces_full_gpu_offload(monkeypatch):
    captured = {}

    class _Res:
        timed_out = False
        returncode = 0
        stdout = stderr = ""

    monkeypatch.setattr(lmstudio, "lms_exe", lambda: "lms.exe")
    def _fake(cmd, *a, **k):
        captured["cmd"] = cmd
        return _Res()
    monkeypatch.setattr(lmstudio, "run_capped", _fake)
    lmstudio.load_model("some/model", context_length=49152)
    cmd = captured["cmd"]
    assert "--gpu" in cmd and cmd[cmd.index("--gpu") + 1] == "max"
    assert "--context-length" in cmd and cmd[cmd.index("--context-length") + 1] == "49152"


def test_auto_offload_omits_the_gpu_flag(monkeypatch):
    captured = {}

    class _Res:
        timed_out = False
        returncode = 0
        stdout = stderr = ""

    monkeypatch.setattr(lmstudio, "lms_exe", lambda: "lms.exe")

    def _fake(cmd, *a, **k):
        captured["cmd"] = cmd
        return _Res()
    monkeypatch.setattr(lmstudio, "run_capped", _fake)
    lmstudio.load_model("some/model", context_length=212992, gpu_offload="auto")
    assert "--gpu" not in captured["cmd"], "auto must omit --gpu, not pass 'auto'"
    assert "--context-length" in captured["cmd"]


def test_gpu_offload_is_overridable(monkeypatch):
    captured = {}

    class _Res:
        timed_out = False
        returncode = 0
        stdout = stderr = ""

    monkeypatch.setattr(lmstudio, "lms_exe", lambda: "lms.exe")
    def _fake(cmd, *a, **k):
        captured["cmd"] = cmd
        return _Res()
    monkeypatch.setattr(lmstudio, "run_capped", _fake)
    lmstudio.load_model("some/model", gpu_offload="0.5")
    assert captured["cmd"][captured["cmd"].index("--gpu") + 1] == "0.5"
