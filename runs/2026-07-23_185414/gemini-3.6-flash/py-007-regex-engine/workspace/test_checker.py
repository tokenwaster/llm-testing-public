import re as _re
from pathlib import Path

import pytest

from solution import match

FORBIDDEN = _re.compile(r"\bimport\s+re\b|\bfrom\s+re\b|import\s+regex|\b__import__\b|\bimportlib\b")


def test_no_regex_library():
    src = (Path(__file__).parent / "solution.py").read_text(encoding="utf-8")
    assert not FORBIDDEN.search(src), "solution must not use re/regex modules"


def test_literals_and_dot():
    assert match("abc", "abc")
    assert not match("abc", "abd")
    assert not match("abc", "ab")        # whole-text match
    assert not match("abc", "abcd")
    assert match("a.c", "axc")
    assert not match("a.c", "ac")
    assert match("", "")
    assert not match("", "x")


def test_star():
    assert match("ab*c", "ac")
    assert match("ab*c", "abbbc")
    assert match(".*", "anything at all")
    assert match(".*", "")
    assert match("a*a", "aaaa")          # backtracking required
    assert not match("a*b", "aac")


def test_plus_and_question():
    assert match("ab+c", "abc")
    assert match("ab+c", "abbc")
    assert not match("ab+c", "ac")
    assert match("ab?c", "ac")
    assert match("ab?c", "abc")
    assert not match("ab?c", "abbc")


def test_classes():
    assert match("[abc]", "b")
    assert not match("[abc]", "d")
    assert match("[a-z]+", "hello")
    assert not match("[a-z]+", "Hello")
    assert match("[a-z0-9]*x", "ab3x")
    assert match("[^abc]", "d")
    assert not match("[^abc]", "a")
    assert match("[^0-9]+", "no digits!")


def test_combined():
    assert match("h[ae]llo?.*", "hello world")
    assert match("h[ae]llo?.*", "hallo")
    assert not match("h[ae]llo?.*", "hillo")
    assert match("[0-9]+.[0-9]+", "3.14")
    assert match("a[bc]*d+", "abcbcddd")
    assert not match("a[bc]*d+", "abcbc")


def test_backtracking_hard():
    assert match("a*a*a*b", "aaab")
    assert match(".*b.*", "abc")
    assert not match("a+a+a+", "aa")     # needs at least 3
    assert match("[ab]*abb", "ababb")    # classic NFA backtrack case


def test_malformed_patterns():
    for bad in ("[abc", "*a", "+x", "?y"):
        with pytest.raises(ValueError):
            match(bad, "whatever")
