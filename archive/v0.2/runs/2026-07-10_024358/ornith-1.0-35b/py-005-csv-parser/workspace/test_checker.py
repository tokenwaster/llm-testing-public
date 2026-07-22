import re
from pathlib import Path

import pytest

from solution import parse_csv


def test_no_csv_module():
    src = (Path(__file__).parent / "solution.py").read_text(encoding="utf-8")
    assert not re.search(r"\bimport\s+csv\b|\bfrom\s+csv\b", src), \
        "solution must not use the csv module"


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
    assert parse_csv("") == []


def test_malformed():
    with pytest.raises(ValueError):
        parse_csv('"never closed')
    with pytest.raises(ValueError):
        parse_csv('"ab"x,y')
