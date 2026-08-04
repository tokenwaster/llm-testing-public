"""A small, dependency-free JSON parser.

parse(text) -> Python object, or None if `text` is not a valid JSON document.
"""

import re

__all__ = ["parse"]


class _JSONError(Exception):
    """Internal signal that the document is malformed."""


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

_HEX_DIGITS = set("0123456789abcdefABCDEF")


def _skip_ws(s, i):
    n = len(s)
    while i < n and s[i] in _WS:
        i += 1
    return i


def _parse_hex4(s, i):
    """Parse exactly 4 hex digits starting at i; return (codepoint, new_i)."""
    if i + 4 > len(s):
        raise _JSONError("truncated unicode escape")
    chunk = s[i:i + 4]
    for ch in chunk:
        if ch not in _HEX_DIGITS:
            raise _JSONError("bad unicode escape")
    return int(chunk, 16), i + 4


def _parse_string(s, i):
    """s[i] must be the opening quote. Returns (value, index_after_close)."""
    if i >= len(s) or s[i] != '"':
        raise _JSONError("expected string")
    i += 1
    n = len(s)
    out = []
    while True:
        if i >= n:
            raise _JSONError("unterminated string")
        ch = s[i]
        if ch == '"':
            return "".join(out), i + 1
        if ch == "\\":
            i += 1
            if i >= n:
                raise _JSONError("unterminated escape")
            esc = s[i]
            if esc in _SIMPLE_ESCAPES:
                out.append(_SIMPLE_ESCAPES[esc])
                i += 1
            elif esc == "u":
                cp, i = _parse_hex4(s, i + 1)
                if 0xD800 <= cp <= 0xDBFF:
                    # Possible surrogate pair.
                    if s[i:i + 2] == "\\u":
                        low, j = _parse_hex4(s, i + 2)
                        if 0xDC00 <= low <= 0xDFFF:
                            cp = 0x10000 + ((cp - 0xD800) << 10) + (low - 0xDC00)
                            i = j
                out.append(chr(cp))
            else:
                raise _JSONError("invalid escape character")
        elif ch < "\x20":
            raise _JSONError("unescaped control character in string")
        else:
            out.append(ch)
            i += 1


def _parse_number(s, i):
    m = _NUMBER_RE.match(s, i)
    if not m or m.end() == i:
        raise _JSONError("invalid number")
    text = m.group(0)
    end = m.end()
    if "." in text or "e" in text or "E" in text:
        return float(text), end
    return int(text), end


def _parse_array(s, i):
    # s[i] == '['
    i = _skip_ws(s, i + 1)
    result = []
    if i < len(s) and s[i] == "]":
        return result, i + 1
    while True:
        value, i = _parse_value(s, i)
        result.append(value)
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError("unterminated array")
        if s[i] == ",":
            i = _skip_ws(s, i + 1)
            continue
        if s[i] == "]":
            return result, i + 1
        raise _JSONError("expected ',' or ']'")


def _parse_object(s, i):
    # s[i] == '{'
    i = _skip_ws(s, i + 1)
    result = {}
    if i < len(s) and s[i] == "}":
        return result, i + 1
    while True:
        if i >= len(s) or s[i] != '"':
            raise _JSONError("expected object key")
        key, i = _parse_string(s, i)
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != ":":
            raise _JSONError("expected ':'")
        i = _skip_ws(s, i + 1)
        value, i = _parse_value(s, i)
        result[key] = value
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError("unterminated object")
        if s[i] == ",":
            i = _skip_ws(s, i + 1)
            continue
        if s[i] == "}":
            return result, i + 1
        raise _JSONError("expected ',' or '}'")


def _parse_value(s, i):
    if i >= len(s):
        raise _JSONError("unexpected end of input")
    ch = s[i]
    if ch == "{":
        return _parse_object(s, i)
    if ch == "[":
        return _parse_array(s, i)
    if ch == '"':
        return _parse_string(s, i)
    if s.startswith("true", i):
        return True, i + 4
    if s.startswith("false", i):
        return False, i + 5
    if s.startswith("null", i):
        return None, i + 4
    if ch == "-" or ch.isdigit():
        return _parse_number(s, i)
    raise _JSONError("unexpected character")


def parse(text):
    """Parse a JSON document, returning the Python equivalent or None."""
    if not isinstance(text, str):
        return None
    try:
        i = _skip_ws(text, 0)
        if i >= len(text):
            return None
        value, i = _parse_value(text, i)
        i = _skip_ws(text, i)
        if i != len(text):
            return None
        return value
    except (_JSONError, RecursionError, ValueError, IndexError):
        return None
