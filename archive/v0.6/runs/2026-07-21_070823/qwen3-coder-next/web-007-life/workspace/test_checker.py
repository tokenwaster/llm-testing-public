import os
from pathlib import Path

import pytest

APP = Path(__file__).parent / "app.html"

for _parent in Path(__file__).resolve().parents:
    _pw = _parent / ".pw-browsers"
    if _pw.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_pw)
        break


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
        browser = _launch(p)
        pg = browser.new_page()
        pg.goto(APP.as_uri())
        pg.wait_for_timeout(400)
        yield pg
        browser.close()


def test_layout_elements(page):
    for sel in ("#life", "#step", "#play", "#random", "#clear"):
        assert page.locator(sel).count() == 1, f"missing {sel}"
    box = page.locator("#life").bounding_box()
    assert box and box["width"] >= 380 and box["height"] >= 380, \
        f"grid renders {box} — spec requires >=400x400"


def test_api_shape(page):
    shape = page.evaluate("""() => ({
        ok: typeof window.life === 'object' && !!window.life,
        w: window.life && window.life.w, h: window.life && window.life.h,
        fns: window.life && ['step','get','set','clear'].every(
            f => typeof window.life[f] === 'function'),
    })""")
    assert shape["ok"] and shape["fns"], f"window.life incomplete: {shape}"
    assert shape["w"] >= 40 and shape["h"] >= 40, \
        f"grid {shape['w']}x{shape['h']} — spec requires >=40x40"


def test_clear_empties(page):
    live = page.evaluate("""() => {
        const L = window.life; L.set(5,5,1); L.set(6,6,1); L.clear();
        let n = 0;
        for (let x = 0; x < L.w; x++) for (let y = 0; y < L.h; y++) n += L.get(x,y);
        return n;
    }""")
    assert live == 0, f"clear() left {live} live cells"


def test_block_is_still_life(page):
    got = page.evaluate("""() => {
        const L = window.life; L.clear();
        // 2x2 block at (10,10) is stable under B3/S23
        for (const [x,y] of [[10,10],[11,10],[10,11],[11,11]]) L.set(x,y,1);
        L.step();
        return [[10,10],[11,10],[10,11],[11,11]].map(([x,y]) => L.get(x,y));
    }""")
    assert got == [1, 1, 1, 1], f"2x2 block did not survive as a still life: {got}"


def test_lone_cell_dies(page):
    got = page.evaluate("""() => {
        const L = window.life; L.clear(); L.set(20,20,1); L.step();
        return L.get(20,20);
    }""")
    assert got == 0, "a lone cell (0 neighbors) must die from underpopulation"


def test_blinker_oscillates(page):
    got = page.evaluate("""() => {
        const L = window.life; L.clear();
        // horizontal blinker at row 15, cols 14-16
        L.set(14,15,1); L.set(15,15,1); L.set(16,15,1);
        L.step();
        // after 1 step it must be a VERTICAL blinker at col 15, rows 14-16
        const vert = [L.get(15,14), L.get(15,15), L.get(15,16)];
        const oldEnds = [L.get(14,15), L.get(16,15)];  // must have died
        L.step();
        const backHoriz = [L.get(14,15), L.get(15,15), L.get(16,15)];
        return { vert, oldEnds, backHoriz };
    }""")
    assert got["vert"] == [1, 1, 1] and got["oldEnds"] == [0, 0], \
        f"blinker did not rotate to vertical after 1 step: {got} " \
        "(a common cause is in-place, non-simultaneous update)"
    assert got["backHoriz"] == [1, 1, 1], \
        f"blinker did not return to horizontal after 2 steps: {got['backHoriz']}"


def test_glider_travels(page):
    """A glider returns to its shape shifted by (+1,+1) every 4 steps. This
    only holds with correct B3/S23 rules AND simultaneous update."""
    moved = page.evaluate("""() => {
        const L = window.life; L.clear();
        // standard glider, top-left at (5,5)
        const g = [[6,5],[7,6],[5,7],[6,7],[7,7]];
        for (const [x,y] of g) L.set(x,y,1);
        for (let s = 0; s < 4; s++) L.step();
        // expected: same 5 cells, each shifted by (+1,+1)
        const exp = g.map(([x,y]) => [x+1,y+1]);
        const hit = exp.every(([x,y]) => L.get(x,y) === 1);
        let total = 0;
        for (let x = 0; x < L.w; x++) for (let y = 0; y < L.h; y++) total += L.get(x,y);
        return { hit, total };
    }""")
    assert moved["hit"] and moved["total"] == 5, \
        f"glider did not advance to (+1,+1) as 5 live cells after 4 steps: {moved}"


def test_canvas_visibly_drawn(page):
    ok = page.evaluate("""() => {
        const L = window.life; L.clear();
        // several 2x2 blocks (still-lifes) then step() — the spec guarantees
        // step() redraws, and blocks persist, so live cells must be on screen
        for (const [bx,by] of [[8,8],[8,20],[20,8],[20,20],[14,14]])
          for (const [dx,dy] of [[0,0],[1,0],[0,1],[1,1]]) L.set(bx+dx,by+dy,1);
        L.step();
        const c = document.querySelector('#life');
        if (!c || c.tagName !== 'CANVAS') {
            return document.querySelector('#life').querySelectorAll('*').length >= 100 ? 1 : 0;
        }
        const d = c.getContext('2d').getImageData(0,0,c.width,c.height).data;
        let lit = 0;
        for (let i = 0; i < d.length; i += 4)
            if (d[i] + d[i+1] + d[i+2] > 60) lit++;
        return lit > 20 ? 1 : 0;
    }""")
    assert ok == 1, "live cells are not visibly rendered on the grid"
