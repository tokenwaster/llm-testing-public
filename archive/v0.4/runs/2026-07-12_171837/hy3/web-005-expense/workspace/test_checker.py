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


def _add(page, amount, category, date, note=""):
    page.fill("#amount", str(amount))
    page.select_option("#category", category)
    page.fill("#date", date)
    if note:
        page.fill("#note", note)
    page.click("#add-expense")
    page.wait_for_timeout(150)


def _visible_rows(page):
    return [r for r in page.locator(".expense").all() if r.is_visible()]


def test_layout(page):
    for sel in ("#amount", "#category", "#date", "#add-expense", "#total",
                "#filter-category", "#filter-from", "#filter-to"):
        assert page.locator(sel).count() == 1, f"missing {sel}"


def test_invalid_amount_rejected(page):
    page.fill("#date", "2026-07-01")
    for bad in ("", "-5", "0"):
        page.fill("#amount", bad)
        page.click("#add-expense")
        page.wait_for_timeout(100)
    assert len(_visible_rows(page)) == 0, "invalid amounts created expenses"
    err = page.locator("#form-error").text_content() or ""
    assert err.strip(), "#form-error empty after invalid submission"


def test_valid_expenses_added(page):
    _add(page, "20.00", "groceries", "2026-07-01")
    _add(page, "34.50", "transport", "2026-07-05")
    _add(page, "20.00", "groceries", "2026-07-09")
    assert len(_visible_rows(page)) == 3
    err = (page.locator("#form-error").text_content() or "").strip()
    assert not err, "#form-error not cleared after valid submission"


def test_total_and_category_summary(page):
    assert "74.50" in page.locator("#total").text_content()
    groc = page.locator('.cat-total[data-cat="groceries"]').text_content()
    assert "40" in groc, f"groceries summary reads {groc!r} (expected 40.00)"


def test_category_filter(page):
    page.select_option("#filter-category", "groceries")
    page.wait_for_timeout(150)
    assert len(_visible_rows(page)) == 2
    assert "40.00" in page.locator("#total").text_content(), \
        "total must reflect only visible expenses"


def test_combined_filters(page):
    page.fill("#filter-from", "2026-07-08")
    page.wait_for_timeout(150)
    rows = _visible_rows(page)
    assert len(rows) == 1, "category+date filters must combine"
    assert "20.00" in page.locator("#total").text_content()


def test_filters_reset(page):
    page.select_option("#filter-category", "all")
    page.fill("#filter-from", "")
    page.wait_for_timeout(150)
    assert len(_visible_rows(page)) == 3
    assert "74.50" in page.locator("#total").text_content()


def test_persistence_across_reload(page):
    page.reload()
    page.wait_for_timeout(400)
    assert len(_visible_rows(page)) == 3, "expenses lost on reload"
    assert "74.50" in page.locator("#total").text_content()


def test_delete_and_persist(page):
    before = len(_visible_rows(page))
    page.locator(".expense .exp-del").first.click()
    page.wait_for_timeout(150)
    assert len(_visible_rows(page)) == before - 1
    page.reload()
    page.wait_for_timeout(400)
    assert len(_visible_rows(page)) == before - 1, "deleted expense returned"
