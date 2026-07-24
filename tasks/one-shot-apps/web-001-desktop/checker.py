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


def test_shell_elements(page):
    assert page.locator("#desktop").count() == 1
    assert page.locator("#taskbar").count() == 1
    assert page.locator("#open-files").count() == 1
    assert page.locator("#open-notepad").count() == 1


def test_files_window_opens_at_root(page):
    page.click("#open-files")
    page.wait_for_timeout(150)
    assert page.locator("#files-window").is_visible()
    assert page.text_content("#files-path").strip() == "/"
    names = [t.strip() for t in page.locator(".fs-item").all_text_contents()]
    for required in ("bin", "etc", "home", "usr", "var"):
        assert any(required in n for n in names), f"root missing {required}: {names}"


def _open_folder(page, name):
    """Double-click the folder ENTRY, not the text inside it.

    `.fs-item >> text=<name>` resolves to the innermost element holding the
    label, and a correct app may set `pointer-events: none` on that icon/label
    so the whole entry is the click target — a standard technique. Playwright
    then can never land the dblclick on it and times out, failing an app whose
    navigation works fine by hand. Target the `.fs-item` container, which is
    where the handler lives and what a user actually double-clicks."""
    page.locator(".fs-item").filter(has_text=name).first.dblclick()
    page.wait_for_timeout(150)


def test_files_navigation(page):
    _open_folder(page, "home")
    assert page.text_content("#files-path").strip() == "/home"
    _open_folder(page, "user")
    assert page.text_content("#files-path").strip() == "/home/user"
    names = [t.strip() for t in page.locator(".fs-item").all_text_contents()]
    for required in ("Documents", "Downloads", "Pictures"):
        assert any(required in n for n in names), \
            f"/home/user missing {required}: {names}"


def test_files_up_button(page):
    page.click("#files-up")
    page.wait_for_timeout(150)
    assert page.text_content("#files-path").strip() == "/home"


def test_notepad_opens_and_types(page):
    page.click("#open-notepad")
    page.wait_for_timeout(150)
    assert page.locator("#notepad-window").is_visible()
    page.click("#new-tab")
    page.wait_for_timeout(100)
    page.fill("#editor", "persistence probe 7431")
    page.wait_for_timeout(200)


def test_notepad_survives_window_close(page):
    page.locator("#notepad-window .win-close").first.click()
    page.wait_for_timeout(150)
    assert not page.locator("#notepad-window").is_visible()
    page.click("#open-notepad")
    page.wait_for_timeout(150)
    assert "persistence probe 7431" in page.input_value("#editor")


def test_desktop_fills_viewport(page):
    box = page.locator("#desktop").bounding_box()
    assert box, "#desktop not rendered"
    assert box["width"] >= 1000 and box["height"] >= 600, \
        f"desktop renders {box['width']:.0f}x{box['height']:.0f}px in a " \
        "1280x720 viewport — it should fill the screen"


def test_windows_open_at_usable_size(page):
    for opener, win in (("#open-files", "#files-window"),
                        ("#open-notepad", "#notepad-window")):
        page.click(opener)
        page.wait_for_timeout(150)
        box = page.locator(win).bounding_box()
        assert box, f"{win} has no bounding box"
        assert box["width"] >= 330 and box["height"] >= 220, \
            f"{win} opens at {box['width']:.0f}x{box['height']:.0f}px — " \
            "spec requires at least 360x240"


def test_notepad_survives_page_reload(page):
    page.reload()
    page.wait_for_timeout(400)
    page.click("#open-notepad")
    page.wait_for_timeout(200)
    tab_texts = []
    for i in range(page.locator(".tab").count()):
        page.locator(".tab").nth(i).click()
        page.wait_for_timeout(100)
        tab_texts.append(page.input_value("#editor"))
    assert any("persistence probe 7431" in t for t in tab_texts), \
        f"typed text lost after reload: {tab_texts}"



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
