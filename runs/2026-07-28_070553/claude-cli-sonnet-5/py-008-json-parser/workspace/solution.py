import re

_WS = " \t\n\r"


class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text):
        self.text = text
        self.i = 0
        self.n = len(text)

    def error(self):
        raise _ParseError()

    def skip_ws(self):
        while self.i < self.n and self.text[self.i] in _WS:
            self.i += 1

    def peek(self):
        if self.i >= self.n:
            self.error()
        return self.text[self.i]

    def expect(self, ch):
        if self.i >= self.n or self.text[self.i] != ch:
            self.error()
        self.i += 1

    def parse_value(self):
        self.skip_ws()
        if self.i >= self.n:
            self.error()
        c = self.text[self.i]
        if c == '{':
            return self.parse_object()
        if c == '[':
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == 't':
            return self.parse_literal("true", True)
        if c == 'f':
            return self.parse_literal("false", False)
        if c == 'n':
            return self.parse_literal("null", None)
        if c == '-' or c.isdigit():
            return self.parse_number()
        self.error()

    def parse_literal(self, word, value):
        if self.text[self.i:self.i + len(word)] != word:
            self.error()
        self.i += len(word)
        return value

    def parse_object(self):
        self.expect('{')
        obj = {}
        self.skip_ws()
        if self.i < self.n and self.text[self.i] == '}':
            self.i += 1
            return obj
        while True:
            self.skip_ws()
            if self.i >= self.n or self.text[self.i] != '"':
                self.error()
            key = self.parse_string()
            self.skip_ws()
            self.expect(':')
            value = self.parse_value()
            obj[key] = value
            self.skip_ws()
            if self.i >= self.n:
                self.error()
            c = self.text[self.i]
            if c == ',':
                self.i += 1
                continue
            elif c == '}':
                self.i += 1
                break
            else:
                self.error()
        return obj

    def parse_array(self):
        self.expect('[')
        arr = []
        self.skip_ws()
        if self.i < self.n and self.text[self.i] == ']':
            self.i += 1
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_ws()
            if self.i >= self.n:
                self.error()
            c = self.text[self.i]
            if c == ',':
                self.i += 1
                continue
            elif c == ']':
                self.i += 1
                break
            else:
                self.error()
        return arr

    def parse_string(self):
        self.expect('"')
        chars = []
        while True:
            if self.i >= self.n:
                self.error()
            c = self.text[self.i]
            if c == '"':
                self.i += 1
                break
            if c == '\\':
                self.i += 1
                if self.i >= self.n:
                    self.error()
                esc = self.text[self.i]
                if esc == '"':
                    chars.append('"')
                    self.i += 1
                elif esc == '\\':
                    chars.append('\\')
                    self.i += 1
                elif esc == '/':
                    chars.append('/')
                    self.i += 1
                elif esc == 'b':
                    chars.append('\b')
                    self.i += 1
                elif esc == 'f':
                    chars.append('\f')
                    self.i += 1
                elif esc == 'n':
                    chars.append('\n')
                    self.i += 1
                elif esc == 'r':
                    chars.append('\r')
                    self.i += 1
                elif esc == 't':
                    chars.append('\t')
                    self.i += 1
                elif esc == 'u':
                    self.i += 1
                    code = self.parse_hex4()
                    if 0xD800 <= code <= 0xDBFF:
                        if (self.i + 1 < self.n and self.text[self.i] == '\\'
                                and self.text[self.i + 1] == 'u'):
                            save = self.i
                            self.i += 2
                            code2 = self.parse_hex4()
                            if 0xDC00 <= code2 <= 0xDFFF:
                                combined = 0x10000 + (code - 0xD800) * 0x400 + (code2 - 0xDC00)
                                chars.append(chr(combined))
                            else:
                                self.i = save
                                chars.append(chr(code))
                        else:
                            chars.append(chr(code))
                    else:
                        chars.append(chr(code))
                else:
                    self.error()
            elif ord(c) < 0x20:
                self.error()
            else:
                chars.append(c)
                self.i += 1
        return ''.join(chars)

    def parse_hex4(self):
        if self.i + 4 > self.n:
            self.error()
        hex_str = self.text[self.i:self.i + 4]
        if not re.fullmatch(r'[0-9a-fA-F]{4}', hex_str):
            self.error()
        self.i += 4
        return int(hex_str, 16)

    def parse_number(self):
        start = self.i
        if self.i < self.n and self.text[self.i] == '-':
            self.i += 1
        if self.i >= self.n or not self.text[self.i].isdigit():
            self.error()
        if self.text[self.i] == '0':
            self.i += 1
        else:
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        is_float = False
        if self.i < self.n and self.text[self.i] == '.':
            is_float = True
            self.i += 1
            if self.i >= self.n or not self.text[self.i].isdigit():
                self.error()
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        if self.i < self.n and self.text[self.i] in 'eE':
            is_float = True
            self.i += 1
            if self.i < self.n and self.text[self.i] in '+-':
                self.i += 1
            if self.i >= self.n or not self.text[self.i].isdigit():
                self.error()
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        num_str = self.text[start:self.i]
        if is_float:
            return float(num_str)
        return int(num_str)


def parse(text):
    if not isinstance(text, str):
        return None
    try:
        parser = _Parser(text)
        value = parser.parse_value()
        parser.skip_ws()
        if parser.i != parser.n:
            return None
        return value
    except _ParseError:
        return None
    except (RecursionError, ValueError):
        return None
