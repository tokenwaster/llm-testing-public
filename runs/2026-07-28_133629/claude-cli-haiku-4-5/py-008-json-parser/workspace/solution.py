def parse(text: str):
    class ParseError(Exception):
        pass
    
    pos = [0]
    
    def skip_whitespace():
        while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
            pos[0] += 1
    
    def parse_value():
        skip_whitespace()
        if pos[0] >= len(text):
            raise ParseError("Unexpected end of input")
        
        c = text[pos[0]]
        
        if c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '"':
            return parse_string()
        elif c == 't':
            return parse_true()
        elif c == 'f':
            return parse_false()
        elif c == 'n':
            return parse_null()
        elif c == '-' or c.isdigit():
            return parse_number()
        else:
            raise ParseError(f"Unexpected character: {c}")
    
    def parse_object():
        obj = {}
        pos[0] += 1
        skip_whitespace()
        
        if pos[0] < len(text) and text[pos[0]] == '}':
            pos[0] += 1
            return obj
        
        while True:
            skip_whitespace()
            
            if pos[0] >= len(text) or text[pos[0]] != '"':
                raise ParseError("Expected string key in object")
            
            key = parse_string()
            
            skip_whitespace()
            
            if pos[0] >= len(text) or text[pos[0]] != ':':
                raise ParseError("Expected ':' in object")
            pos[0] += 1
            
            value = parse_value()
            obj[key] = value
            
            skip_whitespace()
            
            if pos[0] >= len(text):
                raise ParseError("Unterminated object")
            
            if text[pos[0]] == '}':
                pos[0] += 1
                return obj
            elif text[pos[0]] == ',':
                pos[0] += 1
            else:
                raise ParseError("Expected ',' or '}' in object")
    
    def parse_array():
        arr = []
        pos[0] += 1
        skip_whitespace()
        
        if pos[0] < len(text) and text[pos[0]] == ']':
            pos[0] += 1
            return arr
        
        while True:
            value = parse_value()
            arr.append(value)
            
            skip_whitespace()
            
            if pos[0] >= len(text):
                raise ParseError("Unterminated array")
            
            if text[pos[0]] == ']':
                pos[0] += 1
                return arr
            elif text[pos[0]] == ',':
                pos[0] += 1
            else:
                raise ParseError("Expected ',' or ']' in array")
    
    def parse_string():
        if pos[0] >= len(text) or text[pos[0]] != '"':
            raise ParseError("Expected string")
        
        pos[0] += 1
        result = []
        
        while pos[0] < len(text):
            c = text[pos[0]]
            
            if c == '"':
                pos[0] += 1
                return ''.join(result)
            elif c == '\\':
                pos[0] += 1
                if pos[0] >= len(text):
                    raise ParseError("Unterminated string escape")
                
                escape_char = text[pos[0]]
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
                    pos[0] += 1
                    if pos[0] + 4 > len(text):
                        raise ParseError("Invalid unicode escape")
                    hex_str = text[pos[0]:pos[0]+4]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ParseError("Invalid unicode escape")
                    code_point = int(hex_str, 16)
                    result.append(chr(code_point))
                    pos[0] += 3
                else:
                    raise ParseError(f"Invalid escape sequence: \\{escape_char}")
                
                pos[0] += 1
            else:
                result.append(c)
                pos[0] += 1
        
        raise ParseError("Unterminated string")
    
    def parse_number():
        start = pos[0]
        
        if pos[0] < len(text) and text[pos[0]] == '-':
            pos[0] += 1
        
        if pos[0] >= len(text) or not text[pos[0]].isdigit():
            raise ParseError("Invalid number")
        
        if text[pos[0]] == '0':
            pos[0] += 1
            if pos[0] < len(text) and text[pos[0]].isdigit():
                raise ParseError("Leading zeros not allowed")
        else:
            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1
        
        is_float = False
        
        if pos[0] < len(text) and text[pos[0]] == '.':
            is_float = True
            pos[0] += 1
            if pos[0] >= len(text) or not text[pos[0]].isdigit():
                raise ParseError("Invalid fractional part")
            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1
        
        if pos[0] < len(text) and text[pos[0]] in 'eE':
            is_float = True
            pos[0] += 1
            if pos[0] < len(text) and text[pos[0]] in '+-':
                pos[0] += 1
            if pos[0] >= len(text) or not text[pos[0]].isdigit():
                raise ParseError("Invalid exponent")
            while pos[0] < len(text) and text[pos[0]].isdigit():
                pos[0] += 1
        
        num_str = text[start:pos[0]]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)
    
    def parse_true():
        if text[pos[0]:pos[0]+4] == 'true':
            pos[0] += 4
            return True
        raise ParseError("Invalid literal")
    
    def parse_false():
        if text[pos[0]:pos[0]+5] == 'false':
            pos[0] += 5
            return False
        raise ParseError("Invalid literal")
    
    def parse_null():
        if text[pos[0]:pos[0]+4] == 'null':
            pos[0] += 4
            return None
        raise ParseError("Invalid literal")
    
    try:
        result = parse_value()
        skip_whitespace()
        
        if pos[0] != len(text):
            return None
        
        return result
    except ParseError:
        return None
