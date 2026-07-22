def parse(text: str):
    pos = [0]  # mutable position tracker

    def skip_whitespace():
        while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
            pos[0] += 1

    def peek():
        if pos[0] >= len(text):
            return None
        return text[pos[0]]

    def advance():
        ch = text[pos[0]]
        pos[0] += 1
        return ch

    def parse_value():
        skip_whitespace()
        if pos[0] >= len(text):
            return None

        ch = peek()

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
        else:
            return parse_number()

    def parse_string():
        if peek() != '"':
            return None
        pos[0] += 1  # skip opening quote
        result = []
        while True:
            if pos[0] >= len(text):
                return None  # unterminated string
            ch = advance()
            if ch == '"':
                break
            elif ch == '\\':
                if pos[0] >= len(text):
                    return None
                esc = advance()
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
                    if pos[0] + 4 > len(text):
                        return None
                    hex_str = text[pos[0]:pos[0]+4]
                    pos[0] += 4
                    try:
                        code_point = int(hex_str, 16)
                    except ValueError:
                        return None
                    result.append(chr(code_point))
                else:
                    return None
            elif ch == '\n' or ch == '\r':
                return None  # unescaped newline in string
            else:
                result.append(ch)
        return ''.join(result)

    def parse_number():
        start = pos[0]

        # Optional minus sign
        if peek() == '-':
            advance()

        # Must have at least one digit for integer part
        if peek() is None or not peek().isdigit():
            return None

        while peek() and peek().isdigit():
            advance()

        # Reject leading zeros (e.g., 007, 0123) but allow single '0'
        if start + 1 < pos[0] and text[start+1] == '0':
            return None

        is_float = False

        # Decimal part
        if peek() == '.':
            is_float = True
            advance()
            if not peek().isdigit():
                return None
            while peek() and peek().isdigit():
                advance()

        # Exponent part
        if peek() in ('e', 'E'):
            is_float = True
            advance()
            if peek() in ('+', '-'):
                advance()
            if not peek().isdigit():
                return None
            while peek() and peek().isdigit():
                advance()

        num_str = text[start:pos[0]]

        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            return None

    def parse_object():
        pos[0] += 1  # skip '{'
        result = {}
        skip_whitespace()

        if peek() == '}':
            advance()
            return result

        while True:
            key = parse_string()
            if key is None:
                return None

            skip_whitespace()
            if peek() != ':':
                return None
            advance()  # skip ':'

            value = parse_value()
            if value is None:
                return None

            result[key] = value

            skip_whitespace()
            ch = peek()
            if ch == '}':
                advance()
                return result
            elif ch == ',':
                advance()
                continue
            else:
                return None  # missing comma or closing brace

    def parse_array():
        pos[0] += 1  # skip '['
        result = []
        skip_whitespace()

        if peek() == ']':
            advance()
            return result

        while True:
            value = parse_value()
            if value is None:
                return None

            result.append(value)

            skip_whitespace()
            ch = peek()
            if ch == ']':
                advance()
                return result
            elif ch == ',':
                advance()
                continue
            else:
                return None  # missing comma or closing bracket

    def parse_true():
        pos[0] += 1  # skip 't'
        if text[pos[0]:pos[0]+4] != 'rue':
            return None
        pos[0] += 3
        return True

    def parse_false():
        pos[0] += 1  # skip 'f'
        if text[pos[0]:pos[0]+5] != 'alse':
            return None
        pos[0] += 4
        return False

    def parse_null():
        pos[0] += 1  # skip 'n'
        if text[pos[0]:pos[0]+3] != 'ull':
            return None
        pos[0] += 2
        return None

    result = parse_value()

    # Check for trailing garbage
    skip_whitespace()
    if pos[0] < len(text):
        return None

    return result
