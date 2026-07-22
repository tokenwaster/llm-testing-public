def parse(text: str):
    if not text:
        return None
    index = [0]

    def error():
        index[0] = len(text)
        return None

    def whitespace():
        i = index[0]
        while i < len(text) and text[i].isspace():
            i += 1
        index[0] = i

    def parse_value():
        whitespace()
        if index[0] >= len(text):
            return error()
        c = text[index[0]]
        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        elif c in 'tfn':
            return parse_literal()
        elif c.isdigit() or c == '-':
            return parse_number()
        else:
            return error()

    def parse_object():
        if index[0] >= len(text) or text[index[0]] != '{':
            return error()
        index[0] += 1
        obj = {}
        while True:
            whitespace()
            if text[index[0]] == '}':
                index[0] += 1
                return obj
            key = parse_string()
            if key is None:
                return error()
            whitespace()
            if index[0] >= len(text) or text[index[0]] != ':':
                return error()
            index[0] += 1  # skip colon
            value = parse_value()
            if value is None:
                return error()
            obj[key] = value
            whitespace()
            c = text[index[0]] if index[0] < len(text) else ''
            if c == ',':
                index[0] += 1
            elif c == '}':
                continue
            else:
                return error()

    def parse_array():
        if index[0] >= len(text) or text[index[0]] != '[':
            return error()
        index[0] += 1
        arr = []
        while True:
            whitespace()
            if text[index[0]] == ']':
                index[0] += 1
                return arr
            value = parse_value()
            if value is None:
                return error()
            arr.append(value)
            whitespace()
            c = text[index[0]] if index[0] < len(text) else ''
            if c == ',':
                index[0] += 1
            elif c == ']':
                continue
            else:
                return error()

    def parse_string():
        i = index[0]
        if i >= len(text) or text[i] != '"':
            return error()
        i += 1
        s = []
        while i < len(text):
            c = text[i]
            if c == '"':
                index[0] = i + 1
                return ''.join(s)
            elif c == '\\':
                i += 1
                if i >= len(text):
                    return error()
                esc_char = text[i]
                if esc_char == '"':
                    s.append('"')
                elif esc_char == '\\':
                    s.append('\\')
                elif esc_char == '/':
                    s.append('/')
                elif esc_char == 'b':
                    s.append('\b')
                elif esc_char == 'f':
                    s.append('\f')
                elif esc_char == 'n':
                    s.append('\n')
                elif esc_char == 'r':
                    s.append('\r')
                elif esc_char == 't':
                    s.append('\t')
                elif esc_char == 'u':
                    if i + 4 >= len(text):
                        return error()
                    code = text[i+1:i+5]
                    try:
                        char_code = int(code, 16)
                        s.append(chr(char_code))
                    except ValueError:
                        return error()
                    i += 4
                else:
                    return error()
                i += 1
            else:
                s.append(c)
                i += 1
        return error()

    def parse_literal():
        if index[0] >= len(text):
            return error()
        c = text[index[0]]
        if c == 't':
            if text.startswith('true', index[0]):
                index[0] += 4
                return True
        elif c == 'f':
            if text.startswith('false', index[0]):
                index[0] += 5
                return False
        elif c == 'n':
            if text.startswith('null', index[0]):
                index[0] += 4
                return None
        return error()

    def parse_number():
        start = index[0]
        has_sign = False
        if text[index[0]] == '-':
            has_sign = True
            index[0] += 1
            if index[0] >= len(text) or not text[index[0]].isdigit():
                return error()
        digits_start = index[0]
        while index[0] < len(text) and text[index[0]].isdigit():
            index[0] += 1
        integer_part_digits = text[digits_start:index[0]]
        if len(integer_part_digits) > 1 and integer_part_digits[0] == '0':
            return error()
        if index[0] < len(text) and text[index[0]] == '.':
            index[0] += 1
            if index[0] >= len(text) or not text[index[0]].isdigit():
                return error()
            while index[0] < len(text) and text[index[0]].isdigit():
                index[0] += 1
        if index[0] < len(text) and (text[index[0]] in 'eE'):
            index[0] += 1
            if index[0] < len(text) and (text[index[0]] in '+-'):
                index[0] += 1
            if index[0] >= len(text) or not text[index[0]].isdigit():
                return error()
            while index[0] < len(text) and text[index[0]].isdigit():
                index[0] += 1
        num_str = text[start:index[0]]
        has_decimal = '.' in num_str
        has_exponent = 'e' in num_str or 'E' in num_str
        try:
            if has_decimal or has_exponent:
                value = float(num_str)
            else:
                value = int(num_str)
        except ValueError:
            return error()
        return value

    whitespace()
    value = parse_value()
    whitespace()
    if index[0] != len(text):
        return None
    return value
