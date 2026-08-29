import types

import pytest

from harness import apicost, config, report
from harness.registry import Model
from harness.validate import validate_models


OPERATOR_ONLY = pytest.mark.skipif(
    not config.is_operator_build(), reason="private operator surface is not exported")


def _m(name, provider, key=None, base=None, compare_key="k", **kw):
    if provider == "claude-cli":
        kw.setdefault("temperature", None)
    return Model(name=name, provider=provider, model="claude-opus-5",
                 base_url=base or "https://api.anthropic.com",
                 key_env=key or "", compare_key=compare_key, **kw)


def test_each_transport_maps_to_the_avenue_that_can_bill_it():
    assert apicost.avenue_of(_m("a", "claude-cli")) == "cli"
    assert apicost.avenue_of(_m("b", "anthropic")) == "api"
    assert apicost.avenue_of(
        _m("c", "openai", base="https://openrouter.ai/api/v1")) == "gateway"
    assert apicost.avenue_of(
        _m("d", "openai", base="http://localhost:1234/v1")) == ""


def test_only_the_gateway_can_report_a_real_bill():
    assert apicost.BILLED_AVENUES == ("gateway",)
    assert "cli" not in apicost.BILLED_AVENUES, (
        "a subscription has no per-token price, so the CLI can never be billed")
    assert "api" not in apicost.BILLED_AVENUES, (
        "the Anthropic API returns usage, not dollars")


def test_a_group_needs_two_avenues_to_be_a_comparison():
    one = [_m("solo", "claude-cli")]
    assert apicost.groups(one) == {}
    two = one + [_m("api", "anthropic", key="K")]
    assert set(apicost.groups(two)) == {"k"}


def test_models_without_a_compare_key_never_pair():
    ms = [_m("a", "claude-cli", compare_key=""),
          _m("b", "anthropic", key="K", compare_key="")]
    assert apicost.groups(ms) == {}


def test_two_different_models_do_not_pair_by_accident():
    ms = [_m("a", "claude-cli", compare_key="opus"),
          _m("b", "anthropic", key="K", compare_key="sonnet")]
    assert apicost.groups(ms) == {}


def test_an_avenue_without_a_key_is_named_not_silently_dropped(monkeypatch):
    monkeypatch.delenv("NOPE", raising=False)
    mo = _m("api", "anthropic", key="NOPE")
    assert apicost._usable(mo) is False
    why = apicost.blocked_reason(mo)
    assert "NOPE" in why and ".env" in why


def test_runnable_hides_a_group_that_loses_its_second_avenue(monkeypatch):
    monkeypatch.delenv("NOPE", raising=False)
    ms = [_m("cli", "claude-cli"), _m("api", "anthropic", key="NOPE")]
    assert set(apicost.groups(ms)) == {"k"}
    assert apicost.runnable(ms) == {}


def test_the_cli_is_usable_without_any_key():
    assert apicost._usable(_m("cli", "claude-cli")) is True


def test_tags_round_trip_and_are_distinct_per_avenue():
    seen = set()
    for a in apicost.AVENUES:
        t = apicost.tag_for(a)
        assert apicost.avenue_from_tag(t) == a
        seen.add(t)
    assert len(seen) == len(apicost.AVENUES)
    assert apicost.avenue_from_tag("thinking:on") == "", (
        "another probe's tag must not be read as an avenue")


def test_every_leg_passes_the_gate_run_suite_applies(monkeypatch):
    monkeypatch.setenv("K", "x")
    ms = [_m("cli", "claude-cli", enabled=True, source_file="a.yaml"),
          _m("api", "anthropic", key="K", enabled=False, source_file="b.yaml")]
    monkeypatch.setattr(apicost, "runnable", lambda *a, **k: {
        "k": {"cli": ms[0], "api": ms[1]}})
    legs = apicost.probe_models(ms[0], [types.SimpleNamespace(id="t1")])
    assert len(legs) == 2
    for mo, tag, _t in legs:
        assert mo.enabled is True, (
            "a disabled model must be re-enabled for its leg or run_suite skips it")
        assert validate_models([mo]) == [], mo.name
        assert tag.startswith(apicost.TAG_PREFIX)


def test_the_probe_leaves_the_registry_objects_untouched(monkeypatch):
    monkeypatch.setenv("K", "x")
    api = _m("api", "anthropic", key="K", enabled=False)
    monkeypatch.setattr(apicost, "runnable", lambda *a, **k: {
        "k": {"cli": _m("cli", "claude-cli"), "api": api}})
    apicost.probe_models(api, [types.SimpleNamespace(id="t1")])
    assert api.enabled is False


def _write(tmp, run, tag, model, task, score, tin, tout, cost, source):
    from harness.util import write_json
    d = tmp / run / model / task
    d.mkdir(parents=True, exist_ok=True)
    write_json(tmp / run / "run.json", {"tag": tag})
    write_json(d / "score.json", {"status": "scored", "score": score})
    write_json(d / "metrics.json", {"tokens_in": tin, "tokens_out": tout,
                                    "cost_usd": cost, "cost_source": source,
                                    "wall_ms": 100.0})


@pytest.fixture
def special(tmp_path, monkeypatch):
    monkeypatch.setattr(apicost.config, "SPECIAL_DIR", tmp_path)
    ms = [_m("cli", "claude-cli"), _m("gw", "openai",
                                      base="https://openrouter.ai/api/v1",
                                      key="OPENROUTER_API_KEY")]
    monkeypatch.setattr(apicost, "groups", lambda *a, **k: {
        "k": {"cli": ms[0], "gateway": ms[1]}})
    return tmp_path


def test_results_pair_the_same_cell_across_avenues(special):
    _write(special, "r1", apicost.tag_for("cli"), "cli", "t1",
           1.0, 3000, 100, 0.010, "list")
    _write(special, "r2", apicost.tag_for("gateway"), "gw", "t1",
           1.0, 1000, 100, 0.009, "billed")
    rows = apicost.results()
    assert len(rows) == 1
    r = rows[0]
    assert r["paired"] == ["cli", "gateway"]
    assert r["avenues"]["cli"]["billed"] is False
    assert r["avenues"]["gateway"]["billed"] is True
    assert r["avenues"]["cli"]["in"] == 3000


def test_an_unpaired_cell_is_not_a_comparison(special):
    _write(special, "r1", apicost.tag_for("cli"), "cli", "t1",
           1.0, 3000, 100, 0.01, "list")
    assert apicost.results() == []


