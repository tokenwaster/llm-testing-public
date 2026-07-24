"""ext-001: messy email -> strict JSON. Each field is a check; an extra
(hallucinated) key fails its own check, so inventing fields costs points.
"""
import json
import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""


def _load():
    m = re.search(r"```(?:json)?\s*(.*?)```", TEXT, re.S)
    s = m.group(1) if m else TEXT
    a, b = s.find("{"), s.rfind("}")
    if a < 0 or b < 0:
        raise ValueError("no JSON object in response")
    return json.loads(s[a:b + 1])


def test_valid_json_object():
    assert isinstance(_load(), dict)


def test_order_id():
    assert _load().get("order_id") == "A-4471"


def test_customer_name():
    assert _load().get("customer_name") == "Dana Whitfield"


def test_item_count_is_integer_three():
    v = _load().get("item_count")
    assert v == 3 and isinstance(v, int) and not isinstance(v, bool)


def test_total_is_number():
    v = _load().get("total_usd")
    assert isinstance(v, (int, float)) and not isinstance(v, bool)
    assert abs(float(v) - 128.50) < 1e-9


def test_express_true_boolean():
    assert _load().get("express") is True


def test_no_extra_keys():
    assert set(_load()) == {"order_id", "customer_name", "item_count",
                            "total_usd", "express"}
