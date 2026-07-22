def parse(text: str):
    pos = 0
    length = len(text)
    
    def skip_whitespace():
        nonlocal pos
        while pos < length and text[pos] in ' \t\n\r':
            pos += 1
    
    def peek():
        return text[pos] if pos < length else None
    
    def advance():
        nonlocal pos
        if pos < length:
            ch = text[pos]
            pos += 1
            return ch
        return None
    
    def parse_value():
        skip_whitespace()
        if peek() == '{':
            return parse_object()
        elif peek() == '[':
            return parse_array()
        elif peek() == '"':
            return parse_string()
        else:
            # Try to parse a number or literal
            ch = advance()
            if ch is None:
                return None
            
            # Check for negative sign at start
            if ch == '-':
                ch = advance()
            
            # Parse number
            if ch and (ch.isdigit() or ch in 'eE'):
                return parse_number()
            
            # Check for literals
            word = ""
            while peek() and (peek().isalnum() or peek() == '_'):
                word += advance()
            
            if word == 'true':
                return True
            elif word == 'false':
                return False
            elif word == 'null':
                return None
            else:
                # Invalid token
                return None
    
    def parse_object():
        nonlocal pos
        obj = {}
        skip_whitespace()
        if peek() != '{':
            return None
        advance()  # consume '{'
        skip_whitespace()
        
        if peek() == '}':
            advance()
            return obj
        
        while True:
            skip_whitespace()
            if peek() != '"':
                return None
            
            key = parse_string()
            if key is None:
                return None
            
            skip_whitespace()
            if peek() != ':':
                return None
            advance()  # consume ':'
            
            skip_whitespace()
            value = parse_value()
            if value is None:
                return None
            
            obj[key] = value
            
            skip_whitespace()
            ch = peek()
            if ch == '}':
                advance()
                break
            elif ch == ',':
                advance()
            else:
                return None
        
        # Check for trailing content after object
        skip_whitespace()
        if pos < length and text[pos] != '}':
            return None
        
        return obj
    
    def parse_array():
        nonlocal pos
        arr = []
        skip_whitespace()
        if peek() != '[':
            return None
        advance()  # consume '['
        skip_whitespace()
        
        if peek() == ']':
            advance()
            return arr
        
        while True:
            value = parse_value()
            if value is None:
                return None
            
            arr.append(value)
            
            skip_whitespace()
            ch = peek()
            if ch == ']':
                advance()
                break
            elif ch == ',':
                advance()
            else:
                return None
        
        # Check for trailing content after array
        skip_whitespace()
        if pos < length and text[pos] != ']':
            return None
        
        return arr
    
    def parse_string():
        nonlocal pos
        skip_whitespace()
        if peek() != '"':
            return None
        advance()  # consume opening '"'
        
        result = []
        while True:
            ch = advance()
            if ch is None:
                return None
            
            if ch == '"':
                return ''.join(result)
            
            elif ch == '\\':
                next_ch = advance()
                if next_ch is None:
                    return None
                
                escape_map = {
                    '"': '"',
                    '\\': '\\',
                    '/': '/',
                    'b': '\b',
                    'f': '\f',
                    'n': '\n',
                    'r': '\r',
                    't': '\t',
                    'u': None  # unicode escape
                }
                
                if next_ch in escape_map:
                    result.append(escape_map[next_ch])
                elif next_ch == 'u':
                    # Unicode escape \uXXXX
                    hex_str = ""
                    for _ in range(4):
                        ch = advance()
                        if ch is None or not ch.isdigit():
                            return None
                        hex_str += ch
                    
                    code_point = int(hex_str, 16)
                    result.append(chr(code_point))
                else:
                    return None
            
            elif ch == '\n' or ch == '\r':
                # Unterminated string (newline in string is not allowed without escape)
                return None
            else:
                result.append(ch)
        
        return ''.join(result)
    
    def parse_number():
        nonlocal pos
        num_str = ""
        
        # Optional minus sign at start of number
        if peek() == '-':
            num_str += advance()
        
        # Must have digits for integer part
        if peek() is None or not peek().isdigit():
            return None
        
        while peek() and peek().isdigit():
            num_str += advance()
        
        # Check for decimal point
        if peek() == '.':
            num_str += advance()
            
            # Must have digits after decimal point
            if peek() is None or not peek().isdigit():
                return None
            
            while peek() and peek().isdigit():
                num_str += advance()
        
        # Check for exponent
        if peek() in 'eE':
            num_str += advance()
            
            # Optional sign
            if peek() in '+-':
                num_str += advance()
            
            # Must have digits after exponent
            if peek() is None or not peek().isdigit():
                return None
            
            while peek() and peek().isdigit():
                num_str += advance()
        
        try:
            if '.' in num_str or 'e' in num_str.lower():
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            return None
    
    # Parse the value
    result = parse_value()
    
    # Check for trailing content
    skip_whitespace()
    if pos < length:
        return None
    
    return result
