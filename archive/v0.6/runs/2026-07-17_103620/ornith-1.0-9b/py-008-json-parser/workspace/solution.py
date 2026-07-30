def parse(text: str):
    pos = [0]  # mutable position tracker

    def skip_whitespace():
        while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
            pos[0] += 1

    def error(msg=""):
        return None

    def parse_value():
        skip_whitespace()
        if pos[0] >= len(text):
            return None

        c = text[pos[0]]

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
        else:
            # Try to parse a number (must start with digit or '-')
            if text[pos[0]] not in '0123456789-':
                return None
            return parse_number()

    def parse_string():
        pos[0] += 1  # skip opening quote
        result = []
        while pos[0] < len(text):
            c = text[pos[0]]
            if c == '"':
                pos[0] += 1  # skip closing quote
                return ''.join(result)
            elif c == '\\':
                pos[0] += 1
                esc = text[pos[0]]
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
                    pos[0] += 1
                    hex_str = text[pos:pos + 4]
                    if len(hex_str) < 4 or not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        return None
                    code_point = int(hex_str, 16)
                    # Handle surrogate pairs
                    if 0xD800 <= code_point <= 0xDBFF:
                        pos[0] += 1
                        esc2 = text[pos[0]]
                        if esc2 != '\\':
                            return None
                        pos[0] += 1
                        if text[pos[0]] != 'u':
                            return None
                        pos[0] += 1
                        hex_str2 = text[pos:pos + 4]
                        if len(hex_str2) < 4 or not all(c in '0123456789abcdefABCDEF' for c in hex_str2):
                            return None
                        code_point2 = int(hex_str2, 16)
                        if not (0xDC00 <= code_point2 <= 0xDFFF):
                            return None
                        code_point = 0x10000 + (code_point - 0xD800) * 0x400 + (code_point2 - 0xDC00)
                    result.append(chr(code_point))
                else:
                    return None
            elif c == '\n' or c == '\r':
                # Unescaped newline in string is invalid JSON
                return None
            else:
                result.append(c)
        return None  # unterminated string

    def parse_object():
        pos[0] += 1  # skip '{'
        skip_whitespace()
        if pos[0] < len(text) and text[pos[0]] == '}':
            pos[0] += 1
            return {}

        obj = {}
        while True:
            val = parse_string()
            if val is None:
                return None

            skip_whitespace()
            if pos[0] >= len(text) or text[pos[0]] != ':':
                return None
            pos[0] += 1  # skip ':'

            value = parse_value()
            if value is None:
                return None

            obj[val] = value

            skip_whitespace()
            c = text[pos[0]] if pos[0] < len(text) else ''
            if c == ',':
                pos[0] += 1
                # Check for trailing comma
                skip_whitespace()
                if pos[0] < len(text) and text[pos[0]] == '}':
                    return None  # trailing comma
                continue
            elif c == '}':
                pos[0] += 1
                return obj
            else:
                return None

    def parse_array():
        pos[0] += 1  # skip '['
        skip_whitespace()
        if pos[0] < len(text) and text[pos[0]] == ']':
            pos[0] += 1
            return []

        arr = []
        while True:
            value = parse_value()
            if value is None:
                return None

            arr.append(value)

            skip_whitespace()
            c = text[pos[0]] if pos[0] < len(text) else ''
            if c == ',':
                pos[0] += 1
                # Check for trailing comma
                skip_whitespace()
                if pos[0] < len(text) and text[pos[0]] == ']':
                    return None  # trailing comma
                continue
            elif c == ']':
                pos[0] += 1
                return arr
            else:
                return None

    def parse_number():
        start = pos[0]

        # Optional minus sign
        if text[pos[0]] == '-':
            pos[0] += 1

        # Integer part - must have at least one digit
        if pos[0] >= len(text) or not text[pos[0]].isdigit():
            return None

        int_start = pos[0]
        while pos[0] < len(text) and text[pos[0]].isdigit():
            pos[0] += 1

        # Check for leading zeros in integer part (except "0" itself or "-0")
        if pos[0] > int_start + 1:
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
        if pos[0] < len(text) and text[pos[0]] in 'eE':
            is_float = True
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
            else:
                val = int(num_str)
        except ValueError:
            return None

        # Reject NaN and Infinity
        if isinstance(val, float) and (val != val or val == float('inf') or val == float('-inf')):
            return None

        return val

    def parse_true():
        pos[0] += 1  # skip 't'
        if text[pos:pos + 4] != 'true':
            return None
        pos[0] += 3
        return True

    def parse_false():
        pos[0] += 1  # skip 'f'
        if text[pos:pos + 5] != 'false':
            return None
        pos[0] += 4
        return False

    def parse_null():
        pos[0] += 1  # skip 'n'
        if text[pos:pos + 4] != 'null':
            return None
        pos[0] += 3
        return None

    result = parse_value()

    # Check for trailing garbage
    skip_whitespace()
    if pos[0] < len(text):
        return None

    return result
