import types
from pathlib import Path

import pytest

from harness import config, runner
from harness.registry import Model


OPERATOR_ONLY = pytest.mark.skipif(
    not config.is_operator_build(), reason="private operator surface is not exported")


def _m(name="lm", local=True, provider="openai"):
    return Model(name=name, provider=provider, model="x/y",
                 base_url="http://localhost:1234/v1", local=local)


def _task(tid, prompt="p", tier=0):
    return types.SimpleNamespace(id=tid, prompt=prompt, tier=tier,
                                 content_hash="h", category="c",
                                 scoring_type="answer", title=tid)


@pytest.fixture
def lms_present(monkeypatch):
    monkeypatch.setattr("harness.lmstudio.lms_exe", lambda: "lms.exe")


def test_a_single_trial_never_cycles(lms_present):
    assert runner.cycling_models([_m()], 1) == []


def test_a_cloud_model_never_cycles(lms_present):
    assert runner.cycling_models([_m(local=False)], 3) == []


def test_a_local_model_cycles_when_repeats_are_asked_for(lms_present):
    assert [m.name for m in runner.cycling_models([_m()], 3)] == ["lm"]


def test_without_lms_control_a_local_model_cannot_cycle(monkeypatch):
    monkeypatch.setattr("harness.lmstudio.lms_exe", lambda: None)
    assert runner.cycling_models([_m()], 3) == []


def test_cycles_for_and_cycling_models_are_one_rule(lms_present):
    dirs = [Path("a"), Path("b"), Path("c")]
    assert runner.cycles_for(_m(), dirs) == dirs
    assert runner.cycles_for(_m(local=False), dirs) == dirs[:1]
    assert runner.cycles_for(_m(), dirs[:1]) == dirs[:1]


def test_run_ids_are_unique_even_when_minted_in_one_second(tmp_path):
    ids = runner.new_run_ids(5, base=tmp_path)
    assert len(ids) == 5 and len(set(ids)) == 5


def test_run_ids_never_collide_with_a_run_already_on_disk(tmp_path):
    first = runner.new_run_ids(1, base=tmp_path)[0]
    (tmp_path / first).mkdir()
    assert first not in runner.new_run_ids(3, base=tmp_path)


def test_each_bucket_is_loaded_once_no_matter_how_many_cycles(monkeypatch,
                                                             tmp_path):
    loads, ran = [], []

    s1, s2 = _task("s1", "x" * 100), _task("s2", "x" * 100)
    big = _task("big", "x" * 400_000)
    model = _m()

    monkeypatch.setattr(runner, "make_adapter", lambda m: object())
    monkeypatch.setattr(runner, "load_plan",
                        lambda *a, **k: [(8192, "max", [s1, s2]),
                                         (131072, "auto", [big])])
    monkeypatch.setattr("harness.lmstudio.lms_exe", lambda: "lms.exe")
    monkeypatch.setattr("harness.lmstudio.unload_all", lambda **k: True)
    monkeypatch.setattr("harness.lmstudio.model_info", lambda *a, **k: {})
    monkeypatch.setattr("harness.lmstudio.load_model",
                        lambda mdl, **k: loads.append(k["context_length"]) or 1.0)
    monkeypatch.setattr(runner, "gguf", types.SimpleNamespace(
        footprint=lambda *_: None))
    monkeypatch.setattr(runner, "_gpu_vram_mb", lambda: 24576)
    monkeypatch.setattr(runner, "_stamp_load_plan", lambda *a: None)

    class FakeRunner:
        def __init__(self, run_dir, *a, **k):
            self.run_dir = run_dir

        def warm_up(self, **k):
            return {"warmup_error": None, "cold_start_ms": 1.0}

        def run_task(self, task):
            ran.append((self.run_dir.name, task.id))
            return {"status": "ok", "wall_ms": 1.0, "tokens_in": 1,
                    "tokens_out": 1, "n_retries": 0}

    monkeypatch.setattr(runner, "TaskRunner", FakeRunner)
    monkeypatch.setattr(runner, "read_json", lambda *a, **k: {"score": 1.0},
                        raising=False)

    dirs = [tmp_path / f"r{i}" for i in range(3)]
    for d in dirs:
        (d / model.name).mkdir(parents=True)

    runner.run_model_cycles(dirs, model, [s1, s2, big],
                            progress=lambda *_: None, manage_memory=False)

    assert loads == [8192, 131072], (
        f"each context bucket must load exactly once, got {loads}")
    assert ran == [("r0", "s1"), ("r0", "s2"),
                   ("r1", "s1"), ("r1", "s2"),
                   ("r2", "s1"), ("r2", "s2"),
                   ("r0", "big"), ("r1", "big"), ("r2", "big")], (
        "a cycle must sweep the whole bucket before the next cycle starts, "
        f"not repeat one task N times: {ran}")


