def parse(text):
    """Parse a JSON document, returning the equivalent Python object,
    or None if the input is not valid JSON."""

    _WS = " \t\n\r"
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

    class _Error(Exception):
        pass

    n = len(text)

    def skip_ws(i):
        while i < n and text[i] in _WS:
            i += 1
        return i

    def parse_value(i):
        i = skip_ws(i)
        if i >= n:
            raise _Error()
        c = text[i]
        if c == '{':
            return parse_object(i)
        if c == '[':
            return parse_array(i)
        if c == '"':
            return parse_string(i)
        if c == '-' or c.isdigit():
            return parse_number(i)
        if text.startswith("true", i):
            return True, i + 4
        if text.startswith("false", i):
            return False, i + 5
        if text.startswith("null", i):
            return None, i + 4
        raise _Error()

    def parse_string(i):
        # text[i] == '"'
        i += 1
        chars = []
        while True:
            if i >= n:
                raise _Error()
            c = text[i]
            if c == '"':
                return "".join(chars), i + 1
            if c == '\\':
                i += 1
                if i >= n:
                    raise _Error()
                e = text[i]
                if e in _ESCAPES:
                    chars.append(_ESCAPES[e])
                    i += 1
                elif e == 'u':
                    hexdigits = text[i + 1:i + 5]
                    if len(hexdigits) != 4 or not all(
                        h in "0123456789abcdefABCDEF" for h in hexdigits
                    ):
                        raise _Error()
                    chars.append(chr(int(hexdigits, 16)))
                    i += 5
                else:
                    raise _Error()
            elif ord(c) < 0x20:
                # control characters must be escaped
                raise _Error()
            else:
                chars.append(c)
                i += 1

    def parse_number(i):
        start = i
        if i < n and text[i] == '-':
            i += 1
        # integer part
        if i >= n or not text[i].isdigit():
            raise _Error()
        if text[i] == '0':
            i += 1
            # no leading zeros: next char must not be a digit
            if i < n and text[i].isdigit():
                raise _Error()
        else:
            while i < n and text[i].isdigit():
                i += 1
        is_float = False
        # fraction
        if i < n and text[i] == '.':
            is_float = True
            i += 1
            if i >= n or not text[i].isdigit():
                raise _Error()
            while i < n and text[i].isdigit():
                i += 1
        # exponent
        if i < n and text[i] in 'eE':
            is_float = True
            i += 1
            if i < n and text[i] in '+-':
                i += 1
            if i >= n or not text[i].isdigit():
                raise _Error()
            while i < n and text[i].isdigit():
                i += 1
        s = text[start:i]
        if is_float:
            return float(s), i
        return int(s), i

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
                raise _Error()
            if text[i] == ']':
                return result, i + 1
            if text[i] != ',':
                raise _Error()
            i += 1

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
                raise _Error()
            key, i = parse_string(i)
            i = skip_ws(i)
            if i >= n or text[i] != ':':
                raise _Error()
            i += 1
            value, i = parse_value(i)
            result[key] = value
            i = skip_ws(i)
            if i >= n:
                raise _Error()
            if text[i] == '}':
                return result, i + 1
            if text[i] != ',':
                raise _Error()
            i += 1

    if not isinstance(text, str):
        return None

    try:
        value, i = parse_value(0)
        i = skip_ws(i)
        if i != n:
            return None
        return value
    except _Error:
        return None
    except (ValueError, IndexError, RecursionError):
        return None
