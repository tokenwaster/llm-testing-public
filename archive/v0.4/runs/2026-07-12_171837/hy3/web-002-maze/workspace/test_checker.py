import os
from pathlib import Path

import pytest

APP = Path(__file__).parent / "app.html"

# use the project-local browser install when this workspace lives inside the
# project tree (self-locating so the checker also works from temp dirs)
for _parent in Path(__file__).resolve().parents:
    _pw = _parent / ".pw-browsers"
    if _pw.is_dir():
        os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(_pw)
        break


def _launch(p):
    try:
        return p.chromium.launch()
    except Exception:
        # some environments block the headless-shell helper binary —
        # fall back to the full (signed) chromium build in new-headless mode
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
    for sel in ("#maze", "#completed", "#timer", "#reset"):
        assert page.locator(sel).count() == 1, f"missing {sel}"


def test_maze_renders_usable_size(page):
    box = page.locator("#maze").bounding_box()
    assert box, "#maze has no bounding box (not rendered)"
    assert box["width"] >= 380 and box["height"] >= 380, \
        f"maze renders {box['width']:.0f}x{box['height']:.0f}px — " \
        "spec requires at least 400x400"


def test_maze_visibly_drawn(page):
    info = page.evaluate("""() => {
        if (window.game && typeof window.game.reset === 'function')
            window.game.reset();   // bots back at spawn so they're drawn
        const root = document.querySelector('#maze');
        const c = root && (root.tagName === 'CANVAS' ? root
                           : root.querySelector('canvas'));
        if (c) {
            const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            const colors = new Set();
            for (let i = 0; i < d.length; i += 40)
                colors.add((d[i] << 16) | (d[i+1] << 8) | d[i+2]);
            return {kind: 'canvas', detail: colors.size, ok: colors.size >= 4};
        }
        const n = root ? root.querySelectorAll('*').length : 0;
        return {kind: 'dom', detail: n, ok: n >= 50};
    }""")
    assert info["ok"], \
        f"maze not visibly drawn ({info['kind']}: {info['detail']} — " \
        "expected >=4 distinct canvas colors or >=50 grid elements)"


def test_api_shape(page):
    shape = page.evaluate("""() => ({
        hasGame: typeof window.game === 'object' && window.game !== null,
        bots: window.game && Array.isArray(window.game.bots)
              ? window.game.bots.length : -1,
        tick: window.game && typeof window.game.tick === 'function',
        reset: window.game && typeof window.game.reset === 'function',
    })""")
    assert shape["hasGame"], "window.game missing"
    assert shape["bots"] == 24, f"expected 24 bots, got {shape['bots']}"
    assert shape["tick"] and shape["reset"]


def test_bots_have_coordinates(page):
    ok = page.evaluate(
        "() => window.game.bots.every(b => "
        "typeof b.x === 'number' && typeof b.y === 'number')")
    assert ok, "bots must expose numeric .x/.y cell coords"


def test_fresh_game_incomplete(page):
    # reset+read atomically — the app's own animation loop may have finished
    # the first game in real time before this test runs
    completed = page.evaluate(
        "() => { window.game.reset(); return Number(window.game.completed); }")
    assert completed == 0


def test_all_bots_complete_after_ticks(page):
    completed = page.evaluate(
        "() => { window.game.tick(5000); return Number(window.game.completed); }")
    assert completed == 24, f"after tick(5000): completed={completed}"


def test_hud_shows_24(page):
    text = page.text_content("#completed")
    assert "24" in text, f"#completed HUD shows {text!r}"


def test_reset_restores_start_state(page):
    state = page.evaluate("""() => {
        window.game.reset();
        return { completed: Number(window.game.completed),
                 bots: window.game.bots.length };
    }""")
    assert state["completed"] == 0
    assert state["bots"] == 24


def test_playable_again_after_reset(page):
    completed = page.evaluate(
        "() => { window.game.tick(5000); return Number(window.game.completed); }")
    assert completed == 24, "game not functional after reset"