def test_the_manifest_records_which_cycle_a_run_dir_is(tmp_path):
    model = _m()
    t = _task("t1")
    solo = runner._manifest([model], [t], tmp_path, "tag", False, 0, 1, "g")
    assert "cycle" not in solo
    second = runner._manifest([model], [t], tmp_path, "tag", False, 1, 3, "g0")
    assert second["cycle"] == 2 and second["cycles"] == 3
    assert second["cycle_group"] == "g0"


def test_progress_is_written_to_every_cycles_log(tmp_path):
    dirs = [tmp_path / "a", tmp_path / "b"]
    for d in dirs:
        d.mkdir()
    wrapped = runner._persisting_progress(dirs, lambda _: None)
    wrapped("hello")
    for d in dirs:
        assert "hello" in (d / "run.log").read_text(encoding="utf-8")


def test_a_single_run_dir_still_accepts_a_bare_path(tmp_path):
    wrapped = runner._persisting_progress(tmp_path, lambda _: None)
    wrapped("solo")
    assert "solo" in (tmp_path / "run.log").read_text(encoding="utf-8")


def test_stopping_a_model_marks_every_cycles_manifest(tmp_path):
    from harness.util import read_json, write_json
    dirs = [tmp_path / f"r{i}" for i in range(3)]
    for d in dirs:
        d.mkdir()
        write_json(d / "run.json", {"run_id": d.name})
    runner._stop_all(dirs, "lm", "usage_limit", {"reset_at": 123})
    for d in dirs:
        mani = read_json(d / "run.json", {})
        assert mani["stopped_reason"] == "usage_limit"
        assert mani["stopped_models"] == ["lm"]
        assert mani["reset_at"] == 123


def test_no_function_in_the_cli_shadows_a_module_level_import():
    import ast

    from harness import config
    src = (config.ROOT / "harness" / "__main__.py").read_text(encoding="utf-8")
    tree = ast.parse(src)

    def names(node):
        out = set()
        for a in node.names:
            if isinstance(node, ast.Import):
                out.add(a.asname or a.name.split(".")[0])
            else:
                out.add(a.asname or a.name)
        return out

    top = set()
    for n in tree.body:
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            top |= names(n)

    bad = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for n in ast.walk(fn):
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                for name in names(n) & top:
                    bad.append(f"{fn.name}() line {n.lineno} re-imports '{name}'")
    assert not bad, (
        "a function-local import of a module-level name makes that name local "
        "for the WHOLE function, so any use outside the importing branch raises "
        "UnboundLocalError:\n  " + "\n  ".join(bad))


def _plan_stub(monkeypatch, plan):
    monkeypatch.setattr("harness.lmstudio.lms_exe", lambda: "lms.exe")
    monkeypatch.setattr(runner, "load_plan", lambda *a, **k: plan)
    monkeypatch.setattr(runner, "_gpu_vram_mb", lambda: 32607)
    monkeypatch.setattr(runner, "gguf",
                        types.SimpleNamespace(footprint=lambda *_: None))


def test_the_banner_says_nothing_when_nothing_will_cycle(monkeypatch):
    _plan_stub(monkeypatch, [(8192, "max", [_task("t")])])
    assert runner.cycle_plan_summary([_m()], [_task("t")], 1) == []
    assert runner.cycle_plan_summary([_m(local=False)], [_task("t")], 3) == []


def test_the_banner_reports_one_load_when_the_plan_merges(monkeypatch):
    t1, t2 = _task("a"), _task("b")
    _plan_stub(monkeypatch, [(131072, "max", [t1, t2])])
    line = runner.cycle_plan_summary([_m()], [t1, t2], 2)[0]
    assert "1 model load(s)" in line
    assert "was 2 loads" in line
    assert "131,072 max (2 tasks)" in line


