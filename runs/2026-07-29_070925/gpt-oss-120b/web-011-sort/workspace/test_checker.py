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


def test_layout(page):
    for sel in ("#bars", "#sort", "#shuffle", "#reset"):
        assert page.locator(sel).count() == 1, f"missing {sel}"


def test_api_shape(page):
    s = page.evaluate("""() => ({
        ok: typeof window.viz === 'object' && !!window.viz,
        fns: window.viz && ['array','setArray','sortStep','sorted'].every(
            f => typeof window.viz[f] === 'function'),
    })""")
    assert s["ok"] and s["fns"], f"window.viz incomplete: {s}"


def test_setarray_roundtrip(page):
    got = page.evaluate("() => { window.viz.setArray([4,1,3,2]); return window.viz.array(); }")
    assert got == [4, 1, 3, 2], f"setArray/array roundtrip failed: {got}"


def test_sorted_flag(page):
    got = page.evaluate("""() => {
        const v = window.viz;
        v.setArray([3,1,2]); const a = v.sorted();
        v.setArray([1,2,3]); const b = v.sorted();
        return [a, b];
    }""")
    assert got == [False, True], f"sorted() wrong: {got}"


def test_sortstep_sorts_the_array(page):
    got = page.evaluate("""() => {
        const v = window.viz;
        const input = [5,3,8,1,9,2,7,4,6,0];
        v.setArray(input);
        let steps = 0;
        while (!v.sorted() && steps < 100000) { v.sortStep(); steps++; }
        const out = v.array();
        const sortedCopy = input.slice().sort((a,b)=>a-b);
        return { out, correct: JSON.stringify(out) === JSON.stringify(sortedCopy),
                 permutation: JSON.stringify(out.slice().sort((a,b)=>a-b)) ===
                              JSON.stringify(sortedCopy), steps };
    }""")
    assert got["correct"], \
        f"driving sortStep() to completion did not sort the array: {got}"
    assert got["permutation"], "the sorted output is not a permutation of the input"


def test_bars_rendered(page):
    n = page.evaluate("""() => {
        window.viz.setArray([1,2,3,4,5,6,7,8]);
        return document.querySelectorAll('#bars .bar').length;
    }""")
    assert n >= 8, f"#bars shows {n} bars for an 8-element array (expect >= 8)"
