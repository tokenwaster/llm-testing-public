def parse(text):
    if not isinstance(text, str):
        return None

    n = len(text)
    pos = 0

    def skip_ws():
        nonlocal pos
        while pos < n and text[pos] in ' \t\n\r':
            pos += 1

    def parse_value():
        nonlocal pos
        if pos >= n:
            return False, None
        c = text[pos]
        if c == '{':
            return parse_object()
        if c == '[':
            return parse_array()
        if c == '"':
            return parse_string()
        if c == 't':
            if text[pos:pos + 4] == 'true':
                pos += 4
                return True, True
            return False, None
        if c == 'f':
            if text[pos:pos + 5] == 'false':
                pos += 5
                return True, False
            return False, None
        if c == 'n':
            if text[pos:pos + 4] == 'null':
                pos += 4
                return True, None
            return False, None
        if c == '-' or c.isdigit():
            return parse_number()
        return False, None

    def parse_object():
        nonlocal pos
        pos += 1  # skip {
        obj = {}
        skip_ws()
        if pos < n and text[pos] == '}':
            pos += 1
            return True, obj
        while True:
            skip_ws()
            if pos >= n or text[pos] != '"':
                return False, None
            ok, key = parse_string()
            if not ok:
                return False, None
            skip_ws()
            if pos >= n or text[pos] != ':':
                return False, None
            pos += 1
            skip_ws()
            ok, val = parse_value()
            if not ok:
                return False, None
            obj[key] = val
            skip_ws()
            if pos >= n:
                return False, None
            if text[pos] == ',':
                pos += 1
                continue
            elif text[pos] == '}':
                pos += 1
                return True, obj
            else:
                return False, None

    def parse_array():
        nonlocal pos
        pos += 1  # skip [
        arr = []
        skip_ws()
        if pos < n and text[pos] == ']':
            pos += 1
            return True, arr
        while True:
            skip_ws()
            ok, val = parse_value()
            if not ok:
                return False, None
            arr.append(val)
            skip_ws()
            if pos >= n:
                return False, None
            if text[pos] == ',':
                pos += 1
                continue
            elif text[pos] == ']':
                pos += 1
                return True, arr
            else:
                return False, None

    def parse_string():
        nonlocal pos
        pos += 1  # skip opening quote
        chars = []
        while True:
            if pos >= n:
                return False, None
            c = text[pos]
            if c == '"':
                pos += 1
                return True, ''.join(chars)
            if c == '\\':
                pos += 1
                if pos >= n:
                    return False, None
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
                    hex_digits = text[pos + 1:pos + 5]
                    if len(hex_digits) != 4:
                        return False, None
                    try:
                        code = int(hex_digits, 16)
                    except ValueError:
                        return False, None
                    chars.append(chr(code))
                    pos += 4
                else:
                    return False, None
                pos += 1
            else:
                # control characters (0x00-0x1f) are not valid unescaped in JSON strings
                if ord(c) < 0x20:
                    return False, None
                chars.append(c)
                pos += 1

    def parse_number():
        nonlocal pos
        start = pos
        if pos < n and text[pos] == '-':
            pos += 1
        if pos >= n or not text[pos].isdigit():
            return False, None
        if text[pos] == '0':
            pos += 1
        else:
            while pos < n and text[pos].isdigit():
                pos += 1
        is_float = False
        if pos < n and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= n or not text[pos].isdigit():
                return False, None
            while pos < n and text[pos].isdigit():
                pos += 1
        if pos < n and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < n and text[pos] in '+-':
                pos += 1
            if pos >= n or not text[pos].isdigit():
                return False, None
            while pos < n and text[pos].isdigit():
                pos += 1
        num_str = text[start:pos]
        try:
            if is_float:
                return True, float(num_str)
            else:
                return True, int(num_str)
        except ValueError:
            return False, None

    skip_ws()
    ok, value = parse_value()
    if not ok:
        return None
    skip_ws()
    if pos != n:
        return None
    return value
