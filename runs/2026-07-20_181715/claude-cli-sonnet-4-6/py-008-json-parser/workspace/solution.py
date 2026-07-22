def parse(text: str):
    if not isinstance(text, str):
        return None
    
    pos = 0
    
    def peek():
        nonlocal pos
        skip_ws()
        if pos < len(text):
            return text[pos]
        return None
    
    def skip_ws():
        nonlocal pos
        while pos < len(text) and text[pos] in ' \t\n\r':
            pos += 1
    
    def consume(c):
        nonlocal pos
        skip_ws()
        if pos < len(text) and text[pos] == c:
            pos += 1
            return True
        return False
    
    def parse_value():
        skip_ws()
        if pos >= len(text):
            raise ValueError("Unexpected end")
        c = text[pos]
        if c == '"':
            return parse_string()
        elif c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == 't':
            return parse_literal('true', True)
        elif c == 'f':
            return parse_literal('false', False)
        elif c == 'n':
            return parse_literal('null', None)
        elif c == '-' or c.isdigit():
            return parse_number()
        else:
            raise ValueError(f"Unexpected character: {c!r}")
    
    def parse_literal(s, val):
        nonlocal pos
        if text[pos:pos+len(s)] == s:
            pos += len(s)
            return val
        raise ValueError(f"Expected {s!r}")
    
    def parse_string():
        nonlocal pos
        if text[pos] != '"':
            raise ValueError("Expected '\"'")
        pos += 1
        result = []
        while pos < len(text):
            c = text[pos]
            if c == '"':
                pos += 1
                return ''.join(result)
            elif c == '\\':
                pos += 1
                if pos >= len(text):
                    raise ValueError("Unexpected end in escape")
                esc = text[pos]
                if esc == '"':
                    result.append('"')
                elif esc == '\\':
                    result.append('\\')
                elif esc == '/':
                    result.append('/')
                elif esc == 'b':
                    result.append('\b')
                elif esc == 'f':
                    result.append('\f')
                elif esc == 'n':
                    result.append('\n')
                elif esc == 'r':
                    result.append('\r')
                elif esc == 't':
                    result.append('\t')
                elif esc == 'u':
                    pos += 1
                    if pos + 4 > len(text):
                        raise ValueError("Incomplete unicode escape")
                    hex_str = text[pos:pos+4]
                    if not all(h in '0123456789abcdefABCDEF' for h in hex_str):
                        raise ValueError("Invalid unicode escape")
                    code_point = int(hex_str, 16)
                    # Handle surrogate pairs
                    if 0xD800 <= code_point <= 0xDBFF:
                        pos += 4
                        if pos + 2 <= len(text) and text[pos:pos+2] == '\\u':
                            pos += 2
                            if pos + 4 > len(text):
                                raise ValueError("Incomplete surrogate pair")
                            hex_str2 = text[pos:pos+4]
                            if not all(h in '0123456789abcdefABCDEF' for h in hex_str2):
                                raise ValueError("Invalid unicode escape")
                            low = int(hex_str2, 16)
                            if 0xDC00 <= low <= 0xDFFF:
                                code_point = 0x10000 + (code_point - 0xD800) * 0x400 + (low - 0xDC00)
                                result.append(chr(code_point))
                                pos += 4
                                continue
                            else:
                                raise ValueError("Invalid surrogate pair")
                        else:
                            raise ValueError("Lone surrogate")
                    elif 0xDC00 <= code_point <= 0xDFFF:
                        raise ValueError("Lone low surrogate")
                    else:
                        result.append(chr(code_point))
                    pos += 4
                    continue
                else:
                    raise ValueError(f"Invalid escape: \\{esc}")
                pos += 1
            elif ord(c) < 0x20:
                raise ValueError("Control character in string")
            else:
                result.append(c)
                pos += 1
        raise ValueError("Unterminated string")
    
    def parse_number():
        nonlocal pos
        start = pos
        is_float = False
        
        if pos < len(text) and text[pos] == '-':
            pos += 1
        
        if pos >= len(text):
            raise ValueError("Expected digit")
        
        if text[pos] == '0':
            pos += 1
            if pos < len(text) and text[pos].isdigit():
                raise ValueError("Leading zeros not allowed")
        elif text[pos].isdigit():
            while pos < len(text) and text[pos].isdigit():
                pos += 1
        else:
            raise ValueError("Expected digit")
        
        if pos < len(text) and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                raise ValueError("Expected digit after decimal point")
            while pos < len(text) and text[pos].isdigit():
                pos += 1
        
        if pos < len(text) and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < len(text) and text[pos] in '+-':
                pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                raise ValueError("Expected digit in exponent")
            while pos < len(text) and text[pos].isdigit():
                pos += 1
        
        num_str = text[start:pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)
    
    def parse_array():
        nonlocal pos
        if text[pos] != '[':
            raise ValueError("Expected '['")
        pos += 1
        result = []
        skip_ws()
        if pos < len(text) and text[pos] == ']':
            pos += 1
            return result
        while True:
            result.append(parse_value())
            skip_ws()
            if pos >= len(text):
                raise ValueError("Unterminated array")
            if text[pos] == ']':
                pos += 1
                return result
            elif text[pos] == ',':
                pos += 1
                skip_ws()
                if pos < len(text) and text[pos] == ']':
                    raise ValueError("Trailing comma in array")
            else:
                raise ValueError("Expected ',' or ']'")
    
    def parse_object():
        nonlocal pos
        if text[pos] != '{':
            raise ValueError("Expected '{'")
        pos += 1
        result = {}
        skip_ws()
        if pos < len(text) and text[pos] == '}':
            pos += 1
            return result
        while True:
            skip_ws()
            if pos >= len(text) or text[pos] != '"':
                raise ValueError("Expected string key")
            key = parse_string()
            skip_ws()
            if pos >= len(text) or text[pos] != ':':
                raise ValueError("Expected ':'")
            pos += 1
            val = parse_value()
            result[key] = val
            skip_ws()
            if pos >= len(text):
                raise ValueError("Unterminated object")
            if text[pos] == '}':
                pos += 1
                return result
            elif text[pos] == ',':
                pos += 1
                skip_ws()
                if pos < len(text) and text[pos] == '}':
                    raise ValueError("Trailing comma in object")
            else:
                raise ValueError("Expected ',' or '}'")
    
    try:
        value = parse_value()
        skip_ws()
        if pos != len(text):
            return None
        return value
    except (ValueError, IndexError):
        return None
