"""solution.py — a hand-written, dependency-free JSON parser.

`parse(text)` returns the Python object described by the JSON document in
`text`, or ``None`` when `text` is not valid JSON.  (A valid JSON ``null``
also parses to ``None``; that ambiguity is accepted by the spec of this task.)

No JSON library is used — the grammar is implemented directly:
    value   := object | array | string | number | true | false | null
    object  := '{' (string ':' value (',' string ':' value)*)? '}'
    array   := '[' (value (',' value)*)? ']'
    string  := '"' (char | escape)* '"'
    number  := '-'? int frac? exp?        (no leading zeros)
"""

_WS = ' \t\n\r'
_HEX = frozenset('0123456789abcdefABCDEF')
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


class _JSONError(Exception):
    """Internal signal: the input is not valid JSON."""


def parse(text):
    """Parse a JSON document and return the equivalent Python object.

    Returns ``None`` if the input is not valid JSON.
    """
    if not isinstance(text, str):
        return None
    try:
        value, i = _parse_value(text, 0)
    except (_JSONError, RecursionError):
        return None
    # The whole document must be consumed (only whitespace may remain).
    if _skip_ws(text, i) != len(text):
        return None
    return value


# --------------------------------------------------------------- helpers

def _skip_ws(s, i):
    while i < len(s) and s[i] in _WS:
        i += 1
    return i


def _parse_value(s, i):
    i = _skip_ws(s, i)
    if i >= len(s):
        raise _JSONError('unexpected end of input')
    c = s[i]
    if c == '{':
        return _parse_object(s, i)
    if c == '[':
        return _parse_array(s, i)
    if c == '"':
        return _parse_string(s, i)
    if c == 't':
        return _expect_word(s, i, 'true', True)
    if c == 'f':
        return _expect_word(s, i, 'false', False)
    if c == 'n':
        return _expect_word(s, i, 'null', None)
    if c == '-' or '0' <= c <= '9':
        return _parse_number(s, i)
    raise _JSONError('unexpected character %r' % (c,))


def _expect_word(s, i, word, value):
    j = i + len(word)
    if s[i:j] == word:
        return value, j
    raise _JSONError('invalid literal')


def _parse_object(s, i):
    i += 1  # consume '{'
    obj = {}
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == '}':
        return obj, i + 1
    while True:
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != '"':
            raise _JSONError('expected object key')
        key, i = _parse_string(s, i)
        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != ':':
            raise _JSONError("expected ':' in object")
        value, i = _parse_value(s, i + 1)
        obj[key] = value
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError('unterminated object')
        if s[i] == ',':
            i += 1
            continue
        if s[i] == '}':
            return obj, i + 1
        raise _JSONError("expected ',' or '}' in object")


def _parse_array(s, i):
    i += 1  # consume '['
    arr = []
    i = _skip_ws(s, i)
    if i < len(s) and s[i] == ']':
        return arr, i + 1
    while True:
        value, i = _parse_value(s, i)
        arr.append(value)
        i = _skip_ws(s, i)
        if i >= len(s):
            raise _JSONError('unterminated array')
        if s[i] == ',':
            i += 1
            continue
        if s[i] == ']':
            return arr, i + 1
        raise _JSONError("expected ',' or ']' in array")


def _parse_string(s, i):
    i += 1  # consume opening '"'
    parts = []
    while True:
        if i >= len(s):
            raise _JSONError('unterminated string')
        c = s[i]
        if c == '"':
            return ''.join(parts), i + 1
        if c == '\\':
            i += 1
            if i >= len(s):
                raise _JSONError('unterminated escape')
            e = s[i]
            if e in _ESCAPES:
                parts.append(_ESCAPES[e])
                i += 1
            elif e == 'u':
                code, i = _parse_unicode_escape(s, i)
                if 0xD800 <= code <= 0xDBFF:
                    # Possible UTF-16 surrogate pair: \uD8xx\uDCxx
                    pair = None
                    if s[i:i + 2] == '\\u' and i + 6 <= len(s):
                        lo = _hex4(s, i + 2)
                        if lo is not None and 0xDC00 <= lo <= 0xDFFF:
                            pair = 0x10000 + ((code - 0xD800) << 10) + (lo - 0xDC00)
                    if pair is not None:
                        parts.append(chr(pair))
                        i += 6
                    else:
                        parts.append(chr(code))  # lone surrogate, keep as-is
                else:
                    parts.append(chr(code))
            else:
                raise _JSONError('invalid escape \\%s' % (e,))
        elif c < '\x20':
            raise _JSONError('unescaped control character in string')
        else:
            parts.append(c)
            i += 1


def _hex4(s, i):
    """Value of the 4 hex digits at s[i:i+4], or None if not 4 valid digits."""
    chunk = s[i:i + 4]
    if len(chunk) != 4:
        return None
    value = 0
    for ch in chunk:
        if ch not in _HEX:
            return None
        value = value * 16 + int(ch, 16)
    return value


def _parse_unicode_escape(s, i):
    """Parse the 4 hex digits following '\\u' at position i (which is at 'u')."""
    code = _hex4(s, i + 1)
    if code is None:
        raise _JSONError('invalid \\u escape')
    return code, i + 5


def _parse_number(s, i):
    start = i
    if i < len(s) and s[i] == '-':
        i += 1
    if i >= len(s):
        raise _JSONError('invalid number')
    # Integer part: '0' alone, or a nonzero-leading digit sequence.
    if s[i] == '0':
        i += 1
    elif '1' <= s[i] <= '9':
        while i < len(s) and '0' <= s[i] <= '9':
            i += 1
    else:
        raise _JSONError('invalid number')
    is_float = False
    # Fraction
    if i < len(s) and s[i] == '.':
        is_float = True
        i += 1
        if i >= len(s) or not ('0' <= s[i] <= '9'):
            raise _JSONError('invalid number')
        while i < len(s) and '0' <= s[i] <= '9':
            i += 1
    # Exponent
    if i < len(s) and s[i] in 'eE':
        is_float = True
        i += 1
        if i < len(s) and s[i] in '+-':
            i += 1
        if i >= len(s) or not ('0' <= s[i] <= '9'):
            raise _JSONError('invalid number')
        while i < len(s) and '0' <= s[i] <= '9':
            i += 1
    token = s[start:i]
    if is_float:
        return float(token), i
    return int(token), i
