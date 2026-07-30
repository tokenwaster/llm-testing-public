def parse(text: str):
    """Parse a JSON document and return the equivalent Python object.
    Returns None if the input is not valid JSON.
    """
    try:
        idx = 0
        n = len(text)

        def skip_ws():
            nonlocal idx
            while idx < n and text[idx] in ' \t\n\r':
                idx += 1

        def parse_value():
            skip_ws()
            if idx >= n:
                raise ValueError
            c = text[idx]
            if c == '{':
                return parse_object()
            if c == '[':
                return parse_array()
            if c == '"':
                return parse_string()
            if c == '-' or c.isdigit():
                return parse_number()
            if c == 't':
                return parse_literal('true', True)
            if c == 'f':
                return parse_literal('false', False)
            if c == 'n':
                return parse_literal('null', None)
            raise ValueError

        def parse_object():
            nonlocal idx
            idx += 1  # skip '{'
            skip_ws()
            obj = {}
            if idx < n and text[idx] == '}':
                idx += 1
                return obj
            while True:
                skip_ws()
                if idx >= n or text[idx] != '"':
                    raise ValueError
                key = parse_string()
                skip_ws()
                if idx >= n or text[idx] != ':':
                    raise ValueError
                idx += 1
                val = parse_value()
                obj[key] = val
                skip_ws()
                if idx >= n:
                    raise ValueError
                if text[idx] == ',':
                    idx += 1
                    skip_ws()
                    if idx < n and text[idx] == '}':
                        raise ValueError
                elif text[idx] == '}':
                    idx += 1
                    break
                else:
                    raise ValueError
            return obj

        def parse_array():
            nonlocal idx
            idx += 1  # skip '['
            skip_ws()
            arr = []
            if idx < n and text[idx] == ']':
                idx += 1
                return arr
            while True:
                val = parse_value()
                arr.append(val)
                skip_ws()
                if idx >= n:
                    raise ValueError
                if text[idx] == ',':
                    idx += 1
                    skip_ws()
                    if idx < n and text[idx] == ']':
                        raise ValueError
                elif text[idx] == ']':
                    idx += 1
                    break
                else:
                    raise ValueError
            return arr

        def parse_string():
            nonlocal idx
            idx += 1  # skip opening '"'
            chars = []
            while idx < n:
                c = text[idx]
                if c == '"':
                    idx += 1
                    return ''.join(chars)
                elif c == '\\':
                    idx += 1
                    if idx >= n:
                        raise ValueError
                    esc = text[idx]
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
                        if idx + 4 >= n:
                            raise ValueError
                        hex_str = text[idx + 1:idx + 5]
                        try:
                            code = int(hex_str, 16)
                        except ValueError:
                            raise ValueError
                        idx += 4  # now at last hex digit of this \uXXXX
                        # surrogate pair handling
                        if 0xD800 <= code <= 0xDBFF:
                            if (idx + 1 < n and text[idx + 1] == '\\' and
                                    idx + 2 < n and text[idx + 2] == 'u'):
                                if idx + 6 >= n:
                                    raise ValueError
                                hex2 = text[idx + 3:idx + 7]
                                try:
                                    code2 = int(hex2, 16)
                                except ValueError:
                                    raise ValueError
                                if 0xDC00 <= code2 <= 0xDFFF:
                                    combined = 0x10000 + (code - 0xD800) * 0x400 + (code2 - 0xDC00)
                                    chars.append(chr(combined))
                                    idx += 6  # move past second \uXXXX
                                else:
                                    raise ValueError
                            else:
                                # lone high surrogate; append as-is
                                chars.append(chr(code))
                        else:
                            chars.append(chr(code))
                    else:
                        raise ValueError
                    idx += 1
                else:
                    if ord(c) < 0x20:
                        raise ValueError
                    chars.append(c)
                    idx += 1
            raise ValueError  # unterminated string

        def parse_number():
            nonlocal idx
            start = idx
            if idx < n and text[idx] == '-':
                idx += 1
            # integer part
            if idx >= n:
                raise ValueError
            if text[idx] == '0':
                idx += 1
            elif text[idx].isdigit() and text[idx] != '0':
                idx += 1
                while idx < n and text[idx].isdigit():
                    idx += 1
            else:
                raise ValueError
            # fraction
            is_float = False
            if idx < n and text[idx] == '.':
                is_float = True
                idx += 1
                if idx >= n or not text[idx].isdigit():
                    raise ValueError
                while idx < n and text[idx].isdigit():
                    idx += 1
            # exponent
            if idx < n and (text[idx] == 'e' or text[idx] == 'E'):
                is_float = True
                idx += 1
                if idx < n and (text[idx] == '+' or text[idx] == '-'):
                    idx += 1
                if idx >= n or not text[idx].isdigit():
                    raise ValueError
                while idx < n and text[idx].isdigit():
                    idx += 1
            num_str = text[start:idx]
            if is_float:
                return float(num_str)
            else:
                return int(num_str)

        def parse_literal(expected, value):
            nonlocal idx
            if text[idx:idx + len(expected)] == expected:
                idx += len(expected)
                return value
            raise ValueError

        skip_ws()
        if idx >= n:
            return None
        result = parse_value()
        skip_ws()
        if idx != n:
            return None
        return result
    except (ValueError, IndexError):
        return None
