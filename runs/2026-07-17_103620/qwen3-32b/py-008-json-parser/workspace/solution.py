def parse(text: str):
    if not text:
        return None
    index = [0]

    def skip_space():
        while index[0] < len(text) and text[index[0]].isspace():
            index[0] += 1

    def parse_value():
        skip_space()
        if index[0] >= len(text):
            return None
        c = text[index[0]]
        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        else:
            start_kw = index[0]
            if text.startswith('true', start_kw):
                index[0] += 4
                skip_space()
                return True
            elif text.startswith('false', start_kw):
                index[0] += 5
                skip_space()
                return False
            elif text.startswith('null', start_kw):
                index[0] += 4
                skip_space()
                return None
            else:
                start_num = index[0]
                negative = False
                if text[index[0]] == '-':
                    negative = True
                    index[0] += 1
                has_digits = False
                if index[0] < len(text) and text[index[0]] == '0':
                    index[0] += 1
                    has_digits = True
                    if index[0] < len(text) and text[index[0]].isdigit():
                        return None
                else:
                    if index[0] >= len(text) or not text[index[0]].isdigit():
                        return None
                    index[0] += 1
                    has_digits = True
                    while index[0] < len(text) and text[index[0]].isdigit():
                        index[0] += 1
                if index[0] < len(text) and text[index[0]] == '.':
                    index[0] += 1
                    if index[0] >= len(text) or not text[index[0]].isdigit():
                        return None
                    index[0] += 1
                    while index[0] < len(text) and text[index[0]].isdigit():
                        index[0] += 1
                if index[0] < len(text) and (text[index[0]] in 'eE'):
                    index[0] += 1
                    if index[0] < len(text) and (text[index[0]] == '+' or text[index[0]] == '-'):
                        index[0] += 1
                    if index[0] >= len(text) or not text[index[0]].isdigit():
                        return None
                    index[0] += 1
                    while index[0] < len(text) and text[index[0]].isdigit():
                        index[0] += 1
                if not has_digits:
                    return None
                num_str = text[start_num:index[0]]
                full_num_str = ('-' + num_str) if negative else num_str
                try:
                    if '.' in full_num_str or 'e' in full_num_str.lower():
                        value = float(full_num_str)
                    else:
                        value = int(full_num_str)
                    return value
                except ValueError:
                    return None

    def parse_object():
        skip_space()
        if text[index[0]] != '{':
            return None
        index[0] += 1
        obj = {}
        while True:
            key = parse_value()
            if key is None or not isinstance(key, str):
                return None
            skip_space()
            if index[0] >= len(text) or text[index[0]] != ':':
                return None
            index[0] += 1
            value = parse_value()
            if value is None:
                return None
            obj[key] = value
            skip_space()
            if index[0] >= len(text):
                return None
            c = text[index[0]]
            if c == '}':
                index[0] += 1
                skip_space()
                return obj
            elif c == ',':
                index[0] += 1
                continue
            else:
                return None

    def parse_array():
        skip_space()
        if text[index[0]] != '[':
            return None
        index[0] += 1
        arr = []
        while True:
            value = parse_value()
            if value is None and not arr:
                skip_space()
                if text[index[0]] == ']':
                    index[0] += 1
                    return []
                else:
                    return None
            if value is not None:
                arr.append(value)
            skip_space()
            if index[0] >= len(text):
                return None
            c = text[index[0]]
            if c == ']':
                index[0] += 1
                skip_space()
                return arr
            elif c == ',':
                index[0] += 1
                continue
            else:
                return None

    def parse_string():
        skip_space()
        start = index[0]
        if text[index[0]] != '"':
            return None
        index[0] += 1
        s = []
        while index[0] < len(text):
            c = text[index[0]]
            if c == '"':
                index[0] += 1
                skip_space()
                return ''.join(s)
            elif c == '\\':
                index[0] += 1
                if index[0] >= len(text):
                    return None
                next_char = text[index[0]]
                if next_char == '"':
                    s.append('"')
                elif next_char == '\\':
                    s.append('\\')
                elif next_char == '/':
                    s.append('/')
                elif next_char == 'b':
                    s.append('\b')
                elif next_char == 'f':
                    s.append('\f')
                elif next_char == 'n':
                    s.append('\n')
                elif next_char == 'r':
                    s.append('\r')
                elif next_char == 't':
                    s.append('\t')
                elif next_char == 'u':
                    if index[0] + 4 > len(text):
                        return None
                    hex_chars = text[index[0]+1:index[0]+5]
                    if all(c in '0123456789abcdefABCDEF' for c in hex_chars):
                        code_point = int(hex_chars, 16)
                        s.append(chr(code_point))
                        index[0] += 4
                    else:
                        return None
                else:
                    return None
                index[0] += 1
            else:
                s.append(c)
                index[0] += 1
        return None

    result = parse_value()
    skip_space()
    if index[0] < len(text):
        return None
    return result
