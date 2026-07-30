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
    for sel in ("#sim", "#drop", "#play", "#clear"):
        assert page.locator(sel).count() == 1, f"missing {sel}"
    box = page.locator("#sim").bounding_box()
    assert box and box["width"] >= 380 and box["height"] >= 380, f"canvas {box} < 400"


def test_api_shape(page):
    s = page.evaluate("""() => ({
        ok: typeof window.sim === 'object' && !!window.sim,
        w: window.sim && window.sim.w, h: window.sim && window.sim.h,
        fns: window.sim && ['balls','clear','addBall','step'].every(
            f => typeof window.sim[f] === 'function'),
    })""")
    assert s["ok"] and s["fns"], f"window.sim incomplete: {s}"
    assert s["w"] >= 200 and s["h"] >= 200, f"canvas grid {s}"


def test_clear_removes_balls(page):
    n = page.evaluate("() => { sim.addBall(100,100,0,0); sim.clear(); return sim.balls().length; }")
    assert n == 0, f"clear() left {n} balls"


def test_gravity_pulls_down(page):
    got = page.evaluate("""() => {
        sim.clear(); sim.addBall(240, 40, 0, 0);
        for (let i=0;i<10;i++) sim.step(1);
        const b = sim.balls()[0];
        return { y: b.y, vy: b.vy };
    }""")
    assert got["vy"] > 0 and got["y"] > 40, \
        f"a released ball must accelerate downward (got vy={got['vy']}, y={got['y']})"


def test_floor_bounces(page):
    got = page.evaluate("""() => {
        sim.clear(); sim.addBall(240, 40, 0, 0);
        let bounced = false, maxY = 0;
        for (let i=0;i<400;i++){ sim.step(1); const b = sim.balls()[0];
            maxY = Math.max(maxY, b.y);
            if (b.vy < 0) bounced = true; }         // velocity reversed = bounced up
        const b = sim.balls()[0];
        return { bounced, maxY, insideH: b.y <= sim.h + 1 };
    }""")
    assert got["bounced"], "the ball never bounced off the floor (vy never went negative)"
    assert got["insideH"], "the ball escaped through the floor"


def test_wall_bounces(page):
    got = page.evaluate("""() => {
        sim.clear(); sim.addBall(sim.w - 30, sim.h/2, 12, 0);  // moving right into wall
        let reversed = false;
        for (let i=0;i<60;i++){ sim.step(1); if (sim.balls()[0].vx < 0) reversed = true; }
        return { reversed, x: sim.balls()[0].x, inside: sim.balls()[0].x <= sim.w + 1 };
    }""")
    assert got["reversed"] and got["inside"], \
        f"a ball moving into the right wall must bounce back and stay in bounds: {got}"


def test_stays_in_bounds(page):
    escaped = page.evaluate("""() => {
        sim.clear();
        sim.addBall(60, 60, 9, -4); sim.addBall(400, 200, -7, 3);
        let bad = false;
        for (let i=0;i<600;i++){ sim.step(1);
            for (const b of sim.balls())
                if (b.x < -2 || b.y < -2 || b.x > sim.w+2 || b.y > sim.h+2) bad = true; }
        return bad;
    }""")
    assert not escaped, "a ball left the canvas bounds during simulation"


def test_canvas_drawn(page):
    lit = page.evaluate("""() => {
        sim.clear(); sim.addBall(240,240,0,0); sim.step(1);
        const c = document.querySelector('#sim');
        if (!c || c.tagName !== 'CANVAS') return c.querySelectorAll('*').length >= 1 ? 1 : 0;
        const d = c.getContext('2d').getImageData(0,0,c.width,c.height).data;
        let n=0; for (let i=0;i<d.length;i+=4) if (d[i]+d[i+1]+d[i+2] > 80) n++;
        return n > 30 ? 1 : 0;
    }""")
    assert lit == 1, "balls are not visibly drawn"
