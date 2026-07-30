def parse(text: str):
    pos = 0

    def peek():
        return pos < len(text)

    def current():
        return text[pos] if pos < len(text) else ''

    def skip_whitespace():
        nonlocal pos
        while pos < len(text) and text[pos] in ' \t\n\r':
            pos += 1

    def parse_value():
        skip_whitespace()
        if not peek():
            return None, False
        c = current()
        if c == '"':
            return parse_string()
        elif c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == 't':
            return parse_literal('true', True)
        elif c == 'f':
            return parse_literal('false', False)
        elif c == 'n':
            return parse_literal('null', None)
        elif c == '-' or c.isdigit():
            return parse_number()
        else:
            return None, False

    def parse_literal(literal, value):
        nonlocal pos
        if text[pos:pos+len(literal)] == literal:
            pos += len(literal)
            return value, True
        return None, False

    def parse_string():
        nonlocal pos
        if current() != '"':
            return None, False
        pos += 1
        result = []
        while pos < len(text):
            c = text[pos]
            if c == '"':
                pos += 1
                return ''.join(result), True
            elif c == '\\':
                pos += 1
                if pos >= len(text):
                    return None, False
                esc = text[pos]
                if esc == '"':
                    result.append('"')
                elif esc == '\\':
                    result.append('\\')
                elif esc == '/':
                    result.append('/')
                elif esc == 'b':
                    result.append('\b')
                elif esc == 'f':
                    result.append('\f')
                elif esc == 'n':
                    result.append('\n')
                elif esc == 'r':
                    result.append('\r')
                elif esc == 't':
                    result.append('\t')
                elif esc == 'u':
                    if pos + 4 >= len(text):
                        return None, False
                    hex_str = text[pos+1:pos+5]
                    if not all(h in '0123456789abcdefABCDEF' for h in hex_str):
                        return None, False
                    result.append(chr(int(hex_str, 16)))
                    pos += 4
                else:
                    return None, False
                pos += 1
            elif ord(c) < 0x20:
                return None, False
            else:
                result.append(c)
                pos += 1
        return None, False

    def parse_number():
        nonlocal pos
        start = pos
        is_float = False

        if current() == '-':
            pos += 1
        if pos >= len(text):
            return None, False

        if current() == '0':
            pos += 1
            if pos < len(text) and text[pos].isdigit():
                return None, False
        elif current().isdigit():
            while pos < len(text) and text[pos].isdigit():
                pos += 1
        else:
            return None, False

        if pos < len(text) and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                return None, False
            while pos < len(text) and text[pos].isdigit():
                pos += 1

        if pos < len(text) and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < len(text) and text[pos] in '+-':
                pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                return None, False
            while pos < len(text) and text[pos].isdigit():
                pos += 1

        num_str = text[start:pos]
        try:
            if is_float:
                return float(num_str), True
            else:
                return int(num_str), True
        except ValueError:
            return None, False

    def parse_array():
        nonlocal pos
        if current() != '[':
            return None, False
        pos += 1
        result = []
        skip_whitespace()
        if pos < len(text) and current() == ']':
            pos += 1
            return result, True
        while True:
            val, ok = parse_value()
            if not ok:
                return None, False
            result.append(val)
            skip_whitespace()
            if pos >= len(text):
                return None, False
            c = current()
            if c == ']':
                pos += 1
                return result, True
            elif c == ',':
                pos += 1
                skip_whitespace()
                if pos < len(text) and current() == ']':
                    return None, False
            else:
                return None, False

    def parse_object():
        nonlocal pos
        if current() != '{':
            return None, False
        pos += 1
        result = {}
        skip_whitespace()
        if pos < len(text) and current() == '}':
            pos += 1
            return result, True
        while True:
            skip_whitespace()
            if pos >= len(text) or current() != '"':
                return None, False
            key, ok = parse_string()
            if not ok:
                return None, False
            skip_whitespace()
            if pos >= len(text) or current() != ':':
                return None, False
            pos += 1
            val, ok = parse_value()
            if not ok:
                return None, False
            result[key] = val
            skip_whitespace()
            if pos >= len(text):
                return None, False
            c = current()
            if c == '}':
                pos += 1
                return result, True
            elif c == ',':
                pos += 1
                skip_whitespace()
                if pos < len(text) and current() == '}':
                    return None, False
            else:
                return None, False

    try:
        value, ok = parse_value()
        if not ok:
            return None
        skip_whitespace()
        if pos != len(text):
            return None
        return value
    except Exception:
        return None
