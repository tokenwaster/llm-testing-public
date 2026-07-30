class ParseError(Exception):
    pass


class Parser:
    def __init__(self, text: str):
        self.text = text
        self.idx = 0

    def peek(self):
        if self.idx < len(self.text):
            return self.text[self.idx]
        return None

    def consume(self):
        ch = self.peek()
        if ch is not None:
            self.idx += 1
        return ch

    def skip_whitespace(self):
        while self.peek() in (' ', '\t', '\n', '\r'):
            self.idx += 1

    def expect(self, char: str):
        if self.peek() == char:
            self.consume()
        else:
            raise ParseError(f"expected '{char}'")

    def parse_value(self):
        self.skip_whitespace()
        ch = self.peek()
        if ch == '{':
            return self.parse_object()
        elif ch == '[':
            return self.parse_array()
        elif ch == '"':
            return self.parse_string()
        elif ch == 't':
            return self.parse_true()
        elif ch == 'f':
            return self.parse_false()
        elif ch == 'n':
            return self.parse_null()
        elif ch == '-' or (ch is not None and ch.isdigit()):
            return self.parse_number()
        else:
            raise ParseError(f"unexpected character: {ch}")

    def parse_object(self):
        self.expect('{')
        self.skip_whitespace()
        obj = {}
        if self.peek() == '}':
            self.consume()
            return obj
        while True:
            key = self.parse_string()
            self.skip_whitespace()
            self.expect(':')
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            ch = self.peek()
            if ch == '}':
                self.consume()
                break
            self.expect(',')
            self.skip_whitespace()
        return obj

    def parse_array(self):
        self.expect('[')
        self.skip_whitespace()
        arr = []
        if self.peek() == ']':
            self.consume()
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            ch = self.peek()
            if ch == ']':
                self.consume()
                break
            self.expect(',')
            self.skip_whitespace()
        return arr

    def parse_string(self):
        self.expect('"')
        result = []
        while True:
            ch = self.peek()
            if ch is None:
                raise ParseError("unterminated string")
            if ch == '"':
                self.consume()
                break
            if ch == '\\':
                self.consume()
                esc = self.peek()
                if esc is None:
                    raise ParseError("incomplete escape")
                self.consume()
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
                    hex_digits = self.text[self.idx:self.idx + 4]
                    if len(hex_digits) != 4:
                        raise ParseError("invalid unicode escape")
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_digits):
                        raise ParseError("invalid unicode escape")
                    self.idx += 4
                    code = int(hex_digits, 16)
                    result.append(chr(code))
                else:
                    raise ParseError(f"invalid escape: \\{esc}")
            else:
                if ord(ch) < 0x20:
                    raise ParseError("control character in string")
                self.consume()
                result.append(ch)
        return ''.join(result)

    def parse_number(self):
        start = self.idx
        if self.peek() == '-':
            self.consume()
        if self.peek() == '0':
            self.consume()
            if self.peek() is not None and self.peek().isdigit():
                raise ParseError("leading zero")
        elif self.peek() is not None and self.peek().isdigit():
            self.consume()
            while self.peek() is not None and self.peek().isdigit():
                self.consume()
        else:
            raise ParseError("expected digit")
        is_float = False
        if self.peek() == '.':
            self.consume()
            is_float = True
            if not (self.peek() is not None and self.peek().isdigit()):
                raise ParseError("expected digit after decimal point")
            while self.peek() is not None and self.peek().isdigit():
                self.consume()
        if self.peek() in ('e', 'E'):
            self.consume()
            is_float = True
            if self.peek() in ('+', '-'):
                self.consume()
            if not (self.peek() is not None and self.peek().isdigit()):
                raise ParseError("expected digit in exponent")
            while self.peek() is not None and self.peek().isdigit():
                self.consume()
        num_str = self.text[start:self.idx]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)

    def parse_true(self):
        if self.text.startswith('true', self.idx):
            self.idx += 4
            return True
        raise ParseError("expected true")

    def parse_false(self):
        if self.text.startswith('false', self.idx):
            self.idx += 5
            return False
        raise ParseError("expected false")

    def parse_null(self):
        if self.text.startswith('null', self.idx):
            self.idx += 4
            return None
        raise ParseError("expected null")


def parse(text: str):
    parser = Parser(text)
    try:
        value = parser.parse_value()
        parser.skip_whitespace()
        if parser.idx != len(parser.text):
            raise ParseError("trailing garbage")
        return value
    except ParseError:
        return None
