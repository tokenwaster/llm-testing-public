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
        pg.wait_for_timeout(300)
        yield pg
        browser.close()


def _cards_in(page, col):
    return page.locator(f"{col} .card").count()


def test_layout(page):
    for sel in ("#col-todo", "#col-doing", "#col-done", "#new-card", "#add-card"):
        assert page.locator(sel).count() == 1, f"missing {sel}"
    for col in ("#col-todo", "#col-doing", "#col-done"):
        assert page.locator(f"{col} .count").count() == 1, f"{col} missing .count"


def test_add_card(page):
    page.fill("#new-card", "write the report")
    page.click("#add-card")
    page.wait_for_timeout(150)
    assert _cards_in(page, "#col-todo") == 1
    assert "write the report" in page.locator("#col-todo .card").first.text_content()
    assert page.input_value("#new-card") == "", "input not cleared after add"


def test_empty_input_adds_nothing(page):
    before = _cards_in(page, "#col-todo")
    page.fill("#new-card", "")
    page.click("#add-card")
    page.wait_for_timeout(100)
    assert _cards_in(page, "#col-todo") == before


def test_count_updates(page):
    page.fill("#new-card", "second card")
    page.click("#add-card")
    page.wait_for_timeout(100)
    assert "2" in page.locator("#col-todo .count").text_content()


def test_drag_between_columns(page):
    page.locator("#col-todo .card", has_text="write the report") \
        .drag_to(page.locator("#col-doing"))
    page.wait_for_timeout(200)
    assert _cards_in(page, "#col-doing") == 1, "card did not land in Doing"
    assert _cards_in(page, "#col-todo") == 1
    assert "1" in page.locator("#col-doing .count").text_content()


def test_drag_to_done(page):
    page.locator("#col-doing .card").first.drag_to(page.locator("#col-done"))
    page.wait_for_timeout(200)
    assert _cards_in(page, "#col-done") == 1


def test_persistence_across_reload(page):
    page.reload()
    page.wait_for_timeout(400)
    assert _cards_in(page, "#col-todo") == 1, "todo card lost on reload"
    assert _cards_in(page, "#col-done") == 1, "done card lost on reload"
    assert "write the report" in page.locator("#col-done .card").first.text_content()


def test_delete_card_and_persist(page):
    page.locator("#col-done .card .card-del").first.click()
    page.wait_for_timeout(150)
    assert _cards_in(page, "#col-done") == 0
    page.reload()
    page.wait_for_timeout(400)
    assert _cards_in(page, "#col-done") == 0, "deleted card came back after reload"
    assert _cards_in(page, "#col-todo") == 1



def test_no_dead_buttons(page):
    page.reload()
    page.wait_for_timeout(500)
    dead = page.evaluate("""() => {
        const sig = () => document.body.innerHTML.length + '|' +
            JSON.stringify(Object.entries(localStorage)) + '|' +
            [...document.querySelectorAll('input,textarea,select')]
                .map(i => i.value).join('\u0001');
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
            if (sig() === before)
                out.push((b.id || b.textContent.trim()).slice(0, 30));
        }
        return out;
    }""")
    assert not dead, f"dead buttons (click changes nothing): {dead}"
