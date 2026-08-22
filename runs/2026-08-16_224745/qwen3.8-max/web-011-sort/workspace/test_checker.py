import os
from pathlib import Path

import pytest

APP = Path(__file__).parent / "app.html"
for _p in Path(__file__).resolve().parents:
    if (_p / ".pw-browsers").is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_p / ".pw-browsers"); break


def _launch(p):
    try:
        return p.chromium.launch()
    except Exception:
        return p.chromium.launch(channel="chromium")


@pytest.fixture(scope="module")
def page():
    assert APP.exists(), "app.html missing"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = _launch(p); pg = b.new_page(); pg.goto(APP.as_uri()); pg.wait_for_timeout(400)
        yield pg; b.close()


INPUT = [7, 2, 11, 5, 0, 9, 3, 10, 1, 8, 4, 6]
MAX_MOVED_PER_STEP = 3
_DRIVE = {}


def _drive(page):
    if "r" in _DRIVE:
        return _DRIVE["r"]
    try:
        got = page.evaluate("""(input) => {
            const v = window.viz;
            v.setArray(input);
            const sortedCopy = input.slice().sort((a,b)=>a-b);
            const key = a => JSON.stringify(a);
            let prev = v.array().slice(), steps = 0, maxMoved = 0;
            let firstMoved = null, firstSorted = null, stillPermutation = true;
            while (!v.sorted() && steps < 100000) {
                v.sortStep(); steps++;
                const cur = v.array().slice();
                let moved = cur.length === prev.length ? 0 : cur.length + prev.length;
                for (let k = 0; k < cur.length; k++) if (cur[k] !== prev[k]) moved++;
                if (moved > maxMoved) maxMoved = moved;
                if (key(cur.slice().sort((a,b)=>a-b)) !== key(sortedCopy)) stillPermutation = false;
                if (steps === 1) { firstMoved = moved; firstSorted = v.sorted(); }
                prev = cur;
            }
            const out = v.array();
            return { out, steps, maxMoved, firstMoved, firstSorted, stillPermutation,
                     correct: key(out) === key(sortedCopy) };
        }""", INPUT)
    except Exception as e:
        got = {"error": str(e).splitlines()[0][:200]}
    _DRIVE["r"] = got
    return got


def _core_contract(page):
    got = _drive(page)
    assert "error" not in got, f"driving sortStep() raised: {got['error']}"
    assert got["correct"], \
        f"driving sortStep() to completion did not sort the array: {got}"
    assert got["stillPermutation"], "the array stopped being a permutation of the input mid-sort"
    assert got["firstSorted"] is False, \
        f"one sortStep() fully sorted a {len(INPUT)}-element array (one-shot sort): {got}"
    assert got["steps"] >= len(INPUT) - 1, \
        f"{got['steps']} sortStep() call(s) sorted {len(INPUT)} elements; a comparison sort " \
        f"needs at least {len(INPUT) - 1} comparisons, so this is not one step per call"
    assert got["maxMoved"] <= MAX_MOVED_PER_STEP, \
        f"a single sortStep() moved {got['maxMoved']} elements " \
        f"(expect <= {MAX_MOVED_PER_STEP} for one comparison/swap per step): {got}"
    return got


def test_layout(page):
    _core_contract(page)
    for sel in ("#bars", "#sort", "#shuffle", "#reset"):
        assert page.locator(sel).count() == 1, f"missing {sel}"


def test_api_shape(page):
    _core_contract(page)
    s = page.evaluate("""() => ({
        ok: typeof window.viz === 'object' && !!window.viz,
        fns: window.viz && ['array','setArray','sortStep','sorted'].every(
            f => typeof window.viz[f] === 'function'),
    })""")
    assert s["ok"] and s["fns"], f"window.viz incomplete: {s}"


def test_setarray_roundtrip(page):
    _core_contract(page)
    got = page.evaluate("() => { window.viz.setArray([4,1,3,2]); return window.viz.array(); }")
    assert got == [4, 1, 3, 2], f"setArray/array roundtrip failed: {got}"


def test_sorted_flag(page):
    _core_contract(page)
    got = page.evaluate("""() => {
        const v = window.viz;
        v.setArray([3,1,2]); const a = v.sorted();
        v.setArray([1,2,3]); const b = v.sorted();
        return [a, b];
    }""")
    assert got == [False, True], f"sorted() wrong: {got}"


def test_sortstep_sorts_the_array(page):
    got = _core_contract(page)
    assert got["correct"] and got["steps"] >= len(INPUT) - 1


def test_sortstep_is_one_step(page):
    got = _core_contract(page)
    assert got["firstSorted"] is False
    assert got["firstMoved"] is not None and got["firstMoved"] <= MAX_MOVED_PER_STEP, \
        f"first sortStep() moved {got['firstMoved']} elements (expect <= {MAX_MOVED_PER_STEP}): {got}"
    assert got["maxMoved"] <= MAX_MOVED_PER_STEP


def test_bars_rendered(page):
    _core_contract(page)
    n = page.evaluate("""() => {
        window.viz.setArray([1,2,3,4,5,6,7,8]);
        return document.querySelectorAll('#bars .bar').length;
    }""")
    assert n >= 8, f"#bars shows {n} bars for an 8-element array (expect >= 8)"
