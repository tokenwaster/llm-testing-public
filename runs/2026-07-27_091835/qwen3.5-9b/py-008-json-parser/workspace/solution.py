def parse(text: str):
    """
    Parse a JSON document and return the equivalent Python object.
    Returns None if input is not valid JSON.
    """
    
    # Handle empty or whitespace-only strings as invalid JSON (nothing to parse)
    if not text.strip():
        return None
    
    pos = [0]
    n = len(text)
    
    def peek():
        if pos[0] < n:
            return text[pos[0]]
        return '\x00'
    
    def advance():
        c = peek()
        if c != '\x00':
            pos[0] += 1
        return c
    
    def skip_ws():
        while pos[0] < n and text[pos[0]] in ' \t\n\r':
            advance()
    
    # Parse a number (int or float with optional exponent)
    def parse_number():
        start = pos[0]
        
        # Optional minus sign
        if peek() == '-':
            advance()
        
        # Must have at least one digit
        if not peek().isdigit():
            return None
        
        while peek().isdigit():
            advance()
        
        num_start = start
        has_decimal = False
        has_exp = False
        
        if peek() == '.':
            advance()  # consume '.'
            
            if not peek().isdigit():
                return None
            
            while peek().isdigit():
                advance()
            
            num_start -= 1  # Include the decimal point in string
            has_decimal = True
        
        if peek() in 'eE':
            advance()
            has_exp = True
            
            if peek() and peek() in '+-':
                advance()
            
            if not peek().isdigit():
                return None
            
            while peek().isdigit():
                advance()
        
        num_str = text[num_start:pos[0]]
        
        try:
            val = float(num_str)
            
            # Integer check: must have no fractional part and no exponent
            if not has_decimal and not has_exp:
                int_val = int(val)
                if val == float(int_val):
                    return int_val
            
            return val
        except (ValueError, OverflowError):
            return None
    
    # Parse a string with escape sequences
    def parse_string():
        advance()  # consume opening quote
        
        result = []
        
        while pos[0] < n:
            c = peek()
            
            if c == '"':
                advance()  # consume closing quote
                return ''.join(result)
            
            elif c == '\\':
                advance()  # consume backslash
                
                next_c = peek()
                
                if not next_c:
                    return None
                
                # Handle standard escapes
                if next_c in '"\\/\bfnrt':
                    escape_map = {
                        '"': '"',
                        '\\': '\\',
                        '/': '/',
                        'b': '\b',
                        'f': '\f',
                        'n': '\n',
                        'r': '\r',
                        't': '\t'
                    }
                    result.append(escape_map[next_c])
                elif next_c == 'u':
                    # Unicode escape \uXXXX
                    if pos[0] + 4 < n:
                        hex_str = text[pos[0]+1:pos[0]+5]
                        advance()  # consume 'u'
                        
                        try:
                            char_code = int(hex_str, 16)
                            result.append(chr(char_code))
                        except (ValueError, OverflowError):
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                result.append(c)
                advance()
        
        # Unterminated string
        return None
    
    # Parse an object { ... }
    def parse_object():
        skip_ws()
        
        if peek() != '{':
            return None
        
        advance()  # consume opening brace
        
        result = {}
        
        while True:
            skip_ws()
            
            c = peek()
            
            if c == '}':
                advance()  # consume closing brace
                return result
            
            elif c != '"':
                return None  # Keys must be strings
            
            key = parse_string()
            
            if key is None:
                return None
            
            skip_ws()
            
            if peek() != ':':
                return None
            advance()  # consume colon
            
            value = parse_value()
            
            if value is None:
                return None
            
            result[key] = value
            skip_ws()
            
            c = peek()
            if c == ',':
                advance()
                skip_ws()
            elif c != '}':
                return None
    
    # Parse an array [ ... ]
    def parse_array():
        skip_ws()
        
        if peek() != '[':
            return None
        
        advance()  # consume opening bracket
        
        result = []
        
        while True:
            value = parse_value()
            
            if value is None:
                return None
            
            result.append(value)
            
            skip_ws()
            
            c = peek()
            if c == ',':
                advance()
                skip_ws()
            elif c != ']':
                return None
            else:
                advance()  # consume closing bracket
                return result
    
    def parse_value():
        skip_ws()
        
        c = peek()
        
        if c == '"':
            return parse_string()
        elif c == '{':
            return parse_object()
        elif c == '[':
            return parse_array()
        elif c == '-' and pos[0] < n:
            advance()  # consume minus
            if not peek().isdigit():
                return None
            return parse_number()
        elif c in 'tfn':
            word_start = pos[0]
            
            # Read the complete keyword (letters only)
            valid_cont = set('ruelseulnulll')
            while pos[0] < n and text[pos[0]] in valid_cont:
                advance()
            
            if word_start == pos[0]:
                return None  # Invalid start for literal
            
            word = text[word_start:pos[0]]
            
            if c == 't' and word == 'true':
                return True
            elif c == 'f' and word == 'false':
                return False
            elif c == 'n' and word == 'null':
                return None
        
        # Any other character is invalid JSON start
        return None
    
    # Parse initial value
    result = parse_value()
    
    if result is None:
        return None
    
    # Check for trailing content after valid JSON
    skip_ws()
    
    if pos[0] < n:
        return None  # Trailing garbage detected
    
    return result
