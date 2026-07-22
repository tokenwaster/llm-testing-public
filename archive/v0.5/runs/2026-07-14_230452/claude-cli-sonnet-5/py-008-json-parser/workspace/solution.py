def parse(text: str):
    if not isinstance(text, str):
        return None

    n = len(text)
    pos = 0

    def skip_ws(i):
        while i < n and text[i] in ' \t\n\r':
            i += 1
        return i

    def parse_value(i):
        if i >= n:
            return None, None
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
        return None, None

    def fail():
        raise ValueError()

    def parse_object(i):
        obj = {}
        i += 1  # skip {
        i = skip_ws(i)
        if i < n and text[i] == '}':
            return obj, i + 1
        while True:
            i = skip_ws(i)
            if i >= n or text[i] != '"':
                fail()
            key, i = parse_string(i)
            i = skip_ws(i)
            if i >= n or text[i] != ':':
                fail()
            i += 1
            i = skip_ws(i)
            val, i = parse_value(i)
            if i is None:
                fail()
            obj[key] = val
            i = skip_ws(i)
            if i >= n:
                fail()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == '}':
                return obj, i + 1
            fail()

    def parse_array(i):
        arr = []
        i += 1  # skip [
        i = skip_ws(i)
        if i < n and text[i] == ']':
            return arr, i + 1
        while True:
            i = skip_ws(i)
            val, i = parse_value(i)
            if i is None:
                fail()
            arr.append(val)
            i = skip_ws(i)
            if i >= n:
                fail()
            if text[i] == ',':
                i += 1
                continue
            if text[i] == ']':
                return arr, i + 1
            fail()

    def parse_string(i):
        if text[i] != '"':
            fail()
        i += 1
        result = []
        while True:
            if i >= n:
                fail()
            c = text[i]
            if c == '"':
                return ''.join(result), i + 1
            if c == '\\':
                i += 1
                if i >= n:
                    fail()
                e = text[i]
                if e == '"':
                    result.append('"')
                elif e == '\\':
                    result.append('\\')
                elif e == '/':
                    result.append('/')
                elif e == 'b':
                    result.append('\b')
                elif e == 'f':
                    result.append('\f')
                elif e == 'n':
                    result.append('\n')
                elif e == 'r':
                    result.append('\r')
                elif e == 't':
                    result.append('\t')
                elif e == 'u':
                    if i + 4 >= n:
                        fail()
                    hex_str = text[i + 1:i + 5]
                    if len(hex_str) != 4:
                        fail()
                    try:
                        code = int(hex_str, 16)
                    except ValueError:
                        fail()
                    result.append(chr(code))
                    i += 4
                else:
                    fail()
                i += 1
            else:
                # control characters not allowed unescaped
                if ord(c) < 0x20:
                    fail()
                result.append(c)
                i += 1

    def parse_number(i):
        start = i
        if i < n and text[i] == '-':
            i += 1
        if i >= n or not text[i].isdigit():
            fail()
        if text[i] == '0':
            i += 1
        else:
            while i < n and text[i].isdigit():
                i += 1
        is_float = False
        if i < n and text[i] == '.':
            is_float = True
            i += 1
            if i >= n or not text[i].isdigit():
                fail()
            while i < n and text[i].isdigit():
                i += 1
        if i < n and text[i] in 'eE':
            is_float = True
            i += 1
            if i < n and text[i] in '+-':
                i += 1
            if i >= n or not text[i].isdigit():
                fail()
            while i < n and text[i].isdigit():
                i += 1
        num_str = text[start:i]
        if is_float:
            return float(num_str), i
        else:
            return int(num_str), i

    try:
        i = skip_ws(0)
        val, i = parse_value(i)
        if i is None:
            return None
        i = skip_ws(i)
        if i != n:
            return None
        return val
    except (ValueError, IndexError):
        return None
