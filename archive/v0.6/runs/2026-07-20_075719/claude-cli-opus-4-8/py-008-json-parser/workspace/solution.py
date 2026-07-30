def parse(text):
    """Parse a JSON document into a Python object, or return None if invalid."""
    try:
        value, i = _parse_value(text, _skip_ws(text, 0))
        i = _skip_ws(text, i)
        if i != len(text):
            return None
        return value
    except (_JSONError, IndexError):
        return None


class _JSONError(Exception):
    pass


_WS = " \t\n\r"


def _skip_ws(s, i):
    n = len(s)
    while i < n and s[i] in _WS:
        i += 1
    return i


def _parse_value(s, i):
    if i >= len(s):
        raise _JSONError("unexpected end of input")
    c = s[i]
    if c == '{':
        return _parse_object(s, i)
    if c == '[':
        return _parse_array(s, i)
    if c == '"':
        return _parse_string(s, i)
    if c == 't':
        return _parse_literal(s, i, "true", True)
    if c == 'f':
        return _parse_literal(s, i, "false", False)
    if c == 'n':
        return _parse_literal(s, i, "null", None)
    if c == '-' or c.isdigit():
        return _parse_number(s, i)
    raise _JSONError("unexpected character %r" % c)


def _parse_literal(s, i, word, value):
    if s[i:i + len(word)] == word:
        return value, i + len(word)
    raise _JSONError("invalid literal")


def _parse_object(s, i):
    # s[i] == '{'
    i += 1
    obj = {}
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == '}':
        return obj, i + 1
    while True:
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != '"':
            raise _JSONError("expected string key")
        key, i = _parse_string(s, i)
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != ':':
            raise _JSONError("expected ':'")
        i = _skip_ws(s, i + 1)
        value, i = _parse_value(s, i)
        obj[key] = value
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError("unterminated object")
        if s[i] == ',':
            i += 1
            continue
        if s[i] == '}':
            return obj, i + 1
        raise _JSONError("expected ',' or '}'")


def _parse_array(s, i):
    # s[i] == '['
    i += 1
    arr = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == ']':
        return arr, i + 1
    while True:
        i = _skip_ws(s, i)
        value, i = _parse_value(s, i)
        arr.append(value)
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError("unterminated array")
        if s[i] == ',':
            i += 1
            continue
        if s[i] == ']':
            return arr, i + 1
        raise _JSONError("expected ',' or ']'")


_ESCAPES = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}


def _parse_string(s, i):
    # s[i] == '"'
    i += 1
    n = len(s)
    parts = []
    while i < n:
        c = s[i]
        if c == '"':
            return "".join(parts), i + 1
        if c == '\\':
            i += 1
            if i >= n:
                raise _JSONError("unterminated escape")
            e = s[i]
            if e in _ESCAPES:
                parts.append(_ESCAPES[e])
                i += 1
            elif e == 'u':
                hexstr = s[i + 1:i + 5]
                if len(hexstr) != 4:
                    raise _JSONError("invalid unicode escape")
                for h in hexstr:
                    if h not in "0123456789abcdefABCDEF":
                        raise _JSONError("invalid unicode escape")
                code = int(hexstr, 16)
                # Handle UTF-16 surrogate pairs
                if 0xD800 <= code <= 0xDBFF:
                    if s[i + 5:i + 7] == '\\u':
                        low_hex = s[i + 7:i + 11]
                        if len(low_hex) == 4 and all(
                            h in "0123456789abcdefABCDEF" for h in low_hex
                        ):
                            low = int(low_hex, 16)
                            if 0xDC00 <= low <= 0xDFFF:
                                code = 0x10000 + (
                                    ((code - 0xD800) << 10) | (low - 0xDC00)
                                )
                                parts.append(chr(code))
                                i += 11
                                continue
                    parts.append(chr(code))
                    i += 5
                else:
                    parts.append(chr(code))
                    i += 5
            else:
                raise _JSONError("invalid escape %r" % e)
        elif ord(c) < 0x20:
            raise _JSONError("control character in string")
        else:
            parts.append(c)
            i += 1
    raise _JSONError("unterminated string")


def _parse_number(s, i):
    n = len(s)
    start = i
    if i < n and s[i] == '-':
        i += 1
    # integer part
    if i >= n:
        raise _JSONError("invalid number")
    if s[i] == '0':
        i += 1
    elif s[i].isdigit():
        i += 1
        while i < n and s[i].isdigit():
            i += 1
    else:
        raise _JSONError("invalid number")
    is_float = False
    # fraction
    if i < n and s[i] == '.':
        is_float = True
        i += 1
        if i >= n or not s[i].isdigit():
            raise _JSONError("invalid fraction")
        while i < n and s[i].isdigit():
            i += 1
    # exponent
    if i < n and s[i] in "eE":
        is_float = True
        i += 1
        if i < n and s[i] in "+-":
            i += 1
        if i >= n or not s[i].isdigit():
            raise _JSONError("invalid exponent")
        while i < n and s[i].isdigit():
            i += 1
    text = s[start:i]
    if is_float:
        return float(text), i
    return int(text), i