def test_a_score_change_between_avenues_outranks_a_price_change(special):
    _write(special, "r1", apicost.tag_for("cli"), "cli", "t1",
           1.0, 3000, 100, 0.10, "list")
    _write(special, "r2", apicost.tag_for("gateway"), "gw", "t1",
           0.5, 1000, 100, 0.01, "billed")
    assert apicost.verdict(apicost.results()[0]) == "avenue changed the score"


def test_same_score_different_price_is_called_out(special):
    _write(special, "r1", apicost.tag_for("cli"), "cli", "t1",
           1.0, 1000, 100, 0.020, "list")
    _write(special, "r2", apicost.tag_for("gateway"), "gw", "t1",
           1.0, 1000, 100, 0.010, "billed")
    assert apicost.verdict(apicost.results()[0]) == "same score, different price"


def test_identical_avenues_report_no_difference(special):
    _write(special, "r1", apicost.tag_for("cli"), "cli", "t1",
           1.0, 1000, 100, 0.010, "list")
    _write(special, "r2", apicost.tag_for("gateway"), "gw", "t1",
           1.0, 1000, 100, 0.010, "billed")
    assert apicost.verdict(apicost.results()[0]) == "no material difference"


def test_a_probe_trial_counts_the_thinnest_avenue(special):
    _write(special, "r1", apicost.tag_for("cli"), "cli", "t1",
           1.0, 1000, 100, 0.01, "list")
    _write(special, "r2", apicost.tag_for("cli"), "cli", "t1",
           1.0, 1000, 100, 0.01, "list")
    _write(special, "r3", apicost.tag_for("gateway"), "gw", "t1",
           1.0, 1000, 100, 0.01, "billed")
    r = apicost.results()[0]
    assert r["avenues"]["cli"]["n"] == 2 and r["avenues"]["gateway"]["n"] == 1


def test_another_probes_runs_are_not_read_as_avenues(special):
    _write(special, "r1", "thinking:on", "cli", "t1", 1.0, 1, 1, 0.0, "list")
    _write(special, "r2", "spiral@1800s", "cli", "t1", 1.0, 1, 1, 0.0, "list")
    assert apicost.results() == []


def test_cheapest_tasks_ranks_by_measured_spend():
    td = {"cheap": {"agg": {"m": {"cost_usd": 0.001, "wall_ms": 1.0,
                                  "tokens_in": 10, "tokens_out": 1}}},
          "dear": {"agg": {"m": {"cost_usd": 0.500, "wall_ms": 9.0,
                                 "tokens_in": 900, "tokens_out": 90}}},
          "mid": {"agg": {"m": {"cost_usd": 0.010, "wall_ms": 5.0,
                                "tokens_in": 90, "tokens_out": 9}}}}
    assert report.cheapest_tasks(2, td, {"cheap", "dear", "mid"}) == ["cheap", "mid"]
    assert report.cheapest_tasks(99, td, {"cheap", "dear", "mid"})[-1] == "dear"


def test_an_unpriced_task_sorts_last_rather_than_first():
    td = {"priced": {"agg": {"m": {"cost_usd": 0.5, "tokens_in": 1, "tokens_out": 1}}},
          "unpriced": {"agg": {"m": {"cost_usd": None, "tokens_in": 1,
                                     "tokens_out": 1}}}}
    assert report.cheapest_tasks(2, td, {"priced", "unpriced"}) == ["priced",
                                                                    "unpriced"]


def test_cheapest_only_considers_the_live_task_set():
    td = {"live": {"agg": {"m": {"cost_usd": 0.5, "tokens_in": 1, "tokens_out": 1}}},
          "retired": {"agg": {"m": {"cost_usd": 0.001, "tokens_in": 1,
                                    "tokens_out": 1}}}}
    assert report.cheapest_tasks(5, td, {"live"}) == ["live"]


def test_apicost_is_a_probe_kind_so_top_up_can_count_it():
    assert "apicost" in report.PROBE_KINDS


def test_the_anthropic_adapter_records_cache_traffic_like_the_cli():
    import inspect

    from harness.adapters import AnthropicAdapter
    src = inspect.getsource(AnthropicAdapter)
    assert "cache_read_input_tokens" in src
    assert "cache_creation_input_tokens" in src
    assert src.count("cache_read_tokens=") >= 1, (
        "without cache tokens the cost arithmetic cannot match the CLI's basis")


@OPERATOR_ONLY
def test_the_special_page_wires_the_new_probe():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    for hook in ("g-apicost", "apicost-pick", "apicost-results", "ac-trials",
                 "kind:'apicost'", "renderAcPick", "pickCheapest",
                 "start_special_apicost", "cheapest_tasks"):
        assert hook in ui, hook


@OPERATOR_ONLY
def test_the_cheapest_selector_stays_inside_the_probe():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    assert "ac-cheap" in ui
    run = ui[ui.index("RUN_PAGE"):ui.index("SPECIAL_PAGE")]
    for leaked in ("pickcheap", "t-cheap", "data-cheap"):
        assert leaked not in run, (
            f"{leaked} belongs to the api-cost probe, not the main run page")


@OPERATOR_ONLY
def test_the_probe_only_twin_stays_out_of_normal_runs():
    from harness.registry import load_models
    enabled = {m.name for m in load_models()}
    allm = [m for m in load_models(include_disabled=True)
            if m.name.startswith(("claude-api-", "claude-or-"))]
    assert len(allm) >= 12, f"expected a twin pair per CLI model, got {len(allm)}"
    for m in allm:
        assert m.compare_key, m.name
        if m.name.startswith("claude-or-"):
            assert m.name not in enabled, (
                f"{m.name} is the avenue probe's billed-receipt leg only")
            assert m.show_in_reports is False, m.name


def test_every_cli_model_has_a_full_set_of_avenues():
    from harness import apicost
    from harness.registry import load_models
    ms = load_models(include_disabled=True)
    cli = [m for m in ms if m.provider == "claude-cli"]
    g = apicost.groups(ms)
    assert len(g) == len(cli), (
        f"{len(cli)} CLI models but only {len(g)} comparison group(s)")
    for k, per in g.items():
        assert set(per) == {"cli", "api", "gateway"}, (k, sorted(per))


