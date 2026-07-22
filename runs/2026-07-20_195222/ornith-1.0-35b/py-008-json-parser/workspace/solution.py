def parse(text: str):
    try:
        pos = [0]

        def skip_whitespace():
            while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
                pos[0] += 1

        def parse_value():
            skip_whitespace()
            if pos[0] >= len(text):
                raise ValueError("Unexpected end of input")

            ch = text[pos[0]]

            if ch == '"':
                return parse_string()
            elif ch == '{':
                return parse_object()
            elif ch == '[':
                return parse_array()
            elif ch == 't':
                return parse_true()
            elif ch == 'f':
                return parse_false()
            elif ch == 'n':
                return parse_null()
            elif ch == '-' or ('0' <= ch <= '9'):
                return parse_number()
            else:
                raise ValueError(f"Unexpected character: {ch!r}")

        def parse_string():
            assert text[pos[0]] == '"'
            pos[0] += 1
            result = []

            while pos[0] < len(text):
                ch = text[pos[0]]

                if ch == '"':
                    pos[0] += 1
                    return ''.join(result)
                elif ch == '\\':
                    pos[0] += 1
                    esc_ch = text[pos[0]]

                    if esc_ch == '"':
                        result.append('"')
                    elif esc_ch == '\\':
                        result.append('\\')
                    elif esc_ch == '/':
                        result.append('/')
                    elif esc_ch == 'b':
                        result.append('\b')
                    elif esc_ch == 'f':
                        result.append('\f')
                    elif esc_ch == 'n':
                        result.append('\n')
                    elif esc_ch == 'r':
                        result.append('\r')
                    elif esc_ch == 't':
                        result.append('\t')
                    elif esc_ch == 'u':
                        if pos[0] + 5 >= len(text):
                            raise ValueError("Incomplete unicode escape")
                        hex_str = text[pos[0]+1:pos[0]+5]
                        try:
                            code_point = int(hex_str, 16)
                        except ValueError:
                            raise ValueError("Invalid hex in unicode escape")

                        if 0xD800 <= code_point <= 0xDBFF:
                            # High surrogate - expect low surrogate pair
                            if (pos[0] + 7 >= len(text) or
                                    text[pos[0]+5] != '\\' or
                                    text[pos[0]+6] != 'u'):
                                raise ValueError("Expected low surrogate")
                            hex_str2 = text[pos[0]+7:pos[0]+11]
                            try:
                                code_point2 = int(hex_str2, 16)
                            except ValueError:
                                raise ValueError("Invalid hex in unicode escape")

                            if not (0xDC00 <= code_point2 <= 0xDFFF):
                                raise ValueError("Expected low surrogate")

                            combined = 0x10000 + (code_point - 0xD800) * 0x400 + (code_point2 - 0xDC00)
                            result.append(chr(combined))
                            pos[0] += 11
                        else:
                            result.append(chr(code_point))
                            pos[0] += 5
                    else:
                        raise ValueError(f"Invalid escape character: {esc_ch!r}")

                    pos[0] += 1
                elif ord(ch) < 0x20:
                    raise ValueError("Unescaped control character in string")
                else:
                    result.append(ch)
                    pos[0] += 1

            raise ValueError("Unterminated string")

        def parse_number():
            start = pos[0]

            if text[pos[0]] == '-':
                pos[0] += 1

            is_float = False

            if pos[0] >= len(text):
                raise ValueError("Unexpected end in number")

            if text[pos[0]] == '0':
                pos[0] += 1
                if pos[0] < len(text) and '0' <= text[pos[0]] <= '9':
                    raise ValueError("Leading zeros not allowed")
            elif '1' <= text[pos[0]] <= '9':
                while pos[0] < len(text) and '0' <= text[pos[0]] <= '9':
                    pos[0] += 1
            else:
                raise ValueError("Invalid number start")

            if pos[0] < len(text) and text[pos[0]] == '.':
                is_float = True
                pos[0] += 1
                if pos[0] >= len(text) or not ('0' <= text[pos[0]] <= '9'):
                    raise ValueError("Expected digit after decimal point")
                while pos[0] < len(text) and '0' <= text[pos[0]] <= '9':
                    pos[0] += 1

            if pos[0] < len(text) and text[pos[0]] in 'eE':
                is_float = True
                pos[0] += 1
                if pos[0] < len(text) and text[pos[0]] in '+-':
                    pos[0] += 1
                if pos[0] >= len(text) or not ('0' <= text[pos[0]] <= '9'):
                    raise ValueError("Expected digit in exponent")
                while pos[0] < len(text) and '0' <= text[pos[0]] <= '9':
                    pos[0] += 1

            num_str = text[start:pos[0]]

            if is_float:
                return float(num_str)
            else:
                return int(num_str)

        def parse_object():
            assert text[pos[0]] == '{'
            pos[0] += 1
            result = {}

            skip_whitespace()

            if pos[0] < len(text) and text[pos[0]] == '}':
                pos[0] += 1
                return result

            while True:
                skip_whitespace()

                if pos[0] >= len(text) or text[pos[0]] != '"':
                    raise ValueError("Expected string key in object")

                key = parse_string()

                skip_whitespace()

                if pos[0] >= len(text) or text[pos[0]] != ':':
                    raise ValueError("Expected colon after key")
                pos[0] += 1

                value = parse_value()

                result[key] = value

                skip_whitespace()

                if pos[0] < len(text) and text[pos[0]] == ',':
                    pos[0] += 1
                    skip_whitespace()
                    if pos[0] < len(text) and text[pos[0]] == '}':
                        raise ValueError("Trailing comma in object")
                elif pos[0] < len(text) and text[pos[0]] == '}':
                    pos[0] += 1
                    return result
                else:
                    raise ValueError("Expected ',' or '}' in object")

        def parse_array():
            assert text[pos[0]] == '['
            pos[0] += 1
            result = []

            skip_whitespace()

            if pos[0] < len(text) and text[pos[0]] == ']':
                pos[0] += 1
                return result

            while True:
                value = parse_value()
                result.append(value)

                skip_whitespace()

                if pos[0] < len(text) and text[pos[0]] == ',':
                    pos[0] += 1
                    skip_whitespace()
                    if pos[0] < len(text) and text[pos[0]] == ']':
                        raise ValueError("Trailing comma in array")
                elif pos[0] < len(text) and text[pos[0]] == ']':
                    pos[0] += 1
                    return result
                else:
                    raise ValueError("Expected ',' or ']' in array")

        def parse_true():
            if text[pos[0]:pos[0]+4] == 'true':
                pos[0] += 4
                return True
            raise ValueError("Invalid token starting with 't'")

        def parse_false():
            if text[pos[0]:pos[0]+5] == 'false':
                pos[0] += 5
                return False
            raise ValueError("Invalid token starting with 'f'")

        def parse_null():
            if text[pos[0]:pos[0]+4] == 'null':
                pos[0] += 4
                return None
            raise ValueError("Invalid token starting with 'n'")

        result = parse_value()

        skip_whitespace()
        if pos[0] < len(text):
            return None

        return result

    except Exception:
        return None
