def parse(text: str):
    if not isinstance(text, str):
        return None

    class Parser:
        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.length = len(text)

        def error(self):
            raise ValueError("Invalid JSON")

        def peek(self):
            if self.pos < self.length:
                return self.text[self.pos]
            return None

        def consume(self):
            char = self.peek()
            self.pos += 1
            return char

        def skip_whitespace(self):
            while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
                self.pos += 1

        def parse(self):
            self.skip_whitespace()
            if self.pos == self.length:
                self.error()
            
            result = self.parse_value()
            
            self.skip_whitespace()
            if self.pos < self.length:
                self.error()
            
            return result

        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= self.length:
                self.error()
            
            char = self.text[self.pos]
            
            if char == '{':
                return self.parse_object()
            elif char == '[':
                return self.parse_array()
            elif char == '"':
                return self.parse_string()
            elif char == '-' or ('0' <= char <= '9'):
                return self.parse_number()
            else:
                # Literals
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
                    self.error()

        def parse_object(self):
            self.consume() # consume {
            self.skip_whitespace()
            
            if self.pos < self.length and self.text[self.pos] == '}':
                self.consume()
                return {}
            
            result = {}
            while True:
                self.skip_whitespace()
                if self.pos >= self.length:
                    self.error()
                
                if self.text[self.pos] != '"':
                    self.error()
                
                key = self.parse_string()
                
                self.skip_whitespace()
                if self.pos >= self.length or self.text[self.pos] != ':':
                    self.error()
                self.consume() # consume :
                
                self.skip_whitespace()
                value = self.parse_value()
                
                result[key] = value
                
                self.skip_whitespace()
                if self.pos >= self.length:
                    self.error()
                
                if self.text[self.pos] == '}':
                    self.consume()
                    return result
                elif self.text[self.pos] == ',':
                    self.consume()
                else:
                    self.error()

        def parse_array(self):
            self.consume() # consume [
            self.skip_whitespace()
            
            if self.pos < self.length and self.text[self.pos] == ']':
                self.consume()
                return []
            
            result = []
            while True:
                self.skip_whitespace()
                if self.pos >= self.length:
                    self.error()
                
                value = self.parse_value()
                result.append(value)
                
                self.skip_whitespace()
                if self.pos >= self.length:
                    self.error()
                
                if self.text[self.pos] == ']':
                    self.consume()
                    return result
                elif self.text[self.pos] == ',':
                    self.consume()
                else:
                    self.error()

        def parse_string(self):
            self.consume() # consume "
            chars = []
            while self.pos < self.length:
                char = self.text[self.pos]
                if char == '"':
                    self.consume()
                    return "".join(chars)
                elif char == '\\':
                    self.consume() # consume \
                    if self.pos >= self.length:
                        self.error()
                    
                    esc = self.text[self.pos]
                    if esc == '"':
                        chars.append('"')
                        self.consume()
                    elif esc == '\\':
                        chars.append('\\')
                        self.consume()
                    elif esc == '/':
                        chars.append('/')
                        self.consume()
                    elif esc == 'b':
                        chars.append('\b')
                        self.consume()
                    elif esc == 'f':
                        chars.append('\f')
                        self.consume()
                    elif esc == 'n':
                        chars.append('\n')
                        self.consume()
                    elif esc == 'r':
                        chars.append('\r')
                        self.consume()
                    elif esc == 't':
                        chars.append('\t')
                        self.consume()
                    elif esc == 'u':
                        if self.pos + 4 >= self.length:
                            self.error()
                        hex_str = self.text[self.pos+1:self.pos+5]
                        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                            self.error()
                        code_point = int(hex_str, 16)
                        chars.append(chr(code_point))
                        self.pos += 5
                    else:
                        self.error()
                else:
                    if ord(char) < 0x20:
                        self.error()
                    chars.append(char)
                    self.consume()
            self.error() # Unterminated string

        def parse_number(self):
            start_pos = self.pos
            is_float = False
            
            if self.pos < self.length and self.text[self.pos] == '-':
                self.pos += 1
            
            if self.pos >= self.length or not ('0' <= self.text[self.pos] <= '9'):
                self.error()
            
            # Integer part
            if self.text[self.pos] == '0':
                self.pos += 1
                if self.pos < self.length and '0' <= self.text[self.pos] <= '9':
                    self.error()
            else:
                while self.pos < self.length and '0' <= self.text[self.pos] <= '9':
                    self.pos += 1
            
            # Fractional part
            if self.pos < self.length and self.text[self.pos] == '.':
                is_float = True
                self.pos += 1
                if self.pos >= self.length or not ('0' <= self.text[self.pos] <= '9'):
                    self.error()
                while self.pos < self.length and '0' <= self.text[self.pos] <= '9':
                    self.pos += 1
            
            # Exponent
            if self.pos < self.length and self.text[self.pos] in ('e', 'E'):
                is_float = True
                self.pos += 1
                if self.pos < self.length and self.text[self.pos] in ('+', '-'):
                    self.pos += 1
                if self.pos >= self.length or not ('0' <= self.text[self.pos] <= '9'):
                    self.error()
                while self.pos < self.length and '0' <= self.text[self.pos] <= '9':
                    self.pos += 1
            
            number_str = self.text[start_pos:self.pos]
            
            if is_float:
                try:
                    return float(number_str)
                except ValueError:
                    self.error()
            else:
                try:
                    return int(number_str)
                except ValueError:
                    self.error()

    try:
        parser = Parser(text)
        return parser.parse()
    except Exception:
        return None
