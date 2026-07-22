"""Version-over-version compare: the numbers must be like-for-like or nothing.

A model or family only compares on tasks it was scored on in BOTH versions, and
the headline delta uses only 'identical' tasks (same content_hash) — a task
whose test was edited between versions is shown but flagged, never folded into
the verdict, because a lower score there might be a harder test. For families,
a member new in the later version must never register as improvement.
"""

from harness import report


def _tdef(tid, cat, h):
    return type("T", (), {"id": tid, "category": cat, "content_hash": h})()


def _td(scores):
    """{tid: {model: score}} -> task_data-shaped {tid: {'agg': {model: {...}}}}."""
    d = {}
    for tid, per in scores.items():
        d[tid] = {"agg": {m: {"score": {"status": "scored", "score": s}}
                          for m, s in per.items()}}
    return d


TDEFS_A = {"py-x": _tdef("py-x", "coding-python", "h1"),
           "rs-y": _tdef("rs-y", "reasoning", "h2"),
           "old": _tdef("old", "reasoning", "h9")}
TDEFS_B = {"py-x": _tdef("py-x", "coding-python", "h1"),
           "rs-y": _tdef("rs-y", "reasoning", "hEDIT"),
           "new": _tdef("new", "coding-python", "h5")}


def test_headline_uses_only_identical_tasks():
    a = _td({"py-x": {"M": 0.5}, "rs-y": {"M": 1.0}, "old": {"M": 0.2}})
    b = _td({"py-x": {"M": 0.9}, "rs-y": {"M": 0.0}, "new": {"M": 1.0}})
    d = report.version_diff("M", a, TDEFS_A, b, TDEFS_B, "0.5", "0.6")
    assert d["overall"]["n"] == 1
    assert d["overall"]["delta"] == 0.4
    assert d["overall"]["verdict"] == "better"


def test_edited_task_is_flagged_not_counted():
    a = _td({"py-x": {"M": 0.5}, "rs-y": {"M": 1.0}})
    b = _td({"py-x": {"M": 0.5}, "rs-y": {"M": 0.0}})
    d = report.version_diff("M", a, TDEFS_A, b, TDEFS_B)
    tiers = {t["tid"]: t["tier"] for t in d["tasks"]}
    assert tiers["rs-y"] == "changed"
    assert "rs-y" in d["coverage"]["changed"]
    assert d["overall"]["verdict"] == "flat"


def test_added_and_retired_tasks_are_listed_not_compared():
    a = _td({"py-x": {"M": 1.0}, "old": {"M": 0.3}})
    b = _td({"py-x": {"M": 1.0}, "new": {"M": 0.7}})
    d = report.version_diff("M", a, TDEFS_A, b, TDEFS_B)
    assert [x["tid"] for x in d["coverage"]["retired"]] == ["old"]
    assert [x["tid"] for x in d["coverage"]["added"]] == ["new"]


def test_absent_in_either_version_returns_none():
    a = _td({"py-x": {"M": 1.0}})
    b = _td({"py-x": {"N": 1.0}})
    assert report.version_diff("M", a, TDEFS_A, b, TDEFS_B) is None
    assert report.version_diff("N", a, TDEFS_A, b, TDEFS_B) is None


def test_per_category_rollup():
    a = _td({"py-x": {"M": 0.4}, "rs-y": {"M": 0.6}})
    b = _td({"py-x": {"M": 0.8}, "rs-y": {"M": 0.6}})
    d = report.version_diff("M", a, TDEFS_A, b, TDEFS_A)
    cats = {c["cat"]: c for c in d["cats"]}
    assert cats["coding-python"]["delta"] == 0.4
    assert cats["reasoning"]["delta"] == 0.0



def test_family_pools_members_in_both_and_ignores_newcomers():
    a = _td({"py-x": {"M": 0.5, "N": 1.0}})
    b = _td({"py-x": {"M": 0.9, "N": 0.0, "K": 0.5}})
    fd = report.family_version_diff("Fam", {"M", "N", "K"},
                                    a, TDEFS_A, b, TDEFS_A, "0.5", "0.6")
    assert fd["overall"]["n_members"] == 2
    assert fd["coverage"]["added_members"] == ["K"]
    assert fd["overall"]["delta"] == -0.3
    assert fd["overall"]["verdict"] == "worse"


def test_family_members_sorted_worst_first():
    a = _td({"py-x": {"M": 0.5, "N": 1.0}})
    b = _td({"py-x": {"M": 0.9, "N": 0.0}})
    fd = report.family_version_diff("Fam", {"M", "N"}, a, TDEFS_A, b, TDEFS_A)
    assert [m["model"] for m in fd["members"]] == ["N", "M"]


def test_family_none_when_no_member_spans_both():
    a = _td({"py-x": {"M": 1.0}})
    b = _td({"py-x": {"N": 1.0}})
    assert report.family_version_diff("Fam", {"M", "N"}, a, TDEFS_A, b, TDEFS_A) is None



def test_model_payload_lists_versions_and_all_pairs():
    versions = [
        ("0.4", _td({"py-x": {"M": 0.5}}), TDEFS_A),
        ("0.5", _td({"py-x": {"M": 0.7}}), TDEFS_A),
        ("0.6", _td({"py-x": {"M": 0.9}}), TDEFS_A),
    ]
    p = report.model_version_payload("M", versions)
    assert p["versions"] == ["0.4", "0.5", "0.6"]
    assert set(p["pairs"]) == {"0.4|0.5", "0.4|0.6", "0.5|0.6"}
    assert p["pairs"]["0.4|0.6"]["overall"]["delta"] == 0.4


def test_model_payload_skips_versions_without_the_model():
    versions = [
        ("0.4", _td({"py-x": {"OTHER": 0.5}}), TDEFS_A),
        ("0.5", _td({"py-x": {"M": 0.7}}), TDEFS_A),
        ("0.6", _td({"py-x": {"M": 0.9}}), TDEFS_A),
    ]
    p = report.model_version_payload("M", versions)
    assert p["versions"] == ["0.5", "0.6"]
    assert set(p["pairs"]) == {"0.5|0.6"}
