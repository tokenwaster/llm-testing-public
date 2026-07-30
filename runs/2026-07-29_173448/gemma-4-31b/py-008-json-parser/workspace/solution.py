import collections

def parse(text):
    """
    Parses a JSON document and returns the equivalent Python object.
    Returns None if the input is not valid JSON.
    """
    class JSONParser:
        def __init__(self, text):
            self.text = text
            self.pos = 0

        def peek(self):
            return self.text[self.pos] if self.pos < len(self.text) else None

        def consume(self):
            char = self.peek()
            if char is not None:
                self.pos += 1
            return char

        def skip_whitespace(self):
            while self.pos < len(self.text) and self.text[self.pos] in ' \n\r\t':
                self.pos += 1

        def parse_value(self):
            self.skip_whitespace()
            char = self.peek()
            if char is None:
                raise ValueError("Unexpected end of input")

            if char == '{':
                return self.parse_object()
            elif char == '[':
                return self.parse_array()
            elif char == '"':
                return self.parse_string()
            elif char == '-' or char.isdigit():
                return self.parse_number()
            elif char == 't':
                return self.parse_literal('true', True)
            elif char == 'f':
                return self.parse_literal('false', False)
            elif char == 'n':
                return self.parse_literal('null', None)
            else:
                raise ValueError(f"Unexpected character {char}")

        def parse_literal(self, literal, value):
            for char in literal:
                if self.consume() != char:
                    raise ValueError(f"Expected {literal}")
            return value

        def parse_string(self):
            self.consume() # Consume opening quote "
            res = []
            while True:
                char = self.consume()
                if char is None:
                    raise ValueError("Unterminated string")
                if char == '"':
                    break
                if char == '\\':
                    esc = self.consume()
                    if esc is None:
                        raise ValueError("Trailing backslash")
                    escapes = {
                        '"': '"', '\\': '\\', '/': '/',
                        'b': '\x08', 'f': '\x0c', 'n': '\n', 
                        'r': '\r', 't': '\t'
                    }
                    if esc in escapes:
                        res.append(escapes[esc])
                    elif esc == 'u':
                        hex_chars = []
                        for _ in range(4):
                            h = self.consume()
                            if h is None or h not in '0123456789abcdefABCDEF':
                                raise ValueError("Invalid unicode escape")
                            hex_chars.append(h)
                        res.append(chr(int("".join(hex_chars), 16)))
                    else:
                        raise ValueError(f"Invalid escape sequence \\{esc}")
                else:
                    res.append(char)
            return "".join(res)

        def parse_number(self):
            start = self.pos
            is_float = False
            
            if self.peek() == '-':
                self.consume()
            
            char = self.peek()
            if char == '0':
                self.consume()
                if self.peek() and self.peek().isdigit():
                    raise ValueError("Leading zero not allowed")
            elif char is not None and char.isdigit():
                while self.peek() and self.peek().isdigit():
                    self.consume()
            else:
                raise ValueError("Invalid number format")

            if self.peek() == '.':
                is_float = True
                self.consume()
                if self.peek() is None or not self.peek().isdigit():
                    raise ValueError("Expected digits after decimal point")
                while self.peek() and self.peek().isdigit():
                    self.consume()

            if self.peek() in 'eE':
                is_float = True
                self.consume()
                if self.peek() in '+-':
                    self.consume()
                if self.peek() is None or not self.peek().isdigit():
                    raise ValueError("Expected digits after exponent")
                while self.peek() and self.peek().isdigit():
                    self.consume()

            num_str = self.text[start:self.pos]
            try:
                return float(num_str) if is_float else int(num_str)
            except ValueError:
                raise ValueError("Failed to convert number")

        def parse_array(self):
            self.consume() # Consume [
            res = []
            self.skip_whitespace()
            if self.peek() == ']':
                self.consume()
                return res
            
            while True:
                res.append(self.parse_value())
                self.skip_whitespace()
                char = self.consume()
                if char == ']':
                    break
                elif char == ',':
                    self.skip_whitespace()
                    if self.peek() == ']':
                        raise ValueError("Trailing comma in array")
                else:
                    raise ValueError(f"Expected ',' or ']' in array, got {char}")
            return res

        def parse_object(self):
            self.consume() # Consume {
            res = {}
            self.skip_whitespace()
            if self.peek() == '}':
                self.consume()
                return res
            
            while True:
                self.skip_whitespace()
                if self.peek() != '"':
                    raise ValueError("Object keys must be strings")
                key = self.parse_string()
                self.skip_whitespace()
                if self.consume() != ':':
                    raise ValueError("Expected ':' after key")
                val = self.parse_value()
                res[key] = val
                self.skip_whitespace()
                char = self.consume()
                if char == '}':
                    break
                elif char == ',':
                    self.skip_whitespace()
                    if self.peek() == '}':
                        raise ValueError("Trailing comma in object")
                else:
                    raise ValueError(f"Expected ',' or '}}' in object, got {char}")
            return res

    try:
        parser = JSONParser(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(text):
            return None # Trailing garbage
        return result
    except (ValueError, IndexError):
        return None
