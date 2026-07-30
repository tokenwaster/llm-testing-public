def parse(text):
    """Parse a JSON document, returning the equivalent Python object,
    or None if the input is not valid JSON."""

    if not isinstance(text, str):
        return None

    n = len(text)

    WS = " \t\n\r"

    ESCAPES = {
        '"': '"',
        '\\': '\\',
        '/': '/',
        'b': '\b',
        'f': '\f',
        'n': '\n',
        'r': '\r',
        't': '\t',
    }

    def skip_ws(i):
        while i < n and text[i] in WS:
            i += 1
        return i

    def parse_value(i):
        # returns (value, next_index) or raises _Err
        i = skip_ws(i)
        if i >= n:
            raise _Err()
        c = text[i]
        if c == '{':
            return parse_object(i)
        if c == '[':
            return parse_array(i)
        if c == '"':
            return parse_string(i)
        if c == '-' or c.isdigit():
            return parse_number(i)
        if text.startswith('true', i):
            return True, i + 4
        if text.startswith('false', i):
            return False, i + 5
        if text.startswith('null', i):
            return None, i + 4
        raise _Err()

    def parse_string(i):
        # text[i] == '"'
        assert text[i] == '"'
        i += 1
        chars = []
        while True:
            if i >= n:
                raise _Err()
            c = text[i]
            if c == '"':
                return ''.join(chars), i + 1
            if c == '\\':
                i += 1
                if i >= n:
                    raise _Err()
                e = text[i]
                if e in ESCAPES:
                    chars.append(ESCAPES[e])
                    i += 1
                elif e == 'u':
                    hexdigits = text[i + 1:i + 5]
                    if len(hexdigits) != 4 or any(
                        h not in '0123456789abcdefABCDEF' for h in hexdigits
                    ):
                        raise _Err()
                    chars.append(chr(int(hexdigits, 16)))
                    i += 5
                else:
                    raise _Err()
            elif ord(c) < 0x20:
                # control characters must be escaped
                raise _Err()
            else:
                chars.append(c)
                i += 1

    def parse_number(i):
        start = i
        # optional minus
        if i < n and text[i] == '-':
            i += 1
        # integer part
        if i >= n or not text[i].isdigit():
            raise _Err()
        if text[i] == '0':
            i += 1
            # no leading zeros: next must not be a digit
            if i < n and text[i].isdigit():
                raise _Err()
        else:
            while i < n and text[i].isdigit():
                i += 1
        is_float = False
        # fraction
        if i < n and text[i] == '.':
            is_float = True
            i += 1
            if i >= n or not text[i].isdigit():
                raise _Err()
            while i < n and text[i].isdigit():
                i += 1
        # exponent
        if i < n and text[i] in 'eE':
            is_float = True
            i += 1
            if i < n and text[i] in '+-':
                i += 1
            if i >= n or not text[i].isdigit():
                raise _Err()
            while i < n and text[i].isdigit():
                i += 1
        literal = text[start:i]
        if is_float:
            return float(literal), i
        return int(literal), i

    def parse_array(i):
        # text[i] == '['
        i += 1
        result = []
        i = skip_ws(i)
        if i < n and text[i] == ']':
            return result, i + 1
        while True:
            value, i = parse_value(i)
            result.append(value)
            i = skip_ws(i)
            if i >= n:
                raise _Err()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == ']':
                return result, i + 1
            raise _Err()

    def parse_object(i):
        # text[i] == '{'
        i += 1
        result = {}
        i = skip_ws(i)
        if i < n and text[i] == '}':
            return result, i + 1
        while True:
            i = skip_ws(i)
            if i >= n or text[i] != '"':
                raise _Err()
            key, i = parse_string(i)
            i = skip_ws(i)
            if i >= n or text[i] != ':':
                raise _Err()
            i += 1
            value, i = parse_value(i)
            result[key] = value
            i = skip_ws(i)
            if i >= n:
                raise _Err()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == '}':
                return result, i + 1
            raise _Err()

    try:
        value, i = parse_value(0)
        i = skip_ws(i)
        if i != n:
            return None
        return value
    except _Err:
        return None


class _Err(Exception):
    pass
