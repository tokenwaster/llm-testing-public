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
            return None
        
        char = text[pos]
        
        if char == '{':
            return parse_object()
        elif char == '[':
            return parse_array()
        elif char == '"':
            return parse_string()
        elif char == 't' or char == 'f':
            return parse_boolean()
        elif char == 'n':
            return parse_null()
        elif char == '-' or char.isdigit():
            return parse_number()
        else:
            return None
    
    def parse_object():
        skip_whitespace()
        if text[pos] != '{':
            return None
        pos += 1
        skip_whitespace()
        
        result = {}
        
        while True:
            skip_whitespace()
            if text[pos] == '}':
                pos += 1
                break
            
            if text[pos] != '"':
                return None
            
            key = parse_string()
            if key is None:
                return None
            
            skip_whitespace()
            if text[pos] != ':':
                return None
            pos += 1
            skip_whitespace()
            
            value = parse_value()
            if value is None:
                return None
            
            result[key] = value
            
            skip_whitespace()
            if text[pos] == '}':
                pos += 1
                break
            elif text[pos] != ',':
                return None
            pos += 1
        
        skip_whitespace()
        if pos < length:
            return None
        
        return result
    
    def parse_array():
        skip_whitespace()
        if text[pos] != '[':
            return None
        pos += 1
        skip_whitespace()
        
        result = []
        
        while True:
            skip_whitespace()
            if text[pos] == ']':
                pos += 1
                break
            
            value = parse_value()
            if value is None:
                return None
            
            result.append(value)
            
            skip_whitespace()
            if text[pos] == ']':
                pos += 1
                break
            elif text[pos] != ',':
                return None
            pos += 1
        
        skip_whitespace()
        if pos < length:
            return None
        
        return result
    
    def parse_string():
        skip_whitespace()
        if text[pos] != '"':
            return None
        pos += 1
        
        result = []
        
        while True:
            if pos >= length:
                return None
            
            char = text[pos]
            
            if char == '"':
                pos += 1
                return ''.join(result)
            
            elif char == '\\':
                pos += 1
                if pos >= length:
                    return None
                
                escape_char = text[pos]
                pos += 1
                
                if escape_char == '"':
                    result.append('"')
                elif escape_char == '\\':
                    result.append('\\')
                elif escape_char == '/':
                    result.append('/')
                elif escape_char == 'b':
                    result.append('\b')
                elif escape_char == 'f':
                    result.append('\f')
                elif escape_char == 'n':
                    result.append('\n')
                elif escape_char == 'r':
                    result.append('\r')
                elif escape_char == 't':
                    result.append('\t')
                elif escape_char == 'u':
                    if pos + 4 > length:
                        return None
                    hex_str = text[pos+1:pos+5]
                    try:
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        pos += 4
                    except ValueError:
                        return None
                else:
                    return None
            
            else:
                result.append(char)
                pos += 1
        
        return ''.join(result)
    
    def parse_number():
        skip_whitespace()
        
        start = pos
        
        if text[pos] == '-':
            pos += 1
        
        if pos >= length or not text[pos].isdigit():
            return None
        
        while pos < length and text[pos].isdigit():
            pos += 1
        
        has_decimal = False
        if pos < length and text[pos] == '.':
            has_decimal = True
            pos += 1
            
            if pos >= length or not text[pos].isdigit():
                return None
            
            while pos < length and text[pos].isdigit():
                pos += 1
        
        has_exponent = False
        if pos < length and text[pos] in 'eE':
            has_exponent = True
            pos += 1
            
            if pos < length and text[pos] in '+-':
                pos += 1
            
            if pos >= length or not text[pos].isdigit():
                return None
            
            while pos < length and text[pos].isdigit():
                pos += 1
        
        number_str = text[start:pos]
        
        try:
            if not has_decimal and not has_exponent:
                if len(number_str) > 1 and number_str[0] == '0':
                    return None
            
            if has_decimal or has_exponent:
                return float(number_str)
            else:
                return int(number_str)
        except ValueError:
            return None
    
    def parse_boolean():
        skip_whitespace()
        
        if text[pos:pos+4] == 'true':
            pos += 4
            return True
        
        elif text[pos:pos+5] == 'false':
            pos += 5
            return False
        
        return None
    
    def parse_null():
        skip_whitespace()
        
        if text[pos:pos+4] == 'null':
            pos += 4
            return None
        
        return None
    
    result = parse_value()
    
    skip_whitespace()
    if pos < length:
        return None
    
    return result
