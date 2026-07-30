def parse(text: str):
    if not isinstance(text, str):
        return None
    try:
        value, i = _parse_value(text, _skip_ws(text, 0))
        i = _skip_ws(text, i)
        if i != len(text):
            return None
        return value
    except _ParseError:
        return None


class _ParseError(Exception):
    pass


def _skip_ws(s, i):
    while i < len(s) and s[i] in " \t\n\r":
        i += 1
    return i


def _parse_value(s, i):
    if i >= len(s):
        raise _ParseError
    c = s[i]
    if c == '{':
        return _parse_object(s, i)
    if c == '[':
        return _parse_array(s, i)
    if c == '"':
        return _parse_string(s, i)
    if c == '-' or c.isdigit():
        return _parse_number(s, i)
    if s.startswith("true", i):
        return True, i + 4
    if s.startswith("false", i):
        return False, i + 5
    if s.startswith("null", i):
        return None, i + 4
    raise _ParseError


def _parse_object(s, i):
    i = _skip_ws(s, i + 1)
    obj = {}
    if i < len(s) and s[i] == '}':
        return obj, i + 1
    while True:
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != '"':
            raise _ParseError
        key, i = _parse_string(s, i)
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != ':':
            raise _ParseError
        value, i = _parse_value(s, _skip_ws(s, i + 1))
        obj[key] = value
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _ParseError
        if s[i] == ',':
            i += 1
            continue
        if s[i] == '}':
            return obj, i + 1
        raise _ParseError


def _parse_array(s, i):
    i = _skip_ws(s, i + 1)
    arr = []
    if i < len(s) and s[i] == ']':
        return arr, i + 1
    while True:
        value, i = _parse_value(s, _skip_ws(s, i))
        arr.append(value)
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _ParseError
        if s[i] == ',':
            i += 1
            continue
        if s[i] == ']':
            return arr, i + 1
        raise _ParseError


_ESCAPES = {'"': '"', '\\': '\\', '/': '/', 'b': '\b',
            'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}


def _parse_string(s, i):
    i += 1
    out = []
    while True:
        if i >= len(s):
            raise _ParseError
        c = s[i]
        if c == '"':
            return ''.join(out), i + 1
        if c == '\\':
            i += 1
            if i >= len(s):
                raise _ParseError
            e = s[i]
            if e in _ESCAPES:
                out.append(_ESCAPES[e])
                i += 1
            elif e == 'u':
                code, i = _read_hex4(s, i + 1)
                # combine surrogate pairs when both halves are escaped
                if 0xD800 <= code <= 0xDBFF and s.startswith('\\u', i):
                    low, j = _read_hex4(s, i + 2)
                    if 0xDC00 <= low <= 0xDFFF:
                        code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                        i = j
                out.append(chr(code))
            else:
                raise _ParseError
        elif ord(c) < 0x20:
            raise _ParseError
        else:
            out.append(c)
            i += 1


def _read_hex4(s, i):
    h = s[i:i + 4]
    if len(h) != 4 or any(ch not in "0123456789abcdefABCDEF" for ch in h):
        raise _ParseError
    return int(h, 16), i + 4


def _parse_number(s, i):
    start = i
    if i < len(s) and s[i] == '-':
        i += 1
    if i >= len(s) or not s[i].isdigit() or s[i] not in "0123456789":
        raise _ParseError
    if s[i] == '0':
        i += 1
    else:
        while i < len(s) and s[i] in "0123456789":
            i += 1
    is_int = True
    if i < len(s) and s[i] == '.':
        is_int = False
        i += 1
        if i >= len(s) or s[i] not in "0123456789":
            raise _ParseError
        while i < len(s) and s[i] in "0123456789":
            i += 1
    if i < len(s) and s[i] in "eE":
        is_int = False
        i += 1
        if i < len(s) and s[i] in "+-":
            i += 1
        if i >= len(s) or s[i] not in "0123456789":
            raise _ParseError
        while i < len(s) and s[i] in "0123456789":
            i += 1
    lexeme = s[start:i]
    return (int(lexeme) if is_int else float(lexeme)), i
