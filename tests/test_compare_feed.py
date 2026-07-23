"""The compare page and the Atom feed build from the same aggregated data the
leaderboard uses, and both must stay valid on a static host with no server.

The feed's dates are RUN dates, not wall-clock, so a rebuild with unchanged data
produces identical bytes — the property that lets the shipped reports/ stay
churn-free between publishes.
"""

import xml.dom.minidom as minidom

from harness import report


def _runs():
    def cell(run_id, model, task, cat, score, cost=0.01):
        return {"task": task, "model": model, "category": cat, "tier": 1,
                "run_id": run_id, "status": "ok",
                "score": {"status": "scored", "score": score, "summary": ""},
                "attempts": [], "wall_ms": 1000, "tokens_in": 10,
                "tokens_out": 10, "cost_usd": cost, "n_retries": 0,
                "n_attempts": 1, "gen_tokens_per_sec": 50.0, "model_meta": {}}
    r1 = {"run_id": "2026-07-01_000000",
          "manifest": {"started": "2026-07-01T00:00:00Z",
                       "models": ["m-fast", "m-slow"], "tasks": ["t1", "t2"]},
          "results": [cell("2026-07-01_000000", "m-fast", "t1", "reasoning", 1.0),
                      cell("2026-07-01_000000", "m-fast", "t2", "reasoning", 0.8),
                      cell("2026-07-01_000000", "m-slow", "t1", "reasoning", 0.5),
                      cell("2026-07-01_000000", "m-slow", "t2", "reasoning", 0.2)]}
    r2 = {"run_id": "2026-07-05_000000",
          "manifest": {"started": "2026-07-05T00:00:00Z",
                       "models": ["m-new"], "tasks": ["t1", "t2"]},
          "results": [cell("2026-07-05_000000", "m-new", "t1", "reasoning", 0.9),
                      cell("2026-07-05_000000", "m-new", "t2", "reasoning", 0.9)]}
    return [r1, r2]


class _T:
    def __init__(self, tid):
        self.id = tid
        self.category = "reasoning"
        self.tier = 1
        self.title = tid


def _tdefs():
    return {"t1": _T("t1"), "t2": _T("t2")}


def test_compare_page_embeds_every_model_and_task():
    html = report.build_compare_page(_runs(), _tdefs())
    assert "const D = {" in html
    for m in ("m-fast", "m-slow", "m-new"):
        assert m in html
    assert '"t":{' in html or '"t": {' in html


def test_feed_is_valid_atom_newest_first_and_deterministic():
    runs, tdefs = _runs(), _tdefs()
    xml = report.build_feed(runs, tdefs)
    doc = minidom.parseString(xml)
    entries = doc.getElementsByTagName("entry")
    assert len(entries) == 3
    first = entries[0].getElementsByTagName("title")[0].firstChild.data
    assert "m-new" in first
    assert report.build_feed(runs, tdefs) == xml
