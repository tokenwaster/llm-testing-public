"""The task page links each row to the files behind its own numbers.

The link points at the run that produced THAT row — not the model's newest run —
so stepping down the column compares like with like. /data only ever serves the
live runs/, so an archived dataset (runs under archive/<ver>/runs) must not show
the column at all rather than a page of 404s.
"""

import re

from harness import config, report


def _page(monkeypatch, runs_base):
    monkeypatch.setattr(report, "_RUNS_BASE", runs_base)
    entry = {
        "task": "web-012-coin", "model": "some model+x", "category": "one-shot-apps",
        "tier": 1, "run_id": "2026-01-02_030405", "status": "ok",
        "wall_ms": 1000, "tokens_in": 5, "tokens_out": 5, "n_retries": 0,
        "attempts": [], "reasoning_tokens": 0, "cost_usd": 0.0,
        "gen_tokens_per_sec": 10.0,
        "score": {"status": "scored", "score": 0.5, "summary": "s"},
    }
    info = {"category": "one-shot-apps", "tier": 1,
            "agg": {"some model+x": entry}, "history": [entry]}
    tdef = type("T", (), {"id": "web-012-coin", "title": "Coin", "prompt": "p",
                          "scoring_type": "webapp", "content_hash": "h"})()
    return report.build_task_report("web-012-coin", info, tdef, {}, {})


def test_the_link_targets_this_rows_own_run(monkeypatch):
    html = _page(monkeypatch, config.RUNS_DIR)
    hrefs = re.findall(r'class="filelink" href="([^"]+)"', html)
    assert len(hrefs) == 1
    assert hrefs[0].startswith("/data/2026-01-02_030405/"), \
        "must point at the run this row's numbers came from"
    assert hrefs[0].endswith("/web-012-coin/")


def test_a_model_name_needing_escaping_is_quoted(monkeypatch):
    """Every current name is URL-safe; one with a space or + must not break."""
    html = _page(monkeypatch, config.RUNS_DIR)
    href = re.findall(r'class="filelink" href="([^"]+)"', html)[0]
    assert " " not in href
    assert "some%20model%2Bx" in href


def test_an_archived_dataset_gets_no_files_column(monkeypatch, tmp_path):
    """/data serves only the live runs/, so these links could never resolve.
    (The .filelink CSS still ships in BASE_CSS — it is the link that must go.)"""
    html = _page(monkeypatch, tmp_path / "archive" / "v0.5" / "runs")
    assert 'class="filelink"' not in html
    assert "/data/" not in html
    assert ">Files<" not in html


def test_the_live_dataset_does_get_the_column(monkeypatch):
    html = _page(monkeypatch, config.RUNS_DIR)
    assert ">Files<" in html
