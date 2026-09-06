def parse(text: str):
    if not isinstance(text, str):
        return None
    n = len(text)
    pos = 0
    FAIL = object()

    def skip_ws():
        nonlocal pos
        while pos < n and text[pos] in ' \t\n\r':
            pos += 1

    def parse_literal(word, value):
        nonlocal pos
        if text.startswith(word, pos):
            pos += len(word)
            return value
        return FAIL

    def parse_string():
        nonlocal pos
        # assumes text[pos] == '"'
        pos += 1
        out = []
        while pos < n:
            ch = text[pos]
            if ch == '"':
                pos += 1
                return ''.join(out)
            elif ch == '\\':
                pos += 1
                if pos >= n:
                    return FAIL
                esc = text[pos]
                if esc == '"':
                    out.append('"')
                    pos += 1
                elif esc == '\\':
                    out.append('\\')
                    pos += 1
                elif esc == '/':
                    out.append('/')
                    pos += 1
                elif esc == 'b':
                    out.append('\b')
                    pos += 1
                elif esc == 'f':
                    out.append('\f')
                    pos += 1
                elif esc == 'n':
                    out.append('\n')
                    pos += 1
                elif esc == 'r':
                    out.append('\r')
                    pos += 1
                elif esc == 't':
                    out.append('\t')
                    pos += 1
                elif esc == 'u':
                    if pos + 4 >= n:
                        return FAIL
                    hx = text[pos + 1:pos + 5]
                    if len(hx) != 4:
                        return FAIL
                    for c in hx:
                        if c not in '0123456789abcdefABCDEF':
                            return FAIL
                    code = int(hx, 16)
                    pos += 5
                    if 0xD800 <= code <= 0xDBFF:
                        if pos + 5 <= n and text[pos] == '\\' and text[pos + 1] == 'u':
                            hx2 = text[pos + 2:pos + 6]
                            ok = len(hx2) == 4
                            if ok:
                                for c in hx2:
                                    if c not in '0123456789abcdefABCDEF':
                                        ok = False
                                        break
                            if ok:
                                low = int(hx2, 16)
                                if 0xDC00 <= low <= 0xDFFF:
                                    combined = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                                    out.append(chr(combined))
                                    pos += 6
                                    continue
                        out.append(chr(code))
                    elif 0xDC00 <= code <= 0xDFFF:
                        out.append(chr(code))
                    else:
                        out.append(chr(code))
                else:
                    return FAIL
            else:
                if ord(ch) < 0x20:
                    return FAIL
                out.append(ch)
                pos += 1
        return FAIL

    def parse_number():
        nonlocal pos
        start = pos
        if text[pos] == '-':
            pos += 1
            if pos >= n:
                return FAIL
        if pos >= n:
            return FAIL
        c = text[pos]
        if c == '0':
            pos += 1
            if pos < n and '0' <= text[pos] <= '9':
                return FAIL
        elif '1' <= c <= '9':
            pos += 1
            while pos < n and '0' <= text[pos] <= '9':
                pos += 1
        else:
            return FAIL
        is_float = False
        if pos < n and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= n or not ('0' <= text[pos] <= '9'):
                return FAIL
            while pos < n and '0' <= text[pos] <= '9':
                pos += 1
        if pos < n and (text[pos] == 'e' or text[pos] == 'E'):
            is_float = True
            pos += 1
            if pos < n and (text[pos] == '+' or text[pos] == '-'):
                pos += 1
            if pos >= n or not ('0' <= text[pos] <= '9'):
                return FAIL
            while pos < n and '0' <= text[pos] <= '9':
                pos += 1
        s = text[start:pos]
        try:
            if is_float:
                return float(s)
            else:
                return int(s)
        except Exception:
            return FAIL

    def parse_value():
        nonlocal pos
        skip_ws()
        if pos >= n:
            return FAIL
        c = text[pos]
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
        return FAIL

    def parse_array():
        nonlocal pos
        pos += 1
        skip_ws()
        if pos < n and text[pos] == ']':
            pos += 1
            return []
        arr = []
        while True:
            v = parse_value()
            if v is FAIL:
                return FAIL
            arr.append(v)
            skip_ws()
            if pos >= n:
                return FAIL
            c = text[pos]
            if c == ',':
                pos += 1
                skip_ws()
                if pos < n and text[pos] == ']':
                    return FAIL
                if pos >= n:
                    return FAIL
                continue
            elif c == ']':
                pos += 1
                return arr
            else:
                return FAIL

    def parse_object():
        nonlocal pos
        pos += 1
        skip_ws()
        if pos < n and text[pos] == '}':
            pos += 1
            return {}
        obj = {}
        while True:
            skip_ws()
            if pos >= n or text[pos] != '"':
                return FAIL
            k = parse_string()
            if k is FAIL:
                return FAIL
            skip_ws()
            if pos >= n or text[pos] != ':':
                return FAIL
            pos += 1
            v = parse_value()
            if v is FAIL:
                # need to distinguish valid None from FAIL
                # v is FAIL sentinel means failure; None is valid
                return FAIL
            obj[k] = v
            skip_ws()
            if pos >= n:
                return FAIL
            c = text[pos]
            if c == ',':
                pos += 1
                skip_ws()
                if pos < n and text[pos] == '}':
                    return FAIL
                if pos >= n:
                    return FAIL
                continue
            elif c == '}':
                pos += 1
                return obj
            else:
                return FAIL

    try:
        skip_ws()
        if pos >= n:
            return None
        res = parse_value()
        if res is FAIL:
            return None
        skip_ws()
        if pos != n:
            return None
        return res
    except RecursionError:
        return None
    except Exception:
        return None
