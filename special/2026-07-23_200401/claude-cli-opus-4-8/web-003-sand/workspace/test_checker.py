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
    for sel in ("#sand", "#mat-sand", "#mat-water", "#mat-wall", "#mat-acid",
                "#mat-empty", "#clear"):
        assert page.locator(sel).count() == 1, f"missing {sel}"
    box = page.locator("#sand").bounding_box()
    assert box and box["width"] >= 380 and box["height"] >= 380, \
        f"canvas renders {box} — spec requires >=400x400"


def test_api_shape(page):
    shape = page.evaluate("""() => ({
        ok: typeof window.sim === 'object' && !!window.sim,
        w: window.sim && window.sim.w, h: window.sim && window.sim.h,
        fns: window.sim && ['tick','get','set','clear'].every(
            f => typeof window.sim[f] === 'function'),
    })""")
    assert shape["ok"] and shape["fns"], f"window.sim incomplete: {shape}"
    assert shape["w"] >= 80 and shape["h"] >= 80, \
        f"grid {shape['w']}x{shape['h']} — spec requires >=80x80"


def test_clear_empties_grid(page):
    empties = page.evaluate("""() => {
        window.sim.clear();
        let n = 0;
        for (let x = 0; x < window.sim.w; x += 7)
            for (let y = 0; y < window.sim.h; y += 7)
                if (window.sim.get(x, y) === 'empty') n++;
        return n;
    }""")
    assert empties > 0, "clear() left no empty cells (or get() broken)"


def test_sand_falls_one_cell_per_step(page):
    got = page.evaluate("""() => {
        window.sim.clear();
        const x = Math.floor(window.sim.w / 2);
        window.sim.set(x, 0, 'sand');
        window.sim.tick(1);
        const after1 = [];
        for (let y = 0; y < 4; y++) after1.push(window.sim.get(x, y));
        return after1;
    }""")
    assert got[0] == "empty" and got[1] == "sand", \
        f"after 1 tick, column top reads {got} — sand must move exactly 1 cell " \
        "(no teleporting)"


def test_sand_lands_on_bottom(page):
    landed = page.evaluate("""() => {
        window.sim.clear();
        const x = Math.floor(window.sim.w / 2);
        window.sim.set(x, 0, 'sand');
        window.sim.tick(window.sim.h + 20);
        return window.sim.get(x, window.sim.h - 1);
    }""")
    assert landed == "sand", f"bottom cell is {landed!r} — sand should rest there"


def test_walls_are_static_and_support_sand(page):
    # a 5-wide wall platform: sand dropped on the center cannot slide off
    got = page.evaluate("""() => {
        window.sim.clear();
        const x = Math.floor(window.sim.w / 2), wy = window.sim.h - 10;
        for (let dx = -2; dx <= 2; dx++) window.sim.set(x + dx, wy, 'wall');
        window.sim.set(x, 0, 'sand');
        window.sim.tick(window.sim.h + 20);
        let rest = 'none';
        for (let dx = -2; dx <= 2; dx++)
            if (window.sim.get(x + dx, wy - 1) === 'sand') rest = 'sand';
        return { wall: window.sim.get(x, wy), rest };
    }""")
    assert got["wall"] == "wall", "wall moved or vanished"
    assert got["rest"] == "sand", \
        "sand fell through or past a 5-wide wall platform"


def test_water_spreads_horizontally(page):
    spread = page.evaluate("""() => {
        window.sim.clear();
        const x = Math.floor(window.sim.w / 2);
        for (let i = 0; i < 6; i++) window.sim.set(x, i, 'water');
        window.sim.tick(window.sim.h * 3);
        // count distinct columns holding water in the bottom three rows —
        // spreading water must occupy several columns, wherever it wandered
        const cols = new Set();
        for (let cx = 0; cx < window.sim.w; cx++)
            for (let cy = window.sim.h - 3; cy < window.sim.h; cy++)
                if (window.sim.get(cx, cy) === 'water') cols.add(cx);
        return cols.size;
    }""")
    assert spread >= 3, \
        f"water occupies only {spread} column(s) near the floor — it must spread"


def test_acid_dissolves_walls(page):
    got = page.evaluate("""() => {
        window.sim.clear();
        const x = Math.floor(window.sim.w / 2), wy = window.sim.h - 5;
        window.sim.set(x, wy, 'wall');
        window.sim.set(x, wy - 1, 'acid');
        window.sim.tick(80);
        return window.sim.get(x, wy);
    }""")
    assert got != "wall", "acid sat on a wall for 80 ticks without eroding it"


def test_canvas_visibly_drawn(page):
    colors = page.evaluate("""() => {
        window.sim.clear();
        const midx = Math.floor(window.sim.w / 2);
        for (let i = 0; i < 12; i++) {
            window.sim.set(10 + i, window.sim.h - 2, 'sand');
            window.sim.set(30 + i, window.sim.h - 2, 'water');
            window.sim.set(50 + i, window.sim.h - 2, 'wall');
        }
        window.sim.tick(2);
        const c = document.querySelector('#sand');
        if (!c || c.tagName !== 'CANVAS') return -1;
        const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        const set = new Set();
        for (let i = 0; i < d.length; i += 40)
            set.add((d[i] << 16) | (d[i+1] << 8) | d[i+2]);
        return set.size;
    }""")
    assert colors >= 3 or colors == -1, \
        f"canvas shows {colors} distinct colors — materials must be visible"
    if colors == -1:
        # DOM-grid implementation: require a healthy number of cell elements
        n = page.evaluate("() => document.querySelector('#sand').querySelectorAll('*').length")
        assert n >= 100, f"#sand is not a canvas and has only {n} elements"


# ---- v0.5 upgrade: no anti-gravity liquid transport ------------------------

def test_no_liquid_elevator(page):
    """Pouring sand into a pool must not teleport the pool's liquid up the
    falling column. Displaced water may slosh a little; it must NOT climb
    dozens of cells against gravity (naive swap rules do exactly that)."""
    rise = page.evaluate("""() => {
        const W = sim.w, H = sim.h;
        sim.clear();
        const X = Math.floor(W / 2);
        const surface = H - 6;
        for (let y = surface; y < H; y++)
            for (let x = X - 6; x <= X + 6; x++)
                sim.set(x, y, 'water');
        const TOP = Math.max(2, Math.floor(H * 0.1));
        // track the HIGHEST the liquid ever reaches: the elevator is a
        // transient — erupted liquid rains back down after the pour stops
        const scanHighest = () => {
            for (let y = 0; y < H; y++)
                for (let x = 0; x < W; x++) {
                    const m = sim.get(x, y);
                    if (m === 'water' || m === 'acid') return y;
                }
            return H;
        };
        let highest = H;
        for (let f = 0; f < 250; f++) {
            for (let dx = -1; dx <= 1; dx++)
                sim.set(X + dx, TOP, 'sand');
            sim.tick(1);
            if (f % 5 === 0) highest = Math.min(highest, scanHighest());
        }
        for (let f = 0; f < 150; f++) {      // release: eruption window
            sim.tick(1);
            if (f % 5 === 0) highest = Math.min(highest, scanHighest());
        }
        return {surface, highest, rise: surface - highest};
    }""")
    assert rise["rise"] <= 8,         (f"liquid climbed {rise['rise']} rows above its pool surface while "
         "sand poured through it — liquid must be displaced around the "
         "column, not teleported up it")
