def parse(text: str):
    # Parser state
    s = text
    n = len(s)
    i = 0

    def skip_whitespace():
        nonlocal i
        while i < n and s[i] in ' \t\n\r':
            i += 1

    def parse_value():
        nonlocal i
        skip_whitespace()
        if i >= n:
            return None, False
        c = s[i]
        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        elif c == 't':
            return parse_literal('true', True)
        elif c == 'f':
            return parse_literal('false', False)
        elif c == 'n':
            return parse_literal('null', None)
        elif c == '-' or c.isdigit():
            return parse_number()
        else:
            return None, False

    def parse_literal(lit, val):
        nonlocal i
        if s[i:i+len(lit)] == lit:
            i += len(lit)
            return val, True
        return None, False

    def parse_object():
        nonlocal i
        i += 1  # consume '{'
        obj = {}
        skip_whitespace()
        if i < n and s[i] == '}':
            i += 1
            return obj, True
        while True:
            skip_whitespace()
            if i >= n or s[i] != '"':
                return None, False
            key, ok = parse_string()
            if not ok:
                return None, False
            skip_whitespace()
            if i >= n or s[i] != ':':
                return None, False
            i += 1  # consume ':'
            val, ok = parse_value()
            if not ok:
                return None, False
            obj[key] = val
            skip_whitespace()
            if i >= n:
                return None, False
            if s[i] == ',':
                i += 1
                continue
            elif s[i] == '}':
                i += 1
                return obj, True
            else:
                return None, False

    def parse_array():
        nonlocal i
        i += 1  # consume '['
        arr = []
        skip_whitespace()
        if i < n and s[i] == ']':
            i += 1
            return arr, True
        while True:
            val, ok = parse_value()
            if not ok:
                return None, False
            arr.append(val)
            skip_whitespace()
            if i >= n:
                return None, False
            if s[i] == ',':
                i += 1
                continue
            elif s[i] == ']':
                i += 1
                return arr, True
            else:
                return None, False

    def parse_string():
        nonlocal i
        i += 1  # consume opening quote
        chars = []
        while i < n:
            c = s[i]
            if c == '"':
                i += 1
                return ''.join(chars), True
            elif c == '\\':
                i += 1
                if i >= n:
                    return None, False
                e = s[i]
                if e == '"':
                    chars.append('"')
                elif e == '\\':
                    chars.append('\\')
                elif e == '/':
                    chars.append('/')
                elif e == 'b':
                    chars.append('\b')
                elif e == 'f':
                    chars.append('\f')
                elif e == 'n':
                    chars.append('\n')
                elif e == 'r':
                    chars.append('\r')
                elif e == 't':
                    chars.append('\t')
                elif e == 'u':
                    if i + 4 >= n:
                        return None, False
                    hexdigits = s[i+1:i+5]
                    if not all(d in '0123456789abcdefABCDEF' for d in hexdigits):
                        return None, False
                    code = int(hexdigits, 16)
                    chars.append(chr(code))
                    i += 4
                else:
                    return None, False
                i += 1
            else:
                chars.append(c)
                i += 1
        return None, False

    def parse_number():
        nonlocal i
        start = i
        if s[i] == '-':
            i += 1
        if i >= n:
            return None, False
        # integer part
        if s[i] == '0':
            i += 1
            int_part = '0'
        elif s[i].isdigit():
            int_part = ''
            while i < n and s[i].isdigit():
                int_part += s[i]
                i += 1
        else:
            return None, False
        # leading zero check
        if int_part != '0' and int_part.startswith('0'):
            return None, False
        # fraction
        frac_part = ''
        if i < n and s[i] == '.':
            i += 1
            if i >= n or not s[i].isdigit():
                return None, False
            while i < n and s[i].isdigit():
                frac_part += s[i]
                i += 1
        # exponent
        exp_part = ''
        if i < n and s[i] in 'eE':
            i += 1
            if i < n and s[i] in '+-':
                exp_part += s[i]
                i += 1
            if i >= n or not s[i].isdigit():
                return None, False
            while i < n and s[i].isdigit():
                exp_part += s[i]
                i += 1
        num_str = s[start:i]
        if frac_part == '' and exp_part == '':
            return int(num_str), True
        else:
            return float(num_str), True

    val, ok = parse_value()
    if not ok:
        return None
    skip_whitespace()
    if i != n:
        return None
    return val
