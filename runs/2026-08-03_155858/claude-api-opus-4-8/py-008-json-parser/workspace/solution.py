def parse(text: str):
    class ParseError(Exception):
        pass

    s = text
    n = len(s)
    i = 0

    def skip_ws(idx):
        while idx < n and s[idx] in ' \t\n\r':
            idx += 1
        return idx

    def parse_value(idx):
        idx = skip_ws(idx)
        if idx >= n:
            raise ParseError()
        c = s[idx]
        if c == '{':
            return parse_object(idx)
        elif c == '[':
            return parse_array(idx)
        elif c == '"':
            return parse_string(idx)
        elif c == 't':
            if s[idx:idx+4] == 'true':
                return True, idx + 4
            raise ParseError()
        elif c == 'f':
            if s[idx:idx+5] == 'false':
                return False, idx + 5
            raise ParseError()
        elif c == 'n':
            if s[idx:idx+4] == 'null':
                return None, idx + 4
            raise ParseError()
        elif c == '-' or c.isdigit():
            return parse_number(idx)
        else:
            raise ParseError()

    def parse_string(idx):
        # s[idx] == '"'
        idx += 1
        result = []
        while True:
            if idx >= n:
                raise ParseError()
            c = s[idx]
            if c == '"':
                return ''.join(result), idx + 1
            elif c == '\\':
                idx += 1
                if idx >= n:
                    raise ParseError()
                e = s[idx]
                if e == '"':
                    result.append('"')
                elif e == '\\':
                    result.append('\\')
                elif e == '/':
                    result.append('/')
                elif e == 'b':
                    result.append('\b')
                elif e == 'f':
                    result.append('\f')
                elif e == 'n':
                    result.append('\n')
                elif e == 'r':
                    result.append('\r')
                elif e == 't':
                    result.append('\t')
                elif e == 'u':
                    hexdigits = s[idx+1:idx+5]
                    if len(hexdigits) != 4:
                        raise ParseError()
                    for h in hexdigits:
                        if h not in '0123456789abcdefABCDEF':
                            raise ParseError()
                    code = int(hexdigits, 16)
                    idx += 4
                    # handle surrogate pairs
                    if 0xD800 <= code <= 0xDBFF:
                        if s[idx+1:idx+3] == '\\u':
                            lo = s[idx+3:idx+7]
                            if len(lo) == 4 and all(h in '0123456789abcdefABCDEF' for h in lo):
                                locode = int(lo, 16)
                                if 0xDC00 <= locode <= 0xDFFF:
                                    combined = 0x10000 + ((code - 0xD800) << 10) + (locode - 0xDC00)
                                    result.append(chr(combined))
                                    idx += 6
                                else:
                                    result.append(chr(code))
                            else:
                                result.append(chr(code))
                        else:
                            result.append(chr(code))
                    else:
                        result.append(chr(code))
                else:
                    raise ParseError()
                idx += 1
            elif ord(c) < 0x20:
                raise ParseError()
            else:
                result.append(c)
                idx += 1

    def parse_number(idx):
        start = idx
        if idx < n and s[idx] == '-':
            idx += 1
        if idx >= n:
            raise ParseError()
        if s[idx] == '0':
            idx += 1
        elif s[idx].isdigit():
            while idx < n and s[idx].isdigit():
                idx += 1
        else:
            raise ParseError()
        is_float = False
        if idx < n and s[idx] == '.':
            is_float = True
            idx += 1
            if idx >= n or not s[idx].isdigit():
                raise ParseError()
            while idx < n and s[idx].isdigit():
                idx += 1
        if idx < n and s[idx] in 'eE':
            is_float = True
            idx += 1
            if idx < n and s[idx] in '+-':
                idx += 1
            if idx >= n or not s[idx].isdigit():
                raise ParseError()
            while idx < n and s[idx].isdigit():
                idx += 1
        numstr = s[start:idx]
        if is_float:
            return float(numstr), idx
        else:
            return int(numstr), idx

    def parse_array(idx):
        idx += 1  # skip [
        result = []
        idx = skip_ws(idx)
        if idx < n and s[idx] == ']':
            return result, idx + 1
        while True:
            val, idx = parse_value(idx)
            result.append(val)
            idx = skip_ws(idx)
            if idx >= n:
                raise ParseError()
            if s[idx] == ',':
                idx += 1
                continue
            elif s[idx] == ']':
                return result, idx + 1
            else:
                raise ParseError()

    def parse_object(idx):
        idx += 1  # skip {
        result = {}
        idx = skip_ws(idx)
        if idx < n and s[idx] == '}':
            return result, idx + 1
        while True:
            idx = skip_ws(idx)
            if idx >= n or s[idx] != '"':
                raise ParseError()
            key, idx = parse_string(idx)
            idx = skip_ws(idx)
            if idx >= n or s[idx] != ':':
                raise ParseError()
            idx += 1
            val, idx = parse_value(idx)
            result[key] = val
            idx = skip_ws(idx)
            if idx >= n:
                raise ParseError()
            if s[idx] == ',':
                idx += 1
                continue
            elif s[idx] == '}':
                return result, idx + 1
            else:
                raise ParseError()

    try:
        value, idx = parse_value(i)
        idx = skip_ws(idx)
        if idx != n:
            return None
        return value
    except (ParseError, ValueError, IndexError):
        return None
