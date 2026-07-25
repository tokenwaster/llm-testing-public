"""A small, dependency-free JSON parser.

parse(text) -> Python object, or None if `text` is not a valid JSON document.
"""

import re
import sys

__all__ = ["parse"]

_WS = " \t\n\r"

_NUMBER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")

_SIMPLE_ESCAPES = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}


class _JSONError(Exception):
    """Raised internally whenever the document turns out to be malformed."""


def _skip_ws(s, i):
    n = len(s)
    while i < n and s[i] in _WS:
        i += 1
    return i


def _parse_hex4(s, i):
    """Parse exactly four hex digits starting at i; return (codepoint, next_i)."""
    if i + 4 > len(s):
        raise _JSONError("truncated unicode escape")
    chunk = s[i:i + 4]
    for c in chunk:
        if c not in "0123456789abcdefABCDEF":
            raise _JSONError("bad unicode escape")
    return int(chunk, 16), i + 4


def _parse_string(s, i):
    """i points at the opening quote; return (value, index after closing quote)."""
    i += 1  # consume the opening quote
    n = len(s)
    out = []
    while True:
        if i >= n:
            raise _JSONError("unterminated string")
        c = s[i]
        if c == '"':
            return "".join(out), i + 1
        if c == "\\":
            i += 1
            if i >= n:
                raise _JSONError("unterminated escape")
            e = s[i]
            if e in _SIMPLE_ESCAPES:
                out.append(_SIMPLE_ESCAPES[e])
                i += 1
            elif e == "u":
                cp, i = _parse_hex4(s, i + 1)
                if 0xD800 <= cp <= 0xDBFF and s[i:i + 2] == "\\u":
                    low, j = _parse_hex4(s, i + 2)
                    if 0xDC00 <= low <= 0xDFFF:
                        cp = 0x10000 + ((cp - 0xD800) << 10) + (low - 0xDC00)
                        i = j
                out.append(chr(cp))
            else:
                raise _JSONError("invalid escape")
        elif c < "\x20":
            raise _JSONError("control character in string")
        else:
            out.append(c)
            i += 1


def _parse_number(s, i):
    m = _NUMBER_RE.match(s, i)
    if not m or m.start() != i:
        raise _JSONError("invalid number")
    text = m.group(0)
    end = m.end()
    # Reject things like `007` or `1.2.3` where the regex stopped early but the
    # next character would still have been part of a number-ish token.
    if end < len(s) and (s[end].isdigit() or s[end] in ".eE+-"):
        raise _JSONError("invalid number")
    if "." in text or "e" in text or "E" in text:
        return float(text), end
    return int(text), end


def _parse_array(s, i):
    i = _skip_ws(s, i + 1)
    items = []
    if i < len(s) and s[i] == "]":
        return items, i + 1
    while True:
        value, i = _parse_value(s, i)
        items.append(value)
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError("unterminated array")
        if s[i] == ",":
            i = _skip_ws(s, i + 1)
            continue
        if s[i] == "]":
            return items, i + 1
        raise _JSONError("expected ',' or ']'")


def _parse_object(s, i):
    i = _skip_ws(s, i + 1)
    obj = {}
    if i < len(s) and s[i] == "}":
        return obj, i + 1
    while True:
        if i >= len(s) or s[i] != '"':
            raise _JSONError("expected object key")
        key, i = _parse_string(s, i)
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != ":":
            raise _JSONError("expected ':'")
        value, i = _parse_value(s, _skip_ws(s, i + 1))
        obj[key] = value
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError("unterminated object")
        if s[i] == ",":
            i = _skip_ws(s, i + 1)
            continue
        if s[i] == "}":
            return obj, i + 1
        raise _JSONError("expected ',' or '}'")


def _parse_value(s, i):
    if i >= len(s):
        raise _JSONError("unexpected end of input")
    c = s[i]
    if c == "{":
        return _parse_object(s, i)
    if c == "[":
        return _parse_array(s, i)
    if c == '"':
        return _parse_string(s, i)
    if s.startswith("true", i):
        return True, i + 4
    if s.startswith("false", i):
        return False, i + 5
    if s.startswith("null", i):
        return None, i + 4
    if c == "-" or c.isdigit():
        return _parse_number(s, i)
    raise _JSONError("unexpected token")


def parse(text):
    """Parse a JSON document, returning the equivalent Python object.

    Returns None for anything that is not a valid JSON document (and also,
    unavoidably, for the valid document `null`).
    """
    if not isinstance(text, str):
        return None
    try:
        i = _skip_ws(text, 0)
        value, i = _parse_value(text, i)
        i = _skip_ws(text, i)
        if i != len(text):
            return None  # trailing garbage
        return value
    except (_JSONError, RecursionError):
        return None


if __name__ == "__main__":
    sys.stdout.write(repr(parse(sys.stdin.read())) + "\n")
