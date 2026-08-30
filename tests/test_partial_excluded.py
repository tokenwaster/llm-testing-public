import types

from harness import config, report
from harness.fit import task_fit


def _entry(score, cat="agentic", tps=100.0):
    return {"score": {"status": "scored", "score": score},
            "category": cat, "gen_tokens_per_sec": tps, "tokens_out": 100}


def _td(tids, per_task):
    return {t: {"agg": {m: _entry(s) for m, s in per_task.get(t, {}).items()}}
            for t in tids}


def test_covered_models_needs_every_task_in_the_set():
    td = _td(["t1", "t2", "t3"], {
        "t1": {"full": 1.0, "part": 1.0},
        "t2": {"full": 0.5},
        "t3": {"full": 0.5},
    })
    assert report.covered_models(td) == {"full"}


def test_coverage_is_judged_against_the_named_subset_only():
    td = _td(["t1", "t2", "t3"], {
        "t1": {"a": 1.0, "b": 1.0},
        "t2": {"a": 1.0, "b": 1.0},
        "t3": {"a": 1.0},
    })
    assert report.covered_models(td) == {"a"}
    assert report.covered_models(td, ["t1", "t2"]) == {"a", "b"}


def test_an_unscored_cell_does_not_count_as_coverage():
    td = {"t1": {"agg": {"m": _entry(1.0)}},
          "t2": {"agg": {"m": {"score": {"status": "error", "score": None}}}}}
    assert report.covered_models(td) == set()


def test_an_empty_set_covers_nobody():
    assert report.covered_models({}) == set()
    assert report.covered_models({"t1": {"agg": {"m": _entry(1.0)}}}, []) == set()


def test_unknown_task_ids_are_ignored_not_counted_as_missing():
    td = _td(["t1"], {"t1": {"m": 1.0}})
    assert report.covered_models(td, ["t1", "does-not-exist"]) == {"m"}


def test_version_rankings_drop_a_partial_model_and_say_how_many():
    td = _td(["t1", "t2"], {"t1": {"full": 0.5, "part": 1.0},
                            "t2": {"full": 0.5}})
    out = report.version_rankings([("0.9", td, {"t1": None, "t2": None})])
    assert list(out[0]["ranks"]) == ["full"]
    assert out[0]["n_partial_excluded"] == 1
    assert out[0]["n_models"] == 1


def test_a_partial_cannot_top_a_task_category():
    by_model = {
        "full": [_entry(0.5) for _ in range(4)],
        "part": [_entry(1.0)],
    }
    fit = task_fit(by_model, ["agentic"], {"agentic": 4})
    row = fit["rows"][0]
    assert [m for m, _ in row["top"]] == ["full"]
    assert "part" not in row["classes"]
    assert "part" not in [m for m, _, _ in row["value"]]
    assert row["n_partial_excluded"] == 1
    assert fit["partial_excluded"]["agentic"] == ["part"]


def test_a_model_that_finished_the_whole_category_still_counts():
    by_model = {"full": [_entry(0.5) for _ in range(4)],
                "alsofull": [_entry(1.0) for _ in range(4)]}
    row = task_fit(by_model, ["agentic"], {"agentic": 4})["rows"][0]
    assert [m for m, _ in row["top"]] == ["alsofull"]
    assert row["n_partial_excluded"] == 0


def test_task_fit_without_counts_keeps_its_old_behaviour():
    by_model = {"part": [_entry(1.0)]}
    row = task_fit(by_model, ["agentic"])["rows"][0]
    assert [m for m, _ in row["top"]] == ["part"]


SRC = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")


def test_the_efficiency_frontier_plots_only_complete_models():
    i = SRC.index("points = []")
    assert "for m in complete:" in SRC[i:i + 200]


def test_the_frontier_legend_lists_only_plotted_models():
    assert '_plotted = {p["label"] for p in points}' in SRC
    assert 'legend_html = chart_legend([e for e in legend if e["model"] in _plotted])' \
        in SRC


def test_the_speed_and_cost_table_excludes_partial_rows():
    i = SRC.index("speed_rows = []")
    seg = SRC[i:i + 320]
    assert "_full_cov" in seg and "for m in _full_cov:" in seg


def test_the_compare_page_only_offers_fully_covered_models():
    i = SRC.index("def build_compare_page")
    seg = SRC[i:i + 1600]
    assert "_full = covered_models(task_data)" in seg
    assert "by_model = {m: rs for m, rs in by_model.items() if m in _full}" in seg


def test_a_family_leader_must_have_run_the_whole_suite():
    i = SRC.index("def _full(v):")
    seg = SRC[i:i + 1200]
    assert 'x.get("coverage", 0) >= 0.999' in seg
    assert "got = _full(members)" in seg
    assert "if not got:" in seg


def test_the_rendered_pages_make_no_claim_for_a_partial_model():
    idx = config.ROOT / "reports" / "index.html"
    if not idx.is_file():
        return
    import re
    html = idx.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"Rankings across suite versions(.{0,20000}?)<h2", html, re.S)
    if m:
        block = m.group(1)
        for name in re.findall(r'data-m="([^"]+)"', block):
            assert "laguna-s-2-1" not in name, \
                "a partial model appears in the cross-version ranking"
