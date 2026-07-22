def parse(text: str):
    pos = 0

    def peek():
        return pos < len(text)

    def current():
        return text[pos] if peek() else None

    def skip_whitespace():
        nonlocal pos
        while pos < len(text) and text[pos] in ' \t\n\r':
            pos += 1

    def parse_value():
        skip_whitespace()
        if not peek():
            raise ValueError("Unexpected end of input")
        c = current()
        if c == '"':
            return parse_string()
        elif c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == 't':
            return parse_true()
        elif c == 'f':
            return parse_false()
        elif c == 'n':
            return parse_null()
        elif c == '-' or c.isdigit():
            return parse_number()
        else:
            raise ValueError(f"Unexpected character: {c!r}")

    def parse_true():
        nonlocal pos
        if text[pos:pos+4] == 'true':
            pos += 4
            return True
        raise ValueError("Invalid literal")

    def parse_false():
        nonlocal pos
        if text[pos:pos+5] == 'false':
            pos += 5
            return False
        raise ValueError("Invalid literal")

    def parse_null():
        nonlocal pos
        if text[pos:pos+4] == 'null':
            pos += 4
            return None
        raise ValueError("Invalid literal")

    def parse_string():
        nonlocal pos
        assert text[pos] == '"'
        pos += 1
        result = []
        while pos < len(text):
            c = text[pos]
            if c == '"':
                pos += 1
                return ''.join(result)
            elif c == '\\':
                pos += 1
                if pos >= len(text):
                    raise ValueError("Unexpected end in escape")
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
                    pos += 1
                    if pos + 4 > len(text):
                        raise ValueError("Incomplete unicode escape")
                    hex_str = text[pos:pos+4]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ValueError("Invalid unicode escape")
                    code_point = int(hex_str, 16)
                    # Handle surrogate pairs
                    if 0xD800 <= code_point <= 0xDBFF:
                        pos += 4
                        if pos + 2 > len(text) or text[pos:pos+2] != '\\u':
                            raise ValueError("Missing low surrogate")
                        pos += 2
                        if pos + 4 > len(text):
                            raise ValueError("Incomplete surrogate escape")
                        hex_str2 = text[pos:pos+4]
                        if not all(c in '0123456789abcdefABCDEF' for c in hex_str2):
                            raise ValueError("Invalid surrogate escape")
                        low = int(hex_str2, 16)
                        if not (0xDC00 <= low <= 0xDFFF):
                            raise ValueError("Invalid low surrogate")
                        full = 0x10000 + (code_point - 0xD800) * 0x400 + (low - 0xDC00)
                        result.append(chr(full))
                        pos += 4
                        continue
                    elif 0xDC00 <= code_point <= 0xDFFF:
                        raise ValueError("Unexpected low surrogate")
                    result.append(chr(code_point))
                    pos += 4
                    continue
                else:
                    raise ValueError(f"Invalid escape: \\{esc}")
                pos += 1
            elif ord(c) < 0x20:
                raise ValueError("Control character in string")
            else:
                result.append(c)
                pos += 1
        raise ValueError("Unterminated string")

    def parse_number():
        nonlocal pos
        start = pos
        is_float = False

        if pos < len(text) and text[pos] == '-':
            pos += 1

        if pos >= len(text) or not text[pos].isdigit():
            raise ValueError("Invalid number")

        if text[pos] == '0':
            pos += 1
            if pos < len(text) and text[pos].isdigit():
                raise ValueError("Leading zero")
        else:
            while pos < len(text) and text[pos].isdigit():
                pos += 1

        if pos < len(text) and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                raise ValueError("Expected digit after decimal point")
            while pos < len(text) and text[pos].isdigit():
                pos += 1

        if pos < len(text) and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < len(text) and text[pos] in '+-':
                pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                raise ValueError("Expected digit in exponent")
            while pos < len(text) and text[pos].isdigit():
                pos += 1

        num_str = text[start:pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)

    def parse_object():
        nonlocal pos
        assert text[pos] == '{'
        pos += 1
        result = {}
        skip_whitespace()
        if pos < len(text) and text[pos] == '}':
            pos += 1
            return result
        first = True
        while True:
            if not first:
                skip_whitespace()
                if pos >= len(text) or text[pos] != ',':
                    raise ValueError("Expected ',' or '}'")
                pos += 1
            skip_whitespace()
            if pos >= len(text):
                raise ValueError("Unterminated object")
            if text[pos] != '"':
                raise ValueError("Expected string key")
            key = parse_string()
            skip_whitespace()
            if pos >= len(text) or text[pos] != ':':
                raise ValueError("Expected ':'")
            pos += 1
            value = parse_value()
            result[key] = value
            first = False
            skip_whitespace()
            if pos < len(text) and text[pos] == '}':
                pos += 1
                return result
            if pos >= len(text):
                raise ValueError("Unterminated object")

    def parse_array():
        nonlocal pos
        assert text[pos] == '['
        pos += 1
        result = []
        skip_whitespace()
        if pos < len(text) and text[pos] == ']':
            pos += 1
            return result
        first = True
        while True:
            if not first:
                skip_whitespace()
                if pos >= len(text) or text[pos] != ',':
                    raise ValueError("Expected ',' or ']'")
                pos += 1
            value = parse_value()
            result.append(value)
            first = False
            skip_whitespace()
            if pos < len(text) and text[pos] == ']':
                pos += 1
                return result
            if pos >= len(text):
                raise ValueError("Unterminated array")

    try:
        result = parse_value()
        skip_whitespace()
        if pos != len(text):
            return None
        return result
    except Exception:
        return None