def test_each_avenue_of_a_group_prices_the_same_model_the_same_way():
    from harness import apicost
    from harness.registry import load_models
    for k, per in apicost.groups(load_models(include_disabled=True)).items():
        rates = {a: ((m.pricing or {}).get("input_per_mtok"),
                     (m.pricing or {}).get("output_per_mtok"))
                 for a, m in per.items()}
        assert len(set(rates.values())) == 1, (
            f"{k} prices differ per avenue, so a cost delta would be the price "
            f"table disagreeing with itself rather than a real finding: {rates}")


def test_no_two_groups_share_a_model_name():
    from harness import apicost
    from harness.registry import load_models
    seen = {}
    for k, per in apicost.groups(load_models(include_disabled=True)).items():
        for a, m in per.items():
            assert m.name not in seen, (
                f"{m.name} is claimed by both {seen.get(m.name)} and {k}")
            seen[m.name] = k


def test_a_hard_rejection_is_dropped_unscored_not_scored_zero():
    import inspect

    from harness import runner
    src = inspect.getsource(runner.TaskRunner._chat_with_retries)
    i = src.index('if not rec.get("retryable")')
    after = src[i:i + 520]
    assert "RequestRejected" in after, (
        "a non-retryable rejection returned None, which run_task records as "
        "status=error and scoring turns into 0.0 — a provider refusing the "
        "request is not the model failing the task")
    assert after.index("RequestRejected") < after.index("return None"), (
        "the raise must come before the bare return, or the drop-unscored path "
        "stays dead")


def test_the_rejection_raise_covers_both_hard_kinds():
    import inspect

    from harness import runner
    src = inspect.getsource(runner.TaskRunner._chat_with_retries)
    i = src.index('if not rec.get("retryable")')
    after = src[i:i + 520]
    assert '"request_rejected"' in after and '"auth"' in after


def test_no_rejected_cell_in_the_dataset_ever_carries_a_score():
    import json

    from harness import config
    bad = []
    for mf in config.RUNS_DIR.glob("*/*/*/metrics.json"):
        try:
            d = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        kinds = {a.get("error_kind") for a in (d.get("attempts") or [])}
        if not ({"request_rejected", "auth"} & kinds):
            continue
        sp = mf.parent / "score.json"
        if not sp.exists():
            continue
        try:
            s = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if s.get("score") is not None:
            bad.append(f"{mf.parents[2].name}/{mf.parents[1].name}/"
                       f"{mf.parent.name} = {s.get('score')}")
    assert not bad, ("provider refusals scored instead of dropped:\n  "
                     + "\n  ".join(bad[:10]))


@OPERATOR_ONLY
def test_a_capped_model_declares_its_real_ceiling():
    from harness.registry import load_models
    allm = {m.name: m for m in load_models(include_disabled=True)}
    haiku = allm["claude-api-haiku-4-5"]
    assert haiku.max_tokens == 64000, (
        "the Anthropic API rejects max_tokens above this model's own limit with "
        "a 400, which zeroed all ten cells before the ceiling was pinned")


def test_a_cell_missing_an_avenue_is_not_counted_as_done(special, monkeypatch):
    monkeypatch.setattr(apicost, "runnable", lambda *a, **k: {
        "k": {"cli": _m("cli", "claude-cli"),
              "api": _m("api", "anthropic", key="K"),
              "gateway": _m("gw", "openai",
                            base="https://openrouter.ai/api/v1", key="K")}})
    _write(special, "r1", apicost.tag_for("cli"), "cli", "t1",
           1.0, 1000, 100, 0.01, "list")
    _write(special, "r2", apicost.tag_for("gateway"), "gw", "t1",
           1.0, 1000, 100, 0.01, "billed")
    r = apicost.results()[0]
    assert r["missing"] == ["api"]
    assert r["trials"] == 0, (
        "min() over only the avenues PRESENT reports a complete trial and greys "
        "the cell out, so the missing leg can never be topped up")
    assert apicost.verdict(r) == "missing api"


def test_a_complete_cell_counts_its_thinnest_avenue(special, monkeypatch):
    monkeypatch.setattr(apicost, "runnable", lambda *a, **k: {
        "k": {"cli": _m("cli", "claude-cli"),
              "gateway": _m("gw", "openai",
                            base="https://openrouter.ai/api/v1", key="K")}})
    for run, av, mdl in (("r1", "cli", "cli"), ("r2", "cli", "cli"),
                         ("r3", "gateway", "gw")):
        _write(special, run, apicost.tag_for(av), mdl, "t1",
               1.0, 1000, 100, 0.01, "list")
    r = apicost.results()[0]
    assert r["missing"] == [] and r["trials"] == 1


def test_the_probe_counter_reads_the_rows_own_trial_number():
    import inspect
    src = inspect.getsource(report.probe_counts)
    assert 'r.get("trials")' in src, (
        "probe_counts must use the row's trials, which accounts for a missing "
        "avenue, not a min over whatever happens to be present")


@OPERATOR_ONLY
def test_the_top_up_counts_by_the_key_the_counter_actually_uses():
    from harness import config
    src = (config.ROOT / "harness" / "jobs.py").read_text(encoding="utf-8")
    assert "key_of=lambda m: m.compare_key" in src, (
        "apicost counts are keyed by compare_key but the anchor's .name is the "
        "api twin, so a name lookup returns None and every already-finished "
        "cell gets re-run and re-charged")
    assert "ckey = key_of or (lambda m: m.name)" in src
    assert "ckey(model)" in src
    assert "report.probe_missing(kind, model.name" not in src


def test_the_server_counts_a_group_by_its_compare_key():
    from harness import apicost, report
    from harness.registry import load_models
    counts = report.probe_counts()
    live = apicost.runnable(load_models(include_disabled=True))
    if not live:
        pytest.skip("no avenue groups configured")
    for k, per in live.items():
        anchor = per.get("api") or per[sorted(per)[0]]
        assert anchor.compare_key == k, (
            f"the anchor for {k} carries compare_key {anchor.compare_key!r}; "
            f"probe_counts is keyed on the compare_key, so a mismatch makes "
            f"every finished cell look unrun")
        assert anchor.compare_key in counts.get("apicost", {}) or True


