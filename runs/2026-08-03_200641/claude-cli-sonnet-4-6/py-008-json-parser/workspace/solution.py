def parse(text: str):
    FAIL = object()

    def skip_ws(s, i):
        while i < len(s) and s[i] in ' \t\n\r':
            i += 1
        return i

    def parse_string(s, i):
        i += 1  # skip opening "
        chars = []
        while i < len(s):
            c = s[i]
            if c == '"':
                return ''.join(chars), i + 1
            if c == '\\':
                i += 1
                if i >= len(s):
                    return FAIL, i
                esc = s[i]
                if esc == '"':    chars.append('"');  i += 1
                elif esc == '\\': chars.append('\\'); i += 1
                elif esc == '/':  chars.append('/');  i += 1
                elif esc == 'b':  chars.append('\b'); i += 1
                elif esc == 'f':  chars.append('\f'); i += 1
                elif esc == 'n':  chars.append('\n'); i += 1
                elif esc == 'r':  chars.append('\r'); i += 1
                elif esc == 't':  chars.append('\t'); i += 1
                elif esc == 'u':
                    hex4 = s[i+1:i+5]
                    if len(hex4) != 4 or not all(h in '0123456789abcdefABCDEF' for h in hex4):
                        return FAIL, i
                    cp = int(hex4, 16)
                    i += 5
                    if 0xD800 <= cp <= 0xDBFF:
                        if i + 1 < len(s) and s[i] == '\\' and s[i+1] == 'u':
                            low4 = s[i+2:i+6]
                            if len(low4) == 4 and all(h in '0123456789abcdefABCDEF' for h in low4):
                                low = int(low4, 16)
                                if 0xDC00 <= low <= 0xDFFF:
                                    cp = 0x10000 + (cp - 0xD800) * 0x400 + (low - 0xDC00)
                                    i += 6
                    chars.append(chr(cp))
                else:
                    return FAIL, i
            elif ord(c) < 0x20:
                return FAIL, i
            else:
                chars.append(c)
                i += 1
        return FAIL, i  # unterminated string

    def parse_number(s, i):
        start = i
        is_float = False
        if i < len(s) and s[i] == '-':
            i += 1
        if i >= len(s):
            return FAIL, i
        if s[i] == '0':
            i += 1
            if i < len(s) and '0' <= s[i] <= '9':
                return FAIL, i  # leading zero
        elif '1' <= s[i] <= '9':
            while i < len(s) and '0' <= s[i] <= '9':
                i += 1
        else:
            return FAIL, i
        if i < len(s) and s[i] == '.':
            is_float = True
            i += 1
            if i >= len(s) or not ('0' <= s[i] <= '9'):
                return FAIL, i
            while i < len(s) and '0' <= s[i] <= '9':
                i += 1
        if i < len(s) and s[i] in 'eE':
            is_float = True
            i += 1
            if i < len(s) and s[i] in '+-':
                i += 1
            if i >= len(s) or not ('0' <= s[i] <= '9'):
                return FAIL, i
            while i < len(s) and '0' <= s[i] <= '9':
                i += 1
        num_str = s[start:i]
        return (float(num_str) if is_float else int(num_str)), i

    def parse_array(s, i):
        i += 1  # skip '['
        i = skip_ws(s, i)
        if i >= len(s):
            return FAIL, i
        if s[i] == ']':
            return [], i + 1
        result = []
        while True:
            val, i = parse_value(s, i)
            if val is FAIL:
                return FAIL, i
            result.append(val)
            i = skip_ws(s, i)
            if i >= len(s):
                return FAIL, i
            if s[i] == ']':
                return result, i + 1
            if s[i] != ',':
                return FAIL, i
            i += 1  # skip ','
            i = skip_ws(s, i)
            if i < len(s) and s[i] == ']':
                return FAIL, i  # trailing comma

    def parse_object(s, i):
        i += 1  # skip '{'
        i = skip_ws(s, i)
        if i >= len(s):
            return FAIL, i
        if s[i] == '}':
            return {}, i + 1
        result = {}
        while True:
            i = skip_ws(s, i)
            if i >= len(s) or s[i] != '"':
                return FAIL, i
            key, i = parse_string(s, i)
            if key is FAIL:
                return FAIL, i
            i = skip_ws(s, i)
            if i >= len(s) or s[i] != ':':
                return FAIL, i
            i += 1  # skip ':'
            val, i = parse_value(s, i)
            if val is FAIL:
                return FAIL, i
            result[key] = val
            i = skip_ws(s, i)
            if i >= len(s):
                return FAIL, i
            if s[i] == '}':
                return result, i + 1
            if s[i] != ',':
                return FAIL, i
            i += 1  # skip ','
            i = skip_ws(s, i)
            if i < len(s) and s[i] == '}':
                return FAIL, i  # trailing comma

    def parse_value(s, i):
        i = skip_ws(s, i)
        if i >= len(s):
            return FAIL, i
        c = s[i]
        if c == '"': return parse_string(s, i)
        if c == '{': return parse_object(s, i)
        if c == '[': return parse_array(s, i)
        if c == 't': return (True,  i + 4) if s[i:i+4] == 'true'  else (FAIL, i)
        if c == 'f': return (False, i + 5) if s[i:i+5] == 'false' else (FAIL, i)
        if c == 'n': return (None,  i + 4) if s[i:i+4] == 'null'  else (FAIL, i)
        if c == '-' or '0' <= c <= '9': return parse_number(s, i)
        return FAIL, i

    if not isinstance(text, str):
        return None

    val, pos = parse_value(text, 0)
    if val is FAIL:
        return None
    pos = skip_ws(text, pos)
    if pos != len(text):
        return None  # trailing garbage
    return val
