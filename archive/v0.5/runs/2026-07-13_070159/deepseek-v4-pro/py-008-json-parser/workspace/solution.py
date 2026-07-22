def parse(text: str):
    class _JSONParser:
        def __init__(self, text):
            self.text = text
            self.i = 0
            self.n = len(text)

        def skip_whitespace(self):
            while self.i < self.n and self.text[self.i] in ' \t\n\r':
                self.i += 1

        def peek(self):
            if self.i < self.n:
                return self.text[self.i]
            return None

        def advance(self):
            if self.i < self.n:
                c = self.text[self.i]
                self.i += 1
                return c
            return None

        def parse_value(self):
            self.skip_whitespace()
            c = self.peek()
            if c is None:
                raise ValueError("Empty input")
            if c == '{':
                return self.parse_object()
            elif c == '[':
                return self.parse_array()
            elif c == '"':
                return self.parse_string()
            elif c == '-' or c.isdigit():
                return self.parse_number()
            elif self.text.startswith('true', self.i):
                self.i += 4
                if self.i < self.n and self.text[self.i].isalnum():
                    raise ValueError
                return True
            elif self.text.startswith('false', self.i):
                self.i += 5
                if self.i < self.n and self.text[self.i].isalnum():
                    raise ValueError
                return False
            elif self.text.startswith('null', self.i):
                self.i += 4
                if self.i < self.n and self.text[self.i].isalnum():
                    raise ValueError
                return None
            else:
                raise ValueError("Invalid value")

        def parse_object(self):
            self.skip_whitespace()
            if self.peek() != '{':
                raise ValueError
            self.advance()
            obj = {}
            self.skip_whitespace()
            if self.peek() == '}':
                self.advance()
                return obj
            while True:
                self.skip_whitespace()
                if self.peek() != '"':
                    raise ValueError
                key = self.parse_string()
                self.skip_whitespace()
                if self.peek() != ':':
                    raise ValueError
                self.advance()
                self.skip_whitespace()
                value = self.parse_value()
                obj[key] = value
                self.skip_whitespace()
                if self.peek() == '}':
                    self.advance()
                    break
                elif self.peek() == ',':
                    self.advance()
                    self.skip_whitespace()
                    if self.peek() == '}':
                        raise ValueError("Trailing comma")
                else:
                    raise ValueError
            return obj

        def parse_array(self):
            self.skip_whitespace()
            if self.peek() != '[':
                raise ValueError
            self.advance()
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
                if self.peek() == ']':
                    self.advance()
                    break
                elif self.peek() == ',':
                    self.advance()
                    self.skip_whitespace()
                    if self.peek() == ']':
                        raise ValueError("Trailing comma")
                else:
                    raise ValueError
            return arr

        def parse_string(self):
            self.skip_whitespace()
            if self.peek() != '"':
                raise ValueError
            self.advance()
            result = []
            high_surrogate = None
            while True:
                if self.i >= self.n:
                    if high_surrogate is not None:
                        raise ValueError
                    raise ValueError("Unterminated string")
                c = self.advance()
                if c == '"':
                    if high_surrogate is not None:
                        raise ValueError
                    break
                elif c == '\\':
                    if self.i >= self.n:
                        raise ValueError
                    esc = self.advance()
                    if esc == '"':
                        result.append('"')
                    elif esc == '\\':
                        result.append('\\')
                    elif esc == '/':
                        result.append('/')
                    elif esc == 'b':
                        result.append('\b')
                    elif esc == 'f':
                        result.append('\f')
                    elif esc == 'n':
                        result.append('\n')
                    elif esc == 'r':
                        result.append('\r')
                    elif esc == 't':
                        result.append('\t')
                    elif esc == 'u':
                        hex_digits = self.text[self.i:self.i+4]
                        if len(hex_digits) != 4 or not all(c in '0123456789abcdefABCDEF' for c in hex_digits):
                            raise ValueError
                        self.i += 4
                        code_point = int(hex_digits, 16)
                        if 0xD800 <= code_point <= 0xDBFF:  # high surrogate
                            if high_surrogate is not None:
                                raise ValueError
                            high_surrogate = code_point
                        elif 0xDC00 <= code_point <= 0xDFFF:  # low surrogate
                            if high_surrogate is None:
                                raise ValueError
                            combined = 0x10000 + (high_surrogate - 0xD800) * 0x400 + (code_point - 0xDC00)
                            result.append(chr(combined))
                            high_surrogate = None
                        else:  # normal BMP character
                            if high_surrogate is not None:
                                raise ValueError
                            result.append(chr(code_point))
                    else:
                        raise ValueError
                else:
                    if ord(c) < 0x20:
                        raise ValueError
                    if high_surrogate is not None:
                        raise ValueError
                    result.append(c)
            return ''.join(result)

        def parse_number(self):
            start = self.i
            if self.peek() == '-':
                self.advance()
            if self.peek() is None:
                raise ValueError
            if self.peek() == '0':
                self.advance()
                if self.peek() is not None and self.peek().isdigit():
                    raise ValueError
            elif self.peek().isdigit():
                while self.peek() is not None and self.peek().isdigit():
                    self.advance()
            else:
                raise ValueError
            if self.peek() == '.':
                self.advance()
                if not self.peek() or not self.peek().isdigit():
                    raise ValueError
                while self.peek() is not None and self.peek().isdigit():
                    self.advance()
            if self.peek() in ('e', 'E'):
                self.advance()
                if self.peek() in ('+', '-'):
                    self.advance()
                if not self.peek() or not self.peek().isdigit():
                    raise ValueError
                while self.peek() is not None and self.peek().isdigit():
                    self.advance()
            if self.i < self.n and self.peek().isalnum():
                raise ValueError
            num_str = self.text[start:self.i]
            if '.' in num_str or 'e' in num_str or 'E' in num_str:
                return float(num_str)
            else:
                return int(num_str)

        def parse(self):
            self.skip_whitespace()
            value = self.parse_value()
            self.skip_whitespace()
            if self.i != self.n:
                raise ValueError("Trailing garbage")
            return value

    try:
        parser = _JSONParser(text)
        return parser.parse()
    except (ValueError, IndexError, TypeError):
        return None