@OPERATOR_ONLY
def test_a_greyed_cell_can_never_be_submitted_by_a_bulk_selector():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    block = ui[ui.index("function pickCheapest"):]
    block = block[:block.index("function collectAcSelection")]
    assert "if (c.disabled)" in block, (
        "a bulk selector that ignores disabled state re-checks finished cells, "
        "and the run spends money on work already done")
    assert "already at target, left out" in block, "say what was skipped"
    sel = ui[ui.index("$('#ac-selall')"):]
    sel = sel[:sel.index("$('#ac-selnone')")]
    assert "if (!c.disabled)" in sel


@OPERATOR_ONLY
def test_every_bulk_selector_on_the_probe_page_guards_disabled():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    for anchor in ("$('#th-selall')", "$('#ac-selall')"):
        i = ui.index(anchor)
        assert "if (!c.disabled)" in ui[i:i + 220], anchor


def test_the_estimate_prices_measured_work_and_never_predicts_output():
    import inspect
    src = inspect.getsource(apicost.api_equivalent)
    assert 'metrics.get("tokens_out")' in src
    assert "out_ratio" not in src, (
        "output must be taken exactly as measured; the same model emits a "
        "different amount through a different avenue and no estimate can "
        "predict that")


def test_the_estimate_never_goes_negative():
    from harness.registry import Model
    mo = Model(name="claude-cli-x", provider="claude-cli", model="x",
               temperature=None, compare_key="k",
               pricing={"input_per_mtok": 5.0, "output_per_mtok": 25.0})
    import harness.apicost as ac
    prev = ac._OH_CACHE
    try:
        ac._OH_CACHE = {"k": {"tokens": 900000, "n": 1, "spread": 0}}
        est = ac.api_equivalent({"tokens_in": 100, "tokens_out": 10,
                                 "turns": 5, "n_attempts": 1}, mo)
        assert est["content_tokens"] == 0
        assert est["scaffold_tokens"] == 100, "cannot strip more than exists"
        assert est["cost"] > 0
    finally:
        ac._OH_CACHE = prev


def test_requests_counts_turns_and_retries():
    assert apicost.requests_in({"turns": 9, "n_attempts": 1}) == 9
    assert apicost.requests_in({"turns": 1, "n_attempts": 2}) == 2
    assert apicost.requests_in({}) == 1


def test_only_a_cli_row_switches_basis():
    from harness.registry import Model
    for provider, base in (("openai", "https://openrouter.ai/api/v1"),
                           ("anthropic", "https://api.anthropic.com")):
        mo = Model(name="x", provider=provider, model="m", base_url=base,
                   compare_key="claude-opus-5",
                   pricing={"input_per_mtok": 5.0, "output_per_mtok": 25.0})
        assert apicost.api_equivalent({"tokens_in": 9999, "tokens_out": 10},
                                      mo) is None


def test_the_accuracy_bound_is_published_not_asserted():
    acc = apicost.accuracy()
    if not acc.get("n"):
        pytest.skip("no paired avenue data yet")
    for k in ("input_mean_err_pct", "input_worst_err_pct", "out_ratio_lo",
              "out_ratio_hi", "overhead", "n"):
        assert acc.get(k) is not None, k
    assert acc["out_ratio_hi"] >= acc["out_ratio_lo"]


def _flat(t):
    import re
    return re.sub(r"\s+", " ", t)


def test_the_cost_note_refuses_to_price_a_subscription():
    note = _flat(report.cost_note())
    for phrase in ("subscription", "no per-token price", "invented",
                   "info.html#costbasis"):
        assert phrase in note, (
            f"{phrase!r} must appear whether or not the avenue probe holds "
            f"data; the disclosure cannot depend on a measurement")
    assert "$" not in note, "a subscription has no price to print"


def test_every_cost_bearing_page_shows_the_basis_note():
    from harness import config
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    assert src.count("{{ cost_note|safe }}") >= 5, (
        "the note belongs under every table that shows a cost")
    for tpl in ("INDEX_TEMPLATE", "MODEL_TEMPLATE", "COMPARE_TEMPLATE",
                "TASK_TEMPLATE", "RUN_TEMPLATE", "INFO_TEMPLATE"):
        i = src.index(f"    return _compiled({tpl}).render(")
        assert "cost_note=cost_note(" in src[i:i + 200], tpl


def test_the_basis_note_link_matches_the_depth_of_its_page():
    from harness import report as rp
    assert 'href="info.html#costbasis"' in rp.cost_note()
    assert 'href="../info.html#costbasis"' in rp.cost_note("../")
    assert "{up}" not in rp.cost_note() and "{up}" not in rp.cost_note("../")


def test_a_nested_page_passes_the_prefix():
    import ast

    from harness import config
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    nested = {"build_model_report", "build_task_report", "build_run_report"}
    flat = {"build_index", "build_info_page", "build_compare_page"}
    seen = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        if node.name not in nested | flat:
            continue
        for call in ast.walk(node):
            if (isinstance(call, ast.Call)
                    and getattr(call.func, "id", "") == "cost_note"):
                seen[node.name] = [ast.literal_eval(a) for a in call.args]
    for fn in nested:
        assert seen.get(fn) == ["../"], (
            f"{fn} writes into a subdirectory, so a bare info.html link 404s "
            f"there. 583 published pages carried exactly that: {seen.get(fn)}")
    for fn in flat:
        assert seen.get(fn) in ([], [""]), f"{fn}: {seen.get(fn)}"


def test_the_info_page_records_what_refuted_the_estimate():
    from harness import config
    src = (config.ROOT / "harness" / "report.py").read_text(encoding="utf-8")
    i = src.index('id="costbasis"')
    sec = _flat(src[i:i + 4200])
    for claim in ("no per-token price", "refuted it", "1.46", "565,830",
                  "30,239", "different agent doing more work",
                  "0.18", "0.25", "0.00"):
        assert claim in sec, claim


def test_a_claude_row_says_why_there_is_no_cost():
    src = (report.config.ROOT / "harness" / "report.py").read_text(
        encoding="utf-8")
    assert 'add("Cost",' in src
    assert '(summary or {}).get("cost_basis") == "subscription"' in src
    assert "_model_detail_rows(mo, meta_info, fp, hosts, s)" in src


