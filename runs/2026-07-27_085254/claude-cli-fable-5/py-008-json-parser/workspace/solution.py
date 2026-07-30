def parse(text: str):
    if not isinstance(text, str):
        return None

    i = 0
    n = len(text)

    class Fail(Exception):
        pass

    def skip_ws():
        nonlocal i
        while i < n and text[i] in " \t\n\r":
            i += 1

    def parse_value():
        nonlocal i
        skip_ws()
        if i >= n:
            raise Fail()
        c = text[i]
        if c == '{':
            return parse_object()
        if c == '[':
            return parse_array()
        if c == '"':
            return parse_string()
        if c == '-' or c.isdigit():
            return parse_number()
        if text.startswith("true", i):
            i += 4
            return True
        if text.startswith("false", i):
            i += 5
            return False
        if text.startswith("null", i):
            i += 4
            return None
        raise Fail()

    def parse_object():
        nonlocal i
        i += 1  # consume '{'
        obj = {}
        skip_ws()
        if i < n and text[i] == '}':
            i += 1
            return obj
        while True:
            skip_ws()
            if i >= n or text[i] != '"':
                raise Fail()
            key = parse_string()
            skip_ws()
            if i >= n or text[i] != ':':
                raise Fail()
            i += 1
            obj[key] = parse_value()
            skip_ws()
            if i >= n:
                raise Fail()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == '}':
                i += 1
                return obj
            raise Fail()

    def parse_array():
        nonlocal i
        i += 1  # consume '['
        arr = []
        skip_ws()
        if i < n and text[i] == ']':
            i += 1
            return arr
        while True:
            arr.append(parse_value())
            skip_ws()
            if i >= n:
                raise Fail()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == ']':
                i += 1
                return arr
            raise Fail()

    def parse_string():
        nonlocal i
        i += 1  # consume opening '"'
        out = []
        escapes = {'"': '"', '\\': '\\', '/': '/', 'b': '\b',
                   'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}
        while True:
            if i >= n:
                raise Fail()
            c = text[i]
            if c == '"':
                i += 1
                return ''.join(out)
            if c == '\\':
                i += 1
                if i >= n:
                    raise Fail()
                e = text[i]
                if e in escapes:
                    out.append(escapes[e])
                    i += 1
                elif e == 'u':
                    i += 1
                    if i + 4 > n:
                        raise Fail()
                    hex4 = text[i:i + 4]
                    if any(h not in "0123456789abcdefABCDEF" for h in hex4):
                        raise Fail()
                    code = int(hex4, 16)
                    i += 4
                    # combine surrogate pairs when both halves are present
                    if 0xD800 <= code <= 0xDBFF and text.startswith('\\u', i) and i + 6 <= n:
                        hex4b = text[i + 2:i + 6]
                        if all(h in "0123456789abcdefABCDEF" for h in hex4b):
                            low = int(hex4b, 16)
                            if 0xDC00 <= low <= 0xDFFF:
                                code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                                i += 6
                    out.append(chr(code))
                else:
                    raise Fail()
            elif '\x00' <= c <= '\x1f':
                raise Fail()  # unescaped control character
            else:
                out.append(c)
                i += 1

    def parse_number():
        nonlocal i
        start = i
        if i < n and text[i] == '-':
            i += 1
        if i >= n or not text[i].isdigit():
            raise Fail()
        if text[i] == '0':
            i += 1
            if i < n and text[i].isdigit():
                raise Fail()  # leading zero
        else:
            while i < n and text[i].isdigit():
                i += 1
        is_float = False
        if i < n and text[i] == '.':
            is_float = True
            i += 1
            if i >= n or not text[i].isdigit():
                raise Fail()
            while i < n and text[i].isdigit():
                i += 1
        if i < n and text[i] in 'eE':
            is_float = True
            i += 1
            if i < n and text[i] in '+-':
                i += 1
            if i >= n or not text[i].isdigit():
                raise Fail()
            while i < n and text[i].isdigit():
                i += 1
        s = text[start:i]
        return float(s) if is_float else int(s)

    try:
        value = parse_value()
        skip_ws()
        if i != n:
            return None
        return value
    except Fail:
        return None
