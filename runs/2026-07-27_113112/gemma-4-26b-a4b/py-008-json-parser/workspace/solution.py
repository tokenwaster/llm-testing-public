class JSONParseError(Exception):
    pass

class Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \n\r\t':
            self.pos += 1

    def peek(self):
        if self.pos < len(self.text):
            return self.text[self.pos]
        return None

    def consume(self, expected=None):
        if self.pos >= len(self.text):
            raise JSONParseError("EOF")
        char = self.text[self.pos]
        if expected is not None and char != expected:
            raise JSONParseError(f"Expected {expected}, got {char}")
        self.pos += 1
        return char

    def parse_value(self):
        self.skip_whitespace()
        char = self.peek()
        if char == '{':
            return self.parse_object()
        elif char == '[':
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char is not None and (char == '-' or '0' <= char <= '9'):
            return self.parse_number()
        elif char == 't':
            return self.parse_literal('true', True)
        elif char == 'f':
            return self.parse_literal('false', False)
        elif char == 'n':
            return self.parse_literal('null', None)
        else:
            raise JSONParseError("Invalid value")

    def parse_literal(self, literal, value):
        for char in literal:
            self.consume(char)
        next_char = self.peek()
        if next_char is not None and (('a' <= next_char <= 'z') or 
                                      ('A' <= next_char <= 'Z') or 
                                      ('0' <= next_char <= '9') or 
                                      next_char == '_'):
            raise JSONParseError("Invalid literal")
        return value

    def parse_string(self):
        self.consume('"')
        res = []
        while self.pos < len(self.text):
            char = self.consume()
            if char == '"':
                return "".join(res)
            elif char == '\\':
                esc = self.consume()
                if esc == '"': res.append('"')
                elif esc == '\\': res.append('\\')
                elif esc == '/': res.append('/')
                elif esc == 'b': res.append('\b')
                elif esc == 'f': res.append('\f')
                elif esc == 'n': res.append('\n')
                elif esc == 'r': res.append('\r')
                elif esc == 't': res.append('\t')
                elif esc == 'u':
                    hex_digits = ""
                    for _ in range(4):
                        h = self.consume()
                        if not (('0' <= h <= '9') or ('a' <= h <= 'f') or ('A' <= h <= 'F')):
                            raise JSONParseError("Invalid unicode escape")
                        hex_digits += h
                    res.append(chr(int(hex_digits, 16)))
                else:
                    raise JSONParseError("Invalid escape sequence")
            elif ord(char) < 32:
                raise JSONParseError("Control character error")
            else:
                res.append(char)
        raise JSONParseError("Unterminated string")

    def parse_number(self):
        start = self.pos
        if self.peek() == '-':
            self.consume('-')
        
        # Integer part validation (handle 0 and leading zero error)
        if self.peek() == '0':
            self.consume('0')
            if self.peek() is not None and '0' <= self.peek() <= '9':
                raise JSONParseError("Leading zero error")
        elif self.peek() is not None and '1' <= self.peek() <= '9':
            while self.peek() is not None and '0' <= self.peek() <= '9':
                self.consume()
        else:
            raise JSONParseError("Invalid number")

        # Fractional part
        if self.peek() == '.':
            self.consume('.')
            if self.peek() is None or not ('0' <= self.peek() <= '9'):
                raise JSONParseError("Incomplete fractional part")
            while self.peek() is not None and '0' <= self.peek() <= '9':
                self.consume()

        # Exponent part
        if self.peek() in 'eE':
            self.consume()
            if self.peek() in '+-':
                self.consume()
            if self.peek() is None or not ('0' <= self.peek() <= '9'):
                raise JSONParseError("Incomplete exponent part")
            while self.peek() is not None and '0' <= self.peek() <= '9':
                self.consume()

        num_str = self.text[start:self.pos]
        try:
            if '.' in num_str or 'e' in num_str.lower():
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            raise JSONParseError("Failed to parse number")

    def parse_object(self):
        self.consume('{')
        obj = {}
        self.skip_whitespace()
        if self.peek() == '}':
            self.consume('}')
            return obj

        while True:
            self.skip_whitespace()
            if self.peek() != '"':
                raise JSONParseError("Object key must be string")
            key = self.parse_string()
            self.skip_whitespace()
            self.consume(':')
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            char = self.peek()
            if char == '}':
                self.consume('}')
                return obj
            elif char == ',':
                self.consume(',')
                self.skip_whitespace()
                if self.peek() == '}':
                    raise JSONParseError("Trailing comma in object")
            else:
                raise JSONParseError("Missing comma or end of object")

    def parse_array(self):
        self.consume('[')
        arr = []
        self.skip_whitespace()
        if self.peek() == ']':
            self.consume(']')
            return arr

        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            char = self.peek()
            if char == ']':
                self.consume(']')
                return arr
            elif char == ',':
                self.consume(',')
                self.skip_whitespace()
                if self.peek() == ']':
                    raise JSONParseError("Trailing comma in array")
            else:
                raise JSONParseError("Missing comma or end of array")

def parse(text: str):
    try:
        parser = Parser(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(text):
            return None # Trailing garbage
        return result
    except Exception:
        return None
