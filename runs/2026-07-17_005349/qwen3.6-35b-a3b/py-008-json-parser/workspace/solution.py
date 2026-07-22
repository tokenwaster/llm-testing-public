def parse(text: str):
    class Parser:
        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.length = len(text)

        def parse(self):
            self.skip_ws()
            if self.pos >= self.length:
                return None
            val = self.parse_value()
            if val is None:
                return None
            self.skip_ws()
            if self.pos < self.length:
                return None
            return val

        def peek(self):
            if self.pos < self.length:
                return self.text[self.pos]
            return None

        def advance(self):
            self.pos += 1

        def skip_ws(self):
            while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
                self.pos += 1

        def expect(self, char):
            if self.peek() == char:
                self.advance()
                return True
            return False

        def parse_value(self):
            self.skip_ws()
            if self.pos >= self.length:
                return None
            ch = self.peek()
            if ch == '"':
                return self.parse_string()
            elif ch == '{':
                return self.parse_object()
            elif ch == '[':
                return self.parse_array()
            elif ch == 't':
                return self.parse_true()
            elif ch == 'f':
                return self.parse_false()
            elif ch == 'n':
                return self.parse_null()
            elif ch == '-' or ch.isdigit():
                return self.parse_number()
            else:
                return None

        def parse_string(self):
            if not self.expect('"'):
                return None
            chars = []
            while self.pos < self.length:
                ch = self.text[self.pos]
                if ch == '"':
                    self.advance()
                    return ''.join(chars)
                elif ch == '\\':
                    self.advance()
                    if self.pos >= self.length:
                        return None
                    esc = self.text[self.pos]
                    self.advance()
                    if esc == '"':
                        chars.append('"')
                    elif esc == '\\':
                        chars.append('\\')
                    elif esc == '/':
                        chars.append('/')
                    elif esc == 'b':
                        chars.append('\b')
                    elif esc == 'f':
                        chars.append('\f')
                    elif esc == 'n':
                        chars.append('\n')
                    elif esc == 'r':
                        chars.append('\r')
                    elif esc == 't':
                        chars.append('\t')
                    elif esc == 'u':
                        if self.pos + 4 > self.length:
                            return None
                        hex_str = self.text[self.pos+1:self.pos+5]
                        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                            return None
                        code_point = int(hex_str, 16)
                        chars.append(chr(code_point))
                        self.pos += 4
                    else:
                        return None
                else:
                    if ord(ch) < 0x20:
                        return None
                    chars.append(ch)
                    self.advance()
            return None

        def parse_number(self):
            start = self.pos
            if self.peek() == '-':
                self.advance()
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                return None
            if self.peek() == '0':
                self.advance()
                if self.pos < self.length and self.text[self.pos].isdigit():
                    return None
            else:
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.advance()
            
            if self.pos < self.length and self.text[self.pos] == '.':
                self.advance()
                if self.pos >= self.length or not self.text[self.pos].isdigit():
                    return None
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.advance()
            
            if self.pos < self.length and self.text[self.pos] in 'eE':
                self.advance()
                if self.pos < self.length and self.text[self.pos] in '+-':
                    self.advance()
                if self.pos >= self.length or not self.text[self.pos].isdigit():
                    return None
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.advance()
            
            num_str = self.text[start:self.pos]
            try:
                if '.' in num_str or 'e' in num_str.lower():
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                return None

        def parse_object(self):
            if not self.expect('{'):
                return None
            obj = {}
            self.skip_ws()
            if self.peek() == '}':
                self.advance()
                return obj
            while True:
                self.skip_ws()
                if self.peek() == '}':
                    self.advance()
                    return obj
                key = self.parse_string()
                if key is None:
                    return None
                self.skip_ws()
                if not self.expect(':'):
                    return None
                self.skip_ws()
                val = self.parse_value()
                if val is None:
                    return None
                obj[key] = val
                self.skip_ws()
                if self.peek() == '}':
                    self.advance()
                    return obj
                elif self.peek() == ',':
                    self.advance()
                else:
                    return None

        def parse_array(self):
            if not self.expect('['):
                return None
            arr = []
            self.skip_ws()
            if self.peek() == ']':
                self.advance()
                return arr
            while True:
                self.skip_ws()
                if self.peek() == ']':
                    self.advance()
                    return arr
                val = self.parse_value()
                if val is None:
                    return None
                arr.append(val)
                self.skip_ws()
                if self.peek() == ']':
                    self.advance()
                    return arr
                elif self.peek() == ',':
                    self.advance()
                else:
                    return None

        def parse_true(self):
            if self.text[self.pos:self.pos+4] == 'true':
                self.pos += 4
                return True
            return None

        def parse_false(self):
            if self.text[self.pos:self.pos+5] == 'false':
                self.pos += 5
                return False
            return None

        def parse_null(self):
            if self.text[self.pos:self.pos+4] == 'null':
                self.pos += 4
                return None
            return None

    parser = Parser(text)
    return parser.parse()
