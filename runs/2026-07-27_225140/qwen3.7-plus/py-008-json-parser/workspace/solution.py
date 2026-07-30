def parse(text: str):
    if not isinstance(text, str):
        return None

    pos = 0
    length = len(text)

    def skip_ws():
        nonlocal pos
        while pos < length and text[pos] in ' \t\n\r':
            pos += 1

    def parse_value():
        skip_ws()
        if pos >= length:
            raise ValueError("unexpected end")
        c = text[pos]
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
        elif c == '-' or ('0' <= c <= '9'):
            return parse_number()
        else:
            raise ValueError(f"unexpected char {c!r}")

    def parse_string():
        nonlocal pos
        pos += 1  # skip opening "
        result = []
        while pos < length:
            c = text[pos]
            if c == '"':
                pos += 1
                return ''.join(result)
            elif c == '\\':
                pos += 1
                if pos >= length:
                    raise ValueError("unterminated escape")
                esc = text[pos]
                pos += 1
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
                    if pos + 4 > length:
                        raise ValueError("incomplete unicode escape")
                    hex_str = text[pos:pos + 4]
                    for ch in hex_str:
                        if ch not in '0123456789abcdefABCDEF':
                            raise ValueError("invalid unicode escape")
                    code = int(hex_str, 16)
                    pos += 4
                    if 0xD800 <= code <= 0xDBFF:
                        if (pos + 6 <= length and text[pos] == '\\'
                                and text[pos + 1] == 'u'):
                            pos += 2
                            hex_str2 = text[pos:pos + 4]
                            for ch in hex_str2:
                                if ch not in '0123456789abcdefABCDEF':
                                    raise ValueError("invalid low surrogate")
                            code2 = int(hex_str2, 16)
                            pos += 4
                            if 0xDC00 <= code2 <= 0xDFFF:
                                combined = (0x10000
                                            + (code - 0xD800) * 0x400
                                            + (code2 - 0xDC00))
                                result.append(chr(combined))
                            else:
                                raise ValueError("invalid low surrogate")
                        else:
                            raise ValueError("missing low surrogate")
                    elif 0xDC00 <= code <= 0xDFFF:
                        raise ValueError("unexpected low surrogate")
                    else:
                        result.append(chr(code))
                else:
                    raise ValueError(f"invalid escape \\{esc}")
            elif ord(c) < 0x20:
                raise ValueError("control character in string")
            else:
                result.append(c)
                pos += 1
        raise ValueError("unterminated string")

    def parse_number():
        nonlocal pos
        start = pos
        is_float = False

        if pos < length and text[pos] == '-':
            pos += 1

        if pos >= length:
            raise ValueError("unexpected end in number")

        if text[pos] == '0':
            pos += 1
            if pos < length and '0' <= text[pos] <= '9':
                raise ValueError("leading zeros")
        elif '1' <= text[pos] <= '9':
            pos += 1
            while pos < length and '0' <= text[pos] <= '9':
                pos += 1
        else:
            raise ValueError("expected digit")

        if pos < length and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= length or not ('0' <= text[pos] <= '9'):
                raise ValueError("expected digit after decimal point")
            while pos < length and '0' <= text[pos] <= '9':
                pos += 1

        if pos < length and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < length and text[pos] in '+-':
                pos += 1
            if pos >= length or not ('0' <= text[pos] <= '9'):
                raise ValueError("expected digit in exponent")
            while pos < length and '0' <= text[pos] <= '9':
                pos += 1

        num_str = text[start:pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)

    def parse_object():
        nonlocal pos
        pos += 1  # skip {
        result = {}
        skip_ws()
        if pos < length and text[pos] == '}':
            pos += 1
            return result
        while True:
            skip_ws()
            if pos >= length or text[pos] != '"':
                raise ValueError("expected string key")
            key = parse_string()
            skip_ws()
            if pos >= length or text[pos] != ':':
                raise ValueError("expected colon")
            pos += 1
            value = parse_value()
            result[key] = value
            skip_ws()
            if pos >= length:
                raise ValueError("unterminated object")
            if text[pos] == '}':
                pos += 1
                return result
            if text[pos] == ',':
                pos += 1
                skip_ws()
                if pos < length and text[pos] == '}':
                    raise ValueError("trailing comma in object")
                continue
            raise ValueError("expected comma or closing brace")

    def parse_array():
        nonlocal pos
        pos += 1  # skip [
        result = []
        skip_ws()
        if pos < length and text[pos] == ']':
            pos += 1
            return result
        while True:
            value = parse_value()
            result.append(value)
            skip_ws()
            if pos >= length:
                raise ValueError("unterminated array")
            if text[pos] == ']':
                pos += 1
                return result
            if text[pos] == ',':
                pos += 1
                skip_ws()
                if pos < length and text[pos] == ']':
                    raise ValueError("trailing comma in array")
                continue
            raise ValueError("expected comma or closing bracket")

    def parse_true():
        nonlocal pos
        if text[pos:pos + 4] == 'true':
            pos += 4
            return True
        raise ValueError("invalid token")

    def parse_false():
        nonlocal pos
        if text[pos:pos + 5] == 'false':
            pos += 5
            return False
        raise ValueError("invalid token")

    def parse_null():
        nonlocal pos
        if text[pos:pos + 4] == 'null':
            pos += 4
            return None
        raise ValueError("invalid token")

    try:
        result = parse_value()
        skip_ws()
        if pos != length:
            return None
        return result
    except (ValueError, IndexError, KeyError):
        return None
