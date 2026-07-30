class JSONDecodeError(Exception):
    pass

class Parser:
    def __init__(self, text: str):
        self.text = text
        self.length = len(text)
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def peek(self):
        if self.pos < self.length:
            return self.text[self.pos]
        return None

    def get_char(self):
        if self.pos < self.length:
            char = self.text[self.pos]
            self.pos += 1
            return char
        raise JSONDecodeError("Unexpected EOF")

    def match(self, expected):
        if self.pos < self.length and self.text[self.pos] == expected:
            self.pos += 1
            return True
        return False

    def expect(self, expected):
        if not self.match(expected):
            raise JSONDecodeError(f"Expected '{expected}' at position {self.pos}")

    def parse_value(self):
        self.skip_whitespace()
        char = self.peek()
        if char is None:
            raise JSONDecodeError("Unexpected EOF")
        
        if char == '{':
            return self.parse_object()
        elif char == '[':
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char in '-0123456789':
            return self.parse_number()
        elif char == 't':
            return self.parse_literal('true', True)
        elif char == 'f':
            return self.parse_literal('false', False)
        elif char == 'n':
            return self.parse_literal('null', None)
        else:
            raise JSONDecodeError(f"Unexpected character '{char}'")

    def parse_literal(self, literal, value):
        for char in literal:
            if self.get_char() != char:
                raise JSONDecodeError(f"Expected literal '{literal}'")
        return value

    def parse_string(self):
        self.expect('"')
        result = []
        while True:
            char = self.get_char()
            if char == '"':
                break
            elif char == '\\':
                escape = self.get_char()
                if escape == '"':
                    result.append('"')
                elif escape == '\\':
                    result.append('\\')
                elif escape == '/':
                    result.append('/')
                elif escape == 'b':
                    result.append('\b')
                elif escape == 'f':
                    result.append('\f')
                elif escape == 'n':
                    result.append('\n')
                elif escape == 'r':
                    result.append('\r')
                elif escape == 't':
                    result.append('\t')
                elif escape == 'u':
                    # Read 4 hex digits
                    hex_str = ""
                    for _ in range(4):
                        h = self.get_char()
                        if h not in '0123456789abcdefABCDEF':
                            raise JSONDecodeError("Invalid unicode escape")
                        hex_str += h
                    code = int(hex_str, 16)
                    
                    # Handle UTF-16 surrogate pairs
                    if 0xD800 <= code <= 0xDBFF:
                        pos_before = self.pos
                        try:
                            if self.get_char() == '\\' and self.get_char() == 'u':
                                next_hex = ""
                                for _ in range(4):
                                    h = self.get_char()
                                    if h not in '0123456789abcdefABCDEF':
                                        raise JSONDecodeError("Invalid unicode escape")
                                    next_hex += h
                                next_code = int(next_hex, 16)
                                if 0xDC00 <= next_code <= 0xDFFF:
                                    code = 0x10000 + ((code - 0xD800) << 10) + (next_code - 0xDC00)
                                else:
                                    self.pos = pos_before
                            else:
                                self.pos = pos_before
                        except JSONDecodeError:
                            self.pos = pos_before
                    result.append(chr(code))
                else:
                    raise JSONDecodeError(f"Invalid escape sequence '\\{escape}'")
            else:
                if ord(char) < 0x20:
                    raise JSONDecodeError("Unescaped control character in string")
                result.append(char)
        return "".join(result)

    def parse_number(self):
        start_pos = self.pos
        
        if self.peek() == '-':
            self.get_char()
            
        if self.peek() == '0':
            self.get_char()
            if self.peek() in '0123456789':
                raise JSONDecodeError("Leading zeros are not allowed")
        elif self.peek() in '123456789':
            self.get_char()
            while self.peek() in '0123456789':
                self.get_char()
        else:
            raise JSONDecodeError("Expected digit")
            
        is_float = False
        
        if self.peek() == '.':
            is_float = True
            self.get_char()
            if self.peek() not in '0123456789':
                raise JSONDecodeError("Expected digit after decimal point")
            while self.peek() in '0123456789':
                self.get_char()
                
        if self.peek() in 'eE':
            is_float = True
            self.get_char()
            if self.peek() in '+-':
                self.get_char()
            if self.peek() not in '0123456789':
                raise JSONDecodeError("Expected digit in exponent")
            while self.peek() in '0123456789':
                self.get_char()
                
        num_str = self.text[start_pos:self.pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)

    def parse_array(self):
        self.expect('[')
        self.skip_whitespace()
        if self.match(']'):
            return []
            
        elements = []
        while True:
            elements.append(self.parse_value())
            self.skip_whitespace()
            if self.match(']'):
                break
            self.expect(',')
            self.skip_whitespace()
        return elements

    def parse_object(self):
        self.expect('{')
        self.skip_whitespace()
        if self.match('}'):
            return {}
            
        obj = {}
        while True:
            self.skip_whitespace()
            if self.peek() != '"':
                raise JSONDecodeError("Expected string key")
            key = self.parse_string()
            self.skip_whitespace()
            self.expect(':')
            val = self.parse_value()
            obj[key] = val
            self.skip_whitespace()
            if self.match('}'):
                break
            self.expect(',')
        return obj

def parse(text: str):
    parser = Parser(text)
    try:
        parser.skip_whitespace()
        if parser.pos == parser.length:
            return None
        val = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != parser.length:
            return None
        return val
    except JSONDecodeError:
        return None
