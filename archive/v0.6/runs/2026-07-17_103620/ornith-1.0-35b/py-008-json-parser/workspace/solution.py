def parse(text: str):
    _FAIL = object()  # sentinel to distinguish None (JSON null) from failure
    
    pos = [0]
    
    def skip_ws():
        while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
            pos[0] += 1
    
    def peek():
        if pos[0] < len(text):
            return text[pos[0]]
        return None
    
    def advance():
        ch = text[pos[0]]
        pos[0] += 1
        return ch
    
    def parse_string():
        # consume opening "
        assert advance() == '"'
        result = []
        while True:
            if pos[0] >= len(text):
                return _FAIL  # unterminated string
            ch = text[pos[0]]
            if ch == '"':
                advance()
                return ''.join(result)
            elif ch == '\\':
                advance()  # consume backslash
                if pos[0] >= len(text):
                    return _FAIL
                esc = text[pos[0]]
                advance()
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
                    # \uXXXX - need exactly 4 hex digits
                    if pos[0] + 4 > len(text):
                        return _FAIL
                    hex_str = text[pos[0]:pos[0] + 4]
                    pos[0] += 4
                    try:
                        cp = int(hex_str, 16)
                    except ValueError:
                        return _FAIL
                    result.append(chr(cp))
                else:
                    return _FAIL  # invalid escape character
            elif ord(ch) < 0x20:
                # unescaped control characters not allowed in strings
                return _FAIL
            else:
                result.append(ch)
                advance()
    
    def parse_number():
        start = pos[0]
        
        # optional minus sign
        if peek() == '-':
            advance()
        
        if pos[0] >= len(text):
            return _FAIL
        
        # integer part
        if peek() == '0':
            advance()
            # no leading zeros (except 0 itself)
            if pos[0] < len(text) and text[pos[0]].isdigit():
                return _FAIL
        elif peek() and peek().isdigit():
            while pos[0] < len(text) and text[pos[0]].isdigit():
                advance()
        else:
            return _FAIL
        
        is_float = False
        
        # fraction part
        if pos[0] < len(text) and text[pos[0]] == '.':
            is_float = True
            advance()
            if pos[0] >= len(text) or not text[pos[0]].isdigit():
                return _FAIL
            while pos[0] < len(text) and text[pos[0]].isdigit():
                advance()
        
        # exponent part
        if pos[0] < len(text) and text[pos[0]] in 'eE':
            is_float = True
            advance()
            if pos[0] < len(text) and text[pos[0]] in '+-':
                advance()
            if pos[0] >= len(text) or not text[pos[0]].isdigit():
                return _FAIL
            while pos[0] < len(text) and text[pos[0]].isdigit():
                advance()
        
        num_str = text[start:pos[0]]
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            return _FAIL
    
    def parse_value():
        skip_ws()
        ch = peek()
        
        if ch == '"':
            return parse_string()
        elif ch in '-0123456789':
            return parse_number()
        elif ch == 't':
            # true
            end = pos[0] + 4
            if text[pos[0]:end] == 'true' and (end >= len(text) or not _is_ident_char(text[end])):
                pos[0] = end
                return True
            return _FAIL
        elif ch == 'f':
            # false
            end = pos[0] + 5
            if text[pos[0]:end] == 'false' and (end >= len(text) or not _is_ident_char(text[end])):
                pos[0] = end
                return False
            return _FAIL
        elif ch == 'n':
            # null -> Python None
            end = pos[0] + 4
            if text[pos[0]:end] == 'null' and (end >= len(text) or not _is_ident_char(text[end])):
                pos[0] = end
                return None
            return _FAIL
        elif ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        else:
            return _FAIL
    
    def _is_ident_char(c):
        return c.isalnum() or c == '_'
    
    def parse_object():
        advance()  # consume {
        skip_ws()
        
        if peek() == '}':
            advance()
            return {}
        
        result = {}
        while True:
            skip_ws()
            key = parse_string()
            if key is _FAIL:
                return _FAIL
            
            skip_ws()
            if peek() != ':':
                return _FAIL
            advance()  # consume :
            
            value = parse_value()
            if value is _FAIL:
                return _FAIL
            
            result[key] = value
            
            skip_ws()
            ch = peek()
            if ch == ',':
                advance()
                skip_ws()
                if peek() == '}':
                    return _FAIL  # trailing comma not allowed
            elif ch == '}':
                advance()
                return result
            else:
                return _FAIL
    
    def parse_array():
        advance()  # consume [
        skip_ws()
        
        if peek() == ']':
            advance()
            return []
        
        result = []
        while True:
            value = parse_value()
            if value is _FAIL:
                return _FAIL
            
            result.append(value)
            
            skip_ws()
            ch = peek()
            if ch == ',':
                advance()
                skip_ws()
                if peek() == ']':
                    return _FAIL  # trailing comma not allowed
            elif ch == ']':
                advance()
                return result
            else:
                return _FAIL
    
    # Main entry point
    value = parse_value()
    if value is _FAIL:
        return None
    
    skip_ws()
    if pos[0] != len(text):
        return None  # trailing garbage after document
    
    return value
