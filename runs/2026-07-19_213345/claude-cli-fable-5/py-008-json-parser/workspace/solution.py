def parse(text: str):
    if not isinstance(text, str):
        return None

    class _Fail(Exception):
        pass

    n = len(text)

    def skip_ws(i):
        while i < n and text[i] in ' \t\n\r':
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
        if text.startswith('true', i):
            return True, i + 4
        if text.startswith('false', i):
            return False, i + 5
        if text.startswith('null', i):
            return None, i + 4
        raise _Fail()

    def parse_object(i):
        obj = {}
        i = skip_ws(i + 1)
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
        arr = []
        i = skip_ws(i + 1)
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

    def parse_string(i):
        i += 1  # skip opening quote
        chars = []
        while True:
            if i >= n:
                raise _Fail()
            c = text[i]
            if c == '"':
                return ''.join(chars), i + 1
            if c == '\\':
                i += 1
                if i >= n:
                    raise _Fail()
                e = text[i]
                if e == '"':
                    chars.append('"')
                elif e == '\\':
                    chars.append('\\')
                elif e == '/':
                    chars.append('/')
                elif e == 'b':
                    chars.append('\b')
                elif e == 'f':
                    chars.append('\f')
                elif e == 'n':
                    chars.append('\n')
                elif e == 'r':
                    chars.append('\r')
                elif e == 't':
                    chars.append('\t')
                elif e == 'u':
                    hex_digits = text[i + 1:i + 5]
                    if len(hex_digits) != 4 or any(
                        h not in '0123456789abcdefABCDEF' for h in hex_digits
                    ):
                        raise _Fail()
                    code = int(hex_digits, 16)
                    i += 4
                    # handle surrogate pairs
                    if 0xD800 <= code <= 0xDBFF and text.startswith('\\u', i + 1):
                        lo_digits = text[i + 3:i + 7]
                        if len(lo_digits) == 4 and all(
                            h in '0123456789abcdefABCDEF' for h in lo_digits
                        ):
                            lo = int(lo_digits, 16)
                            if 0xDC00 <= lo <= 0xDFFF:
                                code = 0x10000 + ((code - 0xD800) << 10) + (lo - 0xDC00)
                                i += 6
                    chars.append(chr(code))
                else:
                    raise _Fail()
                i += 1
            elif '\x00' <= c <= '\x1f':
                raise _Fail()  # unescaped control character
            else:
                chars.append(c)
                i += 1

    def parse_number(i):
        start = i
        if i < n and text[i] == '-':
            i += 1
        if i >= n or not text[i].isdigit():
            raise _Fail()
        if text[i] == '0':
            i += 1
            if i < n and text[i].isdigit():
                raise _Fail()  # leading zeros
        else:
            while i < n and text[i].isdigit():
                i += 1
        is_float = False
        if i < n and text[i] == '.':
            is_float = True
            i += 1
            if i >= n or not text[i].isdigit():
                raise _Fail()
            while i < n and text[i].isdigit():
                i += 1
        if i < n and text[i] in 'eE':
            is_float = True
            i += 1
            if i < n and text[i] in '+-':
                i += 1
            if i >= n or not text[i].isdigit():
                raise _Fail()
            while i < n and text[i].isdigit():
                i += 1
        literal = text[start:i]
        return (float(literal) if is_float else int(literal)), i

    try:
        value, i = parse_value(0)
        i = skip_ws(i)
        if i != n:
            return None  # trailing garbage
        return value
    except _Fail:
        return None
