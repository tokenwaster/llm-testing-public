def parse(text: str):
    pos = [0]  # mutable index into text

    def skip_ws():
        while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
            pos[0] += 1

    def expect_char(c):
        if pos[0] >= len(text) or text[pos[0]] != c:
            return False
        pos[0] += 1
        return True

    def parse_value():
        skip_ws()
        if pos[0] >= len(text):
            return None

        ch = text[pos[0]]

        if ch == '{':
            return _parse_object()
        elif ch == '[':
            return _parse_array()
        elif ch == '"':
            return _parse_string()
        elif ch == 't' and text.startswith('true', pos[0]):
            return _parse_keyword(pos[0], 4)
        elif ch == 'f' and text.startswith('false', pos[0]):
            return _parse_keyword(pos[0], 5)
        elif ch == 'n' and text.startswith('null', pos[0]):
            return _parse_keyword(pos[0], 4)
        else:
            # Try number (optional leading minus + digits)
            if ch.isdigit() or (ch == '-' and pos[0] + 1 < len(text) and text[pos[0] + 1].isdigit()):
                return _parse_number()
            else:
                return None

    def _parse_keyword(start, length):
        end = start + length
        if end > len(text):
            return None
        if text[start:end] != 'true' and text[start:end] != 'false' and text[start:end] != 'null':
            return None
        skip_ws()
        if pos[0] < len(text) and text[pos[0]] not in ',}]':
            return None  # trailing garbage
        pos[0] = end
        return None

    def _parse_number():
        start = pos[0]
        is_float = False

        # Optional minus sign
        if pos[0] < len(text) and text[pos[0]] == '-':
            pos[0] += 1

        # Integer part — reject leading zeros (except bare "0")
        if pos[0] >= len(text):
            return None
        ch = text[pos[0]]
        if ch == '0':
            pos[0] += 1
        elif ch.isdigit():
            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1
        else:
            return None

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
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            return None

    def _parse_string():
        pos[0] += 1  # skip opening quote
        result = []

        while True:
            if pos[0] >= len(text):
                return None  # unterminated string

            ch = text[pos[0]]

            if ch == '"':
                pos[0] += 1
                return ''.join(result)
            elif ch == '\\':
                pos[0] += 1
                if pos[0] >= len(text):
                    return None
                esc = text[pos[0]]
                pos[0] += 1

                escapes = {
                    '"': '"',
                    '\\': '\\',
                    '/': '/',
                    'b': '\b',
                    'f': '\f',
                    'n': '\n',
                    'r': '\r',
                    't': '\t',
                }

                if esc in escapes:
                    result.append(escapes[esc])
                elif esc == 'u':
                    if pos[0] + 4 > len(text):
                        return None
                    hex_str = text[pos[0]:pos[0] + 4]
                    pos[0] += 4
                    try:
                        result.append(chr(int(hex_str, 16)))
                    except ValueError:
                        return None
                else:
                    return None
            elif ord(ch) < 0x20:
                # Raw control characters are not allowed in JSON strings
                return None
            else:
                result.append(ch)
                pos[0] += 1

    def _parse_array():
        if not expect_char('['):
            return None

        items = []
        skip_ws()

        if pos[0] < len(text) and text[pos[0]] == ']':
            pos[0] += 1
            return items

        while True:
            val = parse_value()
            if val is None:
                return None

            # Reject trailing comma
            skip_ws()
            if pos[0] < len(text) and text[pos[0]] == ',':
                pos[0] += 1
                continue

            items.append(val)

            skip_ws()
            if pos[0] >= len(text):
                return None  # unterminated array
            if text[pos[0]] == ']':
                pos[0] += 1
                return items

        return None

    def _parse_object():
        if not expect_char('{'):
            return None

        items = {}
        skip_ws()

        if pos[0] < len(text) and text[pos[0]] == '}':
            pos[0] += 1
            return items

        while True:
            # Key must be a string (bare words are invalid JSON keys)
            key_start = pos[0]
            ch = text[key_start]
            if ch != '"':
                return None
            val = _parse_string()
            if val is None:
                return None

            skip_ws()
            if not expect_char(':'):
                return None

            obj_val = parse_value()
            if obj_val is None:
                return None

            items[val] = obj_val

            skip_ws()
            if pos[0] >= len(text):
                return None  # unterminated object
            if text[pos[0]] == '}':
                pos[0] += 1
                return items

        return None

    result = parse_value()

    if result is not None:
        skip_ws()
        if pos[0] < len(text):
            return None  # trailing garbage after document

    return result