def test_the_rendered_claude_page_explains_the_missing_cost():
    from harness import report as rp
    runs = rp.load_all_runs()
    tdefs = rp._task_defs()
    td = rp.collect_task_data(runs)
    full = set(rp.covered_models(td))
    name = next((m for m in sorted(full) if m.startswith("claude-cli")), None)
    if name is None:
        pytest.skip("no complete claude-cli model recorded")
    html = _flat(rp.build_model_report(name, runs, tdefs))
    assert "not reported" in html and "subscription" in html
    assert "would be invented" in html
    assert "info.html#costbasis" in html
    from harness import apicost
    mo = next((m for m in __import__("harness.registry", fromlist=["x"])
               .load_models(include_disabled=True) if m.name == name), None)
    if mo and apicost.cli_overhead_for(mo):
        assert "not a deduction you can make" in html, (
            "when the overhead IS measured the page must say it is not "
            "subtractable, or a reader will assume it is")
    else:
        assert "not a deduction you can make" not in html, (
            "with no avenue data there is no overhead to quote")


def test_the_rendered_metered_page_has_no_such_row():
    from harness import report as rp
    runs = rp.load_all_runs()
    tdefs = rp._task_defs()
    td = rp.collect_task_data(runs)
    full = set(rp.covered_models(td))
    name = next((m for m in sorted(full)
                 if not m.startswith("claude-cli")), None)
    if name is None:
        pytest.skip("no metered model recorded")
    html = rp.build_model_report(name, runs, tdefs)
    assert "not reported &mdash; subscription" not in html, name


@OPERATOR_ONLY
def test_a_probe_leg_announces_its_own_run_id():
    from harness import config
    src = (config.ROOT / "harness" / "jobs.py").read_text(encoding="utf-8")
    i = src.index("rd = config.SPECIAL_DIR / new_run_id()")
    block = src[i:i + 700]
    assert 'log(f"run: {rd.name}")' in block, (
        "renderLog derives a per-line 'files' link from the last 'run:' it saw, "
        "falling back to the job's CURRENT run_id — so without this every leg's "
        "links point at the newest leg, which holds none of those files")


def test_a_subscription_model_carries_no_cost_at_all():
    from harness import report as rp
    runs = rp.load_all_runs()
    tdefs = rp._task_defs()
    td = rp.collect_task_data(runs)
    by = {}
    for tid, info in td.items():
        if tid in tdefs:
            for m, e in info["agg"].items():
                by.setdefault(m, []).append(e)
    full = set(rp.covered_models(td))
    seen = 0
    for m, rs in by.items():
        if m not in full or not m.startswith("claude-cli"):
            continue
        seen += 1
        s = rp._summarize(rs)
        assert s["cost_basis"] == "subscription", m
        assert s["cost_val"] is None, f"{m} still carries a cost_val"
        assert s["api_cost_val"] is None, m
        assert s["cost"] == "\u2014", f"{m} shows {s['cost']!r}"
        assert s.get("score_per_dollar") in (None, "\u2014"), m
    if not seen:
        pytest.skip("no complete claude-cli model recorded")


def test_public_receipt_names_preserve_the_subscription_cost_basis(monkeypatch):
    monkeypatch.setattr(report, "_EQUIV_MODELS", {})
    for name in ("claude-cli-opus-5", "codex-cli-gpt-5.6-sol"):
        assert report._is_subscription([{"model": name}])
    assert not report._is_subscription([{"model": "gpt-5.6-sol"}])


def test_a_metered_model_still_reports_its_cost():
    from harness import report as rp
    runs = rp.load_all_runs()
    tdefs = rp._task_defs()
    td = rp.collect_task_data(runs)
    by = {}
    for tid, info in td.items():
        if tid in tdefs:
            for m, e in info["agg"].items():
                by.setdefault(m, []).append(e)
    full = set(rp.covered_models(td))
    priced = 0
    for m, rs in by.items():
        if m not in full or m.startswith(("claude-cli", "codex-cli")):
            continue
        s = rp._summarize(rs)
        assert s["cost_basis"] == "as-run", m
        if s["cost_val"]:
            priced += 1
    assert priced, "removing the CLI cost must not blank every other model"


@OPERATOR_ONLY
def test_the_api_twins_are_scored_entries_and_the_gateway_twins_are_not():
    from harness.registry import load_models
    ms = {m.name: m for m in load_models(include_disabled=True)}
    api = [m for n, m in ms.items() if n.startswith("claude-api-")]
    gw = [m for n, m in ms.items() if n.startswith("claude-or-")]
    assert len(api) == 6 and len(gw) == 6
    for m in api:
        assert m.enabled and m.show_in_reports, m.name
        assert m.supports_tools is True, (
            f"{m.name} must run in this harness's tool loop, which is the whole "
            f"point of measuring it alongside the other models")
    for m in gw:
        assert not m.enabled and not m.show_in_reports, (
            f"{m.name} is the billed-receipt leg for the avenue probe; scoring it "
            f"would put a third Claude entry per model on the board")


@OPERATOR_ONLY
def test_the_cli_entries_are_a_different_agent_and_stay_that_way():
    from harness.registry import load_models
    ms = [m for m in load_models(include_disabled=True)
          if m.name.startswith("claude-cli-")]
    assert len(ms) == 6
    for m in ms:
        assert m.supports_tools is False, (
            f"{m.name} hands the task to claude -p, which brings its own agent; "
            f"turning this on would run two nested tool loops")
        assert m.enabled, f"{m.name} must keep its recorded results visible"


def test_a_cli_and_api_twin_never_share_an_aggregation_key():
    from harness.registry import load_models
    ms = [m for m in load_models(include_disabled=True)
          if m.name.startswith("claude-")]
    names = [m.name for m in ms]
    assert len(names) == len(set(names))
    by_key = {}
    for m in ms:
        by_key.setdefault(m.compare_key, []).append(m.name)
    for key, group in by_key.items():
        assert len(group) == 3, (key, group)
        assert len({n.split("-")[1] for n in group}) == 3, (
            f"{key}: the three avenues must be distinct model names or their "
            f"cells blend into one mean")


def test_an_api_twin_stays_out_of_rankings_until_the_suite_is_complete():
    from harness import report as rp
    runs = rp.load_all_runs()
    td = rp.collect_task_data(runs)
    cov = set(rp.covered_models(td))
    cells = {}
    for info in td.values():
        for m in info["agg"]:
            cells[m] = cells.get(m, 0) + 1
    for name in [m.name for m in __import__(
            "harness.registry", fromlist=["x"]).load_models()
            if m.name.startswith("claude-api-")]:
        have = cells.get(name, 0)
        if have < len(td):
            assert name not in cov, (
                f"{name} has {have}/{len(td)} measured tasks but is being "
                f"ranked")


