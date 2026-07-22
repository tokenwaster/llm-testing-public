def parse(text: str):
    pos = 0
    n = len(text)

    def skip_whitespace():
        nonlocal pos
        while pos < n and text[pos] in ' \n\r\t':
            pos += 1

    def parse_string():
        nonlocal pos
        if pos >= n or text[pos] != '"':
            return None
        pos += 1  # skip opening "
        res = []
        while pos < n and text[pos] != '"':
            char = text[pos]
            if char == '\\':
                pos += 1
                if pos >= n:
                    return None
                esc = text[pos]
                if esc == '"':
                    res.append('"')
                elif esc == '\\':
                    res.append('\\')
                elif esc == '/':
                    res.append('/')
                elif esc == 'b':
                    res.append('\b')
                elif esc == 'f':
                    res.append('\f')
                elif esc == 'n':
                    res.append('\n')
                elif esc == 'r':
                    res.append('\r')
                elif esc == 't':
                    res.append('\t')
                elif esc == 'u':
                    pos += 1
                    if pos + 4 > n:
                        return None
                    hex_code = text[pos:pos+4]
                    try:
                        res.append(chr(int(hex_code, 16)))
                    except ValueError:
                        return None
                    pos += 4
                else:
                    return None
            else:
                res.append(char)
            pos += 1
        if pos >= n or text[pos] != '"':
            return None
        pos += 1  # skip closing "
        return "".join(res)

    def parse_number():
        nonlocal pos
        start = pos
        if pos < n and text[pos] == '-':
            pos += 1
        
        if pos < n and text[pos] == '.':
            pos += 1
            while pos < n and text[pos].isdigit():
                pos += 1
        elif pos < n and text[pos].isdigit():
            if text[pos] == '0' and pos + 1 < n and text[pos+1].isdigit():
                return None  # Leading zero rule: "01" is invalid, but "0." or "0" is okay.
            while pos < n and text[pos].isdigit():
                pos += 1
            if pos < n and text[pos] == '.':
                pos += 1
                while pos < n and text[pos].isdigit():
                    pos += 1
        else:
            return None

        if pos < n and text[pos] in 'eE':
            pos += 1
            if pos < n and text[pos] in '+-':
                pos += 1
            if pos < n and text[pos].isdigit():
                while pos < n and text[pos].isdigit():
                    pos += 1
            else:
                return None

        num_str = text[start:pos]
        try:
            # JSON integers are numbers without decimal points or exponents.
            if '.' not in num_str and 'e' not in num_str.lower() and 'E' not in num_str.lower():
                return int(num_str)
            else:
                return float(num_str)
        except ValueError:
            return None

    def parse_value():
        skip_whitespace()
        if pos >= n:
            return None
        char = text[pos]
        if char == '{':
            return parse_object()
        if char == '[':
            return parse_array()
        if char == '"':
            return parse_string()
        if char == 't':
            if text.startswith('true', pos):
                pos += 4
                return True
            return None
        if char == 'f':
            if text.startswith('false', pos):
                pos += 5
                return False
            return None
        if char == 'n':
            if text.startswith('null', pos):
                pos += 4
                return None
            return None
        if char.isdigit() or char == '-':
            return parse_number()
        return None

    def parse_object():
        nonlocal pos
        pos += 1  # skip {
        skip_whitespace()
        if pos < n and text[pos] == '}':
            pos += 1
            return {}
        obj = {}
        while True:
            skip_whitespace()
            key = parse_string()
            if key is None:
                return None
            skip_whitespace()
            if pos >= n or text[pos] != ':':
                return None
            pos += 1  # skip :
            skip_whitespace()
            val = parse_value()
            if val is None:
                return None
            obj[key] = val
            skip_whitespace()
            if pos < n and text[pos] == '}':
                pos += 1
                return obj
            elif pos < n and text[pos] == ',':
                pos += 1
                skip_whitespace()
                # Trailing comma check: after a comma, there must be another key-value pair.
                if pos >= n or text[pos] == '}':
                    return None
            else:
                return None

    def parse_array():
        nonlocal pos
        pos += 1  # skip [
        skip_whitespace()
        if pos < n and text[pos] == ']':
            pos += 1
            return []
        arr = []
        while True:
            skip_whitespace()
            val = parse_value()
            if val is None:
                return None
            arr.append(val)
            skip_whitespace()
            if pos < n and text[pos] == ']':
                pos += 1
                return arr
            elif pos < n and text[pos] == ',':
                pos += 1
                skip_whitespace()
                # Trailing comma check: after a comma, there must be another value.
                if pos >= n or text[pos] == ']':
                    return None
            else:
                return None

    result = parse_value()
    skip_whitespace()
    # Ensure the entire document was consumed and result is not None (invalid input).
    if result is None or pos != n:
        return None
    return result
