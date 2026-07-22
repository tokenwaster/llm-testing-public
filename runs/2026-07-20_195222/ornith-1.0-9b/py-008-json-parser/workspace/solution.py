def parse(text: str):
    pos = [0]  # mutable position tracker

    def skip_ws():
        while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
            pos[0] += 1

    def err(msg=""):
        return None

    def parse_value():
        skip_ws()
        if pos[0] >= len(text):
            return None

        c = text[pos[0]]

        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        elif c == 't':
            return parse_true()
        elif c == 'f':
            return parse_false()
        elif c == 'n':
            return parse_null()
        elif c == '-' or (c.isdigit()):
            return parse_number()
        else:
            return None

    def parse_object():
        pos[0] += 1  # skip '{'
        result = {}
        skip_ws()

        if pos[0] < len(text) and text[pos[0]] == '}':
            pos[0] += 1
            return result

        while True:
            skip_ws()

            if pos[0] >= len(text) or text[pos[0]] != '"':
                return None

            key = parse_string()
            if key is None:
                return None

            skip_ws()

            if pos[0] >= len(text) or text[pos[0]] != ':':
                return None
            pos[0] += 1

            skip_ws()

            value = parse_value()
            if value is None:
                return None

            result[key] = value

            skip_ws()

            if pos[0] >= len(text):
                return None

            c = text[pos[0]]
            if c == '}':
                pos[0] += 1
                return result
            elif c == ',':
                pos[0] += 1
                continue
            else:
                return None

    def parse_array():
        pos[0] += 1  # skip '['
        result = []
        skip_ws()

        if pos[0] < len(text) and text[pos[0]] == ']':
            pos[0] += 1
            return result

        while True:
            value = parse_value()
            if value is None:
                return None

            result.append(value)

            skip_ws()

            if pos[0] >= len(text):
                return None

            c = text[pos[0]]
            if c == ']':
                pos[0] += 1
                return result
            elif c == ',':
                pos[0] += 1
                continue
            else:
                return None

    def parse_string():
        pos[0] += 1  # skip opening '"'
        chars = []

        while pos[0] < len(text):
            c = text[pos[0]]

            if c == '"':
                pos[0] += 1
                return ''.join(chars)
            elif c == '\\':
                pos[0] += 1
                if pos[0] >= len(text):
                    return None

                esc = text[pos[0]]
                pos[0] += 1

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
                    if pos[0] + 4 > len(text):
                        return None
                    hex_str = text[pos[0]:pos[0]+4]
                    pos[0] += 4
                    try:
                        code_point = int(hex_str, 16)
                        chars.append(chr(code_point))
                    except ValueError:
                        return None
                else:
                    return None
            elif c in '\n\r':
                # Unescaped newline is invalid in JSON strings
                return None
            else:
                chars.append(c)

        return None  # Unterminated string

    def parse_number():
        start = pos[0]

        # Optional minus sign
        if text[pos[0]] == '-':
            pos[0] += 1

        # Integer part — must have at least one digit
        if pos[0] >= len(text) or not text[pos[0]].isdigit():
            return None

        int_start = pos[0]
        while pos[0] < len(text) and text[pos[0]].isdigit():
            pos[0] += 1

        # Reject leading zeros in integer part (e.g. "01", "007") but allow "0" alone
        if text[int_start] == '0' and pos[0] > int_start + 1:
            return None

        is_float = False

        # Fractional part
        if pos[0] < len(text) and text[pos[0]] == '.':
            is_float = True
            pos[0] += 1

            if pos[0] >= len(text) or not text[pos[0]].isdigit():
                return None

            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1

        # Exponent part
        has_exp = False
        if pos[0] < len(text) and text[pos[0]] in 'eE':
            is_float = True
            has_exp = True
            pos[0] += 1

            if pos[0] < len(text) and text[pos[0]] in '+-':
                pos[0] += 1

            if pos[0] >= len(text) or not text[pos[0]].isdigit():
                return None

            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1

        num_str = text[start:pos[0]]

        try:
            if is_float:
                val = float(num_str)
                if val == float('inf') or val == float('-inf'):
                    return None
                return val
            else:
                return int(num_str)
        except (ValueError, OverflowError):
            return None

    def parse_true():
        if pos[0] + 4 > len(text):
            return None
        if text[pos[0]:pos[0]+4] != 'true':
            return None

        next_c = text[pos[0]+4] if pos[0]+4 < len(text) else ''
        if next_c.isalnum() or next_c == '_':
            return None

        pos[0] += 4
        return True

    def parse_false():
        if pos[0] + 5 > len(text):
            return None
        if text[pos[0]:pos[0]+5] != 'false':
            return None

        next_c = text[pos[0]+5] if pos[0]+5 < len(text) else ''
        if next_c.isalnum() or next_c == '_':
            return None

        pos[0] += 5
        return False

    def parse_null():
        if pos[0] + 4 > len(text):
            return None
        if text[pos[0]:pos[0]+4] != 'null':
            return None

        next_c = text[pos[0]+4] if pos[0]+4 < len(text) else ''
        if next_c.isalnum() or next_c == '_':
            return None

        pos[0] += 4
        return None

    # Parse the value and check for trailing content
    result = parse_value()

    skip_ws()

    if pos[0] < len(text):
        return None  # Trailing garbage after document

    return result
