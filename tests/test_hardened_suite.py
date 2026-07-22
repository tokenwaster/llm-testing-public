"""The hardened suite is the curated set worth repeat (3x) runs.

It is provisional and meant to be edited as the baseline finishes, so guard the
invariants rather than the exact membership: every id must resolve to a live
task (a typo or a renamed task would silently select nothing), there are no
duplicates, and every lane is represented (a hardened suite that skips a whole
category can't speak to that category's consistency).
"""

from collections import Counter

from harness import config
from harness.tasks import load_tasks


def _tasks():
    return {t.id: t for t in load_tasks()}


def test_every_hardened_id_is_a_real_task():
    tasks = _tasks()
    missing = [h for h in config.HARDENED_TASKS if h not in tasks]
    assert not missing, f"hardened ids with no matching task: {missing}"


def test_no_duplicates():
    dupes = [k for k, c in Counter(config.HARDENED_TASKS).items() if c > 1]
    assert not dupes, f"duplicated hardened ids: {dupes}"


def test_every_established_lane_is_represented():
    """Every ESTABLISHED lane must have a hardened task. The v0.6.13 capability
    lanes (config.NEW_TASKS) start unhardened on purpose — a discriminator can
    only be chosen once a baseline exists, and theirs is still being collected."""
    tasks = _tasks()
    new_cats = {tasks[t].category for t in config.NEW_TASKS if t in tasks}
    established = {t.category for t in tasks.values()} - new_cats
    covered = {tasks[h].category for h in config.HARDENED_TASKS}
    assert established <= covered, \
        f"established lanes with no hardened task: {established - covered}"


def test_it_is_a_strict_subset_not_the_whole_suite():
    """A hardened set that is everything defeats the point (and 3x cost)."""
    tasks = _tasks()
    assert 0 < len(config.HARDENED_TASKS) < len(tasks)


def test_cli_hardened_keyword_resolves_to_the_constant():
    """`harness run --tasks hardened` must select exactly the constant."""
    tasks = load_tasks()
    selected = [t.id for t in tasks if t.id in config.HARDENED_TASKS]
    assert sorted(selected) == sorted(config.HARDENED_TASKS)


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
    """The ◆ on the overview per-task table must track the constant, so the
    marker can't drift from the /run quick-select or the CLI keyword."""
    import re

    from harness import report
    report.generate_all(out_dir=tmp_path / "reports")
    idx = (tmp_path / "reports" / "index.html").read_text(encoding="utf-8")
    body = idx[idx.find("Task</th>"):idx.find("</table>", idx.find("Task</th>"))]
    marked = [m.group(1) for m in re.finditer(
        r'<tr><td class="nowrap"><a href="tasks/([^"]+)\.html">.*?</tr>',
        body, re.S) if "hardmark" in m.group(0)]
    assert sorted(marked) == sorted(config.HARDENED_TASKS)
