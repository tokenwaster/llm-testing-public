import re
from pathlib import Path

from solution import parse

FORBIDDEN = re.compile(r"\bimport\s+json\b|\bfrom\s+json\b|import\s+simplejson|\b__import__\b|\bimportlib\b")


def test_no_json_library():
    src = (Path(__file__).parent / "solution.py").read_text(encoding="utf-8")
    assert not FORBIDDEN.search(src), "solution must not use the json module"


def test_scalars():
    assert parse("42") == 42 and isinstance(parse("42"), int)
    assert parse("-7") == -7
    assert parse("3.5") == 3.5 and isinstance(parse("3.5"), float)
    assert parse("-1.5e-3") == -0.0015
    assert parse("2E2") == 200.0
    assert parse("true") is True
    assert parse("false") is False
    assert parse("null") is None
    assert parse('"hi"') == "hi"


def test_strings_escapes():
    assert parse(r'"a\"b"') == 'a"b'
    assert parse(r'"line\nbreak"') == "line\nbreak"
    assert parse(r'"tab\there"') == "tab\there"
    assert parse(r'"back\\slash"') == "back\\slash"
    assert parse('"caf\\u00e9"') == "café"
    assert parse('"\\u0041\\u0042"') == "AB"
    assert parse('"\\u00Zz"') is None, "bad unicode escape must be rejected"
    assert parse('["\\u0031\\u0032"]') == ["12"]


def test_containers():
    assert parse("[]") == []
    assert parse("{}") == {}
    assert parse("[1, 2, 3]") == [1, 2, 3]
    assert parse('{"a": 1, "b": [true, null]}') == {"a": 1, "b": [True, None]}
    assert parse('{"nested": {"deep": [{"x": [0.5]}]}}') == \
        {"nested": {"deep": [{"x": [0.5]}]}}


def test_whitespace_tolerance():
    assert parse('  { "a" :\n\t[ 1 ,\r\n 2 ]  } ') == {"a": [1, 2]}


def test_malformed_returns_none():
    bad = ['{', '[1, 2', '"unterminated', "{'single': 1}",
           '{"a": 1,}', '[1, 2,]', '{"a" 1}', '{"a": }', 'nul',
           '007', '1 2', '[1] trailing', '{"a": undefined}',
           '', '   ', '{,}', '[,]', '--1', '+1', '.5', '1.']
    for b in bad:
        assert parse(b) is None, f"should reject {b!r}"


def test_valid_edge_cases():
    assert parse('[""]') == [""]
    assert parse('[0]') == [0]
    assert parse('{"": 0}') == {"": 0}
    assert parse('[[[[1]]]]') == [[[[1]]]]
    assert parse('1e3') == 1000.0
    assert parse('"\\/"') == "/"
