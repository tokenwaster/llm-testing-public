def parse(text: str):
    try:
        pos = [0]

        def skip_ws():
            while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
                pos[0] += 1

        def peek():
            return text[pos[0]] if pos[0] < len(text) else None

        def advance():
            ch = text[pos[0]]
            pos[0] += 1
            return ch

        IDENT_CHARS = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_') | set('0123456789')

        def parse_string():
            assert peek() == '"'
            advance()
            chars = []
            while True:
                if pos[0] >= len(text):
                    raise ValueError("Unterminated string")
                ch = text[pos[0]]
                if ch == '"':
                    advance()
                    return ''.join(chars)
                elif ch == '\\':
                    advance()
                    if pos[0] >= len(text):
                        raise ValueError("Unterminated escape")
                    esc = text[pos[0]]
                    advance()
                    if esc == '"': chars.append('"')
                    elif esc == '\\': chars.append('\\')
                    elif esc == '/': chars.append('/')
                    elif esc == 'b': chars.append('\b')
                    elif esc == 'f': chars.append('\f')
                    elif esc == 'n': chars.append('\n')
                    elif esc == 'r': chars.append('\r')
                    elif esc == 't': chars.append('\t')
                    elif esc == 'u':
                        if pos[0] + 4 > len(text):
                            raise ValueError("Invalid unicode escape")
                        hex_str = text[pos[0]:pos[0]+4]
                        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                            raise ValueError("Invalid hex in unicode escape")
                        pos[0] += 4
                        cp = int(hex_str, 16)

                        # Handle surrogate pairs
                        if 0xD800 <= cp <= 0xDBFF:
                            if (pos[0] + 2 <= len(text) and
                                text[pos[0]:pos[0]+2] == '\\u'):
                                pos[0] += 2
                                if pos[0] + 4 > len(text):
                                    raise ValueError("Invalid unicode escape")
                                hex_str2 = text[pos[0]:pos[0]+4]
                                if not all(c in '0123456789abcdefABCDEF' for c in hex_str2):
                                    raise ValueError("Invalid hex in surrogate pair")
                                pos[0] += 4
                                low = int(hex_str2, 16)
                                if 0xDC00 <= low <= 0xDFFF:
                                    cp = 0x10000 + (cp - 0xD800) * 0x400 + (low - 0xDC00)
                                else:
                                    raise ValueError("Invalid surrogate pair")
                            else:
                                raise ValueError("Expected low surrogate in unicode escape")

                        chars.append(chr(cp))
                    else:
                        raise ValueError(f"Invalid escape character: {esc}")
                elif ord(ch) < 0x20:
                    raise ValueError("Unescaped control character in string")
                else:
                    chars.append(ch)
                    advance()

        def parse_number():
            start = pos[0]

            if peek() == '-':
                advance()

            ch = peek()
            if not ('0' <= ch <= '9'):
                raise ValueError("Invalid number")

            if ch == '0':
                advance()
                # No leading zeros allowed (except "0" itself or "0.xxx"/"0eX")
                if pos[0] < len(text) and text[pos[0]] in '0123456789':
                    raise ValueError("Leading zero not allowed")
            else:
                while pos[0] < len(text) and '0' <= text[pos[0]] <= '9':
                    advance()

            is_float = False

            # Fractional part
            if pos[0] < len(text) and text[pos[0]] == '.':
                is_float = True
                advance()
                ch = peek()
                if not ('0' <= ch <= '9'):
                    raise ValueError("Digit expected after decimal point")
                while pos[0] < len(text) and '0' <= text[pos[0]] <= '9':
                    advance()

            # Exponent part
            if pos[0] < len(text) and text[pos[0]] in 'eE':
                is_float = True
                advance()
                if pos[0] < len(text) and text[pos[0]] in '+-':
                    advance()
                ch = peek()
                if not ('0' <= ch <= '9'):
                    raise ValueError("Digit expected after exponent sign")
                while pos[0] < len(text) and '0' <= text[pos[0]] <= '9':
                    advance()

            num_str = text[start:pos[0]]
            return float(num_str) if is_float else int(num_str)

        def parse_value():
            skip_ws()
            ch = peek()

            if ch == '"':
                return parse_string()
            elif ch == '{':
                return parse_object()
            elif ch == '[':
                return parse_array()
            elif ch == 't':
                if (text[pos[0]:pos[0]+4] == 'true' and
                    (pos[0]+4 >= len(text) or text[pos[0]+4] not in IDENT_CHARS)):
                    pos[0] += 4
                    return True
                raise ValueError("Invalid token")
            elif ch == 'f':
                if (text[pos[0]:pos[0]+5] == 'false' and
                    (pos[0]+5 >= len(text) or text[pos[0]+5] not in IDENT_CHARS)):
                    pos[0] += 5
                    return False
                raise ValueError("Invalid token")
            elif ch == 'n':
                if (text[pos[0]:pos[0]+4] == 'null' and
                    (pos[0]+4 >= len(text) or text[pos[0]+4] not in IDENT_CHARS)):
                    pos[0] += 4
                    return None
                raise ValueError("Invalid token")
            elif ch == '-' or ('0' <= ch <= '9'):
                return parse_number()
            else:
                raise ValueError(f"Unexpected character: {ch!r}")

        def parse_object():
            assert peek() == '{'
            advance()

            obj = {}
            skip_ws()

            if peek() == '}':
                advance()
                return obj

            while True:
                skip_ws()
                if peek() != '"':
                    raise ValueError("Expected string key in object")
                key = parse_string()

                skip_ws()
                if peek() != ':':
                    raise ValueError("Expected ':' after key")
                advance()

                skip_ws()
                value = parse_value()
                obj[key] = value

                skip_ws()
                ch = peek()
                if ch == ',':
                    advance()
                    skip_ws()
                    if peek() in ('}', ']'):
                        raise ValueError("Trailing comma")
                elif ch == '}':
                    advance()
                    return obj
                else:
                    raise ValueError(f"Expected ',' or '}}' in object, got {ch!r}")

        def parse_array():
            assert peek() == '['
            advance()

            arr = []
            skip_ws()

            if peek() == ']':
                advance()
                return arr

            while True:
                value = parse_value()
                arr.append(value)

                skip_ws()
                ch = peek()
                if ch == ',':
                    advance()
                    skip_ws()
                    if peek() == ']':
                        raise ValueError("Trailing comma")
                elif ch == ']':
                    advance()
                    return arr
                else:
                    raise ValueError(f"Expected ',' or ']' in array, got {ch!r}")

        result = parse_value()
        skip_ws()

        if pos[0] < len(text):
            return None

        return result

    except Exception:
        return None
