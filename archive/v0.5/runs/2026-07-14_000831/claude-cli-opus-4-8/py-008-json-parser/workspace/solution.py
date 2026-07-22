def parse(text):
    """Parse a JSON document, returning the equivalent Python object,
    or None if the input is not valid JSON."""

    WHITESPACE = " \t\n\r"
    ESCAPES = {
        '"': '"',
        '\\': '\\',
        '/': '/',
        'b': '\b',
        'f': '\f',
        'n': '\n',
        'r': '\r',
        't': '\t',
    }

    class _JSONError(Exception):
        pass

    n = len(text)

    def skip_ws(i):
        while i < n and text[i] in WHITESPACE:
            i += 1
        return i

    def parse_value(i):
        i = skip_ws(i)
        if i >= n:
            raise _JSONError("unexpected end")
        c = text[i]
        if c == '{':
            return parse_object(i)
        if c == '[':
            return parse_array(i)
        if c == '"':
            return parse_string(i)
        if c == '-' or c.isdigit():
            return parse_number(i)
        if text.startswith("true", i):
            return True, i + 4
        if text.startswith("false", i):
            return False, i + 5
        if text.startswith("null", i):
            return None, i + 4
        raise _JSONError("unexpected token")

    def parse_string(i):
        # text[i] == '"'
        i += 1
        chars = []
        while True:
            if i >= n:
                raise _JSONError("unterminated string")
            c = text[i]
            if c == '"':
                return "".join(chars), i + 1
            if c == '\\':
                i += 1
                if i >= n:
                    raise _JSONError("bad escape")
                e = text[i]
                if e == 'u':
                    hexdigits = text[i + 1:i + 5]
                    if len(hexdigits) != 4 or any(
                        h not in "0123456789abcdefABCDEF" for h in hexdigits
                    ):
                        raise _JSONError("bad unicode escape")
                    code = int(hexdigits, 16)
                    # Handle surrogate pairs
                    if 0xD800 <= code <= 0xDBFF:
                        if (text[i + 5:i + 7] == '\\u'):
                            lo = text[i + 7:i + 11]
                            if len(lo) == 4 and all(
                                h in "0123456789abcdefABCDEF" for h in lo
                            ):
                                locode = int(lo, 16)
                                if 0xDC00 <= locode <= 0xDFFF:
                                    combined = 0x10000 + (
                                        (code - 0xD800) << 10
                                    ) + (locode - 0xDC00)
                                    chars.append(chr(combined))
                                    i += 11
                                    continue
                        chars.append(chr(code))
                        i += 5
                        continue
                    chars.append(chr(code))
                    i += 5
                    continue
                if e in ESCAPES:
                    chars.append(ESCAPES[e])
                    i += 1
                    continue
                raise _JSONError("invalid escape")
            if ord(c) < 0x20:
                raise _JSONError("control character in string")
            chars.append(c)
            i += 1

    def parse_number(i):
        start = i
        if i < n and text[i] == '-':
            i += 1
        # integer part
        if i >= n:
            raise _JSONError("bad number")
        if text[i] == '0':
            i += 1
        elif text[i] in "123456789":
            i += 1
            while i < n and text[i].isdigit():
                i += 1
        else:
            raise _JSONError("bad number")

        is_float = False
        # fraction
        if i < n and text[i] == '.':
            is_float = True
            i += 1
            if i >= n or not text[i].isdigit():
                raise _JSONError("bad fraction")
            while i < n and text[i].isdigit():
                i += 1
        # exponent
        if i < n and text[i] in "eE":
            is_float = True
            i += 1
            if i < n and text[i] in "+-":
                i += 1
            if i >= n or not text[i].isdigit():
                raise _JSONError("bad exponent")
            while i < n and text[i].isdigit():
                i += 1

        numstr = text[start:i]
        if is_float:
            return float(numstr), i
        return int(numstr), i

    def parse_array(i):
        # text[i] == '['
        i += 1
        result = []
        i = skip_ws(i)
        if i < n and text[i] == ']':
            return result, i + 1
        while True:
            value, i = parse_value(i)
            result.append(value)
            i = skip_ws(i)
            if i >= n:
                raise _JSONError("unterminated array")
            if text[i] == ',':
                i += 1
                continue
            if text[i] == ']':
                return result, i + 1
            raise _JSONError("expected ',' or ']'")

    def parse_object(i):
        # text[i] == '{'
        i += 1
        result = {}
        i = skip_ws(i)
        if i < n and text[i] == '}':
            return result, i + 1
        while True:
            i = skip_ws(i)
            if i >= n or text[i] != '"':
                raise _JSONError("expected string key")
            key, i = parse_string(i)
            i = skip_ws(i)
            if i >= n or text[i] != ':':
                raise _JSONError("expected ':'")
            i += 1
            value, i = parse_value(i)
            result[key] = value
            i = skip_ws(i)
            if i >= n:
                raise _JSONError("unterminated object")
            if text[i] == ',':
                i += 1
                continue
            if text[i] == '}':
                return result, i + 1
            raise _JSONError("expected ',' or '}'")

    try:
        value, i = parse_value(0)
        i = skip_ws(i)
        if i != n:
            return None
        return value
    except _JSONError:
        return None
    except (ValueError, IndexError, RecursionError):
        return None
