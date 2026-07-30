class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.n = len(text)

    def error(self):
        raise _ParseError()

    def skip_ws(self):
        while self.pos < self.n and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_ws()
        if self.pos >= self.n:
            self.error()
        c = self.text[self.pos]
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

    def parse_literal(self, lit: str, val):
        if self.text.startswith(lit, self.pos):
            self.pos += len(lit)
            return val
        self.error()

    def parse_object(self):
        self.pos += 1  # skip '{'
        obj = {}
        self.skip_ws()
        if self.pos < self.n and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_ws()
            if self.pos >= self.n or self.text[self.pos] != '"':
                self.error()
            key = self.parse_string()
            self.skip_ws()
            if self.pos >= self.n or self.text[self.pos] != ':':
                self.error()
            self.pos += 1  # skip ':'
            value = self.parse_value()
            obj[key] = value
            self.skip_ws()
            if self.pos >= self.n:
                self.error()
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
                continue
            if c == '}':
                self.pos += 1
                return obj
            self.error()

    def parse_array(self):
        self.pos += 1  # skip '['
        arr = []
        self.skip_ws()
        if self.pos < self.n and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_ws()
            if self.pos >= self.n:
                self.error()
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
                continue
            if c == ']':
                self.pos += 1
                return arr
            self.error()

    def parse_string(self):
        self.pos += 1  # skip opening quote
        chars = []
        while True:
            if self.pos >= self.n:
                self.error()
            c = self.text[self.pos]
            if c == '"':
                self.pos += 1
                return ''.join(chars)
            if c == '\\':
                self.pos += 1
                if self.pos >= self.n:
                    self.error()
                esc = self.text[self.pos]
                if esc in '"\\/bfnrt':
                    chars.append({'"': '"', '\\': '\\', '/': '/', 'b': '\b',
                                  'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}[esc])
                    self.pos += 1
                elif esc == 'u':
                    self.pos += 1
                    code = self.parse_hex4()
                    if 0xD800 <= code <= 0xDBFF:  # high surrogate
                        if (self.pos + 1 < self.n and
                                self.text[self.pos] == '\\' and
                                self.text[self.pos + 1] == 'u'):
                            save = self.pos
                            self.pos += 2
                            low = self.parse_hex4()
                            if 0xDC00 <= low <= 0xDFFF:
                                code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                                chars.append(chr(code))
                            else:
                                self.pos = save
                                chars.append(chr(code))
                        else:
                            chars.append(chr(code))
                    else:
                        chars.append(chr(code))
                else:
                    self.error()
            else:
                if ord(c) < 0x20:
                    self.error()
                chars.append(c)
                self.pos += 1

    def parse_hex4(self):
        if self.pos + 4 > self.n:
            self.error()
        hex_str = self.text[self.pos:self.pos + 4]
        if not all(ch in '0123456789abcdefABCDEF' for ch in hex_str):
            self.error()
        self.pos += 4
        return int(hex_str, 16)

    def parse_number(self):
        start = self.pos
        if self.pos < self.n and self.text[self.pos] == '-':
            self.pos += 1
        if self.pos >= self.n:
            self.error()
        if self.text[self.pos] == '0':
            self.pos += 1
        elif '1' <= self.text[self.pos] <= '9':
            while self.pos < self.n and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
        else:
            self.error()
        is_float = False
        if self.pos < self.n and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= self.n or not ('0' <= self.text[self.pos] <= '9'):
                self.error()
            while self.pos < self.n and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
        if self.pos < self.n and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < self.n and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.n or not ('0' <= self.text[self.pos] <= '9'):
                self.error()
            while self.pos < self.n and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
        num_str = self.text[start:self.pos]
        if is_float:
            return float(num_str)
        return int(num_str)


def parse(text: str):
    if not isinstance(text, str):
        return None
    parser = _Parser(text)
    try:
        value = parser.parse_value()
        parser.skip_ws()
        if parser.pos != parser.n:
            return None
        return value
    except _ParseError:
        return None
