import re

class JSONParser:
    """
    A custom parser for JSON strings, adhering strictly to grammar rules
    and returning None upon any parsing failure.
    """
    def __init__(self, text: str):
        self.text = text
        self.index = 0
        self.length = len(text)

    def _skip_whitespace(self):
        """Advances the index past any whitespace characters."""
        while self.index < self.length and self.text[self.index].isspace():
            self.index += 1

    def _peek(self, offset: int = 0) -> str | None:
        """Peeks at the character at index + offset without advancing."""
        target_index = self.index + offset
        if target_index < self.length:
            return self.text[target_index]
        return None

    def _consume(self, expected: str | None = None) -> str:
        """Consumes the current character and advances the index."""
        char = self.text[self.index]
        if expected is not None and char != expected:
            raise ValueError(f"Expected '{expected}' but found '{char}'")
        self.index += 1
        return char

    def _parse_string(self) -> str | None:
        """Parses a JSON string, handling escapes and unicode."""
        if self._peek() != '"':
            return None # Should not happen if called correctly

        # Consume the opening quote
        self.index += 1
        start = self.index
        result = []

        while self.index < self.length:
            char = self.text[self.index]

            if char == '"':
                # Found closing quote
                self.index += 1
                return "".join(result)

            elif char == '\\':
                # Handle escape sequences
                self.index += 1 # Consume '\'
                escape_char = self._peek()
                if escape_char is None:
                    raise ValueError("Unterminated string")

                if escape_char in ('"', '\\', '/', 'b', 'f', 'n', 'r', 't'):
                    escapes = {
                        '\\': '\\', '"': '"', '/': '/', 'b': '\b', 
                        'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'
                    }
                    result.append(escapes[escape_char])
                    self.index += 1
                elif escape_char == 'u':
                    # Unicode escape: \uXXXX
                    self.index += 1 # Consume 'u'
                    hex_code = self.text[self.index:self.index+4]
                    if len(hex_code) != 4 or not all(c in '0123456789abcdefABCDEF' for c in hex_code):
                        raise ValueError("Invalid unicode escape sequence")
                    
                    try:
                        unicode_val = int(hex_code, 16)
                        result.append(chr(unicode_val))
                        self.index += 4
                    except ValueError:
                        raise ValueError("Malformed unicode escape")
                else:
                    # Invalid escape sequence (e.g., \z)
                    raise ValueError(f"Invalid escape sequence \\{escape_char}")

            else:
                result.append(char)
                self.index += 1
        
        # If loop finishes without finding closing quote
        raise ValueError("Unterminated string")


    def _parse_number(self) -> int | float | None:
        """Parses a JSON number, handling scientific notation and strict leading zero rules."""
        start = self.index
        
        # 1. Read the full potential number token
        while self.index < self.length:
            char = self._peek()
            if char in '0123456789.-eE':
                self.index += 1
            else:
                break
        
        num_str = self.text[start:self.index]

        # Check for empty or invalid tokens (shouldn't happen if called correctly)
        if not num_str:
            self.index -= len(num_str) # Backtrack
            return None

        # 2. Strict Leading Zero Validation (e.g., "007" fails, but "0" passes)
        # If the number starts with '0' and has length > 1 AND does not contain '.' or 'e', it is invalid.
        if num_str.startswith('0') and len(num_str) > 1 and ('.' not in num_str and 'e' not in num_str.lower()):
            # Check if the remaining characters are all digits after the initial zero
            if re.fullmatch(r"0\d+", num_str):
                 raise ValueError("Leading zeros in integer format")

        try:
            # 3. Determine type (int vs float)
            if '.' in num_str or 'e' in num_str.lower():
                return float(num_str)
            else:
                # If it passed the leading zero check and has no decimal/exponent, treat as int
                return int(num_str)
        except ValueError:
            # Catch cases where Python's built-in conversion fails (e.g., "1.2.3")
            self.index = start # Backtrack index if parsing failed
            return None


    def _parse_literal(self, literal: str, value: any) -> bool:
        """Checks for and consumes reserved literals (true, false, null)."""
        if self.text[self.index:self.index + len(literal)] == literal:
            self.index += len(literal)
            return True
        return False

    def _parse_array(self) -> list | None:
        """Parses a JSON array."""
        # Expect '['
        if self._peek() != '[': return None
        self.index += 1 # Consume '['
        
        arr = []
        while True:
            self._skip_whitespace()

            if self._peek() == ']':
                self.index += 1 # Consume ']'
                return arr

            # Handle empty array case (e.g., "[]")
            if not arr and self._peek() == ']':
                 pass # Handled above, but good safety check

            value = self._parse_value()
            if value is None:
                return None # Parsing failed inside the element

            arr.append(value)

            self._skip_whitespace()

            # Check for comma or closing bracket
            next_char = self._peek()
            if next_char == ']':
                self.index += 1 # Consume ']'
                return arr
            elif next_char == ',':
                self.index += 1 # Consume ','
                continue
            else:
                # Missing comma or closing bracket after element
                raise ValueError("Expected ',' or ']' in array")

    def _parse_object(self) -> dict | None:
        """Parses a JSON object."""
        # Expect '{'
        if self._peek() != '{': return None
        self.index += 1 # Consume '{'
        
        obj = {}
        while True:
            self._skip_whitespace()

            if self._peek() == '}':
                self.index += 1 # Consume '}'
                return obj

            # Handle empty object case (e.g., "{}")
            if not obj and self._peek() == '}':
                 pass # Handled above, but good safety check

            # 1. Parse Key (must be a string)
            key_str = self._parse_string()
            if key_str is None:
                raise ValueError("Object missing key or key is not a string")
            
            self._skip_whitespace()

            # 2. Expect ':'
            if self._peek() != ':':
                raise ValueError("Expected ':' after key in object")
            self.index += 1 # Consume ':'
            
            self._skip_whitespace()

            # 3. Parse Value (recursive call)
            value = self._parse_value()
            if value is None:
                return None # Parsing failed inside the element

            obj[key_str] = value

            self._skip_whitespace()

            # Check for comma or closing brace
            next_char = self._peek()
            if next_char == '}':
                self.index += 1 # Consume '}'
                return obj
            elif next_char == ',':
                self.index += 1 # Consume ','
                continue
            else:
                # Missing comma or closing brace after pair
                raise ValueError("Expected ',' or '}' in object")


    def _parse_value(self) -> dict | list | str | int | float | bool | None:
        """Determines the type of value and calls the appropriate parser."""
        self._skip_whitespace()

        if self.index >= self.length:
            return None # EOF reached unexpectedly

        char = self._peek()

        # 1. Object Start
        if char == '{':
            try:
                return self._parse_object()
            except ValueError:
                return None

        # 2. Array Start
        elif char == '[':
            try:
                return self._parse_array()
            except ValueError:
                return None

        # 3. String
        elif char == '"':
            try:
                return self._parse_string()
            except ValueError:
                return None

        # 4. Number (starts with digit or minus sign)
        elif char.isdigit() or char == '-':
            try:
                return self._parse_number()
            except ValueError:
                return None

        # 5. Literals (true, false, null)
        elif char == 't':
            if self._parse_literal("true", True):
                return True
        elif char == 'f':
            if self._parse_literal("false", False):
                return False
        elif char == 'n':
            if self._parse_literal("null", None):
                return None

        # 6. Invalid start character (bare word, etc.)
        else:
            raise ValueError(f"Unexpected token starting with '{char}'")


    def parse(self) -> dict | list | str | int | float | bool | None:
        """Main entry point for parsing."""
        try:
            result = self._parse_value()
            if result is None and self.text.strip(): # Handle case where input was just whitespace
                return None

            self._skip_whitespace()
            
            # Check for trailing garbage after successful parse
            if self.index < self.length:
                raise ValueError("Trailing garbage found after JSON document")
            
            return result

        except (ValueError, IndexError):
            # Catch all parsing errors (unterminated structures, missing commas, etc.)
            return None


def parse(text: str) -> dict | list | str | int | float | bool | None:
    """
    Parses a JSON document string into the equivalent Python object.
    Returns None if the input is not valid JSON or contains malformations.
    """
    if not text:
        return None
    parser = JSONParser(text)
    return parser.parse()
