def parse(text: str):
    pos = 0
    length = len(text)

    def skip_whitespace():
        nonlocal pos
        while pos < length and text[pos] in ' \t\n\r':
            pos += 1

    def parse_value():
        skip_whitespace()
        if pos >= length:
            return None, False
        
        c = text[pos]
        
        if c == '"':
            return parse_string()
        elif c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == 't':
            return parse_true()
        elif c == 'f':
            return parse_false()
        elif c == 'n':
            return parse_null()
        elif c == '-' or c.isdigit():
            return parse_number()
        else:
            return None, False

    def parse_string():
        nonlocal pos
        if pos >= length or text[pos] != '"':
            return None, False
        pos += 1  # skip opening quote
        result = []
        while pos < length:
            c = text[pos]
            if c == '"':
                pos += 1  # skip closing quote
                return ''.join(result), True
            elif c == '\\':
                pos += 1
                if pos >= length:
                    return None, False
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
                    if pos + 4 > length:
                        return None, False
                    hex_str = text[pos:pos+4]
                    if not all(h in '0123456789abcdefABCDEF' for h in hex_str):
                        return None, False
                    code_point = int(hex_str, 16)
                    # Handle surrogate pairs
                    if 0xD800 <= code_point <= 0xDBFF:
                        pos += 4
                        if pos + 2 > length or text[pos] != '\\' or text[pos+1] != 'u':
                            return None, False
                        pos += 2
                        if pos + 4 > length:
                            return None, False
                        hex_str2 = text[pos:pos+4]
                        if not all(h in '0123456789abcdefABCDEF' for h in hex_str2):
                            return None, False
                        code_point2 = int(hex_str2, 16)
                        if not (0xDC00 <= code_point2 <= 0xDFFF):
                            return None, False
                        full_code = 0x10000 + (code_point - 0xD800) * 0x400 + (code_point2 - 0xDC00)
                        result.append(chr(full_code))
                        pos += 4
                        continue
                    else:
                        result.append(chr(code_point))
                    pos += 4
                    continue
                else:
                    return None, False
                pos += 1
            elif ord(c) < 0x20:
                # Control characters not allowed unescaped
                return None, False
            else:
                result.append(c)
                pos += 1
        return None, False  # Unterminated string

    def parse_object():
        nonlocal pos
        if pos >= length or text[pos] != '{':
            return None, False
        pos += 1  # skip '{'
        result = {}
        skip_whitespace()
        if pos < length and text[pos] == '}':
            pos += 1
            return result, True
        
        first = True
        while pos < length:
            skip_whitespace()
            if not first:
                if pos >= length or text[pos] != ',':
                    return None, False
                pos += 1  # skip ','
                skip_whitespace()
            first = False
            
            # Check for trailing comma
            if pos < length and text[pos] == '}':
                return None, False  # trailing comma
            
            # Parse key
            if pos >= length or text[pos] != '"':
                return None, False
            key, ok = parse_string()
            if not ok:
                return None, False
            
            skip_whitespace()
            if pos >= length or text[pos] != ':':
                return None, False
            pos += 1  # skip ':'
            
            value, ok = parse_value()
            if not ok:
                return None, False
            
            result[key] = value
            
            skip_whitespace()
            if pos < length and text[pos] == '}':
                pos += 1
                return result, True
        
        return None, False  # Unterminated object

    def parse_array():
        nonlocal pos
        if pos >= length or text[pos] != '[':
            return None, False
        pos += 1  # skip '['
        result = []
        skip_whitespace()
        if pos < length and text[pos] == ']':
            pos += 1
            return result, True
        
        first = True
        while pos < length:
            skip_whitespace()
            if not first:
                if pos >= length or text[pos] != ',':
                    return None, False
                pos += 1  # skip ','
                skip_whitespace()
            first = False
            
            # Check for trailing comma
            if pos < length and text[pos] == ']':
                return None, False  # trailing comma
            
            value, ok = parse_value()
            if not ok:
                return None, False
            
            result.append(value)
            
            skip_whitespace()
            if pos < length and text[pos] == ']':
                pos += 1
                return result, True
        
        return None, False  # Unterminated array

    def parse_true():
        nonlocal pos
        if text[pos:pos+4] == 'true':
            pos += 4
            return True, True
        return None, False

    def parse_false():
        nonlocal pos
        if text[pos:pos+5] == 'false':
            pos += 5
            return False, True
        return None, False

    def parse_null():
        nonlocal pos
        if text[pos:pos+4] == 'null':
            pos += 4
            return None, True
        return None, False

    def parse_number():
        nonlocal pos
        start = pos
        is_float = False
        
        # Optional negative sign
        if pos < length and text[pos] == '-':
            pos += 1
        
        if pos >= length or not text[pos].isdigit():
            pos = start
            return None, False
        
        # Integer part
        if text[pos] == '0':
            pos += 1
            # After leading zero, must be '.', 'e', 'E', or end
            if pos < length and text[pos].isdigit():
                pos = start
                return None, False
        else:
            while pos < length and text[pos].isdigit():
                pos += 1
        
        # Fractional part
        if pos < length and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= length or not text[pos].isdigit():
                pos = start
                return None, False
            while pos < length and text[pos].isdigit():
                pos += 1
        
        # Exponent part
        if pos < length and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < length and text[pos] in '+-':
                pos += 1
            if pos >= length or not text[pos].isdigit():
                pos = start
                return None, False
            while pos < length and text[pos].isdigit():
                pos += 1
        
        num_str = text[start:pos]
        try:
            if is_float:
                return float(num_str), True
            else:
                return int(num_str), True
        except ValueError:
            pos = start
            return None, False

    value, ok = parse_value()
    if not ok:
        return None
    
    skip_whitespace()
    if pos != length:
        return None  # Trailing garbage
    
    return value
