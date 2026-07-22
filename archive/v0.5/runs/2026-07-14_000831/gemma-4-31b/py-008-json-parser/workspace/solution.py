class JSONError(Exception):
    """Custom exception to signal parsing failures."""
    pass

class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \n\r\t':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= len(self.text):
            raise JSONError("Unexpected end of input")
        
        char = self.text[self.pos]
        if char == '{':
            return self.parse_object()
        elif char == '[':
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char == '-' or '0' <= char <= '9':
            return self.parse_number()
        elif self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        elif self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        elif self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        else:
            raise JSONError(f"Unexpected character {char} at position {self.pos}")

    def parse_string(self):
        if self.pos >= len(self.text) or self.text[self.pos] != '"':
            raise JSONError("Expected opening quote")
        
        self.pos += 1  # skip "
        res = []
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char == '"':
                self.pos += 1
                return "".join(res)
            elif char == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    raise JSONError("Unterminated escape sequence")
                esc = self.text[self.pos]
                if esc == '"': res.append('"')
                elif esc == '\\': res.append('\\')
                elif esc == '/': res.append('/')
                elif esc == 'b': res.append('\x08')
                elif esc == 'f': res.append('\x0c')
                elif esc == 'n': res.append('\n')
                elif esc == 'r': res.append('\r')
                elif esc == 't': res.append('\t')
                elif esc == 'u':
                    self.pos += 1
                    if self.pos + 3 >= len(self.text):
                        raise JSONError("Unterminated unicode escape")
                    hex_val = self.text[self.pos : self.pos + 4]
                    try:
                        res.append(chr(int(hex_val, 16)))
                    except ValueError:
                        raise JSONError("Invalid unicode escape sequence")
                    self.pos += 4
                else:
                    raise JSONError(f"Invalid escape character {esc}")
            else:
                if ord(char) < 32:
                    raise JSONError("Unescaped control character in string")
                res.append(char)
            self.pos += 1
        raise JSONError("Unterminated string")

    def parse_number(self):
        start = self.pos
        is_float = False
        
        if self.text[self.pos] == '-':
            self.pos += 1
        
        if self.pos >= len(self.text):
            raise JSONError("Number interrupted")

        # Integer part
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                raise JSONError("Leading zeros are not allowed")
        elif '1' <= self.text[self.pos] <= '9':
            while self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
        else:
            raise JSONError("Invalid number format")

        # Fraction part
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= len(self.text) or not ('0' <= self.text[self.pos] <= '9'):
                raise JSONError("Fractional part must contain digits")
            while self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                self.pos += 1

        # Exponent part
        if self.pos < len(self.text) and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= len(self.text) or not ('0' <= self.text[self.pos] <= '9'):
                raise JSONError("Exponent must contain digits")
            while self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                self.pos += 1

        num_str = self.text[start:self.pos]
        try:
            return float(num_str) if is_float else int(num_str)
        except ValueError:
            raise JSONError("Failed to convert number string")

    def parse_array(self):
        self.pos += 1  # skip [
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == ']':
            self.pos += 1
            return []
        
        res = []
        while True:
            res.append(self.parse_value())
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == ']':
                self.pos += 1
                return res
            if self.pos >= len(self.text) or self.text[self.pos] != ',':
                raise JSONError("Expected comma or closing bracket in array")
            self.pos += 1  # skip ,
            self.skip_whitespace()

    def parse_object(self):
        self.pos += 1  # skip {
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == '}':
            self.pos += 1
            return {}
        
        res = {}
        while True:
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                raise JSONError("Object keys must be strings")
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                raise JSONError("Expected colon after object key")
            self.pos += 1  # skip :
            val = self.parse_value()
            res[key] = val
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == '}':
                self.pos += 1
                return res
            if self.pos >= len(self.text) or self.text[self.pos] != ',':
                raise JSONError("Expected comma or closing brace in object")
            self.pos += 1  # skip ,

def parse(text: str):
    try:
        parser = JSONParser(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != len(text):
            return None  # Trailing garbage
        return result
    except (JSONError, ValueError, IndexError):
        return None
