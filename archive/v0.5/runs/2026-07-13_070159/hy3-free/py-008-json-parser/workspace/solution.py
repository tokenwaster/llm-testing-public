class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= len(self.text):
            raise _ParseError
        c = self.text[self.pos]
        if c == '{':
            return self.parse_object()
        if c == '[':
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == 't':
            return self.parse_literal('true', True)
        if c == 'f':
            return self.parse_literal('false', False)
        if c == 'n':
            return self.parse_literal('null', None)
        if c == '-' or c in '0123456789':
            return self.parse_number()
        raise _ParseError

    def parse_literal(self, word, value):
        if self.text.startswith(word, self.pos):
            self.pos += len(word)
            return value
        raise _ParseError

    def parse_number(self):
        start = self.pos
        if self.text[self.pos] == '-':
            self.pos += 1
        if self.pos >= len(self.text):
            raise _ParseError
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] in '0123456789':
                raise _ParseError
        elif self.text[self.pos] in '123456789':
            self.pos += 1
            while self.pos < len(self.text) and self.text[self.pos] in '0123456789':
                self.pos += 1
        else:
            raise _ParseError

        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            if self.pos >= len(self.text) or self.text[self.pos] not in '0123456789':
                raise _ParseError
            while self.pos < len(self.text) and self.text[self.pos] in '0123456789':
                self.pos += 1

        if self.pos < len(self.text) and self.text[self.pos] in 'eE':
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= len(self.text) or self.text[self.pos] not in '0123456789':
                raise _ParseError
            while self.pos < len(self.text) and self.text[self.pos] in '0123456789':
                self.pos += 1

        num_str = self.text[start:self.pos]
        if '.' not in num_str and 'e' not in num_str and 'E' not in num_str:
            return int(num_str)
        else:
            return float(num_str)

    def parse_string(self):
        self.pos += 1
        result = []
        while True:
            if self.pos >= len(self.text):
                raise _ParseError
            c = self.text[self.pos]
            self.pos += 1
            if c == '"':
                break
            if c == '\\':
                if self.pos >= len(self.text):
                    raise _ParseError
                e = self.text[self.pos]
                self.pos += 1
                if e == '"':
                    result.append('"')
                elif e == '\\':
                    result.append('\\')
                elif e == '/':
                    result.append('/')
                elif e == 'b':
                    result.append('\b')
                elif e == 'f':
                    result.append('\f')
                elif e == 'n':
                    result.append('\n')
                elif e == 'r':
                    result.append('\r')
                elif e == 't':
                    result.append('\t')
                elif e == 'u':
                    if self.pos + 4 > len(self.text):
                        raise _ParseError
                    hexdigits = self.text[self.pos:self.pos + 4]
                    if not all(ch in '0123456789abcdefABCDEF' for ch in hexdigits):
                        raise _ParseError
                    code = int(hexdigits, 16)
                    self.pos += 4
                    if 0xD800 <= code <= 0xDBFF:
                        if (self.pos + 2 <= len(self.text) and
                                self.text[self.pos] == '\\' and
                                self.text[self.pos + 1] == 'u'):
                            if self.pos + 6 <= len(self.text):
                                hex2 = self.text[self.pos + 2:self.pos + 6]
                                if all(ch in '0123456789abcdefABCDEF' for ch in hex2):
                                    code2 = int(hex2, 16)
                                    if 0xDC00 <= code2 <= 0xDFFF:
                                        self.pos += 6
                                        code = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
                                        result.append(chr(code))
                                        continue
                        result.append(chr(code))
                    else:
                        result.append(chr(code))
                else:
                    raise _ParseError
            elif ord(c) < 0x20:
                raise _ParseError
            else:
                result.append(c)
        return ''.join(result)

    def parse_object(self):
        self.pos += 1
        self.skip_whitespace()
        obj = {}
        if self.pos < len(self.text) and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                raise _ParseError
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                raise _ParseError
            self.pos += 1
            val = self.parse_value()
            obj[key] = val
            self.skip_whitespace()
            if self.pos >= len(self.text):
                raise _ParseError
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
            elif c == '}':
                self.pos += 1
                return obj
            else:
                raise _ParseError

    def parse_array(self):
        self.pos += 1
        self.skip_whitespace()
        arr = []
        if self.pos < len(self.text) and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            val = self.parse_value()
            arr.append(val)
            self.skip_whitespace()
            if self.pos >= len(self.text):
                raise _ParseError
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
            elif c == ']':
                self.pos += 1
                return arr
            else:
                raise _ParseError


def parse(text: str):
    try:
        parser = _Parser(text)
        val = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != len(parser.text):
            return None
        return val
    except _ParseError:
        return None
