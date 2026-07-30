def parse(text: str):
    if not isinstance(text, str):
        return None
    n = len(text)
    i = [0]

    def skip_ws():
        while i[0] < n and text[i[0]] in ' \t\n\r':
            i[0] += 1

    def peek():
        if i[0] < n:
            return text[i[0]]
        return None

    def parse_value():
        skip_ws()
        c = peek()
        if c is None:
            return None, False
        if c == '{':
            return parse_object()
        if c == '[':
            return parse_array()
        if c == '"':
            return parse_string()
        if c == 't':
            return parse_literal('true', True)
        if c == 'f':
            return parse_literal('false', False)
        if c == 'n':
            return parse_literal('null', None)
        if c == '-' or ('0' <= c <= '9'):
            return parse_number()
        return None, False

    def parse_literal(s, val):
        if text[i[0]:i[0] + len(s)] == s:
            i[0] += len(s)
            return val, True
        return None, False

    def parse_string():
        if peek() != '"':
            return None, False
        i[0] += 1
        chars = []
        while i[0] < n:
            c = text[i[0]]
            if c == '"':
                i[0] += 1
                return ''.join(chars), True
            if c == '\\':
                i[0] += 1
                if i[0] >= n:
                    return None, False
                e = text[i[0]]
                escapes = {
                    '"': '"',
                    '\\': '\\',
                    '/': '/',
                    'b': '\b',
                    'f': '\f',
                    'n': '\n',
                    'r': '\r',
                    't': '\t',
                }
                if e in escapes:
                    chars.append(escapes[e])
                    i[0] += 1
                elif e == 'u':
                    i[0] += 1
                    if i[0] + 4 > n:
                        return None, False
                    hexpart = text[i[0]:i[0] + 4]
                    try:
                        cp = int(hexpart, 16)
                    except ValueError:
                        return None, False
                    chars.append(chr(cp))
                    i[0] += 4
                else:
                    return None, False
            elif ord(c) < 0x20:
                return None, False
            else:
                chars.append(c)
                i[0] += 1
        return None, False

    def parse_number():
        start = i[0]
        if peek() == '-':
            i[0] += 1
        if peek() is None or not ('0' <= peek() <= '9'):
            return None, False
        if peek() == '0':
            i[0] += 1
            if peek() is not None and '0' <= peek() <= '9':
                return None, False
        else:
            while peek() is not None and '0' <= peek() <= '9':
                i[0] += 1
        is_float = False
        if peek() == '.':
            is_float = True
            i[0] += 1
            if peek() is None or not ('0' <= peek() <= '9'):
                return None, False
            while peek() is not None and '0' <= peek() <= '9':
                i[0] += 1
        if peek() in ('e', 'E'):
            is_float = True
            i[0] += 1
            if peek() in ('+', '-'):
                i[0] += 1
            if peek() is None or not ('0' <= peek() <= '9'):
                return None, False
            while peek() is not None and '0' <= peek() <= '9':
                i[0] += 1
        s = text[start:i[0]]
        try:
            if is_float:
                return float(s), True
            return int(s), True
        except ValueError:
            return None, False

    def parse_object():
        if peek() != '{':
            return None, False
        i[0] += 1
        skip_ws()
        obj = {}
        if peek() == '}':
            i[0] += 1
            return obj, True
        while True:
            skip_ws()
            if peek() != '"':
                return None, False
            key, ok = parse_string()
            if not ok:
                return None, False
            skip_ws()
            if peek() != ':':
                return None, False
            i[0] += 1
            val, ok = parse_value()
            if not ok:
                return None, False
            obj[key] = val
            skip_ws()
            if peek() == '}':
                i[0] += 1
                return obj, True
            if peek() != ',':
                return None, False
            i[0] += 1
            skip_ws()
            if peek() == '}':
                return None, False

    def parse_array():
        if peek() != '[':
            return None, False
        i[0] += 1
        skip_ws()
        arr = []
        if peek() == ']':
            i[0] += 1
            return arr, True
        while True:
            val, ok = parse_value()
            if not ok:
                return None, False
            arr.append(val)
            skip_ws()
            if peek() == ']':
                i[0] += 1
                return arr, True
            if peek() != ',':
                return None, False
            i[0] += 1
            skip_ws()
            if peek() == ']':
                return None, False

    result, ok = parse_value()
    if not ok:
        return None
    skip_ws()
    if i[0] != n:
        return None
    return result
