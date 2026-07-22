def parse(text: str):
    try:
        parser = JSONParser(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(parser.text):
            raise ValueError("Trailing garbage")
        return result
    except Exception:
        return None

class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def peek(self):
        return self.text[self.pos] if self.pos < self.length else None

    def advance(self):
        if self.pos < self.length:
            self.pos += 1
            return self.text[self.pos - 1]
        return None

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= self.length:
            raise ValueError("Unexpected end of input")
        
        char = self.peek()
        if char == '{':
            return self.parse_object()
        elif char == '[':
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char == '-' or char in '0123456789':
            return self.parse_number()
        elif char == 't':
            return self.parse_true()
        elif char == 'f':
            return self.parse_false()
        elif char == 'n':
            return self.parse_null()
        else:
            raise ValueError(f"Unexpected character: {char}")

    def parse_object(self):
        if self.advance() != '{':
            raise ValueError("Expected '{'")
        
        obj = {}
        self.skip_whitespace()
        if self.peek() == '}':
            self.advance()
            return obj
            
        while True:
            self.skip_whitespace()
            if self.pos >= self.length or self.peek() != '"':
                raise ValueError("Expected string key")
            key = self.parse_string()
            
            self.skip_whitespace()
            if self.pos >= self.length or self.advance() != ':':
                raise ValueError("Expected ':'")
                
            self.skip_whitespace()
            value = self.parse_value()
            obj[key] = value
            
            self.skip_whitespace()
            if self.pos >= self.length:
                raise ValueError("Unterminated object")
            char = self.peek()
            if char == '}':
                self.advance()
                return obj
            elif char == ',':
                self.advance()
                self.skip_whitespace()
                if self.peek() == '}':
                    raise ValueError("Trailing comma in object")
            else:
                raise ValueError(f"Expected ',' or '}}'")

    def parse_array(self):
        if self.advance() != '[':
            raise ValueError("Expected '['")
            
        arr = []
        self.skip_whitespace()
        if self.peek() == ']':
            self.advance()
            return arr
            
        while True:
            self.skip_whitespace()
            value = self.parse_value()
            arr.append(value)
            
            self.skip_whitespace()
            if self.pos >= self.length:
                raise ValueError("Unterminated array")
            char = self.peek()
            if char == ']':
                self.advance()
                return arr
            elif char == ',':
                self.advance()
                self.skip_whitespace()
                if self.peek() == ']':
                    raise ValueError("Trailing comma in array")
            else:
                raise ValueError(f"Expected ',' or ']'")

    def parse_string(self):
        if self.advance() != '"':
            raise ValueError("Expected '\"'")
        
        result = []
        while True:
            if self.pos >= self.length:
                raise ValueError("Unterminated string")
            char = self.advance()
            if char == '"':
                return ''.join(result)
            elif char == '\\':
                if self.pos >= self.length:
                    raise ValueError("Unterminated escape")
                esc = self.advance()
                if esc == '"': result.append('"')
                elif esc == '\\': result.append('\\')
                elif esc == '/': result.append('/')
                elif esc == 'b': result.append('\b')
                elif esc == 'f': result.append('\f')
                elif esc == 'n': result.append('\n')
                elif esc == 'r': result.append('\r')
                elif esc == 't': result.append('\t')
                elif esc == 'u':
                    if self.pos + 4 > self.length:
                        raise ValueError("Invalid unicode escape")
                    hex_str = self.text[self.pos:self.pos+4]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ValueError("Invalid unicode escape")
                    result.append(chr(int(hex_str, 16)))
                    self.pos += 4
                else:
                    raise ValueError(f"Invalid escape character: {esc}")
            else:
                if ord(char) < 0x20:
                    raise ValueError("Unescaped control character")
                result.append(char)

    def parse_number(self):
        start = self.pos
        if self.peek() == '-':
            self.advance()
        
        if self.pos >= self.length or self.text[self.pos] not in '0123456789':
            raise ValueError("Invalid number")
            
        if self.text[self.pos] == '0':
            self.advance()
            if self.pos < self.length and self.text[self.pos] in '0123456789':
                raise ValueError("Leading zeros not allowed")
        else:
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.advance()
                
        is_float = False
        if self.pos < self.length and self.text[self.pos] == '.':
            is_float = True
            self.advance()
            if self.pos >= self.length or self.text[self.pos] not in '0123456789':
                raise ValueError("Invalid number after decimal point")
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.advance()
                
        if self.pos < self.length and self.text[self.pos] in ('e', 'E'):
            is_float = True
            self.advance()
            if self.pos < self.length and self.text[self.pos] in ('+', '-'):
                self.advance()
            if self.pos >= self.length or self.text[self.pos] not in '0123456789':
                raise ValueError("Invalid exponent")
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.advance()
                
        num_str = self.text[start:self.pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)

    def parse_true(self):
        self.expect_literal("true")
        return True

    def parse_false(self):
        self.expect_literal("false")
        return False

    def parse_null(self):
        self.expect_literal("null")
        return None

    def expect_literal(self, literal):
        if self.text[self.pos:self.pos+len(literal)] == literal:
            self.pos += len(literal)
        else:
            raise ValueError(f"Expected {literal}")
