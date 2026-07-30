def parse(text: str):
    # Skip whitespace and return the index after skipping
    def skip_whitespace(s, i):
        while i < len(s) and s[i] in ' \t\n\r':
            i += 1
        return i
    
    # Check if current character is a digit
    def is_digit(c):
        return c.isdigit()
    
    # Check if current character is an octal digit (for validation)
    def is_octal(c):
        return c in '01234567'
    
    # Parse string: handle escapes and unicode
    def parse_string(s, i):
        if s[i] != '"':
            return None, i
        
        result = []
        i += 1  # Skip opening quote
        
        while i < len(s):
            c = s[i]
            
            if c == '"':  # End of string
                i += 1
                return ''.join(result), i
            
            if c == '\\':
                i += 1
                if i >= len(s):
                    return None, i  # Unterminated escape
                
                escape_char = s[i]
                
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
                elif escape_char == 'u':  # Unicode escape
                    if i + 4 >= len(s):
                        return None, i  # Not enough chars for \uXXXX
                    
                    hex_digits = s[i+1:i+5]
                    try:
                        code_point = int(hex_digits, 16)
                        result.append(chr(code_point))
                        i += 4
                    except ValueError:
                        return None, i  # Invalid unicode escape
                else:
                    return None, i  # Invalid escape sequence
            else:
                if c in '\n\r':
                    # Newlines are not allowed directly in JSON strings without being escaped
                    return None, i
                
                result.append(c)
            
            i += 1
        
        # If we exited the loop because we ran out of characters, string is unterminated
        return None, i
    
    # Parse number: handles int, float, negative, and exponents
    def parse_number(s, i):
        start = i
        
        # Handle negative sign
        if s[i] == '-':
            i += 1
            if i >= len(s) or not is_digit(s[i]):
                return None, i  # Invalid after minus: no digit
            
        # Integer part
        if s[i] == '0':
            i += 1
            # Check for leading zeros (invalid unless it's just "0")
            if i < len(s) and is_digit(s[i]):
                return None, i  # Leading zero like 007, 01, etc.
        elif is_digit(s[i]):
            while i < len(s) and is_digit(s[i]):
                i += 1
        else:
            return None, i  # No digit after minus or invalid start
        
        # Check for decimal part
        if i < len(s) and s[i] == '.':
            i += 1
            if i >= len(s) or not is_digit(s[i]):
                return None, i  # Decimal point without following digits
            
            while i < len(s) and is_digit(s[i]):
                i += 1
        
        # Check for exponent part
        if i < len(s) and s[i] in 'eE':
            i += 1
            if i >= len(s):
                return None, i  # e/E at end without exponent
            
            # Handle sign in exponent
            if s[i] == '+' or s[i] == '-':
                i += 1
            
            if i >= len(s) or not is_digit(s[i]):
                return None, i  # No digit after exponent indicator
            
            while i < len(s) and is_digit(s[i]):
                i += 1
        
        num_str = s[start:i]
        
        try:
            # Try integer first; if it has a decimal point or exponent, use float
            if any(c in num_str for c in '.eE'):
                return float(num_str), i
            else:
                return int(num_str), i
        except ValueError:
            return None, i
    
    # Parse token: true, false, null
    def parse_keyword(s, i):
        for keyword, value in [('true', True), ('false', False), ('null', None)]:
            if s[i:i+len(keyword)] == keyword:
                # Make sure it's not part of a longer identifier
                end = i + len(keyword)
                if end >= len(s) or (s[end] not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_$'):
                    return value, end
        
        return None, i
    
    # Main recursive parser
    def parse_value(s, i):
        i = skip_whitespace(s, i)
        
        if i >= len(s):
            return None, i  # Empty input
        
        c = s[i]
        
        if c == '"':
            val, i = parse_string(s, i)
            if val is None:
                return None, i
            return val, i
        
        elif c in '0123456789-':
            val, i = parse_number(s, i)
            if val is None:
                return None, i
            return val, i
        
        elif c == 't':
            val, i = parse_keyword(s, i)
            if val is None and s[i:i+4] != 'true':
                return None, i
            return val, i
        
        elif c == 'f':
            val, i = parse_keyword(s, i)
            if val is None and s[i:i+5] != 'false':
                return None, i
            return val, i
        
        elif c == 'n':
            val, i = parse_keyword(s, i)
            if val is None and s[i:i+4] != 'null':
                return None, i
            return val, i
        
        elif c == '[':
            arr = []
            i += 1
            i = skip_whitespace(s, i)
            
            # Empty array
            if i < len(s) and s[i] == ']':
                return arr, i + 1
            
            while True:
                val, i = parse_value(s, i)
                if val is None:
                    return None, i
                
                arr.append(val)
                
                i = skip_whitespace(s, i)
                
                if i >= len(s):
                    return None, i  # Missing closing bracket
                
                if s[i] == ']':
                    return arr, i + 1
                elif s[i] == ',':
                    i += 1
                    i = skip_whitespace(s, i)
                    # After comma, expect another value
                    if i >= len(s) or s[i] in '],}':
                        return None, i  # Trailing comma or missing value after comma
                else:
                    return None, i  # Missing comma between array elements
        
        elif c == '{':
            obj = {}
            i += 1
            i = skip_whitespace(s, i)
            
            # Empty object
            if i < len(s) and s[i] == '}':
                return obj, i + 1
            
            while True:
                i = skip_whitespace(s, i)
                
                # Parse key (must be a string)
                if s[i] != '"':
                    return None, i
                
                key, i = parse_string(s, i)
                if key is None:
                    return None, i
                
                i = skip_whitespace(s, i)
                
                if i >= len(s) or s[i] != ':':
                    return None, i  # Missing colon after key
                i += 1
                
                val, i = parse_value(s, i)
                if val is None:
                    return None, i
                
                obj[key] = val
                
                i = skip_whitespace(s, i)
                
                if i >= len(s):
                    return None, i  # Missing closing brace
                
                if s[i] == '}':
                    return obj, i + 1
                elif s[i] == ',':
                    i += 1
                    i = skip_whitespace(s, i)
                    # After comma, expect another key-value pair (starting with string)
                    if i >= len(s) or s[i] not in '"{[tfn0123456789-':
                        return None, i  # Trailing comma or missing value after comma
                else:
                    return None, i  # Missing comma between object members
        
        else:
            return None, i
    
    # Main parsing entry point
    if not isinstance(text, str):
        return None
    
    i = skip_whitespace(text, 0)
    
    # Empty string is not valid JSON
    if i >= len(text):
        return None
    
    result, i = parse_value(text, i)
    if result is None:
        return None
    
    # Ensure we've consumed the entire input (no trailing garbage)
    i = skip_whitespace(text, i)
    if i < len(text):
        return None  # Trailing content after JSON
    
    return result
