import decimal


class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def peek(self):
        if self.pos < self.length:
            return self.text[self.pos]
        else:
            return None

    def consume(self):
        ch = self.peek()
        self.pos += 1
        return ch

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def error(self):
        raise ValueError("Invalid JSON")

    def parse_value(self):
        # This method assumes whitespace has been consumed before the start of a value.
        ch = self.peek()
        if ch is None:
            return None  # No token, caller should handle (unlikely)
        if ch == '"':
            return self.parse_string()
        elif ch == '{':
            return self.parse_object()
        elif ch == '[':
            return self.parse_array()
        elif ch in '0123456789-':
            return self.parse_number()
        else:
            # Anything else is invalid.
            return None

    def parse_string(self):
        start = self.pos
        if self.consume() != '"':
            self.error()  # Expecting opening quote; we already checked it above but just in case.
        result = []
        pos = self.pos
        while True:
            if pos >= self.length:
                raise ValueError("Unterminated string")
            ch = self.text[pos]
            if ch == '"':
                # closing quote found; update parser position and return string
                self.pos = pos + 1
                return ''.join(result)
            elif ch == '\\':
                # Escape sequence: need next char(s) after backslash.
                if pos + 1 >= self.length:
                    raise ValueError("Unterminated escape")
                esc = self.text[pos + 1]
                try:
                    simple_map = {'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t', '\\': '\\', '/': '/', '"': '"'}
                    if esc in simple_map:
                        result.append(simple_map[esc])
                        pos += 2  # skip both backslash and escape character
                        continue
                    elif esc == 'u':
                        # Unicode escape, need exactly four hex digits after the current position.
                        # After seeing \u, we have already consumed the backslash at current index; now pos points to start of u? Actually pos is still pointing at backslash (since ch = '\\')
                        # So esc is text[pos+1]; we want hex digits starting at pos+2 through pos+5.
                        if pos + 5 >= self.length:
                            raise ValueError("Invalid \\u escape")
                        hex_str = self.text[pos + 2:pos + 6]
                        for c in hex_str:
                            if not (c.isdigit() or c in 'abcdefABCDEF'):
                                raise ValueError("Invalid \\u escape")
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        pos += 6  # advance past backslash + u + four digits
                        continue
                    else:
                        raise ValueError("Invalid escape character after backslash")
                except Exception as e:
                    self.error()
            else:
                if ord(ch) < 32:
                    raise ValueError("Control character not escaped in string")
                result.append(ch)
                pos += 1

    def parse_number(self):
        # Record start index for token substring.
        start_idx = self.pos
        negative = False
        if self.peek() == '-':
            self.consume()
            negative = True
        # Must have at least one digit after optional minus and before '.' or 'e'/'E'.
        if not self.peek().isdigit():
            self.error()  # No digits for integer part -> invalid number
        int_digits = []
        while self.peek().isdigit():
            int_digits.append(self.consume())
        # Leading zeros check: if more than one digit and starts with '0', invalid.
        if len(int_digits) > 1 and int_digits[0] == '0':
            self.error()

        has_fraction = False
        frac_digits = []
        if self.peek() == '.':
            self.consume()
            # Must have at least one digit after decimal point
            while self.peek().isdigit():
                frac_digits.append(self.consume())
            if not frac_digits:
                self.error()  # No digits after '.' -> invalid
            has_fraction = True

        exponent_val = None
        exp_sign = 1
        if self.peek() in 'eE':
            self.consume()
            if self.peek() == '+':
                self.consume()
            elif self.peek() == '-':
                self.consume()
                exp_sign = -1
            exp_digits = []
            while self.peek().isdigit():
                exp_digits.append(self.consume())
            if not exp_digits:
                self.error()  # Missing exponent digits -> invalid
            exponent_val = int(''.join(exp_digits)) * exp_sign

        # Reconstruct the full numeric token string from start_idx to current pos.
        token_str = self.text[start_idx:self.pos]
        try:
            value = decimal.Decimal(token_str)
        except Exception as e:
            # If Decimal parsing fails for any reason, treat as invalid JSON number
            self.error()

        if value.is_integer():
            return int(value)
        else:
            return float(value)

    def parse_object(self):
        start = self.pos
        if self.consume() != '{':
            self.error()
        result = {}
        while True:
            self.skip_whitespace()
            # End of object?
            if self.peek() == '}':
                break
            # Parse key (must be a string)
            ch = self.peek()
            if ch != '"':
                self.error()  # Expected string for key
            key = self.parse_string()
            self.skip_whitespace()
            if self.consume() != ':':
                self.error()  # Expected colon after key
            value = self.parse_value()
            result[key] = value
            self.skip_whitespace()
            if self.peek() == '}':
                break
            elif self.peek() == ',':
                self.consume()
                continue
            else:
                self.error()  # Unexpected character after key-value pair (e.g., missing comma, trailing comma)
        return result

    def parse_array(self):
        start = self.pos
        if self.consume() != '[':
            self.error()
        result = []
        while True:
            self.skip_whitespace()
            if self.peek() == ']':
                break
            value = self.parse_value()
            result.append(value)
            self.skip_whitespace()
            if self.peek() == ']':
                break
            elif self.peek() == ',':
                self.consume()
                continue
            else:
                self.error()  # Unexpected character after element (e.g., missing comma, trailing comma)
        return result


def parse(text: str):
    """Parses a JSON document and returns the equivalent Python object.
    Returns None if the input is not valid JSON.
    """
    parser = JSONParser(text)
    try:
        # Skip any leading whitespace before parsing root value
        parser.skip_whitespace()
        if parser.pos >= parser.length:
            return None  # No token at all, invalid document
        root_value = parser.parse_value()
        if root_value is None:
            return None
        # After the top-level value, skip any remaining whitespace.
        parser.skip_whitespace()
        # If there are still characters left that aren't whitespace, it's malformed (trailing garbage).
        if parser.pos < parser.length:
            raise ValueError("Trailing content after JSON")
        return root_value
    except Exception:
        return None
