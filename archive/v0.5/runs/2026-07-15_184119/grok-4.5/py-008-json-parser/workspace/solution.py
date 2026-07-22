def parse(text: str):
    if not isinstance(text, str):
        return None

    n = len(text)
    pos = 0

    def peek():
        return text[pos] if pos < n else None

    def skip_whitespace():
        nonlocal pos
        while pos < n and text[pos] in ' \t\n\r':
            pos += 1

    def parse_string():
        nonlocal pos
        if peek() != '"':
            raise ValueError('expected "')
        pos += 1
        parts = []
        while True:
            if pos >= n:
                raise ValueError('unterminated string')
            c = text[pos]
            if c == '"':
                pos += 1
                return ''.join(parts)
            if c == '\\':
                pos += 1
                if pos >= n:
                    raise ValueError('unterminated escape')
                esc = text[pos]
                pos += 1
                if esc == '"':
                    parts.append('"')
                elif esc == '\\':
                    parts.append('\\')
                elif esc == '/':
                    parts.append('/')
                elif esc == 'b':
                    parts.append('\b')
                elif esc == 'f':
                    parts.append('\f')
                elif esc == 'n':
                    parts.append('\n')
                elif esc == 'r':
                    parts.append('\r')
                elif esc == 't':
                    parts.append('\t')
                elif esc == 'u':
                    if pos + 4 > n:
                        raise ValueError('bad unicode escape')
                    hex_str = text[pos:pos + 4]
                    if not all(ch in '0123456789abcdefABCDEF' for ch in hex_str):
                        raise ValueError('bad unicode escape')
                    parts.append(chr(int(hex_str, 16)))
                    pos += 4
                else:
                    raise ValueError('invalid escape')
            elif ord(c) < 0x20:
                raise ValueError('control character in string')
            else:
                parts.append(c)
                pos += 1

    def parse_number():
        nonlocal pos
        start = pos
        if peek() == '-':
            pos += 1
        ch = peek()
        if ch is None or not ch.isdigit():
            raise ValueError('invalid number')
        if ch == '0':
            pos += 1
            if peek() is not None and peek().isdigit():
                raise ValueError('leading zero')
        else:
            while peek() is not None and peek().isdigit():
                pos += 1
        is_float = False
        if peek() == '.':
            is_float = True
            pos += 1
            if peek() is None or not peek().isdigit():
                raise ValueError('invalid fraction')
            while peek() is not None and peek().isdigit():
                pos += 1
        if peek() in ('e', 'E'):
            is_float = True
            pos += 1
            if peek() in ('+', '-'):
                pos += 1
            if peek() is None or not peek().isdigit():
                raise ValueError('invalid exponent')
            while peek() is not None and peek().isdigit():
                pos += 1
        num_str = text[start:pos]
        if is_float:
            return float(num_str)
        return int(num_str)

    def parse_literal(lit, value):
        nonlocal pos
        end = pos + len(lit)
        if text[pos:end] != lit:
            raise ValueError('invalid literal')
        pos = end
        return value

    def parse_array():
        nonlocal pos
        pos += 1  # [
        skip_whitespace()
        arr = []
        if peek() == ']':
            pos += 1
            return arr
        while True:
            arr.append(parse_value())
            skip_whitespace()
            if peek() == ',':
                pos += 1
                skip_whitespace()
                if peek() == ']':
                    raise ValueError('trailing comma')
            elif peek() == ']':
                pos += 1
                return arr
            else:
                raise ValueError('expected , or ]')

    def parse_object():
        nonlocal pos
        pos += 1  # {
        skip_whitespace()
        obj = {}
        if peek() == '}':
            pos += 1
            return obj
        while True:
            if peek() != '"':
                raise ValueError('expected string key')
            key = parse_string()
            skip_whitespace()
            if peek() != ':':
                raise ValueError('expected :')
            pos += 1
            obj[key] = parse_value()
            skip_whitespace()
            if peek() == ',':
                pos += 1
                skip_whitespace()
                if peek() == '}':
                    raise ValueError('trailing comma')
            elif peek() == '}':
                pos += 1
                return obj
            else:
                raise ValueError('expected , or }')

    def parse_value():
        skip_whitespace()
        c = peek()
        if c is None:
            raise ValueError('unexpected end')
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
        if c == '-' or c.isdigit():
            return parse_number()
        raise ValueError('unexpected character')

    try:
        result = parse_value()
        skip_whitespace()
        if pos != n:
            return None
        return result
    except (ValueError, IndexError):
        return None
