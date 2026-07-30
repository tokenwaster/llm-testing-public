import sys

sys.setrecursionlimit(10000)

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, s):
        self.s = s
        self.i = 0
        self.n = len(s)

    def skip_ws(self):
        while self.i < self.n:
            c = self.s[self.i]
            if c == ' ' or c == '\t' or c == '\n' or c == '\r':
                self.i += 1
            else:
                break

    def parse_value(self):
        self.skip_ws()
        if self.i >= self.n:
            raise ParseError("unexpected end")
        c = self.s[self.i]
        if c == '{':
            return self.parse_object()
        elif c == '[':
            return self.parse_array()
        elif c == '"':
            return self.parse_string()
        elif c == 't':
            return self.parse_literal('true', True)
        elif c == 'f':
            return self.parse_literal('false', False)
        elif c == 'n':
            return self.parse_literal('null', None)
        elif c == '-' or c in '0123456789':
            return self.parse_number()
        else:
            raise ParseError("unexpected character")

    def parse_literal(self, word, value):
        if self.s.startswith(word, self.i):
            self.i += len(word)
            return value
        raise ParseError("invalid literal")

    def parse_object(self):
        self.i += 1
        obj = {}
        self.skip_ws()
        if self.i < self.n and self.s[self.i] == '}':
            self.i += 1
            return obj
        while True:
            self.skip_ws()
            if self.i >= self.n or self.s[self.i] != '"':
                raise ParseError("expected string key")
            key = self.parse_string()
            self.skip_ws()
            if self.i >= self.n or self.s[self.i] != ':':
                raise ParseError("expected colon")
            self.i += 1
            val = self.parse_value()
            obj[key] = val
            self.skip_ws()
            if self.i >= self.n:
                raise ParseError("unterminated object")
            c = self.s[self.i]
            if c == ',':
                self.i += 1
                self.skip_ws()
                if self.i < self.n and self.s[self.i] == '}':
                    raise ParseError("trailing comma")
                continue
            elif c == '}':
                self.i += 1
                return obj
            else:
                raise ParseError("expected comma or closing brace")

    def parse_array(self):
        self.i += 1
        arr = []
        self.skip_ws()
        if self.i < self.n and self.s[self.i] == ']':
            self.i += 1
            return arr
        while True:
            val = self.parse_value()
            arr.append(val)
            self.skip_ws()
            if self.i >= self.n:
                raise ParseError("unterminated array")
            c = self.s[self.i]
            if c == ',':
                self.i += 1
                self.skip_ws()
                if self.i < self.n and self.s[self.i] == ']':
                    raise ParseError("trailing comma")
                continue
            elif c == ']':
                self.i += 1
                return arr
            else:
                raise ParseError("expected comma or closing bracket")

    def parse_string(self):
        if self.i >= self.n or self.s[self.i] != '"':
            raise ParseError("expected quote")
        self.i += 1
        buf = []
        while True:
            if self.i >= self.n:
                raise ParseError("unterminated string")
            c = self.s[self.i]
            if c == '"':
                self.i += 1
                return ''.join(buf)
            elif c == '\\':
                self.i += 1
                if self.i >= self.n:
                    raise ParseError("bad escape")
                e = self.s[self.i]
                self.i += 1
                if e == '"':
                    buf.append('"')
                elif e == '\\':
                    buf.append('\\')
                elif e == '/':
                    buf.append('/')
                elif e == 'b':
                    buf.append('\b')
                elif e == 'f':
                    buf.append('\f')
                elif e == 'n':
                    buf.append('\n')
                elif e == 'r':
                    buf.append('\r')
                elif e == 't':
                    buf.append('\t')
                elif e == 'u':
                    if self.i + 4 > self.n:
                        raise ParseError("bad unicode escape")
                    hexdigits = self.s[self.i:self.i+4]
                    if not all(ch in '0123456789abcdefABCDEF' for ch in hexdigits):
                        raise ParseError("bad unicode escape")
                    code = int(hexdigits, 16)
                    self.i += 4
                    if 0xD800 <= code <= 0xDBFF:
                        if self.i + 6 <= self.n and self.s[self.i] == '\\' and self.s[self.i+1] == 'u':
                            hex2 = self.s[self.i+2:self.i+6]
                            if all(ch in '0123456789abcdefABCDEF' for ch in hex2):
                                code2 = int(hex2, 16)
                                if 0xDC00 <= code2 <= 0xDFFF:
                                    self.i += 6
                                    full = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
                                    buf.append(chr(full))
                                    continue
                        raise ParseError("invalid surrogate pair")
                    elif 0xDC00 <= code <= 0xDFFF:
                        raise ParseError("invalid low surrogate")
                    else:
                        buf.append(chr(code))
                else:
                    raise ParseError("invalid escape")
            elif ord(c) < 0x20:
                raise ParseError("unescaped control character")
            else:
                buf.append(c)
                self.i += 1

    def parse_number(self):
        start = self.i
        has_frac = False
        has_exp = False
        if self.s[self.i] == '-':
            self.i += 1
        if self.i >= self.n:
            raise ParseError("invalid number")
        ch = self.s[self.i]
        if ch == '0':
            self.i += 1
            if self.i < self.n and self.s[self.i] in '0123456789':
                raise ParseError("leading zero")
        elif ch in '0123456789':
            while self.i < self.n and self.s[self.i] in '0123456789':
                self.i += 1
        else:
            raise ParseError("invalid number")
        if self.i < self.n and self.s[self.i] == '.':
            has_frac = True
            self.i += 1
            if self.i >= self.n or self.s[self.i] not in '0123456789':
                raise ParseError("expected digits after dot")
            while self.i < self.n and self.s[self.i] in '0123456789':
                self.i += 1
        if self.i < self.n and self.s[self.i] in 'eE':
            has_exp = True
            self.i += 1
            if self.i < self.n and self.s[self.i] in '+-':
                self.i += 1
            if self.i >= self.n or self.s[self.i] not in '0123456789':
                raise ParseError("expected digits in exponent")
            while self.i < self.n and self.s[self.i] in '0123456789':
                self.i += 1
        num_str = self.s[start:self.i]
        if has_frac or has_exp:
            try:
                return float(num_str)
            except ValueError:
                raise ParseError("invalid float")
        else:
            try:
                return int(num_str)
            except ValueError:
                raise ParseError("invalid int")

def parse(text: str):
    try:
        parser = Parser(text)
        val = parser.parse_value()
        parser.skip_ws()
        if parser.i != len(text):
            return None
        return val
    except Exception:
        return None
