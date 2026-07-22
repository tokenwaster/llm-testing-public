def parse(text: str):
    try:
        result, pos = _parse_value(text, 0)
        # Allow only trailing whitespace after the document
        while pos < len(text) and text[pos] in ' \t\n\r':
            pos += 1
        if pos != len(text):
            return None
        return result
    except (ValueError, IndexError):
        return None


_ALNUM = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')


def _skip_ws(s, i):
    while i < len(s) and s[i] in ' \t\n\r':
        i += 1
    return i


def _parse_value(s, i):
    i = _skip_ws(s, i)
    if i >= len(s):
        raise ValueError("unexpected end of input")

    c = s[i]

    if c == '"':
        return _parse_string(s, i)
    elif c in '-0123456789':
        return _parse_number(s, i)
    elif c == 't':
        if (s[i:i+4] == 'true' and
                (i + 4 >= len(s) or s[i+4] not in _ALNUM)):
            return True, i + 4
        raise ValueError("invalid token")
    elif c == 'f':
        if (s[i:i+5] == 'false' and
                (i + 5 >= len(s) or s[i+5] not in _ALNUM)):
            return False, i + 5
        raise ValueError("invalid token")
    elif c == 'n':
        if (s[i:i+4] == 'null' and
                (i + 4 >= len(s) or s[i+4] not in _ALNUM)):
            return None, i + 4
        raise ValueError("invalid token")
    elif c == '{':
        return _parse_object(s, i)
    elif c == '[':
        return _parse_array(s, i)
    else:
        raise ValueError(f"unexpected character: {c!r}")


def _parse_number(s, i):
    start = i

    if s[i] == '-':
        i += 1

    if i >= len(s) or not s[i].isdigit():
        raise ValueError("expected digit")

    # Integer part — reject leading zeros (only bare "0" is allowed)
    if s[i] == '0':
        i += 1
        if i < len(s) and s[i].isdigit():
            raise ValueError("leading zero not allowed")
    else:
        i += 1
        while i < len(s) and s[i].isdigit():
            i += 1

    is_float = False

    # Fractional part
    if i < len(s) and s[i] == '.':
        is_float = True
        i += 1
        if i >= len(s) or not s[i].isdigit():
            raise ValueError("expected digit after '.'")
        while i < len(s) and s[i].isdigit():
            i += 1

    # Exponent part
    if i < len(s) and s[i] in 'eE':
        is_float = True
        i += 1
        if i < len(s) and s[i] in '+-':
            i += 1
        if i >= len(s) or not s[i].isdigit():
            raise ValueError("expected digit in exponent")
        while i < len(s) and s[i].isdigit():
            i += 1

    num_str = s[start:i]
    if is_float:
        return float(num_str), i
    else:
        return int(num_str), i


def _parse_string(s, i):
    assert s[i] == '"'
    i += 1
    chars = []

    while i < len(s):
        c = s[i]

        if c == '"':
            return ''.join(chars), i + 1

        elif c == '\\':
            i += 1
            if i >= len(s):
                raise ValueError("unterminated escape sequence")

            esc = s[i]
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
                if i + 4 >= len(s):
                    raise ValueError("incomplete \\u escape")
                hex_str = s[i+1:i+5]
                try:
                    code_point = int(hex_str, 16)
                except ValueError:
                    raise ValueError("invalid hex digits in \\u escape")
                chars.append(chr(code_point))
                i += 4          # consumed \uXXXX; the trailing i+=1 below moves past 'X'
            else:
                raise ValueError(f"invalid escape character: {esc!r}")

        elif ord(c) < 0x20:
            # Unescaped control characters are not allowed in JSON strings
            raise ValueError("unescaped control character in string")

        else:
            chars.append(c)

        i += 1

    raise ValueError("unterminated string literal")


def _parse_object(s, i):
    assert s[i] == '{'
    i += 1
    result = {}

    i = _skip_ws(s, i)
    if i < len(s) and s[i] == '}':
        return result, i + 1

    while True:
        i = _skip_ws(s, i)

        # Key must be a string
        if i >= len(s) or s[i] != '"':
            raise ValueError("expected string key in object")
        key, i = _parse_string(s, i)

        i = _skip_ws(s, i)
        if i >= len(s) or s[i] != ':':
            raise ValueError("expected ':' after object key")
        i += 1

        val, i = _parse_value(s, i)
        result[key] = val

        i = _skip_ws(s, i)
        if i < len(s) and s[i] == ',':
            i += 1
            # Reject trailing comma: look ahead past whitespace for '}'
            j = _skip_ws(s, i)
            if j < len(s) and s[j] == '}':
                raise ValueError("trailing comma in object")
            continue
        elif i < len(s) and s[i] == '}':
            return result, i + 1
        else:
            raise ValueError("expected ',' or '}' in object")


def _parse_array(s, i):
    assert s[i] == '['
    i += 1
    result = []

    i = _skip_ws(s, i)
    if i < len(s) and s[i] == ']':
        return result, i + 1

    while True:
        val, i = _parse_value(s, i)
        result.append(val)

        i = _skip_ws(s, i)
        if i < len(s) and s[i] == ',':
            i += 1
            # Reject trailing comma: look ahead past whitespace for ']'
            j = _skip_ws(s, i)
            if j < len(s) and s[j] == ']':
                raise ValueError("trailing comma in array")
            continue
        elif i < len(s) and s[i] == ']':
            return result, i + 1
        else:
            raise ValueError("expected ',' or ']' in array")
