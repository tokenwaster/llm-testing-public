def parse(text):
    if not isinstance(text, str):
        return None
    try:
        result, pos = _parse_value(text, 0)
        pos = _skip_ws(text, pos)
        if pos != len(text):
            return None
        return result
    except (ValueError, IndexError, TypeError):
        return None


_HEX_CHARS = frozenset('0123456789abcdefABCDEF')
_DIGITS = frozenset('0123456789')
_WS = frozenset(' \t\n\r')


def _skip_ws(text, pos):
    n = len(text)
    while pos < n and text[pos] in _WS:
        pos += 1
    return pos


def _parse_value(text, pos):
    pos = _skip_ws(text, pos)
    n = len(text)
    if pos >= n:
        raise ValueError("empty")
    c = text[pos]
    if c == '{':
        return _parse_object(text, pos)
    if c == '[':
        return _parse_array(text, pos)
    if c == '"':
        return _parse_string(text, pos)
    if c == 't':
        return _parse_literal(text, pos, 'true', True)
    if c == 'f':
        return _parse_literal(text, pos, 'false', False)
    if c == 'n':
        return _parse_literal(text, pos, 'null', None)
    if c == '-' or c in _DIGITS:
        return _parse_number(text, pos)
    raise ValueError(f"unexpected {c!r}")


def _parse_literal(text, pos, literal, value):
    n = len(text)
    end = pos + len(literal)
    if end > n or text[pos:end] != literal:
        raise ValueError(f"expected {literal}")
    return value, end


def _parse_string(text, pos):
    n = len(text)
    if pos >= n or text[pos] != '"':
        raise ValueError("expected string")
    pos += 1
    chars = []
    while pos < n:
        c = text[pos]
        if c == '"':
            return ''.join(chars), pos + 1
        if c == '\\':
            pos += 1
            if pos >= n:
                raise ValueError("bad escape")
            esc = text[pos]
            if esc == '"':
                chars.append('"')
            elif esc == '\\':
                chars.append('\\')
            elif esc == '/':
                chars.append('/')
            elif esc == 'b':
                chars.append('\b')
            elif esc == 'f':
                chars.append('\f')
            elif esc == 'n':
                chars.append('\n')
            elif esc == 'r':
                chars.append('\r')
            elif esc == 't':
                chars.append('\t')
            elif esc == 'u':
                pos += 1
                if pos + 4 > n:
                    raise ValueError("bad unicode")
                hex_chars = text[pos:pos + 4]
                for h in hex_chars:
                    if h not in _HEX_CHARS:
                        raise ValueError("bad unicode hex")
                code = int(hex_chars, 16)
                pos += 4
                if 0xD800 <= code <= 0xDBFF:
                    if pos + 6 <= n and text[pos] == '\\' and text[pos + 1] == 'u':
                        hex2 = text[pos + 2:pos + 6]
                        ok = True
                        for h in hex2:
                            if h not in _HEX_CHARS:
                                ok = False
                                break
                        if ok:
                            code2 = int(hex2, 16)
                            if 0xDC00 <= code2 <= 0xDFFF:
                                combined = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
                                chars.append(chr(combined))
                                pos += 6
                                continue
                chars.append(chr(code))
            else:
                raise ValueError(f"bad escape \\{esc}")
            pos += 1
        else:
            if ord(c) < 0x20:
                raise ValueError("control char in string")
            chars.append(c)
            pos += 1
    raise ValueError("unterminated string")


def _parse_number(text, pos):
    n = len(text)
    start = pos
    if text[pos] == '-':
        pos += 1
        if pos >= n:
            raise ValueError("expected digit")
    if pos < n and text[pos] == '0':
        pos += 1
        if pos < n and text[pos] in _DIGITS:
            raise ValueError("leading zero")
    elif pos < n and text[pos] in '123456789':
        while pos < n and text[pos] in _DIGITS:
            pos += 1
    else:
        raise ValueError("expected digit")
    is_float = False
    if pos < n and text[pos] == '.':
        is_float = True
        pos += 1
        if pos >= n or text[pos] not in _DIGITS:
            raise ValueError("expected digit after .")
        while pos < n and text[pos] in _DIGITS:
            pos += 1
    if pos < n and text[pos] in 'eE':
        is_float = True
        pos += 1
        if pos < n and text[pos] in '+-':
            pos += 1
        if pos >= n or text[pos] not in _DIGITS:
            raise ValueError("expected digit in exp")
        while pos < n and text[pos] in _DIGITS:
            pos += 1
    num_str = text[start:pos]
    if is_float:
        return float(num_str), pos
    return int(num_str), pos


def _parse_array(text, pos):
    n = len(text)
    pos += 1
    pos = _skip_ws(text, pos)
    items = []
    if pos < n and text[pos] == ']':
        return items, pos + 1
    if pos >= n:
        raise ValueError("unterminated array")
    while True:
        pos = _skip_ws(text, pos)
        if pos >= n:
            raise ValueError("unterminated array")
        value, pos = _parse_value(text, pos)
        items.append(value)
        pos = _skip_ws(text, pos)
        if pos >= n:
            raise ValueError("unterminated array")
        if text[pos] == ',':
            pos += 1
            continue
        if text[pos] == ']':
            return items, pos + 1
        raise ValueError("expected , or ]")


def _parse_object(text, pos):
    n = len(text)
    pos += 1
    pos = _skip_ws(text, pos)
    obj = {}
    if pos < n and text[pos] == '}':
        return obj, pos + 1
    if pos >= n:
        raise ValueError("unterminated object")
    while True:
        pos = _skip_ws(text, pos)
        if pos >= n:
            raise ValueError("unterminated object")
        if text[pos] != '"':
            raise ValueError("expected string key")
        key, pos = _parse_string(text, pos)
        pos = _skip_ws(text, pos)
        if pos >= n or text[pos] != ':':
            raise ValueError("expected :")
        pos += 1
        value, pos = _parse_value(text, pos)
        obj[key] = value
        pos = _skip_ws(text, pos)
        if pos >= n:
            raise ValueError("unterminated object")
        if text[pos] == ',':
            pos += 1
            continue
        if text[pos] == '}':
            return obj, pos + 1
        raise ValueError("expected , or }")
