def parse(text: str):
    if not isinstance(text, str):
        return None

    n = len(text)
    pos = 0

    class ParseError(Exception):
        pass

    def skip_ws():
        nonlocal pos
        while pos < n and text[pos] in ' \t\n\r':
            pos += 1

    def parse_value():
        nonlocal pos
        skip_ws()
        if pos >= n:
            raise ParseError()
        c = text[pos]
        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        elif c == 't':
            return parse_literal('true', True)
        elif c == 'f':
            return parse_literal('false', False)
        elif c == 'n':
            return parse_literal('null', None)
        elif c == '-' or c.isdigit():
            return parse_number()
        else:
            raise ParseError()

    def parse_literal(lit, value):
        nonlocal pos
        if text[pos:pos+len(lit)] == lit:
            pos += len(lit)
            return value
        raise ParseError()

    def parse_number():
        nonlocal pos
        start = pos
        if pos < n and text[pos] == '-':
            pos += 1
        if pos >= n or not text[pos].isdigit():
            raise ParseError()
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
                raise ParseError()
            while pos < n and text[pos].isdigit():
                pos += 1

        if pos < n and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < n and text[pos] in '+-':
                pos += 1
            if pos >= n or not text[pos].isdigit():
                raise ParseError()
            while pos < n and text[pos].isdigit():
                pos += 1

        s = text[start:pos]
        if is_float:
            return float(s)
        else:
            return int(s)

    def parse_string():
        nonlocal pos
        if pos >= n or text[pos] != '"':
            raise ParseError()
        pos += 1
        result = []
        while True:
            if pos >= n:
                raise ParseError()
            c = text[pos]
            if c == '"':
                pos += 1
                return ''.join(result)
            elif c == '\\':
                pos += 1
                if pos >= n:
                    raise ParseError()
                esc = text[pos]
                if esc == '"':
                    result.append('"')
                    pos += 1
                elif esc == '\\':
                    result.append('\\')
                    pos += 1
                elif esc == '/':
                    result.append('/')
                    pos += 1
                elif esc == 'b':
                    result.append('\b')
                    pos += 1
                elif esc == 'f':
                    result.append('\f')
                    pos += 1
                elif esc == 'n':
                    result.append('\n')
                    pos += 1
                elif esc == 'r':
                    result.append('\r')
                    pos += 1
                elif esc == 't':
                    result.append('\t')
                    pos += 1
                elif esc == 'u':
                    pos += 1
                    if pos + 4 > n:
                        raise ParseError()
                    hex_digits = text[pos:pos+4]
                    if len(hex_digits) != 4:
                        raise ParseError()
                    for ch in hex_digits:
                        if ch not in '0123456789abcdefABCDEF':
                            raise ParseError()
                    code = int(hex_digits, 16)
                    pos += 4
                    result.append(chr(code))
                else:
                    raise ParseError()
            elif ord(c) < 0x20:
                raise ParseError()
            else:
                result.append(c)
                pos += 1

    def parse_array():
        nonlocal pos
        if pos >= n or text[pos] != '[':
            raise ParseError()
        pos += 1
        result = []
        skip_ws()
        if pos < n and text[pos] == ']':
            pos += 1
            return result
        while True:
            val = parse_value()
            result.append(val)
            skip_ws()
            if pos >= n:
                raise ParseError()
            if text[pos] == ',':
                pos += 1
                skip_ws()
                continue
            elif text[pos] == ']':
                pos += 1
                return result
            else:
                raise ParseError()

    def parse_object():
        nonlocal pos
        if pos >= n or text[pos] != '{':
            raise ParseError()
        pos += 1
        result = {}
        skip_ws()
        if pos < n and text[pos] == '}':
            pos += 1
            return result
        while True:
            skip_ws()
            if pos >= n or text[pos] != '"':
                raise ParseError()
            key = parse_string()
            skip_ws()
            if pos >= n or text[pos] != ':':
                raise ParseError()
            pos += 1
            val = parse_value()
            result[key] = val
            skip_ws()
            if pos >= n:
                raise ParseError()
            if text[pos] == ',':
                pos += 1
                continue
            elif text[pos] == '}':
                pos += 1
                return result
            else:
                raise ParseError()

    try:
        value = parse_value()
        skip_ws()
        if pos != n:
            return None
        return value
    except ParseError:
        return None
    except (IndexError, ValueError, RecursionError):
        return None
