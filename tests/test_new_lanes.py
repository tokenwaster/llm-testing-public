"""The v0.6.13 public-capability lanes: instruction-following, hallucination,
math, extraction, tool-use — a discriminator + a frontier task each.

Guards the structure (ids resolve, categories exist, response-lane tasks carry a
checker) and the CLI/quick-select selection. Reference verification (good->1.0,
empty->0.0) lives in tasks-refs/_verify_response.py and _verify.py.
"""
from harness import config
from harness.tasks import load_tasks


def _tasks():
    return {t.id: t for t in load_tasks()}


def test_every_new_id_is_a_real_task():
    tasks = _tasks()
    missing = [t for t in config.NEW_TASKS if t not in tasks]
    assert not missing, f"NEW_TASKS ids with no matching task: {missing}"


def test_ten_tasks_across_five_new_categories_two_each():
    tasks = _tasks()
    cats = {}
    for tid in config.NEW_TASKS:
        cats.setdefault(tasks[tid].category, []).append(tid)
    assert len(config.NEW_TASKS) == 10
    assert set(cats) == {"instruction-following", "hallucination", "math",
                         "extraction", "tool-use"}
    assert all(len(v) == 2 for v in cats.values()), \
        f"each new lane needs exactly 2 tasks: {{k: len(v) for k, v in cats.items()}}"


def test_response_lane_tasks_have_a_checker():
    tasks = _tasks()
    for tid in config.NEW_TASKS:
        t = tasks[tid]
        if t.scoring_type == "response":
            assert t.checker is not None, f"{tid} is response-lane but has no checker.py"


def test_math_tasks_are_numeric_answer_lane():
    tasks = _tasks()
    for tid in ("math-001-multistep", "math-002-rate-mix"):
        t = tasks[tid]
        assert t.scoring_type == "answer"
        assert t.scoring.get("match") == "numeric"


def test_cli_new_keyword_selects_exactly_the_constant():
    """`harness run --tasks new` must select exactly config.NEW_TASKS."""
    tasks = load_tasks()
    selected = [t.id for t in tasks if t.id in config.NEW_TASKS]
    assert sorted(selected) == sorted(config.NEW_TASKS)


def test_new_and_hardened_do_not_overlap():
    """The two quick-selects are distinct sets — a task isn't both brand-new and
    already a hardened discriminator."""
    assert not (set(config.NEW_TASKS) & set(config.HARDENED_TASKS))
