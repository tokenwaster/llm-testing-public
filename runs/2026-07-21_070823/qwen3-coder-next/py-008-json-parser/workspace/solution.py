def parse(text: str):
    """
    Parse a JSON document and return the equivalent Python object.
    Returns None if the input is not valid JSON.
    """
    if text is None:
        return None
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    if not text:
        return None
    
    pos = [0]  # Use list to allow modification in nested functions
    
    def peek():
        """Return current character without advancing position."""
        if pos[0] < len(text):
            return text[pos[0]]
        return None
    
    def advance():
        """Advance position by one and return the character."""
        ch = peek()
        pos[0] += 1
        return ch
    
    def skip_whitespace():
        """Skip whitespace characters."""
        while pos[0] < len(text) and text[pos[0]] in ' \t\n\r':
            pos[0] += 1
    
    def parse_value():
        """Parse any JSON value: object, array, string, number, true, false, null."""
        skip_whitespace()
        
        if peek() is None:
            return None
        
        ch = peek()
        
        if ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch == '"':
            return parse_string()
        elif ch in '0123456789-':
            return parse_number()
        elif text[pos[0]:pos[0]+4] == 'true':
            pos[0] += 4
            return True
        elif text[pos[0]:pos[0]+5] == 'false':
            pos[0] += 5
            return False
        elif text[pos[0]:pos[0]+4] == 'null':
            pos[0] += 4
            return None
        
        # Invalid starting character
        return None
    
    def parse_object():
        """Parse a JSON object."""
        result = {}
        
        if advance() != '{':
            return None
        
        skip_whitespace()
        
        # Handle empty object
        if peek() == '}':
            pos[0] += 1
            return result
        
        while True:
            skip_whitespace()
            
            # Parse key (must be a string)
            if peek() != '"':
                return None
            
            key = parse_string()
            if key is None:
                return None
            
            skip_whitespace()
            
            # Expect colon
            if advance() != ':':
                return None
            
            skip_whitespace()
            
            # Parse value
            value = parse_value()
            if value is None:
                return None
            
            result[key] = value
            
            skip_whitespace()
            
            ch = peek()
            if ch == '}':
                pos[0] += 1
                return result
            elif ch != ',':
                return None
            
            advance()  # consume comma
    
    def parse_array():
        """Parse a JSON array."""
        result = []
        
        if advance() != '[':
            return None
        
        skip_whitespace()
        
        # Handle empty array
        if peek() == ']':
            pos[0] += 1
            return result
        
        while True:
            skip_whitespace()
            
            value = parse_value()
            if value is None:
                return None
            
            result.append(value)
            
            skip_whitespace()
            
            ch = peek()
            if ch == ']':
                pos[0] += 1
                return result
            elif ch != ',':
                return None
            
            advance()  # consume comma
    
    def parse_string():
        """Parse a JSON string."""
        if advance() != '"':
            return None
        
        result = []
        
        while True:
            ch = peek()
            
            if ch is None:
                return None  # Unterminated string
            
            if ch == '"':
                pos[0] += 1
                return ''.join(result)
            
            if ch == '\\':
                advance()  # consume backslash
                
                escaped_ch = peek()
                if escaped_ch is None:
                    return None
                
                if escaped_ch == '"':
                    result.append('"')
                elif escaped_ch == '\\':
                    result.append('\\')
                elif escaped_ch == '/':
                    result.append('/')
                elif escaped_ch == 'b':
                    result.append('\b')
                elif escaped_ch == 'f':
                    result.append('\f')
                elif escaped_ch == 'n':
                    result.append('\n')
                elif escaped_ch == 'r':
                    result.append('\r')
                elif escaped_ch == 't':
                    result.append('\t')
                elif escaped_ch == 'u':
                    advance()  # consume 'u'
                    
                    # Get 4 hex digits
                    hex_digits = []
                    for _ in range(4):
                        digit = peek()
                        if digit is None or (digit not in '0123456789abcdefABCDEF'):
                            return None
                        advance()
                        hex_digits.append(digit)
                    
                    try:
                        code_point = int(''.join(hex_digits), 16)
                        result.append(chr(code_point))
                    except ValueError:
                        return None
                else:
                    # Invalid escape sequence
                    return None
            else:
                # Regular character (must be valid Unicode)
                if ord(ch) < 0x20:  # Control characters not allowed in strings
                    return None
                
                result.append(advance())
        
        return ''.join(result)
    
    def parse_number():
        """Parse a JSON number (integer or float)."""
        start = pos[0]
        
        # Handle negative sign
        if peek() == '-':
            advance()
        
        # Integer part
        if peek() == '0':
            advance()
            # No additional digits allowed after 0 in integer part
            if peek() is not None and peek().isdigit():
                return None  # Leading zero like 007
        elif peek() is not None and peek().isdigit():
            while peek() is not None and peek().isdigit():
                advance()
        else:
            return None
        
        # Check for fractional part
        if peek() == '.':
            advance()
            
            # Must have at least one digit after decimal point
            if peek() is None or not peek().isdigit():
                return None
            
            while peek() is not None and peek().isdigit():
                advance()
        
        # Check for exponent part
        if peek() in 'eE':
            advance()
            
            # Optional sign
            if peek() in '+-':
                advance()
            
            # Must have at least one digit in exponent
            if peek() is None or not peek().isdigit():
                return None
            
            while peek() is not None and peek().isdigit():
                advance()
        
        number_str = text[start:pos[0]]
        
        try:
            # Try to parse as integer first, then float
            if '.' in number_str or 'e' in number_str.lower():
                return float(number_str)
            else:
                return int(number_str)
        except ValueError:
            return None
    
    # Parse the main value
    result = parse_value()
    
    # Check for trailing content (after skipping whitespace)
    skip_whitespace()
    
    # If we haven't consumed all input, it's invalid JSON
    if pos[0] != len(text):
        return None
    
    return result
