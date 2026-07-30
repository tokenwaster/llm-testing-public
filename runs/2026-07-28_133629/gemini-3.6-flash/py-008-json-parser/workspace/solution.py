class JSONParseError(Exception):
    pass


def parse(text: str):
    if not isinstance(text, str):
        return None

    i = 0
    n = len(text)

    def skip_ws():
        nonlocal i
        while i < n and text[i] in ' \t\n\r':
            i += 1

    def parse_value():
        nonlocal i
        skip_ws()
        if i >= n:
            raise JSONParseError("Unexpected EOF")
        ch = text[i]
        if ch == '"':
            return parse_string()
        elif ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch in '0123456789-':
            return parse_number()
        elif ch == 't':
            return parse_true()
        elif ch == 'f':
            return parse_false()
        elif ch == 'n':
            return parse_null()
        else:
            raise JSONParseError(f"Unexpected character {ch}")

    def parse_true():
        nonlocal i
        if text[i:i+4] == "true":
            i += 4
            return True
        raise JSONParseError("Expected 'true'")

    def parse_false():
        nonlocal i
        if text[i:i+5] == "false":
            i += 5
            return False
        raise JSONParseError("Expected 'false'")

    def parse_null():
        nonlocal i
        if text[i:i+4] == "null":
            i += 4
            return None
        raise JSONParseError("Expected 'null'")

    def parse_string():
        nonlocal i
        if i >= n or text[i] != '"':
            raise JSONParseError("Expected '\"'")
        i += 1
        res = []
        while i < n:
            ch = text[i]
            if ch == '"':
                i += 1
                return "".join(res)
            elif ch == '\\':
                i += 1
                if i >= n:
                    raise JSONParseError("Unterminated escape sequence")
                esc = text[i]
                if esc == '"':
                    res.append('"')
                    i += 1
                elif esc == '\\':
                    res.append('\\')
                    i += 1
                elif esc == '/':
                    res.append('/')
                    i += 1
                elif esc == 'b':
                    res.append('\b')
                    i += 1
                elif esc == 'f':
                    res.append('\f')
                    i += 1
                elif esc == 'n':
                    res.append('\n')
                    i += 1
                elif esc == 'r':
                    res.append('\r')
                    i += 1
                elif esc == 't':
                    res.append('\t')
                    i += 1
                elif esc == 'u':
                    i += 1
                    if i + 4 > n:
                        raise JSONParseError("Invalid unicode escape")
                    hex_str = text[i:i+4]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise JSONParseError("Invalid hex digits in unicode escape")
                    i += 4
                    val = int(hex_str, 16)
                    # Check for UTF-16 surrogate pair
                    if 0xD800 <= val <= 0xDBFF:
                        if i + 6 <= n and text[i:i+2] == '\\u':
                            hex_str2 = text[i+2:i+6]
                            if all(c in '0123456789abcdefABCDEF' for c in hex_str2):
                                val2 = int(hex_str2, 16)
                                if 0xDC00 <= val2 <= 0xDFFF:
                                    code_point = (val - 0xD800) * 0x400 + (val2 - 0xDC00) + 0x10000
                                    res.append(chr(code_point))
                                    i += 6
                                    continue
                    res.append(chr(val))
                else:
                    raise JSONParseError(f"Invalid escape sequence \\{esc}")
            else:
                code = ord(ch)
                if code < 0x20:
                    raise JSONParseError("Control character in string")
                res.append(ch)
                i += 1
        raise JSONParseError("Unterminated string")

    def parse_number():
        nonlocal i
        start_i = i

        if i < n and text[i] == '-':
            i += 1
            if i >= n:
                raise JSONParseError("Expected digit after '-'")

        if i >= n:
            raise JSONParseError("Expected digit in number")

        if text[i] == '0':
            i += 1
            if i < n and text[i].isdigit():
                raise JSONParseError("Leading zero in number")
        elif '1' <= text[i] <= '9':
            i += 1
            while i < n and text[i].isdigit():
                i += 1
        else:
            raise JSONParseError("Invalid number format")

        is_float = False

        if i < n and text[i] == '.':
            is_float = True
            i += 1
            if i >= n or not text[i].isdigit():
                raise JSONParseError("Expected digit after '.'")
            while i < n and text[i].isdigit():
                i += 1

        if i < n and text[i] in 'eE':
            is_float = True
            i += 1
            if i < n and text[i] in '+-':
                i += 1
            if i >= n or not text[i].isdigit():
                raise JSONParseError("Expected digit in exponent")
            while i < n and text[i].isdigit():
                i += 1

        num_str = text[start_i:i]
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            raise JSONParseError(f"Invalid number {num_str}")

    def parse_array():
        nonlocal i
        if i >= n or text[i] != '[':
            raise JSONParseError("Expected '['")
        i += 1
        skip_ws()
        res = []
        if i < n and text[i] == ']':
            i += 1
            return res

        while True:
            val = parse_value()
            res.append(val)
            skip_ws()
            if i >= n:
                raise JSONParseError("Unterminated array")
            if text[i] == ']':
                i += 1
                return res
            elif text[i] == ',':
                i += 1
                skip_ws()
                if i < n and text[i] == ']':
                    raise JSONParseError("Trailing comma in array")
            else:
                raise JSONParseError("Expected ',' or ']' in array")

    def parse_object():
        nonlocal i
        if i >= n or text[i] != '{':
            raise JSONParseError("Expected '{'")
        i += 1
        skip_ws()
        res = {}
        if i < n and text[i] == '}':
            i += 1
            return res

        while True:
            skip_ws()
            if i >= n or text[i] != '"':
                raise JSONParseError("Object key must be a string")
            key = parse_string()
            skip_ws()
            if i >= n or text[i] != ':':
                raise JSONParseError("Expected ':' after object key")
            i += 1
            val = parse_value()
            res[key] = val
            skip_ws()
            if i >= n:
                raise JSONParseError("Unterminated object")
            if text[i] == '}':
                i += 1
                return res
            elif text[i] == ',':
                i += 1
                skip_ws()
                if i < n and text[i] == '}':
                    raise JSONParseError("Trailing comma in object")
            else:
                raise JSONParseError("Expected ',' or '}' in object")

    try:
        skip_ws()
        if i >= n:
            return None
        val = parse_value()
        skip_ws()
        if i < n:
            return None
        return val
    except JSONParseError:
        return None
