"""tool-002 (frontier): sending the message needs a contact_id, which only
search_contacts can supply — so the correct NEXT call is search_contacts, not
send_message with an invented id. The trap is the "helpful" model that emits
send_message{contact_id: "jordan" / "123" / ...}, fabricating a value it cannot
know yet.
"""
import json
import pathlib
import re

_TXT = pathlib.Path("response.txt")
TEXT = _TXT.read_text(encoding="utf-8") if _TXT.exists() else ""


def _call():
    m = re.search(r"```(?:json)?\s*(.*?)```", TEXT, re.S)
    s = m.group(1) if m else TEXT
    a, b = s.find("{"), s.rfind("}")
    if a < 0 or b < 0:
        raise ValueError("no JSON object")
    return json.loads(s[a:b + 1])


def test_valid_json_call():
    assert isinstance(_call(), dict)


def test_calls_search_contacts_first():
    assert _call().get("name") == "search_contacts", \
        "must resolve the contact id before it can send — search_contacts is the next call"


def test_searches_for_jordan():
    assert "jordan" in str(_call().get("arguments", {}).get("name", "")).lower()


def test_did_not_fabricate_a_send():
    c = _call()
    assert c.get("name") != "send_message", \
        "cannot send yet — contact_id is unknown and must not be invented"
    args = c.get("arguments") or {}
    assert "contact_id" not in args, f"fabricated a contact_id: {args}"
