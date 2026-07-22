def parse(text: str):
    # Tokenize and parse JSON manually without using json module
    
    i = 0
    n = len(text)
    
    def skip_whitespace():
        nonlocal i
        while i < n and text[i].isspace():
            i += 1
    
    def peek():
        if i < n:
            return text[i]
        return None
    
    def consume(expected=None):
        nonlocal i
        if i >= n:
            return None
        ch = text[i]
        i += 1
        if expected is not None and ch != expected:
            raise ValueError("Unexpected character")
        return ch
    
    def parse_string():
        nonlocal i
        if peek() != '"':
            raise ValueError("String must start with double quote")
        consume('"')
        
        result = []
        while True:
            ch = peek()
            if ch is None:
                raise ValueError("Unterminated string")
            
            if ch == '"':
                consume('"')
                return ''.join(result)
            
            if ch == '\\':
                consume('\\')
                escape_char = peek()
                if escape_char is None:
                    raise ValueError("Unterminated escape sequence in string")
                
                # Consume the escape character
                consume()
                
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
                    hex_digits = []
                    for _ in range(4):
                        digit = peek()
                        if digit is None or not (digit.isdigit() or digit.lower() in 'abcdef'):
                            raise ValueError("Invalid unicode escape")
                        consume()
                        hex_digits.append(digit)
                    
                    try:
                        code_point = int(''.join(hex_digits), 16)
                        result.append(chr(code_point))
                    except (ValueError, OverflowError):
                        raise ValueError("Invalid unicode escape")
                else:
                    # Invalid escape sequence
                    raise ValueError(f"Invalid escape character: {escape_char}")
            else:
                # Regular character or invalid control character
                if ord(ch) < 0x20:
                    raise ValueError("Control characters not allowed in string")
                result.append(consume())
    
    def parse_number():
        nonlocal i
        
        start = i
        
        # Handle negative sign
        if peek() == '-':
            consume('-')
        
        # Integer part
        if peek() is None:
            raise ValueError("Invalid number")
        
        # Check for leading zero
        if peek() == '0':
            consume()
            # If there's another digit after 0, it's invalid (leading zeros)
            if peek() is not None and peek().isdigit():
                raise ValueError("Leading zeros not allowed")
        elif peek() is not None and peek().isdigit():
            while peek() is not None and peek().isdigit():
                consume()
        else:
            raise ValueError("Invalid number: expected digit")
        
        # Check for fractional part
        if peek() == '.':
            consume('.')
            
            # Must have at least one digit after decimal point
            if peek() is None or not peek().isdigit():
                raise ValueError("Invalid number: expected digit after decimal point")
            
            while peek() is not None and peek().isdigit():
                consume()
        
        # Check for exponent part
        if peek() in ('e', 'E'):
            consume()
            
            # Optional sign
            if peek() in ('+', '-'):
                consume()
            
            # Must have at least one digit in exponent
            if peek() is None or not peek().isdigit():
                raise ValueError("Invalid number: expected digit in exponent")
            
            while peek() is not None and peek().isdigit():
                consume()
        
        num_str = text[start:i]
        
        # Try to parse as int first, then float
        try:
            return int(num_str)
        except ValueError:
            return float(num_str)
    
    def parse_value():
        skip_whitespace()
        
        if i >= n:
            raise ValueError("Empty input")
        
        ch = peek()
        
        if ch == '"':
            return parse_string()
        elif ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch == 't':  # true
            if text[i:i+4] == 'true':
                i += 4
                return True
            else:
                raise ValueError("Invalid token")
        elif ch == 'f':  # false
            if text[i:i+5] == 'false':
                i += 5
                return False
            else:
                raise ValueError("Invalid token")
        elif ch == 'n':  # null
            if text[i:i+4] == 'null':
                i += 4
                return None
            else:
                raise ValueError("Invalid token")
        elif ch in '-0123456789':
            return parse_number()
        else:
            raise ValueError(f"Unexpected character: {ch}")
    
    def parse_object():
        nonlocal i
        
        consume('{')
        result = {}
        
        skip_whitespace()
        
        # Empty object
        if peek() == '}':
            consume('}')
            return result
        
        while True:
            skip_whitespace()
            
            # Parse key (must be a string)
            if peek() != '"':
                raise ValueError("Object keys must be strings")
            key = parse_string()
            
            skip_whitespace()
            
            # Expect colon
            if peek() != ':':
                raise ValueError("Expected ':' after object key")
            consume(':')
            
            skip_whitespace()
            
            # Parse value
            value = parse_value()
            
            result[key] = value
            
            skip_whitespace()
            
            ch = peek()
            if ch == '}':
                consume('}')
                return result
            elif ch == ',':
                consume(',')
                skip_whitespace()
                # Check for trailing comma (not allowed)
                if peek() == '}':
                    raise ValueError("Trailing commas not allowed")
            else:
                raise ValueError(f"Expected ',' or '}}' in object, got '{ch}'")
    
    def parse_array():
        nonlocal i
        
        consume('[')
        result = []
        
        skip_whitespace()
        
        # Empty array
        if peek() == ']':
            consume(']')
            return result
        
        while True:
            skip_whitespace()
            
            value = parse_value()
            result.append(value)
            
            skip_whitespace()
            
            ch = peek()
            if ch == ']':
                consume(']')
                return result
            elif ch == ',':
                consume(',')
                skip_whitespace()
                # Check for trailing comma (not allowed)
                if peek() == ']':
                    raise ValueError("Trailing commas not allowed")
            else:
                raise ValueError(f"Expected ',' or ']' in array, got '{ch}'")
    
    try:
        skip_whitespace()
        
        if i >= n:
            return None
        
        # Parse the main value
        result = parse_value()
        
        skip_whitespace()
        
        # Check for trailing content
        if i < n:
            return None
        
        return result
    
    except (ValueError, IndexError):
        return None