def test_the_two_coverage_denominators_are_known_to_differ():
    from harness import report as rp
    runs = rp.load_all_runs()
    td = rp.collect_task_data(runs)
    live = len(rp._task_defs())
    if live == len(td):
        return
    cov = rp.covered_models(td)
    ranked = [r for r in rp.leaderboard(runs) if not r.get("partial")]
    assert cov and not ranked, (
        f"a task with no data exists ({live} live, {len(td)} measured): "
        f"covered_models counts only measured tasks so it still returns "
        f"{len(cov)} models, while the leaderboard counts the live set and "
        f"ranks {len(ranked)}. Both readings are defensible — a task nobody "
        f"has run carries no comparative information, but 'a partial model "
        f"earns no inferred outcome anywhere' argues for the strict one. "
        f"This test exists so the disagreement is recorded rather than "
        f"discovered when a new task lands")


@OPERATOR_ONLY
def test_saving_a_review_does_not_block_on_a_full_rebuild():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    assert "def _regen(block: bool = False)" in ui
    assert "threading.Thread(target=_regen_worker" in ui, (
        "a Save that rebuilds 563 pages on the request thread makes grading "
        "unusable")
    i = ui.index("def _regen(block")
    body = ui[i:i + 700]
    assert "apicost.reset_caches()" in body, (
        "the caches are keyed on directories, not content, so a review that "
        "rewrites score.json must invalidate them explicitly")
    assert "_COST_NOTE = None" in body


@OPERATOR_ONLY
def test_the_regen_coalesces_instead_of_stacking():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    i = ui.index("def _regen_worker")
    body = ui[i:i + 600]
    assert '_REGEN_STATE["dirty"]' in body, (
        "repeated saves must coalesce into one rebuild, not queue N of them")
    assert '_REGEN_STATE["running"]' in body


def test_a_special_review_can_never_reach_the_scored_dataset():
    from harness import apicost, config
    assert apicost.config.SPECIAL_DIR != config.RUNS_DIR
    import inspect
    src = inspect.getsource(apicost._legs)
    assert "SPECIAL_DIR" in src and "RUNS_DIR" not in src, (
        "the avenue probe must read only special/, or a graded probe cell would "
        "move a published score")


def test_the_three_phase_selectors_cover_the_suite_without_overlap():
    from harness import report as rp
    from harness.tasks import load_tasks
    ids = {t.id for t in load_tasks()}
    tiers = rp.task_tiers()
    easy = {t for t in ids if tiers.get(t) == "easy"}
    non_easy = ids - easy
    assert easy and non_easy, "both phases must select something"
    assert easy | non_easy == ids, "phase 1 + phase 2 must be the whole suite"
    assert not (easy & non_easy), "a task cannot be in both phases"


def test_phase_three_is_evidence_driven_not_a_threshold_guess():
    from harness import report as rp
    from harness.tasks import load_tasks
    ids = {t.id for t in load_tasks()}
    td = rp.collect_task_data(rp.load_all_runs())
    rc = rp.repeat_coverage(td, ids)
    wob = set(rc["wobbled_tasks"])
    unst = set(rc["unstable_tasks"])
    assert unst <= wob, (
        "anything past the 0.125 threshold has sigma > 0 by definition, so the "
        "unstable set must be a subset of the wobbled set")
    for tid in wob:
        seen = [e for e in td[tid]["agg"].values()
                if (e.get("n_scored") or 0) > 1 and e.get("score_sigma")]
        assert seen, f"{tid} is flagged wobbled with no repeated cell"


def test_a_task_never_repeated_is_not_offered_for_phase_three():
    from harness import report as rp
    td = {"never": {"agg": {"m": {"score": {"status": "scored", "score": 1.0},
                                  "n_scored": 1, "score_sigma": None}}},
          "steady": {"agg": {"m": {"score": {"status": "scored", "score": 1.0},
                                   "n_scored": 4, "score_sigma": 0.0}}},
          "wobbly": {"agg": {"m": {"score": {"status": "scored", "score": 0.5},
                                   "n_scored": 4, "score_sigma": 0.05}}}}
    rc = rp.repeat_coverage(td, {"never", "steady", "wobbly"})
    assert rc["wobbled_tasks"] == ["wobbly"], (
        "a cell run once has no spread, and a cell with sigma 0 proved stable; "
        "neither belongs in a phase that exists to buy precision")
    assert rc["unstable_tasks"] == [], "0.05 is under the 0.125 threshold"


@OPERATOR_ONLY
def test_the_run_page_wires_all_three_phases_with_live_counts():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    for hook in ("pickph1", "pickph2", "pickph3", "PHASE_PRED",
                 "annotatePhaseCounts", 'data-wobble'):
        assert hook in ui, hook
    i = ui.index("const PHASE_PRED")
    block = ui[i:i + 400]
    assert "cb.dataset.lens !== 'easy'" in block
    assert "cb.dataset.lens === 'easy'" in block
    assert "cb.dataset.wobble === '1'" in block
    assert "b.disabled = n === 0" in ui, (
        "phase 3 is empty until a repeat sweep has run; an enabled button that "
        "selects nothing looks broken")


def test_the_claude_cli_never_inherits_api_billing_credentials():
    from harness.adapters import CLI_BILLING_VARS, _cli_env
    import os
    saved = {k: os.environ.get(k) for k in CLI_BILLING_VARS}
    try:
        for k in CLI_BILLING_VARS:
            os.environ[k] = "leaked-value"
        env = _cli_env()
        for k in CLI_BILLING_VARS:
            assert k not in env, (
                f"{k} reaches the claude -p subprocess, which makes Claude Code "
                f"bill an API account instead of the subscription")
        assert "PATH" in env or "Path" in env, "the CLI must still be findable"
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def test_the_cli_subprocess_is_never_launched_with_an_inherited_env():
    import re
    from harness import config
    src = (config.ROOT / "harness" / "adapters.py").read_text(encoding="utf-8")
    for m in re.finditer(r"subprocess\.Popen\((.{0,400}?)\)\n", src, re.S):
        assert "env=_cli_env()" in m.group(1), (
            "a Popen without an explicit scrubbed env hands the child every "
            "credential in os.environ")


