"""tool-001: pick create_reminder and fill args from the request. Prompt-based
(the call is emitted as JSON), so every model can attempt it — no native
tools API required.
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


def test_selects_create_reminder():
    assert _call().get("name") == "create_reminder"


def test_date_argument():
    assert _call().get("arguments", {}).get("date") == "2024-06-10"


def test_text_argument_mentions_dentist():
    assert "dentist" in str(_call().get("arguments", {}).get("text", "")).lower()


def test_no_foreign_arguments():
    # only text/date belong to create_reminder — no city/to/subject leakage
    args = set(_call().get("arguments", {}))
    assert args <= {"text", "date"}, f"unexpected arguments: {args}"
