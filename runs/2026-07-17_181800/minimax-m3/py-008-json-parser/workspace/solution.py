def parse(text: str):
    if not isinstance(text, str):
        return None
    try:
        result, end = _parse_value(text, 0)
        end = _skip_ws(text, end)
        if end != len(text):
            return None
        return result
    except (ValueError, IndexError):
        return None

def _skip_ws(text, i):
    while i < len(text) and text[i] in ' \t\n\r':
        i += 1
    return i

def _parse_value(text, i):
    i = _skip_ws(text, i)
    if i >= len(text):
        raise ValueError("unexpected end")
    c = text[i]
    if c == '{':
        return _parse_object(text, i)
    elif c == '[':
        return _parse_array(text, i)
    elif c == '"':
        return _parse_string(text, i)
    elif c == 't':
        return _parse_literal(text, i, 'true', True)
    elif c == 'f':
        return _parse_literal(text, i, 'false', False)
    elif c == 'n':
        return _parse_literal(text, i, 'null', None)
    elif c == '-' or '0' <= c <= '9':
        return _parse_number(text, i)
    else:
        raise ValueError("unexpected character")

def _parse_object(text, i):
    i = _skip_ws(text, i)
    if i >= len(text) or text[i] != '{':
        raise ValueError("expected {")
    i += 1
    i = _skip_ws(text, i)
    result = {}
    if i < len(text) and text[i] == '}':
        return result, i + 1
    while True:
        i = _skip_ws(text, i)
        if i >= len(text) or text[i] != '"':
            raise ValueError("expected string key")
        key, i = _parse_string(text, i)
        i = _skip_ws(text, i)
        if i >= len(text) or text[i] != ':':
            raise ValueError("expected colon")
        i += 1
        value, i = _parse_value(text, i)
        result[key] = value
        i = _skip_ws(text, i)
        if i >= len(text):
            raise ValueError("unexpected end")
        if text[i] == ',':
            i += 1
            continue
        elif text[i] == '}':
            return result, i + 1
        else:
            raise ValueError("expected , or }")

def _parse_array(text, i):
    i = _skip_ws(text, i)
    if i >= len(text) or text[i] != '[':
        raise ValueError("expected [")
    i += 1
    i = _skip_ws(text, i)
    result = []
    if i < len(text) and text[i] == ']':
        return result, i + 1
    while True:
        value, i = _parse_value(text, i)
        result.append(value)
        i = _skip_ws(text, i)
        if i >= len(text):
            raise ValueError("unexpected end")
        if text[i] == ',':
            i += 1
            continue
        elif text[i] == ']':
            return result, i + 1
        else:
            raise ValueError("expected , or ]")

def _parse_string(text, i):
    if i >= len(text) or text[i] != '"':
        raise ValueError("expected string")
    i += 1
    chars = []
    while i < len(text):
        c = text[i]
        if c == '"':
            return ''.join(chars), i + 1
        elif c == '\\':
            i += 1
            if i >= len(text):
                raise ValueError("unterminated escape")
            esc = text[i]
            if esc == '"':
                chars.append('"')
                i += 1
            elif esc == '\\':
                chars.append('\\')
                i += 1
            elif esc == '/':
                chars.append('/')
                i += 1
            elif esc == 'b':
                chars.append('\b')
                i += 1
            elif esc == 'f':
                chars.append('\f')
                i += 1
            elif esc == 'n':
                chars.append('\n')
                i += 1
            elif esc == 'r':
                chars.append('\r')
                i += 1
            elif esc == 't':
                chars.append('\t')
                i += 1
            elif esc == 'u':
                if i + 4 >= len(text):
                    raise ValueError("unterminated unicode escape")
                hex_str = text[i+1:i+5]
                if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                    raise ValueError("invalid unicode escape")
                code = int(hex_str, 16)
                if 0xD800 <= code <= 0xDBFF:
                    if i + 10 >= len(text) or text[i+5] != '\\' or text[i+6] != 'u':
                        raise ValueError("expected low surrogate")
                    hex_str2 = text[i+7:i+11]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str2):
                        raise ValueError("invalid unicode escape")
                    code2 = int(hex_str2, 16)
                    if not (0xDC00 <= code2 <= 0xDFFF):
                        raise ValueError("expected low surrogate")
                    code = 0x10000 + (code - 0xD800) * 0x400 + (code2 - 0xDC00)
                    chars.append(chr(code))
                    i += 11
                elif 0xDC00 <= code <= 0xDFFF:
                    raise ValueError("lone low surrogate")
                else:
                    chars.append(chr(code))
                    i += 5
            else:
                raise ValueError("invalid escape")
        elif ord(c) < 0x20:
            raise ValueError("control character in string")
        else:
            chars.append(c)
            i += 1
    raise ValueError("unterminated string")

def _parse_literal(text, i, literal, value):
    if text[i:i+len(literal)] == literal:
        return value, i + len(literal)
    raise ValueError("invalid literal")

def _parse_number(text, i):
    start = i
    if text[i] == '-':
        i += 1
        if i >= len(text):
            raise ValueError("invalid number")
    if text[i] == '0':
        i += 1
        if i < len(text) and '0' <= text[i] <= '9':
            raise ValueError("leading zero")
    elif '0' <= text[i] <= '9':
        while i < len(text) and '0' <= text[i] <= '9':
            i += 1
    else:
        raise ValueError("invalid number")
    is_float = False
    if i < len(text) and text[i] == '.':
        is_float = True
        i += 1
        if i >= len(text) or not ('0' <= text[i] <= '9'):
            raise ValueError("invalid number")
        while i < len(text) and '0' <= text[i] <= '9':
            i += 1
    if i < len(text) and text[i] in 'eE':
        is_float = True
        i += 1
        if i < len(text) and text[i] in '+-':
            i += 1
        if i >= len(text) or not ('0' <= text[i] <= '9'):
            raise ValueError("invalid number")
        while i < len(text) and '0' <= text[i] <= '9':
            i += 1
    num_str = text[start:i]
    if is_float:
        return float(num_str), i
    else:
        return int(num_str), i
