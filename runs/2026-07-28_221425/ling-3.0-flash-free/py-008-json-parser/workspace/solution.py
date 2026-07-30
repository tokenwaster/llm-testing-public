def parse(text: str):
    if not isinstance(text, str):
        return None

    idx = 0

    def skip_whitespace():
        nonlocal idx
        while idx < len(text) and text[idx] in ' \t\n\r':
            idx += 1

    def parse_value():
        nonlocal idx
        skip_whitespace()
        if idx >= len(text):
            raise ValueError()
        ch = text[idx]
        if ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch == '"':
            return parse_string()
        elif ch == 't':
            return parse_true()
        elif ch == 'f':
            return parse_false()
        elif ch == 'n':
            return parse_null()
        elif ch == '-' or ch.isdigit():
            return parse_number()
        else:
            raise ValueError()

    def parse_object():
        nonlocal idx
        idx += 1
        skip_whitespace()
        result = {}
        if idx < len(text) and text[idx] == '}':
            idx += 1
            return result
        while True:
            skip_whitespace()
            key = parse_string()
            if key is None:
                raise ValueError()
            skip_whitespace()
            if idx >= len(text) or text[idx] != ':':
                raise ValueError()
            idx += 1
            value = parse_value()
            result[key] = value
            skip_whitespace()
            if idx >= len(text):
                raise ValueError()
            if text[idx] == '}':
                idx += 1
                return result
            elif text[idx] == ',':
                idx += 1
                skip_whitespace()
                if idx >= len(text) or text[idx] == '}':
                    raise ValueError()
                continue
            else:
                raise ValueError()

    def parse_array():
        nonlocal idx
        idx += 1
        skip_whitespace()
        result = []
        if idx < len(text) and text[idx] == ']':
            idx += 1
            return result
        while True:
            value = parse_value()
            result.append(value)
            skip_whitespace()
            if idx >= len(text):
                raise ValueError()
            if text[idx] == ']':
                idx += 1
                return result
            elif text[idx] == ',':
                idx += 1
                skip_whitespace()
                if idx >= len(text) or text[idx] == ']':
                    raise ValueError()
                continue
            else:
                raise ValueError()

    def parse_string():
        nonlocal idx
        if idx >= len(text) or text[idx] != '"':
            raise ValueError()
        idx += 1
        result = []
        while idx < len(text):
            ch = text[idx]
            if ch == '"':
                idx += 1
                return ''.join(result)
            elif ch == '\\':
                idx += 1
                if idx >= len(text):
                    raise ValueError()
                esc = text[idx]
                if esc == '"':
                    result.append('"')
                    idx += 1
                elif esc == '\\':
                    result.append('\\')
                    idx += 1
                elif esc == '/':
                    result.append('/')
                    idx += 1
                elif esc == 'b':
                    result.append('\b')
                    idx += 1
                elif esc == 'f':
                    result.append('\f')
                    idx += 1
                elif esc == 'n':
                    result.append('\n')
                    idx += 1
                elif esc == 'r':
                    result.append('\r')
                    idx += 1
                elif esc == 't':
                    result.append('\t')
                    idx += 1
                elif esc == 'u':
                    idx += 1
                    if idx + 4 > len(text):
                        raise ValueError()
                    hex_str = text[idx:idx+4]
                    try:
                        code_point = int(hex_str, 16)
                        idx += 4
                        if 0xD800 <= code_point <= 0xDBFF:
                            if idx + 2 > len(text) or text[idx:idx+2] != '\\u':
                                raise ValueError()
                            idx += 2
                            if idx + 4 > len(text):
                                raise ValueError()
                            hex_str2 = text[idx:idx+4]
                            try:
                                code_point2 = int(hex_str2, 16)
                            except ValueError:
                                raise ValueError()
                            idx += 4
                            if not (0xDC00 <= code_point2 <= 0xDFFF):
                                raise ValueError()
                            code_point = 0x10000 + ((code_point - 0xD800) << 10) | (code_point2 - 0xDC00)
                        result.append(chr(code_point))
                    except ValueError:
                        raise ValueError()
                else:
                    raise ValueError()
            else:
                result.append(ch)
                idx += 1
        raise ValueError()

    def parse_true():
        nonlocal idx
        if text[idx:idx+4] == 'true':
            idx += 4
            return True
        raise ValueError()

    def parse_false():
        nonlocal idx
        if text[idx:idx+5] == 'false':
            idx += 5
            return False
        raise ValueError()

    def parse_null():
        nonlocal idx
        if text[idx:idx+4] == 'null':
            idx += 4
            return None
        raise ValueError()

    def parse_number():
        nonlocal idx
        start = idx
        if text[idx] == '-':
            idx += 1
        if idx >= len(text) or not text[idx].isdigit():
            raise ValueError()
        if text[idx] == '0':
            idx += 1
            if idx < len(text) and text[idx].isdigit():
                raise ValueError()
        else:
            while idx < len(text) and text[idx].isdigit():
                idx += 1
        is_float = False
        if idx < len(text) and text[idx] == '.':
            is_float = True
            idx += 1
            if idx >= len(text) or not text[idx].isdigit():
                raise ValueError()
            while idx < len(text) and text[idx].isdigit():
                idx += 1
        if idx < len(text) and text[idx] in ('e', 'E'):
            is_float = True
            idx += 1
            if idx < len(text) and text[idx] in ('+', '-'):
                idx += 1
            if idx >= len(text) or not text[idx].isdigit():
                raise ValueError()
            while idx < len(text) and text[idx].isdigit():
                idx += 1
        num_str = text[start:idx]
        if is_float:
            try:
                return float(num_str)
            except ValueError:
                raise ValueError()
        else:
            try:
                return int(num_str)
            except ValueError:
                raise ValueError()

    try:
        result = parse_value()
        skip_whitespace()
        if idx != len(text):
            raise ValueError()
        return result
    except ValueError:
        return None
