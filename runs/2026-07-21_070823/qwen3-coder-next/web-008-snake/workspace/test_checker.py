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
    for sel in ("#snake", "#start", "#pause", "#reset"):
        assert page.locator(sel).count() == 1, f"missing {sel}"
    box = page.locator("#snake").bounding_box()
    assert box and box["width"] >= 380 and box["height"] >= 380, \
        f"board renders {box} — spec requires >=400x400"


def test_api_shape(page):
    shape = page.evaluate("""() => ({
        ok: typeof window.game === 'object' && !!window.game,
        w: window.game && window.game.w, h: window.game && window.game.h,
        fns: window.game && ['reset','tick','setDir','setFood','snake','food',
            'alive','score'].every(f => typeof window.game[f] === 'function'),
    })""")
    assert shape["ok"] and shape["fns"], f"window.game incomplete: {shape}"
    assert shape["w"] >= 10 and shape["h"] >= 10, \
        f"board {shape['w']}x{shape['h']} — spec requires >=10x10"


def test_reset_state(page):
    got = page.evaluate("""() => {
        const g = window.game; g.reset();
        return { len: g.snake().length, alive: g.alive(), score: g.score() };
    }""")
    assert got["len"] >= 3 and got["alive"] is True and got["score"] == 0, \
        f"reset() state wrong: {got} (expect length>=3, alive, score 0)"


def test_moves_in_direction(page):
    got = page.evaluate("""() => {
        const g = window.game; g.reset();
        const h0 = g.snake()[0];
        g.setDir('right'); g.tick();
        const h1 = g.snake()[0];
        return { dx: h1[0]-h0[0], dy: h1[1]-h0[1] };
    }""")
    assert got == {"dx": 1, "dy": 0}, \
        f"after a right-tick the head moved {got} (expect one cell right)"


def test_eating_grows_and_scores(page):
    got = page.evaluate("""() => {
        const g = window.game; g.reset();
        const head = g.snake()[0], len0 = g.snake().length;
        g.setDir('right');
        g.setFood(head[0]+1, head[1]);        // food directly ahead
        g.tick();                             // move onto it
        return { grew: g.snake().length - len0, score: g.score(), alive: g.alive() };
    }""")
    assert got["grew"] == 1 and got["score"] == 1 and got["alive"] is True, \
        f"eating food should grow +1 and score +1: {got}"


def test_no_reverse(page):
    got = page.evaluate("""() => {
        const g = window.game; g.reset();       // moving right
        const h0 = g.snake()[0];
        g.setDir('left');                        // 180° reversal — must be ignored
        g.tick();
        const h1 = g.snake()[0];
        return { dx: h1[0]-h0[0], alive: g.alive() };
    }""")
    assert got["dx"] == 1, \
        f"a 180-degree reversal must be ignored (head still moves right): {got}"


def test_wall_collision_kills(page):
    dead = page.evaluate("""() => {
        const g = window.game; g.reset(); g.setDir('right');
        for (let i = 0; i < g.w + 5 && g.alive(); i++) { g.setFood(-1,-1); g.tick(); }
        return g.alive();
    }""")
    assert dead is False, "driving into the right wall did not end the game"


def test_self_collision_kills(page):
    dead = page.evaluate("""() => {
        const g = window.game; g.reset();        // head (10,12), moving right, len3
        g.setDir('right');
        // grow to length 6 by eating straight ahead
        for (let i = 1; i <= 3; i++) { const h = g.snake()[0];
            g.setFood(h[0]+1, h[1]); g.tick(); }
        g.setFood(-1,-1);                         // park food off-path
        // a tight up/left/down loop turns the head back into its own body
        g.setDir('up');   g.tick();
        g.setDir('left'); g.tick();
        g.setDir('down'); g.tick();
        return g.alive();
    }""")
    assert dead is False, \
        "the snake ran its head into its own body but stayed alive"


def test_canvas_drawn(page):
    ok = page.evaluate("""() => {
        const g = window.game; g.reset();
        const c = document.querySelector('#snake');
        if (!c || c.tagName !== 'CANVAS')
            return document.querySelector('#snake').querySelectorAll('*').length >= 50 ? 1 : 0;
        const d = c.getContext('2d').getImageData(0,0,c.width,c.height).data;
        let lit = 0;
        for (let i = 0; i < d.length; i += 4)
            if (d[i] + d[i+1] + d[i+2] > 60) lit++;
        return lit > 20 ? 1 : 0;
    }""")
    assert ok == 1, "snake/food are not visibly rendered"
