class ParseError(Exception):
    pass

class Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.len = len(text)

    def parse(self):
        self.skip_ws()
        if self.pos >= self.len:
            raise ParseError("empty input")
        value = self.parse_value()
        self.skip_ws()
        if self.pos != self.len:
            raise ParseError("trailing garbage")
        return value

    def skip_ws(self):
        while self.pos < self.len and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_ws()
        if self.pos >= self.len:
            raise ParseError("unexpected end of input")
        ch = self.text[self.pos]
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
        elif ch == '-' or ch.isdigit():
            return self.parse_number()
        else:
            raise ParseError(f"invalid value start: {ch!r}")

    def parse_object(self):
        self.pos += 1  # skip '{'
        self.skip_ws()
        obj = {}
        if self.pos < self.len and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_ws()
            if self.pos >= self.len or self.text[self.pos] != '"':
                raise ParseError("expected string key")
            key = self.parse_string()
            self.skip_ws()
            if self.pos >= self.len or self.text[self.pos] != ':':
                raise ParseError("expected colon after key")
            self.pos += 1
            value = self.parse_value()
            obj[key] = value
            self.skip_ws()
            if self.pos >= self.len:
                raise ParseError("unexpected end in object")
            ch = self.text[self.pos]
            if ch == '}':
                self.pos += 1
                break
            elif ch == ',':
                self.pos += 1
                continue
            else:
                raise ParseError("expected comma or closing brace")
        return obj

    def parse_array(self):
        self.pos += 1  # skip '['
        self.skip_ws()
        arr = []
        if self.pos < self.len and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_ws()
            if self.pos >= self.len:
                raise ParseError("unexpected end in array")
            ch = self.text[self.pos]
            if ch == ']':
                self.pos += 1
                break
            elif ch == ',':
                self.pos += 1
                continue
            else:
                raise ParseError("expected comma or closing bracket")
        return arr

    def parse_string(self):
        self.pos += 1  # skip opening '"'
        chars = []
        while self.pos < self.len:
            ch = self.text[self.pos]
            if ch == '"':
                self.pos += 1
                return ''.join(chars)
            elif ch == '\\':
                self.pos += 1
                if self.pos >= self.len:
                    raise ParseError("unterminated escape sequence")
                esc = self.text[self.pos]
                if esc == 'u':
                    self.pos += 1
                    if self.pos + 3 >= self.len:
                        raise ParseError("incomplete unicode escape")
                    hex_str = self.text[self.pos:self.pos+4]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ParseError("invalid unicode escape")
                    code = int(hex_str, 16)
                    self.pos += 4
                    # surrogate pair handling
                    if 0xD800 <= code <= 0xDBFF:
                        # high surrogate, look ahead for low surrogate
                        if (self.pos + 5 < self.len and
                                self.text[self.pos] == '\\' and
                                self.text[self.pos+1] == 'u'):
                            next_hex = self.text[self.pos+2:self.pos+6]
                            if (len(next_hex) == 4 and
                                    all(c in '0123456789abcdefABCDEF' for c in next_hex)):
                                code2 = int(next_hex, 16)
                                if 0xDC00 <= code2 <= 0xDFFF:
                                    code = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
                                    self.pos += 6
                    chars.append(chr(code))
                elif esc == '"':
                    chars.append('"')
                    self.pos += 1
                elif esc == '\\':
                    chars.append('\\')
                    self.pos += 1
                elif esc == '/':
                    chars.append('/')
                    self.pos += 1
                elif esc == 'b':
                    chars.append('\b')
                    self.pos += 1
                elif esc == 'f':
                    chars.append('\f')
                    self.pos += 1
                elif esc == 'n':
                    chars.append('\n')
                    self.pos += 1
                elif esc == 'r':
                    chars.append('\r')
                    self.pos += 1
                elif esc == 't':
                    chars.append('\t')
                    self.pos += 1
                else:
                    raise ParseError(f"invalid escape sequence: \\{esc}")
            else:
                if ord(ch) < 0x20:
                    raise ParseError("control character in string")
                chars.append(ch)
                self.pos += 1
        raise ParseError("unterminated string")

    def parse_true(self):
        if self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        raise ParseError("expected 'true'")

    def parse_false(self):
        if self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        raise ParseError("expected 'false'")

    def parse_null(self):
        if self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        raise ParseError("expected 'null'")

    def parse_number(self):
        start = self.pos
        # optional minus
        if self.text[self.pos] == '-':
            self.pos += 1
        # integer part
        if self.pos >= self.len:
            raise ParseError("incomplete number")
        if self.text[self.pos] == '0':
            self.pos += 1
        elif self.text[self.pos].isdigit():
            self.pos += 1
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise ParseError("invalid number format")
        is_float = False
        # fraction
        if self.pos < self.len and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= self.len or not self.text[self.pos].isdigit():
                raise ParseError("invalid fraction part")
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        # exponent
        if self.pos < self.len and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < self.len and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.len or not self.text[self.pos].isdigit():
                raise ParseError("invalid exponent part")
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        num_str = self.text[start:self.pos]
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            raise ParseError("number conversion failed")

def parse(text: str):
    try:
        parser = Parser(text)
        return parser.parse()
    except ParseError:
        return None
