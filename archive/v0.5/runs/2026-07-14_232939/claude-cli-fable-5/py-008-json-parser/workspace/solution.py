def parse(text: str):
    """Parse a JSON document; return the Python equivalent, or None if invalid."""
    if not isinstance(text, str):
        return None

    WS = " \t\n\r"
    n = len(text)

    class _Fail(Exception):
        pass

    def skip_ws(i):
        while i < n and text[i] in WS:
            i += 1
        return i

    def parse_value(i):
        i = skip_ws(i)
        if i >= n:
            raise _Fail()
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
        raise _Fail()

    def parse_object(i):
        i += 1  # past '{'
        obj = {}
        i = skip_ws(i)
        if i < n and text[i] == '}':
            return obj, i + 1
        while True:
            i = skip_ws(i)
            if i >= n or text[i] != '"':
                raise _Fail()
            key, i = parse_string(i)
            i = skip_ws(i)
            if i >= n or text[i] != ':':
                raise _Fail()
            value, i = parse_value(i + 1)
            obj[key] = value
            i = skip_ws(i)
            if i >= n:
                raise _Fail()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == '}':
                return obj, i + 1
            raise _Fail()

    def parse_array(i):
        i += 1  # past '['
        arr = []
        i = skip_ws(i)
        if i < n and text[i] == ']':
            return arr, i + 1
        while True:
            value, i = parse_value(i)
            arr.append(value)
            i = skip_ws(i)
            if i >= n:
                raise _Fail()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == ']':
                return arr, i + 1
            raise _Fail()

    ESCAPES = {
        '"': '"', '\\': '\\', '/': '/', 'b': '\b',
        'f': '\f', 'n': '\n', 'r': '\r', 't': '\t',
    }

    def parse_hex4(i):
        if i + 4 > n:
            raise _Fail()
        quad = text[i:i + 4]
        for ch in quad:
            if ch not in "0123456789abcdefABCDEF":
                raise _Fail()
        return int(quad, 16), i + 4

    def parse_string(i):
        i += 1  # past opening quote
        parts = []
        while True:
            if i >= n:
                raise _Fail()
            c = text[i]
            if c == '"':
                return "".join(parts), i + 1
            if c == '\\':
                i += 1
                if i >= n:
                    raise _Fail()
                e = text[i]
                if e in ESCAPES:
                    parts.append(ESCAPES[e])
                    i += 1
                elif e == 'u':
                    code, i = parse_hex4(i + 1)
                    if 0xD800 <= code <= 0xDBFF and text.startswith('\\u', i):
                        low, j = parse_hex4(i + 2)
                        if 0xDC00 <= low <= 0xDFFF:
                            code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                            i = j
                    parts.append(chr(code))
                else:
                    raise _Fail()
            elif ord(c) < 0x20:
                raise _Fail()
            else:
                parts.append(c)
                i += 1

    def parse_number(i):
        start = i
        if text[i] == '-':
            i += 1
        if i >= n or not text[i].isdigit():
            raise _Fail()
        if text[i] == '0':
            i += 1
            if i < n and text[i].isdigit():
                raise _Fail()  # leading zero
        else:
            while i < n and text[i].isdigit():
                i += 1
        is_int = True
        if i < n and text[i] == '.':
            is_int = False
            i += 1
            if i >= n or not text[i].isdigit():
                raise _Fail()
            while i < n and text[i].isdigit():
                i += 1
        if i < n and text[i] in 'eE':
            is_int = False
            i += 1
            if i < n and text[i] in '+-':
                i += 1
            if i >= n or not text[i].isdigit():
                raise _Fail()
            while i < n and text[i].isdigit():
                i += 1
        literal = text[start:i]
        return (int(literal) if is_int else float(literal)), i

    try:
        value, i = parse_value(0)
        i = skip_ws(i)
        if i != n:
            return None  # trailing garbage
        return value
    except (_Fail, RecursionError):
        return None
