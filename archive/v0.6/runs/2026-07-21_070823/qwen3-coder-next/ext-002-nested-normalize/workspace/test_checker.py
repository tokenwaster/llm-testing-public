"""ext-002 (frontier): the same order id appears in two separate lines and must
be MERGED (X-10's amount is in one mention, its paid status in another); X-11's
amount is never given (null, not guessed); three date formats; sort by date. A
model that emits five rows (one per line) instead of three merged orders, or
guesses X-11's amount, fails.
"""
import json
import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""

EXPECT = {
    "X-9": {"date": "2023-01-03", "amount_usd": 85.50, "customer": "Ben", "paid": True},
    "X-11": {"date": "2023-03-28", "amount_usd": None, "customer": "Ana", "paid": False},
    "X-10": {"date": "2023-04-05", "amount_usd": 120, "customer": "Ana", "paid": True},
}


def _orders():
    m = re.search(r"```(?:json)?\s*(.*?)```", TEXT, re.S)
    s = m.group(1) if m else TEXT
    a, b = s.find("{"), s.rfind("}")
    if a < 0 or b < 0:
        raise ValueError("no JSON object")
    return json.loads(s[a:b + 1])["orders"]


def _by_id():
    return {r.get("order_id"): r for r in _orders()}


def test_three_merged_orders():
    o = _orders()
    assert len(o) == 3, f"expected 3 merged orders, got {len(o)}"
    assert set(_by_id()) == set(EXPECT)


def test_dates_normalized():
    by = _by_id()
    for k, e in EXPECT.items():
        assert by[k].get("date") == e["date"], f"{k} date {by[k].get('date')!r} != {e['date']}"


def test_amounts_and_null_not_guessed():
    by = _by_id()
    assert abs(float(by["X-9"]["amount_usd"]) - 85.50) < 1e-9
    assert abs(float(by["X-10"]["amount_usd"]) - 120) < 1e-9
    assert by["X-11"].get("amount_usd") is None, "X-11 amount is not given — must be null"


def test_paid_merged_correctly():
    by = _by_id()
    assert by["X-9"].get("paid") is True
    assert by["X-10"].get("paid") is True, "X-10's 'paid in full' is in its second mention"
    assert by["X-11"].get("paid") is False


def test_customers():
    by = _by_id()
    assert by["X-9"].get("customer") == "Ben"
    assert by["X-10"].get("customer") == "Ana"
    assert by["X-11"].get("customer") == "Ana"


def test_sorted_by_date_ascending():
    dates = [r.get("date") for r in _orders()]
    assert dates == sorted(dates), f"not sorted ascending: {dates}"
