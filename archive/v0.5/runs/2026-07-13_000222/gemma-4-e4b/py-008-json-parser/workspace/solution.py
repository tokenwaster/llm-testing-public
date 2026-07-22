import re

def parse(text: str):
    """
    Parses a JSON document string into its equivalent Python object 
    (dict, list, str, int, float, bool, None). Returns None if the input is invalid JSON.
    """
    
    # Use an index wrapper to allow mutable state tracking across recursive calls
    i = [0]

    def skip_whitespace():
        while i[0] < len(text) and text[i[0]].isspace():
            i[0] += 1

    def parse_string() -> tuple[str, bool]:
        """Parses a JSON string literal. Returns (value, success_flag)."""
        start = i[0]
        if text[start] != '"':
            return None, False
        
        i[0] += 1  # Consume opening quote
        result = []
        while i[0] < len(text):
            char = text[i[0]]
            if char == '"':
                i[0] += 1  # Consume closing quote
                return "".join(result), True
            elif char == '\\':
                i[0] += 1 # Consume backslash
                if i[0] >= len(text): return None, False # Unterminated escape
                
                escaped_char = text[i[0]]
                
                if escaped_char == '"':
                    result.append('"')
                elif escaped_char == '\\':
                    result.append('\\')
                elif escaped_char == '/':
                    result.append('/')
                elif escaped_char == 'b':
                    result.append('\b')
                elif escaped_char == 'f':
                    result.append('\f')
                elif escaped_char == 'n':
                    result.append('\n')
                elif escaped_char == 'r':
                    result.append('\r')
                elif escaped_char == 't':
                    result.append('\t')
                elif escaped_char == 'u':
                    # Unicode escape: \uXXXX
                    i[0] += 4 # Consume the four hex digits
                    hex_code = text[i[0]-1:i[0]+1]
                    if len(hex_code) != 4 or not all(c in '0123456789abcdefABCDEF' for c in hex_code):
                        return None, False # Malformed unicode escape
                    try:
                        unicode_char = chr(int(hex_code, 16))
                        result.append(unicode_char)
                    except ValueError:
                        return None, False # Should not happen if regex/checks are right, but safe guard
                else:
                    # Unknown escape sequence (e.g., \z)
                    return None, False

            else:
                result.append(char)
                i[0] += 1
        
        # Reached EOF without closing quote
        return None, False

    def parse_number() -> tuple[float | int, bool]:
        """Parses a JSON number. Returns (value, success_flag)."""
        start = i[0]
        
        # Regex pattern for robust JSON number parsing: 
        # Optional sign, digits, optional fractional part (.digits), optional exponent (e/E [+-] digits)
        # We must also enforce the "no leading zeros like 007" rule.
        
        match = re.match(r'^-?(?:0|[1-9]\d*|\.\d+)(?:\(?:[eE][+-]?\d+))?', text[start:])
        if not match:
            return None, False

        num_str = match.group(0)
        i[0] += len(num_str)

        # Check for leading zeros failure condition (e.g., "007")
        # If the number starts with '0' and has length > 1 AND it is not just "0", it fails.
        if num_str.startswith('0') and len(num_str) > 1 and num_str != '0':
             # Exception: if it's like "0.5" or "-0.5", this check passes because the dot breaks the pattern.
             # We only care about integer-like leading zeros (e.g., "007").
            if '.' not in num_str and 'e' not in num_str.lower():
                return None, False

        try:
            # Determine if it should be an int or float
            if '.' in num_str or 'e' in num_str.lower():
                value = float(num_str)
            else:
                # If it parses cleanly as an integer string (no decimal/exponent), return int
                value = int(num_str)
            return value, True
        except ValueError:
            # Should not happen if regex is correct, but safe guard
            return None, False

    def parse_literal(expected_literal: str) -> tuple[bool, bool]:
        """Parses true, false, or null."""
        start = i[0]
        if text.startswith(expected_literal, start):
            i[0] += len(expected_literal)
            return expected_literal == 'true', True # We only care about success here
        return False, False

    def parse_array() -> tuple[list, bool]:
        """Parses a JSON array."""
        if text[i[0]] != '[':
            return None, False
        
        i[0] += 1 # Consume '['
        arr = []
        
        while True:
            skip_whitespace()
            start_index = i[0]

            # Check for empty array or end of array
            if text[start_index] == ']':
                i[0] += 1 # Consume ']'
                return arr, True
            
            # Parse the first element
            value, success = parse_value()
            if not success:
                return None, False

            arr.append(value)

            skip_whitespace()
            start_index = i[0]

            # Check for comma or closing bracket
            if text[start_index] == ']':
                i[0] += 1 # Consume ']'
                return arr, True
            elif text[start_index] == ',':
                i[0] += 1 # Consume ','
                skip_whitespace()
                # Continue loop to parse next element
            else:
                # Expected comma or closing bracket, found something else (e.g., garbage)
                return None, False

    def parse_object() -> tuple[dict, bool]:
        """Parses a JSON object."""
        if text[i[0]] != '{':
            return None, False
        
        i[0] += 1 # Consume '{'
        obj = {}
        
        while True:
            skip_whitespace()
            start_index = i[0]

            # Check for empty object or end of object
            if text[start_index] == '}':
                i[0] += 1 # Consume '}'
                return obj, True
            
            # Parse Key (must be a string)
            key, success = parse_string()
            if not success:
                return None, False

            skip_whitespace()
            start_index = i[0]

            # Expect colon separator
            if text[start_index] != ':':
                return None, False # Missing colon
            i[0] += 1 # Consume ':'
            
            skip_whitespace()
            start_index = i[0]

            # Parse Value
            value, success = parse_value()
            if not success:
                return None, False

            obj[key] = value

            skip_whitespace()
            start_index = i[0]

            # Check for comma or closing brace
            if text[start_index] == '}':
                i[0] += 1 # Consume '}'
                return obj, True
            elif text[start_index] == ',':
                i[0] += 1 # Consume ','
                skip_whitespace()
                # Continue loop to parse next pair
            else:
                # Expected comma or closing brace, found something else (e.g., garbage)
                return None, False


    def parse_value() -> tuple[any, bool]:
        """Determines the type of value and calls the appropriate parser."""
        skip_whitespace()
        start = i[0]

        if start >= len(text):
            return None, False # Unexpected EOF when expecting a value

        char = text[start]

        # 1. String
        if char == '"':
            value, success = parse_string()
            return value, success
        
        # 2. Number
        elif char.isdigit() or char == '-' or (char == '.' and text[start+1].isdigit()):
            value, success = parse_number()
            return value, success

        # 3. Object
        elif char == '{':
            return parse_object()

        # 4. Array
        elif char == '[':
            return parse_array()

        # 5. Literals (true, false, null)
        elif char == 't' and text[start:].startswith('true'):
            return True, True
        elif char == 'f' and text[start:].startswith('false'):
            return False, True
        elif char == 'n' and text[start:].startswith('null'):
            return None, True

        # 6. Error: Unexpected character
        else:
            return None, False


    # --- Main Execution Flow ---
    
    skip_whitespace()
    result, success = parse_value()

    if not success:
        return None # Failed to parse the root value

    # Crucial check: Ensure no trailing garbage remains after successful parsing.
    skip_whitespace()
    if i[0] != len(text):
        return None # Trailing garbage found

    return result
