import io
import re
import tokenize
from pathlib import Path

import pytest

FORBIDDEN = re.compile(r"\bimport\s+csv\b|\bfrom\s+csv\b|\b__import__\b|\bimportlib\b")

def _code_only(src):
    try:
        toks = tokenize.generate_tokens(io.StringIO(src).readline)
        skip = (tokenize.COMMENT, tokenize.STRING, getattr(tokenize, "FSTRING_MIDDLE", -1))
        return " ".join(t.string for t in toks if t.type not in skip)
    except (tokenize.TokenError, SyntaxError):
        return src

if FORBIDDEN.search(_code_only((Path(__file__).parent / "solution.py").read_text(encoding="utf-8"))):
    raise ImportError("solution must not use the csv module")

from solution import parse_csv


def _guards_intact():
    assert parse_csv("a,b") == [["a", "b"]]


def test_simple():
    assert parse_csv("a,b,c") == [["a", "b", "c"]]
    assert parse_csv("a,b\nc,d") == [["a", "b"], ["c", "d"]]


def test_crlf():
    assert parse_csv("a,b\r\nc,d\r\n") == [["a", "b"], ["c", "d"]]


def test_quoted_comma_and_newline():
    assert parse_csv('"a,b",c') == [["a,b", "c"]]
    assert parse_csv('"line1\nline2",x') == [["line1\nline2", "x"]]


def test_escaped_quotes():
    assert parse_csv('"she said ""hi""",ok') == [['she said "hi"', "ok"]]
    assert parse_csv('""""') == [['"']]


def test_quote_only_special_at_start():
    assert parse_csv('ab"cd,e') == [['ab"cd', "e"]]


def test_empty_fields():
    assert parse_csv("a,,b") == [["a", "", "b"]]
    assert parse_csv(",") == [["", ""]]


def test_trailing_newline_and_blank_middle_line():
    assert parse_csv("a\n") == [["a"]]
    assert parse_csv("a\n\nb") == [["a"], [""], ["b"]]


def test_empty_input():
    _guards_intact()
    assert parse_csv("") == []


def test_malformed():
    _guards_intact()
    with pytest.raises(ValueError):
        parse_csv('"never closed')
    with pytest.raises(ValueError):
        parse_csv('"ab"x,y')
