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
        browser = _launch(p)
        pg = browser.new_page()
        pg.goto(APP.as_uri())
        pg.wait_for_timeout(400)
        yield _Page(pg)
        browser.close()


def _set(page, cell, text):
    _ev(page, f"() => window.sheet.set('{cell}', {text!r})")


def _get(page, cell):
    return str(_ev(page, f"() => window.sheet.get('{cell}')"))


def test_no_dead_buttons(page):
    dead = _ev(page, """() => {
        const sig = () => document.body.innerHTML.length + '|' +
            JSON.stringify(Object.entries(localStorage)) + '|' +
            [...document.querySelectorAll('input,textarea')]
                .map(i => i.value).join('\\u0001');
        // validation no-ops aren't dead UI: give every text input a
        // plausible value first so add/submit buttons have something to do
        for (const i of document.querySelectorAll(
                'input[type=text], input:not([type]), input[type=number]')) {
            i.value = i.type === 'number' ? '42' : 'test item';
            i.dispatchEvent(new Event('input', {bubbles: true}));
        }
        const out = [];
        for (const b of document.querySelectorAll('button')) {
            if (b.disabled || b.offsetParent === null) continue;
            const before = sig();
            b.click();
            if (sig() === before) out.push(b.textContent.trim().slice(0, 30));
        }
        return out;
    }""")
    assert not dead, f"dead buttons (click changes nothing): {dead}"
    page.reload()
    page.wait_for_timeout(400)


def test_layout(page):
    assert page.locator("#cell-A1").count() == 1
    assert page.locator("#cell-J10").count() == 1
    assert page.locator("#export").count() == 1
    box = page.locator("body").bounding_box()
    assert box and box["width"] >= 500, "app too small"


def test_api_shape(page):
    ok = _ev(page, """() => window.sheet
        && typeof sheet.set === 'function'
        && typeof sheet.get === 'function'
        && typeof sheet.raw === 'function'""")
    assert ok, "window.sheet.set/get/raw missing"


def test_values_and_formulas(page):
    _set(page, "A1", "5")
    assert _get(page, "A1") == "5"
    _set(page, "B1", "=A1*2")
    assert _get(page, "B1") == "10"
    assert _ev(page, "() => window.sheet.raw('B1')") == "=A1*2"


def test_precedence(page):
    _set(page, "C1", "=2+3*4")
    assert float(_get(page, "C1")) == 14
    _set(page, "C2", "=(2+3)*4")
    assert float(_get(page, "C2")) == 20
    _set(page, "C3", "=10-4-3")
    assert float(_get(page, "C3")) == 3


def test_transitive_recalc(page):
    _set(page, "D1", "2")
    _set(page, "D2", "=D1*10")
    _set(page, "D3", "=D2+D1")
    assert float(_get(page, "D3")) == 22
    _set(page, "D1", "3")
    assert float(_get(page, "D2")) == 30
    assert float(_get(page, "D3")) == 33


def test_cycle_detection(page):
    _set(page, "E1", "=E2")
    _set(page, "E2", "=E1")
    assert _get(page, "E1") == "#CYCLE"
    assert _get(page, "E2") == "#CYCLE"
    _set(page, "E2", "7")
    assert float(_get(page, "E1")) == 7


def test_errors_and_empty(page):
    _set(page, "F1", "=A1+")
    assert _get(page, "F1") == "#ERR"
    _set(page, "F2", "=Z99")
    assert _get(page, "F2") == "#ERR"
    _set(page, "F3", "=G9+1")
    assert float(_get(page, "F3")) == 1


def test_dom_editing(page):
    inp = page.locator("#cell-H1")
    inp.click()
    inp.fill("=2*21")
    inp.press("Enter")
    page.wait_for_timeout(150)
    assert float(_get(page, "H1")) == 42
    _set(page, "H2", "=H1/2")
    inp.click()
    inp.fill("=2*10")
    inp.press("Enter")
    page.wait_for_timeout(150)
    assert float(_get(page, "H2")) == 10


def test_csv_export(page):
    _set(page, "A1", "5")
    _set(page, "B1", "=A1*2")
    page.locator("#export").click()
    page.wait_for_timeout(150)
    csv = page.locator("#csv").input_value()
    lines = [ln for ln in csv.strip().splitlines()]
    assert len(lines) == 10, f"CSV must have 10 rows, got {len(lines)}"
    first = lines[0].split(",")
    assert len(first) == 10, "CSV rows must have 10 columns"
    assert first[0] == "5" and first[1] == "10", \
        f"CSV must contain computed values, row1 starts {first[:2]}"




def _dom_edit(page, cell, text):
    inp = page.locator("#" + cell)
    inp.click()
    inp.fill(text)
    inp.press("Enter")
    page.wait_for_timeout(120)


def _shown(page, cell):
    return page.locator("#" + cell).input_value()


def test_dom_recalc_and_cycle(page):
    _dom_edit(page, "cell-A5", "5")
    _dom_edit(page, "cell-B5", "=A5*3")
    assert _shown(page, "cell-B5") == "15", \
        f"typed formula didn't compute in the cell (showed {_shown(page,'cell-B5')!r})"
    _dom_edit(page, "cell-A5", "10")
    assert _shown(page, "cell-B5") == "30", \
        f"dependent cell didn't recalc when its input changed by typing " \
        f"(showed {_shown(page,'cell-B5')!r})"
    _dom_edit(page, "cell-C5", "=D5")
    _dom_edit(page, "cell-D5", "=C5")
    assert _shown(page, "cell-C5") == "#CYCLE" and _shown(page, "cell-D5") == "#CYCLE", \
        f"cycle not shown in the cells (C5={_shown(page,'cell-C5')!r}, " \
        f"D5={_shown(page,'cell-D5')!r})"
