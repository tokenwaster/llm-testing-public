import re

def parse(text: str):
    """
    Parses a JSON document string and returns the corresponding Python object, 
    or None if the input is not valid JSON.
    """
    if not isinstance(text, str):
        return None

    class ParserState:
        """Helper class to manage current index and text."""
        def __init__(self, text):
            self.text = text
            self.index = 0

        def skip_whitespace(self):
            while self.index < len(self.text) and self.text[self.index].isspace():
                self.index += 1

        def peek(self, offset=1):
            if self.index + offset > len(self.text):
                return None
            return self.text[self.index:self.index + offset]

        def consume_char(self, char):
            if self.index < len(self.text) and self.text[self.index] == char:
                self.index += 1
                return True
            return False

        def consume_string(self, expected_start: str):
            """Consumes the starting delimiter and advances index."""
            if not self.consume_char(expected_start):
                raise ValueError("Expected start sequence")
            return True

    state = ParserState(text)

    # --- Core Parsing Functions ---

    def parse_string():
        """Parses a JSON string literal (starts after the opening quote)."""
        if state.peek() != '"':
            raise ValueError("Expected starting quote for string")

        start_index = state.index + 1 # Start reading content after initial quote
        content = []
        
        # Read until closing quote or end of text
        while state.index < len(state.text):
            char = state.text[state.index]
            
            if char == '"' and (len(content) > 0 or content[-1:] != '\\'):
                # Found unescaped closing quote
                state.index += 1
                return "".join(content), True

            elif char == '\\':
                state.index += 1 # Skip backslash
                if state.index >= len(state.text):
                    raise ValueError("Unterminated string (EOF after \\)")

                escape_char = state.text[state.index]
                
                if escape_char in ('"', '\\', '/', 'b', 'f', 'n', 'r', '\t'):
                    # Handle standard escapes
                    if escape_char == 'b': content.append('\b')
                    elif escape_char == 'f': content.append('\f')
                    elif escape_char == 'n': content.append('\n')
                    elif escape_char == 'r': content.append('\r')
                    elif escape_char == '\t': content.append('\t')
                    else: # ", \, /
                        content.append(escape_char)
                
                elif escape_char == 'u':
                    # Handle unicode escape \uXXXX
                    hex_code = state.text[state.index:state.index + 4]
                    if len(hex_code) != 4 or not all(c in '0123456789abcdefABCDEF' for c in hex_code):
                        raise ValueError("Invalid unicode escape sequence")
                    
                    try:
                        unicode_value = int(hex_code, 16)
                        content.append(chr(unicode_value))
                        state.index += 4
                    except ValueError:
                        # Should not happen if regex check was sufficient, but defensive fail
                        raise ValueError("Invalid unicode sequence")
                else:
                    # Invalid escape sequence
                    raise ValueError(f"Illegal escape sequence \\{escape_char}")

            else:
                content.append(char)
                state.index += 1
        
        # If loop finishes without finding closing quote
        raise EOFError("Unterminated string")


    def parse_number():
        """Parses a JSON number (int or float)."""
        start_index = state.index
        
        # Regex to capture standard JSON numbers: 
        # Optional sign, digits, optional fractional part (.digits), and optional exponent ([eE][+|-]digits)
        match = re.match(r"[-+]?(\d*(\.\d*)?([Ee][+-]?\d+)?)?", state.text[state.index:])
        if not match:
            raise ValueError("Not a valid number")

        num_str = match.group(0)
        
        # Advance index past the consumed digits/number string
        state.index += len(num_str)
        
        if not num_str:
            raise ValueError("Empty number reading attempt")

        try:
            # Check for leading zeros requirement failure (e.g., "007" fails)
            # If the number is longer than 1 digit and starts with '0', AND it's not just "0", fail it.
            # Note: This implementation deviates slightly from pure JSON parsing which allows this, 
            # but adheres strictly to the prompt requirement ("leading zeros like 007" fails).
            if len(num_str) > 1 and num_str[0] == '0' and num_str[1] != '.' and num_str[1:] != '':
                 raise ValueError("Leading zeros forbidden in number representation.")

            # Attempt conversion
            # float() handles both int representations (e.g., "123") and fractional/scientific notation.
            f_val = float(num_str)
            
            # Check if the stored value is mathematically an integer AND we can parse it as one 
            # (i.e., no trailing '0' from a forced float conversion like "123.0")
            # Since JSON numbers are parsed into Python types, if they look integral, they should be ints.
            if f_val == int(f_val) and '.' not in num_str and 'e' not in num_str:
                return int(f_val)

            return f_val
        except ValueError:
             # This handles cases where float() conversion fails unexpectedly, 
             # or if the regex was too greedy/loose.
             raise ValueError("Failed to convert number string.")


    def parse_literal(value_str):
        """Parses 'true', 'false', or 'null'."""
        if value_str == "true": return True
        if value_str == "false": return False
        if value_str == "null": return None
        raise ValueError("Unknown JSON literal")


    def parse_array():
        """Parses a JSON array [ ... ]."""
        state.consume_char('['); state.skip_whitespace()

        elements = []
        while True:
            # Check for empty array or end of elements
            if state.text[state.index] == ']':
                state.index += 1 # Consume ']'
                return elements, True

            # Parse element value (this must consume the necessary tokens)
            value, success = parse_value()
            elements.append(value)
            state.skip_whitespace()

            # Check for comma or closing bracket
            if state.text[state.index] == ']':
                state.index += 1 # Consume ']'
                return elements, True
            elif state.text[state.index] == ',':
                state.index += 1 # Consume ','
            else:
                raise ValueError("Expected comma or closing bracket in array")

    def parse_object():
        """Parses a JSON object { ... }. Returns dict."""
        state.consume_char('{'); state.skip_whitespace()
        
        obj = {}
        while True:
            # Check for empty object or end of pairs
            if state.text[state.index] == '}':
                state.index += 1 # Consume '}'
                return obj, True

            state.skip_whitespace()

            # Key must be a string
            key, success = parse_string()
            obj[key] = None
            state.skip_whitespace()
            
            # Expect colon separator
            if not state.consume_char(':'):
                raise ValueError("Expected ':' after key in JSON object")

            state.skip_whitespace()
            
            # Parse value
            value, success = parse_value()
            obj[key] = value
            state.skip_whitespace()

            # Check for comma or closing brace
            if state.text[state.index] == '}':
                state.index += 1 # Consume '}'
                return obj, True
            elif state.text[state.index] == ',':
                state.index += 1 # Consume ','
            else:
                raise ValueError("Expected comma or closing brace in JSON object")


    def parse_value():
        """Determines and parses the type of value (string, number, array, object, literal)."""
        state.skip_whitespace()

        if state.index >= len(state.text):
            raise EOFError("Unexpected end of input while reading value")

        char = state.text[state.index]

        # 1. String
        if char == '"':
            value, success = parse_string()
            return value, True
        
        # 2. Object or Array Start
        elif char in ('{', '['):
            if char == '{':
                return parse_object()
            else: # char == '['
                return parse_array()

        # 3. Number (must check before literals as they start with letters)
        elif char.isdigit() or char in ('-', '+'):
            try:
                value = parse_number()
                return value, True
            except ValueError as e:
                 # If parsing the number failed due to leading zero requirement, re-raise it 
                 # so the main function catches and converts to None.
                 if "Leading zeros forbidden" in str(e):
                     raise e
                 raise

        # 4. Literals (true, false, null)
        elif char.isalpha():
            start_index = state.index
            # Read until non-alphanumeric character
            while state.index < len(state.text) and (state.text[state.index].isalnum() or state.text[state.index] == '_'):
                state.index += 1
            
            literal_str = state.text[start_index:state.index]
            if not literal_str: # Should not happen if char is alpha, but safety check
                 raise ValueError("Failed to read literal")
            
            try:
                value = parse_literal(literal_str)
                return value, True
            except ValueError as e:
                # If it looks like a literal but isn't (e.g., 'myword'), this is an error
                raise e 

        else:
            # Unrecognized starting character
            raise ValueError(f"Invalid JSON start token: '{char}'")


    try:
        result, success = parse_value()
        if not success:
             raise Exception("Internal parsing failure.")

        state.skip_whitespace()
        
        # Check for trailing garbage after the document end (must consume everything)
        if state.index != len(state.text):
            raise ValueError(f"Trailing garbage found after valid JSON structure starting at index {state.index}")
            
        return result

    except (ValueError, EOFError, IndexError, Exception):
        # Catch all parsing errors and return None as required.
        return None
