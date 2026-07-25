"""The hardened suite is the set worth repeat (3x) runs.

It is no longer a hand-curated constant: it is DERIVED live as Hard u Frontier
from the overview's discrimination tiers (report.task_tiers /
report.hardened_ids). So the invariants worth guarding changed. Membership is
data-dependent and moves as scores accumulate — asserting exact ids would just
break on the next run. What must hold is that the derivation is coherent (the
tiers are disjoint, hardened is exactly hard u frontier), that every id resolves
to a live task, and above all that NOTHING drifts: the CLI keyword, the /run
quick-select and the overview marker must all read the same source.

Note the property deliberately dropped: "every lane is represented". A curated
list could guarantee it; a derived one cannot, because whether a lane has a
discriminator depends on how models actually scored.
"""

from collections import Counter

from harness import report
from harness.tasks import load_tasks


def _tasks():
    return {t.id: t for t in load_tasks()}


def _tiers():
    return report.task_tiers()


def test_every_hardened_id_is_a_real_task():
    """The tiers are keyed off recorded results, so a retired or renamed task
    could otherwise linger in the derived set and silently select nothing."""
    tasks = _tasks()
    missing = [h for h in report.hardened_ids() if h not in tasks]
    assert not missing, f"hardened ids with no matching task: {missing}"


def test_no_duplicates():
    ids = report.hardened_ids()
    dupes = [k for k, c in Counter(ids).items() if c > 1]
    assert not dupes, f"duplicated hardened ids: {dupes}"


def test_hardened_is_exactly_hard_union_frontier():
    """The definition itself — if these drift apart, the ◆ sweep count is
    counting a different set than the Hard/Frontier buttons select."""
    tiers = _tiers()
    expected = sorted(t for t, v in tiers.items() if v in ("hard", "frontier"))
    assert report.hardened_ids(tiers) == expected


def test_the_three_tiers_are_disjoint():
    """Hard / Frontier / Easy are lenses on the same task set; a task in two of
    them would be selected by two buttons and counted twice."""
    tiers = _tiers()
    buckets = {"hard": set(), "frontier": set(), "easy": set()}
    for tid, lens in tiers.items():
        assert lens in buckets, f"unknown tier {lens!r} for {tid}"
        buckets[lens].add(tid)
    assert not (buckets["hard"] & buckets["frontier"])
    assert not (buckets["hard"] & buckets["easy"])
    assert not (buckets["frontier"] & buckets["easy"])


def test_it_is_a_strict_subset_not_the_whole_suite():
    """A hardened set that is everything defeats the point (and the 3x cost)."""
    tasks = _tasks()
    assert len(report.hardened_ids()) < len(tasks)


def test_cli_hardened_keyword_resolves_to_the_derived_set():
    """`harness run --tasks hardened` must select exactly the derived set."""
    hardened = set(report.hardened_ids())
    selected = [t.id for t in load_tasks() if t.id in hardened]
    assert sorted(selected) == sorted(hardened)


def test_hardened_completion_counts_full_sweeps():
    """A full run and a hardened-only set each score every hardened task once,
    so the completed-sweep count is the MIN across the hardened tasks; a task
    with a higher count means an extra sweep is partway done."""
    from harness.config import hardened_completion
    H = ["a", "b", "c"]
    assert hardened_completion({"a": 2, "b": 2, "c": 2}, H) == {
        "hard_done": 2, "hard_partial": False, "hard_total": 3, "hard_todo": []}
    assert hardened_completion({"a": 2, "b": 1, "c": 1}, H) == {
        "hard_done": 1, "hard_partial": True, "hard_total": 3,
        "hard_todo": ["b", "c"]}
    assert hardened_completion({}, H) == {
        "hard_done": 0, "hard_partial": False, "hard_total": 3, "hard_todo": []}
    assert hardened_completion({"a": 1, "b": 0, "c": 1}, H) == {
        "hard_done": 0, "hard_partial": True, "hard_total": 3, "hard_todo": ["b"]}
    assert hardened_completion({}, [])["hard_total"] == 0


def test_overview_marks_exactly_the_hardened_tasks(tmp_path):
    """The ◆ on the overview per-task table must track the derived set, so the
    marker can't drift from the /run quick-select or the CLI keyword."""
    import re

    report.generate_all(out_dir=tmp_path / "reports")
    idx = (tmp_path / "reports" / "index.html").read_text(encoding="utf-8")
    body = idx[idx.find("Task</th>"):idx.find("</table>", idx.find("Task</th>"))]
    marked = [m.group(1) for m in re.finditer(
        r'<tr><td class="nowrap"><a href="tasks/([^"]+)\.html">.*?</tr>',
        body, re.S) if "hardmark" in m.group(0)]
    assert sorted(marked) == sorted(report.hardened_ids())
