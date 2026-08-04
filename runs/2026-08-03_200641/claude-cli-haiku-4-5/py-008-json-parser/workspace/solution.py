def parse(text: str):
    pos = 0
    
    def skip_whitespace():
        nonlocal pos
        while pos < len(text) and text[pos] in ' \t\n\r':
            pos += 1
    
    def parse_value():
        nonlocal pos
        skip_whitespace()
        
        if pos >= len(text):
            return None, False
        
        ch = text[pos]
        
        if ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch == '"':
            return parse_string()
        elif ch == 't':
            if text[pos:pos+4] == 'true':
                pos += 4
                return True, True
            return None, False
        elif ch == 'f':
            if text[pos:pos+5] == 'false':
                pos += 5
                return False, True
            return None, False
        elif ch == 'n':
            if text[pos:pos+4] == 'null':
                pos += 4
                return None, True
            return None, False
        elif ch == '-' or ch.isdigit():
            return parse_number()
        else:
            return None, False
    
    def parse_object():
        nonlocal pos
        pos += 1
        skip_whitespace()
        
        obj = {}
        
        if pos < len(text) and text[pos] == '}':
            pos += 1
            return obj, True
        
        while True:
            skip_whitespace()
            
            if pos >= len(text) or text[pos] != '"':
                return None, False
            
            key, success = parse_string()
            if not success or not isinstance(key, str):
                return None, False
            
            skip_whitespace()
            
            if pos >= len(text) or text[pos] != ':':
                return None, False
            pos += 1
            
            value, success = parse_value()
            if not success:
                return None, False
            
            obj[key] = value
            
            skip_whitespace()
            
            if pos >= len(text):
                return None, False
            
            if text[pos] == '}':
                pos += 1
                return obj, True
            elif text[pos] == ',':
                pos += 1
                skip_whitespace()
                if pos < len(text) and text[pos] == '}':
                    return None, False
            else:
                return None, False
    
    def parse_array():
        nonlocal pos
        pos += 1
        skip_whitespace()
        
        arr = []
        
        if pos < len(text) and text[pos] == ']':
            pos += 1
            return arr, True
        
        while True:
            value, success = parse_value()
            if not success:
                return None, False
            
            arr.append(value)
            
            skip_whitespace()
            
            if pos >= len(text):
                return None, False
            
            if text[pos] == ']':
                pos += 1
                return arr, True
            elif text[pos] == ',':
                pos += 1
                skip_whitespace()
                if pos < len(text) and text[pos] == ']':
                    return None, False
            else:
                return None, False
    
    def parse_string():
        nonlocal pos
        if pos >= len(text) or text[pos] != '"':
            return None, False
        
        pos += 1
        result = []
        
        while pos < len(text):
            ch = text[pos]
            
            if ch == '"':
                pos += 1
                return ''.join(result), True
            elif ch == '\\':
                pos += 1
                if pos >= len(text):
                    return None, False
                
                escape_ch = text[pos]
                if escape_ch == '"':
                    result.append('"')
                    pos += 1
                elif escape_ch == '\\':
                    result.append('\\')
                    pos += 1
                elif escape_ch == '/':
                    result.append('/')
                    pos += 1
                elif escape_ch == 'b':
                    result.append('\b')
                    pos += 1
                elif escape_ch == 'f':
                    result.append('\f')
                    pos += 1
                elif escape_ch == 'n':
                    result.append('\n')
                    pos += 1
                elif escape_ch == 'r':
                    result.append('\r')
                    pos += 1
                elif escape_ch == 't':
                    result.append('\t')
                    pos += 1
                elif escape_ch == 'u':
                    pos += 1
                    if pos + 3 >= len(text):
                        return None, False
                    hex_str = text[pos:pos+4]
                    try:
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        pos += 4
                    except (ValueError, OverflowError):
                        return None, False
                else:
                    return None, False
            elif ord(ch) < 0x20:
                return None, False
            else:
                result.append(ch)
                pos += 1
        
        return None, False
    
    def parse_number():
        nonlocal pos
        start = pos
        
        if pos < len(text) and text[pos] == '-':
            pos += 1
        
        if pos >= len(text) or not text[pos].isdigit():
            return None, False
        
        if text[pos] == '0':
            pos += 1
            if pos < len(text) and text[pos].isdigit():
                return None, False
        else:
            while pos < len(text) and text[pos].isdigit():
                pos += 1
        
        is_float = False
        
        if pos < len(text) and text[pos] == '.':
            is_float = True
            pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                return None, False
            while pos < len(text) and text[pos].isdigit():
                pos += 1
        
        if pos < len(text) and text[pos] in 'eE':
            is_float = True
            pos += 1
            if pos < len(text) and text[pos] in '+-':
                pos += 1
            if pos >= len(text) or not text[pos].isdigit():
                return None, False
            while pos < len(text) and text[pos].isdigit():
                pos += 1
        
        num_str = text[start:pos]
        try:
            if is_float:
                return float(num_str), True
            else:
                return int(num_str), True
        except ValueError:
            return None, False
    
    value, success = parse_value()
    if not success:
        return None
    
    skip_whitespace()
    if pos != len(text):
        return None
    
    return value
