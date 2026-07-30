def parse(text: str):
    if not isinstance(text, str):
        return None

    n = len(text)
    pos = 0

    WS = " \t\n\r"

    def skip_ws(p):
        while p < n and text[p] in WS:
            p += 1
        return p

    def parse_value(p):
        if p >= n:
            return None, None
        c = text[p]
        if c == '{':
            return parse_object(p)
        if c == '[':
            return parse_array(p)
        if c == '"':
            return parse_string(p)
        if c == 't':
            if text[p:p+4] == 'true':
                return True, p + 4
            return None, None
        if c == 'f':
            if text[p:p+5] == 'false':
                return False, p + 5
            return None, None
        if c == 'n':
            if text[p:p+4] == 'null':
                return None, p + 4
            return None, None
        if c == '-' or c.isdigit():
            return parse_number(p)
        return None, None

    def parse_object(p):
        assert text[p] == '{'
        p += 1
        obj = {}
        p = skip_ws(p)
        if p < n and text[p] == '}':
            return obj, p + 1
        while True:
            p = skip_ws(p)
            if p >= n or text[p] != '"':
                return None, None
            key, p = parse_string(p)
            if key is None and (p is None):
                return None, None
            p = skip_ws(p)
            if p >= n or text[p] != ':':
                return None, None
            p += 1
            p = skip_ws(p)
            val, p = parse_value(p)
            if p is None:
                return None, None
            obj[key] = val
            p = skip_ws(p)
            if p >= n:
                return None, None
            if text[p] == ',':
                p += 1
                continue
            if text[p] == '}':
                return obj, p + 1
            return None, None

    def parse_array(p):
        assert text[p] == '['
        p += 1
        arr = []
        p = skip_ws(p)
        if p < n and text[p] == ']':
            return arr, p + 1
        while True:
            p = skip_ws(p)
            val, p = parse_value(p)
            if p is None:
                return None, None
            arr.append(val)
            p = skip_ws(p)
            if p >= n:
                return None, None
            if text[p] == ',':
                p += 1
                continue
            if text[p] == ']':
                return arr, p + 1
            return None, None

    def parse_string(p):
        assert text[p] == '"'
        p += 1
        chars = []
        while True:
            if p >= n:
                return None, None
            c = text[p]
            if c == '"':
                return ''.join(chars), p + 1
            if ord(c) < 0x20:
                return None, None
            if c == '\\':
                p += 1
                if p >= n:
                    return None, None
                esc = text[p]
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
                    hex_digits = text[p+1:p+5]
                    if len(hex_digits) != 4:
                        return None, None
                    try:
                        code = int(hex_digits, 16)
                    except ValueError:
                        return None, None
                    chars.append(chr(code))
                    p += 4
                else:
                    return None, None
                p += 1
            else:
                chars.append(c)
                p += 1

    def parse_number(p):
        start = p
        if p < n and text[p] == '-':
            p += 1
        if p >= n or not text[p].isdigit():
            return None, None
        if text[p] == '0':
            p += 1
        else:
            while p < n and text[p].isdigit():
                p += 1
        is_float = False
        if p < n and text[p] == '.':
            is_float = True
            p += 1
            if p >= n or not text[p].isdigit():
                return None, None
            while p < n and text[p].isdigit():
                p += 1
        if p < n and text[p] in 'eE':
            is_float = True
            p += 1
            if p < n and text[p] in '+-':
                p += 1
            if p >= n or not text[p].isdigit():
                return None, None
            while p < n and text[p].isdigit():
                p += 1
        num_str = text[start:p]
        try:
            if is_float:
                return float(num_str), p
            else:
                return int(num_str), p
        except ValueError:
            return None, None

    pos = skip_ws(pos)
    if pos >= n:
        return None
    value, pos = parse_value(pos)
    if pos is None:
        return None
    pos = skip_ws(pos)
    if pos != n:
        return None
    return value
