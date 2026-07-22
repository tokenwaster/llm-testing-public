def parse(text: str):
    if not isinstance(text, str):
        return None
    parser = _Parser(text)
    try:
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != len(parser.text):
            return None
        return result
    except (_ParseError, RecursionError):
        return None


class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def error(self):
        raise _ParseError()

    def peek(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        c = self.peek()
        if c is None:
            self.error()
        if c == '{':
            return self.parse_object()
        if c == '[':
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == '-' or ('0' <= c <= '9'):
            return self.parse_number()
        if c == 't':
            return self.parse_literal('true', True)
        if c == 'f':
            return self.parse_literal('false', False)
        if c == 'n':
            return self.parse_literal('null', None)
        self.error()

    def parse_literal(self, literal, value):
        if self.text[self.pos:self.pos + len(literal)] == literal:
            self.pos += len(literal)
            return value
        self.error()

    def parse_object(self):
        self.pos += 1
        obj = {}
        self.skip_whitespace()
        if self.peek() == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            if self.peek() != '"':
                self.error()
            key = self.parse_string()
            self.skip_whitespace()
            if self.peek() != ':':
                self.error()
            self.pos += 1
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            c = self.peek()
            if c == ',':
                self.pos += 1
                continue
            elif c == '}':
                self.pos += 1
                return obj
            else:
                self.error()

    def parse_array(self):
        self.pos += 1
        arr = []
        self.skip_whitespace()
        if self.peek() == ']':
            self.pos += 1
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            c = self.peek()
            if c == ',':
                self.pos += 1
                continue
            elif c == ']':
                self.pos += 1
                return arr
            else:
                self.error()

    def parse_string(self):
        self.pos += 1
        chars = []
        while True:
            c = self.peek()
            if c is None:
                self.error()
            if c == '"':
                self.pos += 1
                return ''.join(chars)
            if c == '\\':
                self.pos += 1
                e = self.peek()
                if e is None:
                    self.error()
                if e == '"':
                    chars.append('"')
                elif e == '\\':
                    chars.append('\\')
                elif e == '/':
                    chars.append('/')
                elif e == 'b':
                    chars.append('\b')
                elif e == 'f':
                    chars.append('\f')
                elif e == 'n':
                    chars.append('\n')
                elif e == 'r':
                    chars.append('\r')
                elif e == 't':
                    chars.append('\t')
                elif e == 'u':
                    hex_str = self.text[self.pos + 1:self.pos + 5]
                    if len(hex_str) != 4 or not all(
                        h in '0123456789abcdefABCDEF' for h in hex_str
                    ):
                        self.error()
                    code = int(hex_str, 16)
                    self.pos += 4
                    if 0xD800 <= code <= 0xDBFF:
                        if self.text[self.pos + 1:self.pos + 3] == '\\u':
                            hex2 = self.text[self.pos + 3:self.pos + 7]
                            if len(hex2) == 4 and all(
                                h in '0123456789abcdefABCDEF' for h in hex2
                            ):
                                code2 = int(hex2, 16)
                                if 0xDC00 <= code2 <= 0xDFFF:
                                    code = 0x10000 + (
                                        (code - 0xD800) << 10
                                    ) + (code2 - 0xDC00)
                                    self.pos += 6
                    chars.append(chr(code))
                else:
                    self.error()
                self.pos += 1
            else:
                if ord(c) < 0x20:
                    self.error()
                chars.append(c)
                self.pos += 1

    def parse_number(self):
        start = self.pos
        if self.peek() == '-':
            self.pos += 1
        c = self.peek()
        if c is None:
            self.error()
        if c == '0':
            self.pos += 1
            n = self.peek()
            if n is not None and '0' <= n <= '9':
                self.error()
        elif '1' <= c <= '9':
            self.pos += 1
            while self.peek() is not None and '0' <= self.peek() <= '9':
                self.pos += 1
        else:
            self.error()

        is_float = False

        if self.peek() == '.':
            is_float = True
            self.pos += 1
            c = self.peek()
            if c is None or not ('0' <= c <= '9'):
                self.error()
            while self.peek() is not None and '0' <= self.peek() <= '9':
                self.pos += 1

        if self.peek() in ('e', 'E'):
            is_float = True
            self.pos += 1
            if self.peek() in ('+', '-'):
                self.pos += 1
            c = self.peek()
            if c is None or not ('0' <= c <= '9'):
                self.error()
            while self.peek() is not None and '0' <= self.peek() <= '9':
                self.pos += 1

        num_str = self.text[start:self.pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)