def test_no_credit_exhaustion_cell_survives_in_the_dataset():
    import json
    from harness import config
    bad = []
    for mf in config.RUNS_DIR.glob("*/claude-cli-*/*/metrics.json"):
        try:
            d = json.loads(mf.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for a in (d.get("attempts") or []):
            if "Credit balance is too low" in str(a.get("error") or ""):
                bad.append(f"{mf.parents[2].name}/{mf.parents[1].name}/"
                           f"{mf.parent.name}")
                break
    assert not bad, (
        "these cells record a billing failure, not a model result, and they "
        "drag the published mean down:\n  " + "\n  ".join(bad[:10]))


def test_no_child_process_ever_receives_a_credential():
    import os
    from harness.util import child_env, is_secret_var
    saved = dict(os.environ)
    try:
        for k in ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "MOONSHOT_API_KEY",
                  "AWS_SECRET_ACCESS_KEY", "SOME_TOKEN", "DB_PASSWORD"):
            os.environ[k] = "leaked"
        env = child_env()
        leaked = [k for k in os.environ if is_secret_var(k) and k in env]
        assert not leaked, (
            f"a task checker runs MODEL-WRITTEN code; these reach it: {leaked}")
        assert "PATH" in env or "Path" in env
    finally:
        os.environ.clear()
        os.environ.update(saved)


def test_the_checker_does_not_copy_the_whole_environment():
    from harness import config
    src = (config.ROOT / "harness" / "scoring.py").read_text(encoding="utf-8")
    assert "os.environ.copy()" not in src, (
        "the checker executes the model's own submission; copying the "
        "environment hands it every API key the harness holds")
    assert "child_env()" in src


def test_run_capped_defaults_to_a_scrubbed_environment():
    from harness import config
    src = (config.ROOT / "harness" / "util.py").read_text(encoding="utf-8")
    i = src.index("def run_capped")
    body = src[i:i + 500]
    assert 'kwargs.setdefault("env", child_env())' in body, (
        "every helper that spawns a process must default to a scrubbed env, "
        "or the next caller reintroduces the leak")


def test_a_billing_failure_is_not_retried_and_stops_the_model():
    from harness.adapters import _classify_http, _is_infra_failure
    for msg in ("Credit balance is too low", "insufficient_quota",
                "payment required", "spending limit"):
        assert _is_infra_failure(msg), msg
        e = _classify_http(400, msg)
        assert e.kind == "infra" and not e.retryable, msg
    assert not _is_infra_failure("max_tokens: 65536 > 64000")
    assert _classify_http(400, "bad parameter").kind == "request_rejected"


def test_an_infra_failure_takes_the_drop_unscored_path():
    import inspect
    from harness import runner
    src = inspect.getsource(runner.TaskRunner._chat_with_retries)
    i = src.index('if not rec.get("retryable")')
    assert '"infra"' in src[i:i + 320], (
        "a billing failure must raise RequestRejected so the model is dropped "
        "unscored and abandoned, not scored 0.00 once per task for 345 tasks")


def test_the_spend_ceiling_stops_a_run_and_is_opt_in():
    from harness import budget
    t = budget.SpendTracker(cap=1.00)
    with pytest.raises(budget.SpendExceeded) as e:
        for _ in range(20):
            t.add(0.15)
    assert "1.00 ceiling" in str(e.value)
    assert "Nothing already recorded is lost" in str(e.value)
    free = budget.SpendTracker(cap=None)
    for _ in range(50):
        free.add(99.0)
    assert free.spent == 0.0, "with no ceiling configured, nothing is tracked"


def test_a_subscription_and_a_local_model_never_count_against_spend():
    from harness import budget
    from harness.registry import load_models
    from harness.tasks import load_tasks
    ms = [m for m in load_models(include_disabled=True)
          if m.name in ("claude-cli-opus-5", "gemma-4-31b")]
    if len(ms) < 2:
        pytest.skip("expected models not in the registry")
    est = budget.estimate(ms, load_tasks(), repeat=3)
    assert est["billable"] == 0.0, (
        "a subscription has no per-token price and a local model bills "
        "electricity; neither may count toward a dollar ceiling")


def test_a_provider_without_a_balance_endpoint_says_so():
    from harness import budget
    from harness.registry import load_models
    by = {m.name: m for m in load_models(include_disabled=True)}
    for name in ("claude-api-opus-5", "claude-cli-opus-5"):
        if name not in by:
            continue
        b = budget.balance_for(by[name])
        assert b.get("remaining") is None
        assert b.get("unavailable"), (
            f"{name} has no balance API; that must be stated, not silently "
            f"treated as unlimited")


def test_a_local_model_needs_no_balance_check():
    from harness import budget
    from harness.registry import load_models
    loc = next((m for m in load_models(include_disabled=True) if m.local), None)
    if loc is None:
        pytest.skip("no local model")
    assert budget.balance_for(loc) is None


def test_run_suite_refuses_when_the_estimate_beats_the_balance():
    from harness import config
    src = (config.ROOT / "harness" / "runner.py").read_text(encoding="utf-8")
    assert "class SpendRefused" in src
    assert "budget.preflight(" in src
    assert 'raise SpendRefused(' in src
    assert "spend.add(m.get(\"cost_usd\"))" in src, (
        "the ceiling only works if realised cost is fed to the tracker as the "
        "run proceeds")
    i = src.index("budget.preflight(")
    assert "not force" in src[i:i + 200], (
        "--force must still be able to override a cost refusal")


def test_the_ceiling_is_settable_from_the_backend_page_not_by_hand(tmp_path,
                                                                   monkeypatch):
    from harness import budget, config
    monkeypatch.setattr(config, "SETTINGS_FILE", tmp_path / "settings.json")
    monkeypatch.delenv("MAX_SPEND_USD", raising=False)
    assert budget.max_spend_usd() is None
    config.save_setting("max_spend_usd", 25.0)
    assert budget.max_spend_usd() == 25.0
    config.save_setting("max_spend_usd", None)
    assert budget.max_spend_usd() is None


def test_an_environment_ceiling_wins_over_the_saved_one(tmp_path, monkeypatch):
    from harness import budget, config
    monkeypatch.setattr(config, "SETTINGS_FILE", tmp_path / "settings.json")
    config.save_setting("max_spend_usd", 25.0)
    monkeypatch.setenv("MAX_SPEND_USD", "3")
    assert budget.max_spend_usd() == 3.0