def test_the_banner_names_every_load_when_the_plan_splits(monkeypatch):
    t1, t2 = _task("a"), _task("b")
    _plan_stub(monkeypatch, [(81920, "max", [t1]), (212992, "auto", [t2])])
    line = runner.cycle_plan_summary([_m()], [t1, t2], 2)[0]
    assert "2 model load(s)" in line
    assert "was 4 loads" in line
    assert "81,920 max (1 task)" in line and "212,992 auto (1 task)" in line


def test_the_banner_load_count_is_the_plan_not_a_guess(monkeypatch):
    tasks = [_task(f"t{i}") for i in range(4)]
    plan = [(65536, "max", tasks[:2]), (131072, "auto", tasks[2:3]),
            (212992, "auto", tasks[3:])]
    _plan_stub(monkeypatch, plan)
    line = runner.cycle_plan_summary([_m()], tasks, 3)[0]
    assert f"{len(plan)} model load(s)" in line
    assert f"was {len(plan) * 3} loads" in line


@OPERATOR_ONLY
def test_no_caller_prints_a_cycle_promise_of_its_own():
    from harness import config
    for name in ("__main__.py", "jobs.py"):
        src = (config.ROOT / "harness" / name).read_text(encoding="utf-8")
        assert "will cycle" not in src, (
            f"{name} must report the real load plan via cycle_plan_summary, "
            f"not promise cycling before the plan is known")
        assert "cycle_plan_summary" in src


def _cell(score, sigma, n_scored):
    return {"score": {"status": "scored", "score": score},
            "score_sigma": sigma, "n_scored": n_scored, "n_runs": n_scored}


def test_repeat_coverage_splits_measured_from_never_repeated():
    from harness import report
    td = {"t1": {"agg": {"m": _cell(1.0, 0.0, 3)}},
          "t2": {"agg": {"m": _cell(1.0, None, 1)}},
          "t3": {"agg": {"m": _cell(0.5, 0.5, 2)}}}
    rc = report.repeat_coverage(td, {"t1", "t2", "t3"})
    s = rc["models"]["m"]
    assert s["have"] == ["t1", "t3"]
    assert s["todo"] == ["t2"], "a single-run cell has no spread, so it is todo"
    assert s["unstable"] == ["t3"]
    assert rc["unstable_tasks"] == ["t3"]


def test_a_reproducible_cell_is_never_called_unstable():
    from harness import report
    td = {"t1": {"agg": {"m": _cell(1.0, 0.0, 5)}}}
    rc = report.repeat_coverage(td, {"t1"})
    assert rc["models"]["m"]["have"] == ["t1"]
    assert rc["models"]["m"]["unstable"] == []
    assert rc["unstable_tasks"] == []


def test_the_threshold_is_one_number_and_it_is_documented():
    from harness import report
    assert report.UNSTABLE_SIGMA == 0.125
    td = {"t1": {"agg": {"m": _cell(0.5, report.UNSTABLE_SIGMA, 2)}},
          "t2": {"agg": {"m": _cell(0.5, report.UNSTABLE_SIGMA - 0.001, 2)}}}
    rc = report.repeat_coverage(td, {"t1", "t2"})
    assert rc["models"]["m"]["unstable"] == ["t1"], "the threshold is inclusive"


def test_a_task_outside_the_live_set_is_ignored():
    from harness import report
    td = {"live": {"agg": {"m": _cell(0.5, 0.5, 2)}},
          "retired": {"agg": {"m": _cell(0.5, 0.5, 2)}}}
    rc = report.repeat_coverage(td, {"live"})
    assert rc["unstable_tasks"] == ["live"]
    assert rc["models"]["m"]["have"] == ["live"]


def test_an_unscored_cell_counts_as_neither():
    from harness import report
    td = {"t1": {"agg": {"m": {"score": {"status": "error"}, "n_scored": 0,
                               "score_sigma": None}}}}
    rc = report.repeat_coverage(td, {"t1"})
    assert rc["models"]["m"] == {"have": [], "todo": [], "unstable": []}


@OPERATOR_ONLY
def test_the_run_page_wires_both_badges_and_the_unstable_button():
    from harness import config
    ui = (config.ROOT / "harness" / "review.py").read_text(encoding="utf-8")
    for hook in ("pickunstable", "t-unstable", 'data-unstable="${t.unstable',
                 "gcovclick", "gbadclick", "sig_todo", "sig_unstable",
                 "repeat_coverage"):
        assert hook in ui, hook
    assert "rep.value = String(repeat)" in ui, (
        "a one-click repeat target must also set the Repeat control, or the "
        "click still needs a second manual step")
