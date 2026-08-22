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


EV_MS = 15000


class _Page:
    """A hung page is closed and reopened, so one spinning evaluate fails its
    own test instead of every test after it."""

    def __init__(self, pg):
        self._pg = pg
        pg.set_default_timeout(EV_MS)

    def __getattr__(self, name):
        return getattr(self._pg, name)

    def _revive(self):
        browser = self._pg.context.browser
        viewport = self._pg.viewport_size
        try:
            self._pg.close()
        except Exception:
            pass
        self._pg = browser.new_page(viewport=viewport)
        self._pg.set_default_timeout(EV_MS)
        self._pg.goto(APP.as_uri())
        self._pg.wait_for_timeout(400)


def _ev(page, expr, arg=None):
    from playwright.sync_api import TimeoutError as _Timeout
    pg = page._pg if isinstance(page, _Page) else page
    wrapped = ("async (a) => { const f = (" + expr + "); "
               "const r = (typeof f === 'function') ? await f(a) : await f; "
               "return {v: r}; }")
    try:
        return pg.wait_for_function(wrapped, arg=arg,
                                    timeout=EV_MS).json_value().get("v")
    except _Timeout:
        if isinstance(page, _Page):
            page._revive()
        raise AssertionError(
            f"the app did not respond within {EV_MS // 1000}s: "
            f"{expr.strip()[:80]}")


@pytest.fixture(scope="module")
def page():
    assert APP.exists(), "app.html missing"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = _launch(p); pg = b.new_page(); pg.goto(APP.as_uri()); pg.wait_for_timeout(400)
        yield _Page(pg); b.close()


def test_layout(page):
    for sel in ("#board", "#reset", "#score"):
        assert page.locator(sel).count() == 1, f"missing {sel}"
    box = page.locator("#board").bounding_box()
    assert box and box["width"] >= 240, f"board too small: {box}"


def test_api_shape(page):
    s = _ev(page, """() => ({
        ok: typeof window.game === 'object' && !!window.game,
        size: window.game && window.game.size,
        fns: window.game && ['reset','move','board','setBoard','score'].every(
            f => typeof window.game[f] === 'function'),
    })""")
    assert s["ok"] and s["fns"], f"window.game incomplete: {s}"
    assert s["size"] >= 4, f"grid size {s['size']} (expect >=4)"


def test_reset_two_tiles(page):
    got = _ev(page, """() => {
        const g = window.game; g.reset();
        let n = 0; for (const row of g.board()) for (const v of row) if (v) n++;
        return { tiles: n, score: g.score() };
    }""")
    assert got["tiles"] == 2 and got["score"] == 0, \
        f"a new game should have exactly 2 tiles and score 0: {got}"


def test_merge_left(page):
    got = _ev(page, """() => {
        const g = window.game;
        g.setBoard([[2,2,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]);
        const s0 = g.score();
        g.move('left');
        return { cell: g.board()[0][0], gained: g.score() - s0 };
    }""")
    assert got["cell"] == 4 and got["gained"] >= 4, \
        f"[2,2,..] moved left should merge to 4 and score +4: {got}"


def test_slide_without_merge(page):
    got = _ev(page, """() => {
        const g = window.game;
        g.setBoard([[2,0,4,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]);
        g.move('left');
        return [g.board()[0][0], g.board()[0][1]];
    }""")
    assert got == [2, 4], f"[2,0,4,0] left should slide to [2,4,..], got {got}"


def test_no_double_merge(page):
    got = _ev(page, """() => {
        const g = window.game;
        g.setBoard([[2,2,2,2],[0,0,0,0],[0,0,0,0],[0,0,0,0]]);
        g.move('left');
        return [g.board()[0][0], g.board()[0][1]];
    }""")
    assert got == [4, 4], \
        f"[2,2,2,2] left must merge into two 4s (not one 8): got {got}"


def test_no_move_returns_false(page):
    got = _ev(page, """() => {
        const g = window.game;
        g.setBoard([[2,4,8,16],[0,0,0,0],[0,0,0,0],[0,0,0,0]]);
        return g.move('left');   // already packed, no merge -> nothing moves
    }""")
    assert got is False, "move() must return false when nothing changes"


def test_tiles_rendered(page):
    ok = _ev(page, """() => {
        const g = window.game;
        g.setBoard([[2,4,8,16],[32,64,0,0],[0,0,0,0],[0,0,0,0]]);
        return document.querySelector('#board').textContent.replace(/\\s/g,'');
    }""")
    for v in ("2", "16", "64"):
        assert v in ok, f"tile value {v} not shown in #board (got {ok!r})"
