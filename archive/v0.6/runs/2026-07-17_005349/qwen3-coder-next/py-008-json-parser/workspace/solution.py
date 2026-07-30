def parse(text: str):
    """
    Parse a JSON document and return the equivalent Python object.
    Returns None if the input is not valid JSON.
    """
    if not isinstance(text, str):
        return None
    
    i = 0
    n = len(text)
    
    def skip_whitespace():
        nonlocal i
        while i < n and text[i] in ' \t\n\r':
            i += 1
    
    def peek():
        if i < n:
            return text[i]
        return None
    
    def consume(expected):
        nonlocal i
        if i >= n or text[i] != expected:
            return False
        i += 1
        return True
    
    def parse_string():
        nonlocal i
        if peek() != '"':
            return None
        
        i += 1  # consume opening quote
        result = []
        
        while i < n:
            c = text[i]
            
            if c == '"':
                i += 1  # consume closing quote
                return ''.join(result)
            
            if c == '\\':
                i += 1  # consume backslash
                
                if i >= n:
                    return None
                
                escape_char = text[i]
                
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
                    # Parse unicode escape
                    i += 1
                    if i + 3 >= n:
                        return None
                    
                    hex_digits = text[i:i+4]
                    
                    # Check that all characters are valid hex digits
                    for digit in hex_digits:
                        if digit not in '0123456789abcdefABCDEF':
                            return None
                    
                    try:
                        code_point = int(hex_digits, 16)
                        
                        # Handle surrogate pairs for characters outside BMP
                        if 0xD800 <= code_point <= 0xDBFF:  # High surrogate
                            i += 4  # Move past the first surrogate
                            if i + 1 < n and text[i:i+2] == '\\u':
                                i += 2  # consume \u
                                if i + 3 >= n:
                                    return None
                                
                                next_hex = text[i:i+4]
                                for digit in next_hex:
                                    if digit not in '0123456789abcdefABCDEF':
                                        return None
                                
                                try:
                                    low_surrogate = int(next_hex, 16)
                                    if 0xDC00 <= low_surrogate <= 0xDFFF:  # Low surrogate
                                        code_point = 0x10000 + ((code_point - 0xD800) << 10) + (low_surrogate - 0xDC00)
                                        result.append(chr(code_point))
                                        i += 4
                                    else:
                                        return None
                                except ValueError:
                                    return None
                            else:
                                return None
                        else:
                            result.append(chr(code_point))
                    except (ValueError, OverflowError):
                        return None
                else:
                    # Invalid escape sequence
                    return None
                
                i += 1
            elif ord(c) < 0x20:
                # Control characters are not allowed in strings
                return None
            else:
                result.append(c)
                i += 1
        
        # Unterminated string
        return None
    
    def parse_number():
        nonlocal i
        start = i
        
        # Optional negative sign
        if peek() == '-':
            i += 1
        
        # Integer part
        if i >= n:
            return None
        
        c = peek()
        
        # Must start with a digit or just '-' (invalid)
        if not c.isdigit():
            return None
        
        # Handle leading zeros
        if c == '0':
            i += 1
            # After a zero, we can only have '.', 'e', 'E' or nothing
            next_char = peek()
            if next_char is not None and next_char.isdigit():
                return None  # Leading zero like 007
        else:
            while i < n and text[i].isdigit():
                i += 1
        
        # Fractional part
        is_float = False
        if peek() == '.':
            is_float = True
            i += 1
            
            if i >= n or not text[i].isdigit():
                return None
            
            while i < n and text[i].isdigit():
                i += 1
        
        # Exponent part
        if peek() in ('e', 'E'):
            is_float = True
            i += 1
            
            if i < n and text[i] in '+-':
                i += 1
            
            if i >= n or not text[i].isdigit():
                return None
            
            while i < n and text[i].isdigit():
                i += 1
        
        num_str = text[start:i]
        
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            return None
    
    def parse_literal():
        nonlocal i
        skip_whitespace()
        
        # Check for true, false, null
        if text[i:i+4] == 'true':
            i += 4
            return True
        
        if text[i:i+5] == 'false':
            i += 5
            return False
        
        if text[i:i+4] == 'null':
            i += 4
            return None
        
        return None
    
    def parse_value():
        nonlocal i
        skip_whitespace()
        
        c = peek()
        
        # String
        if c == '"':
            return parse_string()
        
        # Object
        if c == '{':
            return parse_object()
        
        # Array
        if c == '[':
            return parse_array()
        
        # Number
        if c in '0123456789-':
            return parse_number()
        
        # Literal (true, false, null)
        if c in 'tfn':
            return parse_literal()
        
        return None
    
    def parse_object():
        nonlocal i
        result = {}
        
        i += 1  # consume opening brace
        
        while True:
            skip_whitespace()
            
            # Check for closing brace
            if peek() == '}':
                i += 1
                return result
            
            # Parse key (must be a string)
            key = parse_string()
            if key is None:
                return None
            
            skip_whitespace()
            
            # Expect colon
            if not consume(':'):
                return None
            
            skip_whitespace()
            
            # Parse value
            value = parse_value()
            if value is None and peek() != '}':
                return None
            
            result[key] = value
            
            skip_whitespace()
            
            # Check for comma or closing brace
            c = peek()
            if c == ',':
                i += 1
            elif c != '}':
                return None
    
    def parse_array():
        nonlocal i
        result = []
        
        i += 1  # consume opening bracket
        
        while True:
            skip_whitespace()
            
            # Check for closing bracket
            if peek() == ']':
                i += 1
                return result
            
            # Parse value
            value = parse_value()
            if value is None and peek() != ']':
                return None
            
            result.append(value)
            
            skip_whitespace()
            
            # Check for comma or closing bracket
            c = peek()
            if c == ',':
                i += 1
            elif c != ']':
                return None
    
    # Start parsing
    skip_whitespace()
    
    if i >= n:
        return None
    
    result = parse_value()
    
    if result is None:
        return None
    
    # Check for trailing content
    skip_whitespace()
    
    if i < n:
        return None
    
    return result
