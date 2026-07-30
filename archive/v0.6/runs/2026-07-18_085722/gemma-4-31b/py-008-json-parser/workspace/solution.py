def parse(text):
    """
    Parses a JSON document and returns the equivalent Python object.
    Returns None if the input is not valid JSON.
    """
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
                raise ValueError("Unexpected end of input")
            
            char = self.text[self.pos]
            if char == '{':
                return self.parse_object()
            elif char == '[':
                return self.parse_array()
            elif char == '"':
                return self.parse_string()
            elif char == 't' or char == 'f' or char == 'n':
                return self.parse_constant()
            elif char == '-' or char.isdigit():
                return self.parse_number()
            else:
                raise ValueError(f"Unexpected character {char}")

        def parse_string(self):
            self.pos += 1  # skip opening quote
            res = []
            while self.pos < len(self.text) and self.text[self.pos] != '"':
                char = self.text[self.pos]
                if char == '\\':
                    self.pos += 1
                    if self.pos >= len(self.text):
                        raise ValueError("Unterminated escape sequence")
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
                        hex_val = self.text[self.pos:self.pos+4]
                        if len(hex_val) < 4:
                            raise ValueError("Invalid unicode escape")
                        try:
                            res.append(chr(int(hex_val, 16)))
                        except ValueError:
                            raise ValueError("Invalid hex in unicode escape")
                        self.pos += 3
                    else:
                        raise ValueError(f"Invalid escape sequence \\{esc}")
                else:
                    res.append(char)
                self.pos += 1
            
            if self.pos >= len(self.text):
                raise ValueError("Unterminated string")
            self.pos += 1  # skip closing quote
            return "".join(res)

        def parse_number(self):
            start = self.pos
            is_float = False
            if self.text[self.pos] == '-':
                self.pos += 1
            
            if self.pos >= len(self.text):
                raise ValueError("Number interrupted")

            # Integer part
            if self.text[self.pos] == '0':
                self.pos += 1
                if self.pos < len(self.text) and self.text[self.pos].isdigit():
                    raise ValueError("Leading zeros not allowed")
            else:
                if not self.text[self.pos].isdigit():
                    raise ValueError("Invalid number start")
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1

            # Fractional part
            if self.pos < len(self.text) and self.text[self.pos] == '.':
                is_float = True
                self.pos += 1
                if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                    raise ValueError("Missing digits after decimal point")
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1

            # Exponent part
            if self.pos < len(self.text) and self.text[self.pos] in 'eE':
                is_float = True
                self.pos += 1
                if self.pos < len(self.text) and self.text[self.pos] in '+-':
                    self.pos += 1
                if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                    raise ValueError("Invalid exponent")
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1

            num_str = self.text[start:self.pos]
            try:
                return float(num_str) if is_float else int(num_str)
            except ValueError:
                raise ValueError("Invalid number format")

        def parse_constant(self):
            if self.text.startswith('true', self.pos):
                self.pos += 4
                return True
            elif self.text.startswith('false', self.pos):
                self.pos += 5
                return False
            elif self.text.startswith('null', self.pos):
                self.pos += 4
                return None
            else:
                raise ValueError("Invalid constant")

        def parse_array(self):
            self.pos += 1  # skip [
            arr = []
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            
            while True:
                val = self.parse_value()
                arr.append(val)
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == ']':
                    self.pos += 1
                    return arr
                if self.pos >= len(self.text) or self.text[self.pos] != ',':
                    raise ValueError("Expected comma or ] in array")
                self.pos += 1  # skip ,
                self.skip_whitespace()

        def parse_object(self):
            self.pos += 1  # skip {
            obj = {}
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            
            while True:
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != '"':
                    raise ValueError("Object keys must be strings")
                key = self.parse_string()
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != ':':
                    raise ValueError("Expected colon in object")
                self.pos += 1  # skip :
                val = self.parse_value()
                obj[key] = val
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    self.pos += 1
                    return obj
                if self.pos >= len(self.text) or self.text[self.pos] != ',':
                    raise ValueError("Expected comma or } in object")
                self.pos += 1  # skip ,

    try:
        parser = JSONParser(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(text):
            return None  # Trailing garbage
        return result
    except (ValueError, IndexError):
        return None