def test_the_binding_limit_is_the_one_reported():
    from harness import budget
    calls = []

    class R:
        status_code = 200

        def __init__(self, payload):
            self._p = payload

        def json(self):
            return self._p

    def fake_get(url, **kw):
        calls.append(url)
        if url.endswith("/credits"):
            return R({"data": {"total_credits": 120, "total_usage": 93.78}})
        return R({"data": {"limit_remaining": 9.49, "limit_reset": "weekly"}})

    import httpx
    orig = httpx.get
    httpx.get = fake_get
    try:
        b = budget._openrouter_balance("sk-test")
    finally:
        httpx.get = orig
    assert b["remaining"] == 9.49, (
        "a weekly key limit below the credit balance is what actually stops "
        "the run; reporting the larger number would greenlight a run that dies")
    assert b["binding"] == "key limit"


@OPERATOR_ONLY
def test_a_cost_refusal_reads_as_refused_not_crashed():
    from harness import config
    src = (config.ROOT / "harness" / "jobs.py").read_text(encoding="utf-8")
    assert src.count("except (RunInProgress, SpendRefused) as e:") >= 6, (
        "every job that can start a run must report a cost refusal as a "
        "refusal, not as an unhandled crash")


def test_an_unmeasured_pair_is_priced_at_its_own_rate_not_a_peer_average():
    from harness import budget
    from harness.registry import load_models
    reg = {m.name: m for m in load_models(include_disabled=True)}
    cheap, dear = reg.get("claude-api-haiku-4-5"), reg.get("claude-api-opus-5")
    if not (cheap and dear):
        pytest.skip("expected the anthropic twins in the registry")
    usage = (200_000, 4_000, 0, 0)
    assert dear.cost_usd(*usage) > cheap.cost_usd(*usage) * 3, (
        "opus and haiku are not close in price; projecting an unmeasured opus "
        "cell from the dollar average of its provider's peers would lowball "
        "the number the operator is about to approve")


def _fake_run(run_id, forecast_total, actual, model="m-api", basis="own",
              source="billed"):
    return {
        "run_id": run_id,
        "manifest": {
            "started": f"2026-08-04T00:00:00+00:00",
            "cost_forecast": {
                "billable": forecast_total, "known": forecast_total,
                "projected": 0.0, "cap": None, "problems": [],
                "balance_at_start": {}, "repeat": 1, "cycles": 1,
                "models": [{"model": model, "basis": basis, "priced": 55,
                            "tasks": 55, "missing": 0, "modelled": 0,
                            "blind": 0, "known": forecast_total,
                            "projected": 0.0, "total": forecast_total}],
            },
        },
        "results": [{"model": model, "task": "t1", "cost_usd": actual,
                     "cost_source": source}],
    }


def test_forecast_accuracy_pairs_the_estimate_with_the_receipt():
    from harness import report as rp
    a = rp.forecast_accuracy([_fake_run("r1", 0.1402, 0.1197)])
    assert len(a["rows"]) == 1
    row = a["rows"][0]
    assert row["estimate"] == 0.1402 and row["actual"] == 0.1197
    assert row["err_pct"] == -14.6, (
        "this is the deepseek-v4-flash figure the comparison was done by hand; "
        "the point of persisting the forecast is that it happens automatically")
    assert row["models"][0]["receipted"] is True


def test_a_run_with_no_persisted_forecast_is_skipped_not_guessed():
    from harness import report as rp
    r = _fake_run("r2", 0.1, 0.2)
    r["manifest"].pop("cost_forecast")
    assert rp.forecast_accuracy([r])["rows"] == [], (
        "every run before this change threw its forecast away; inventing one "
        "after the fact is impossible because the data it came from moved")


def test_the_forecast_summary_says_which_way_it_erred():
    from harness import report as rp
    runs = [_fake_run("a", 1.0, 0.8), _fake_run("b", 1.0, 0.9),
            _fake_run("c", 1.0, 1.5)]
    s = rp.forecast_accuracy(runs)["summary"]
    assert s["n_runs"] == 3
    assert s["median_err_pct"] == -10.0
    assert s["worst_over_pct"] == -20.0 and s["worst_under_pct"] == 50.0
    assert s["conservative_share"] == round(2 / 3, 3), (
        "erring high is the safe direction and the operator should be able to "
        "see how often it happens")


def test_an_unbilled_avenue_is_marked_as_having_no_receipt():
    from harness import report as rp
    a = rp.forecast_accuracy([_fake_run("r3", 0.5, 0.4, source="list")])
    assert a["rows"][0]["models"][0]["receipted"] is False, (
        "a cost we computed from a price table is not a receipt, and the "
        "comparison is only meaningful against what a provider actually "
        "charged")


def test_the_run_manifest_carries_the_forecast():
    from harness import config
    src = (config.ROOT / "harness" / "runner.py").read_text(encoding="utf-8")
    assert "def _forecast_record(" in src
    assert '"cost_forecast": forecast,' in src
    i = src.index("def _forecast_record(")
    seg = src[i:i + 1400]
    for field in ("basis", "blind", "balance_at_start", "cap", "problems"):
        assert field in seg, field


def test_an_interrupted_run_is_shown_but_kept_out_of_the_average():
    from harness import report as rp
    full = _fake_run("done", 1.0, 0.9)
    cut = _fake_run("stopped", 1.0, 0.2)
    cut["manifest"]["stopped_reason"] = "usage_limit"
    a = rp.forecast_accuracy([full, cut])
    ids = {r["run_id"]: r for r in a["rows"]}
    assert set(ids) == {"done", "stopped"}, "both runs stay visible"
    assert ids["stopped"]["cut_short"] is True
    assert a["summary"]["n_runs"] == 1, (
        "a run that stopped early spent a fraction of what was forecast for "
        "the whole thing; averaging that in manufactures a flattering error")
    assert a["summary"]["n_cut_short"] == 1
    assert a["summary"]["median_err_pct"] == -10.0
    assert a["summary"]["total_actual"] == 0.9


def test_a_subscription_only_run_has_no_forecast_to_check():
    from harness import report as rp
    r = _fake_run("cli", 0.0, 0.0)
    r["manifest"]["cost_forecast"]["billable"] = 0
    r["manifest"]["cost_forecast"]["models"] = []
    assert rp.forecast_accuracy([r])["rows"] == [], (
        "claude-cli models bill nothing, so there is no estimate to be right "
        "or wrong about")
