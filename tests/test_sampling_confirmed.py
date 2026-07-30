import textwrap

from harness import config, lmstudio
from harness.util import write_json

LOG = """\
[2026-07-26 12:00:00][INFO] Server started
[2026-07-26 12:00:01][DEBUG] Received request: POST to /v1/chat/completions with body {
  "model": "m-local",
  "messages": [
    {
      "role": "user",
      "content": "Build a thing ... <Truncated in logs> ... and stop."
    }
  ],
  "max_tokens": 32768,
  "temperature": 0.85,
  "top_p": 0.95,
  "min_p": 0,
  "repetition_penalty": 1,
  "stream": true,
  "stream_options": {
    "include_usage": true
  }
}
[2026-07-26 12:00:02][INFO] Streaming response...
"""


def _log(tmp_path, monkeypatch, text=LOG, name="2026-07-26.1.log"):
    d = tmp_path / "server-logs" / "2026-07"
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(text, encoding="utf-8")
    monkeypatch.setattr(lmstudio, "SERVER_LOG_DIR", tmp_path / "server-logs")


def test_the_parser_reads_the_body_and_its_clock(tmp_path, monkeypatch):
    _log(tmp_path, monkeypatch)
    reqs = lmstudio.received_requests()
    assert len(reqs) == 1
    r = reqs[0]
    assert r["model"] == "m-local"
    assert r["ts"].isoformat() == "2026-07-26T12:00:01"
    assert r["body"]["temperature"] == 0.85
    assert r["body"]["max_tokens"] == 32768
    assert "Truncated in logs" in r["body"]["messages"][0]["content"]


def test_days_filter_limits_which_logs_are_read(tmp_path, monkeypatch):
    _log(tmp_path, monkeypatch)
    assert lmstudio.received_requests({"2026-07-26"})
    assert lmstudio.received_requests({"2026-07-01"}) == []


def test_an_interrupted_block_is_dropped_not_guessed(tmp_path, monkeypatch):
    cut = LOG.split('  "max_tokens"')[0] + "[2026-07-26 12:00:02][INFO] boom\n"
    _log(tmp_path, monkeypatch, cut)
    assert lmstudio.received_requests() == []


def test_a_log_over_the_size_cap_is_skipped(tmp_path, monkeypatch):
    _log(tmp_path, monkeypatch)
    monkeypatch.setattr(lmstudio, "_LOG_READ_CAP", 10)
    assert lmstudio.received_requests() == []



def test_json_ints_and_floats_compare_equal():
    assert lmstudio._match({"repetition_penalty": 1.0}, {"repetition_penalty": 1}) == []
    assert lmstudio._match({"min_p": 0.0}, {"min_p": 0}) == []


def test_a_changed_value_is_reported():
    diffs = lmstudio._match({"temperature": 0.85}, {"temperature": 0.2})
    assert diffs and "sent 0.85" in diffs[0] and "received 0.2" in diffs[0]


def test_a_value_that_never_arrived_is_reported():
    diffs = lmstudio._match({"presence_penalty": 1.1}, {"temperature": 0.85})
    assert diffs and "NOT RECEIVED" in diffs[0]


def test_a_value_we_never_sent_is_reported():
    diffs = lmstudio._match({"temperature": 0.85},
                            {"temperature": 0.85, "top_k": 40})
    assert diffs and "never sent" in diffs[0]



def _cell(tmp_path, model, task, used, t_start, max_tokens=32768):
    d = tmp_path / "runs" / "2026-07-26_120000" / model / task
    d.mkdir(parents=True, exist_ok=True)
    rec = {"model": model, "task": task, "max_tokens": max_tokens,
           "attempts": [{"n": 1, "t_start": t_start}]}
    if used is not None:
        rec["sampling_used"] = used
    write_json(d / "metrics.json", rec)


class _M:
    SAMPLING_KEYS = ()

    def __init__(self, name, model, local=True):
        self.name, self.model, self.local = name, model, local


SENT = {"temperature": 0.85, "top_p": 0.95, "min_p": 0.0,
        "repetition_penalty": 1.0}
T_START = "2026-07-26T17:00:00+00:00"


def _run(tmp_path, monkeypatch, used=SENT, max_tokens=32768, models=None,
         t_start=T_START):
    _log(tmp_path, monkeypatch)
    monkeypatch.setattr(config, "RUNS_DIR", tmp_path / "runs")
    _cell(tmp_path, "m1", "t-001", used, t_start, max_tokens)
    return lmstudio.confirm_sampling(
        models=models or [_M("m1", "m-local")])


def test_a_matching_request_confirms_the_cell(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch)
    assert res["m1"]["confirmed"] == 1
    assert res["m1"]["mismatched"] == 0 and res["m1"]["unlogged"] == 0


def test_a_value_the_server_did_not_get_is_a_mismatch(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, used={**SENT, "presence_penalty": 1.1})
    assert res["m1"]["mismatched"] == 1 and res["m1"]["confirmed"] == 0
    task, diffs = res["m1"]["details"][0]
    assert task == "t-001"
    assert any("presence_penalty" in d and "NOT RECEIVED" in d for d in diffs)


def test_a_differing_value_is_a_mismatch(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, used={**SENT, "temperature": 0.2})
    assert res["m1"]["mismatched"] == 1


def test_a_budget_that_did_not_arrive_is_a_mismatch(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, max_tokens=65536)
    assert res["m1"]["mismatched"] == 1


def test_a_cell_with_no_logged_request_is_unlogged_not_failed(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, t_start="2026-07-20T17:00:00+00:00")
    assert res["m1"]["unlogged"] == 1 and res["m1"]["mismatched"] == 0


def test_cells_predating_the_sampling_record_are_skipped(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, used=None)
    assert res == {}


def test_cloud_models_are_not_checked(tmp_path, monkeypatch):
    res = _run(tmp_path, monkeypatch, models=[_M("m1", "m-local", local=False)])
    assert res == {}
