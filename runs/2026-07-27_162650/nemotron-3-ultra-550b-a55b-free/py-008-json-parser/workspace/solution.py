class ParseError(Exception):
    pass


class JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.len = len(text)

    def parse(self):
        self.skip_whitespace()
        if self.pos >= self.len:
            raise ParseError
        value = self.parse_value()
        self.skip_whitespace()
        if self.pos != self.len:
            raise ParseError
        return value

    def skip_whitespace(self):
        while self.pos < self.len and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= self.len:
            raise ParseError
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
            raise ParseError

    def parse_object(self):
        self.pos += 1  # skip '{'
        self.skip_whitespace()
        obj = {}
        if self.pos < self.len and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            if self.pos >= self.len or self.text[self.pos] != '"':
                raise ParseError
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= self.len or self.text[self.pos] != ':':
                raise ParseError
            self.pos += 1
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            if self.pos >= self.len:
                raise ParseError
            ch = self.text[self.pos]
            if ch == '}':
                self.pos += 1
                break
            elif ch == ',':
                self.pos += 1
            else:
                raise ParseError
        return obj

    def parse_array(self):
        self.pos += 1  # skip '['
        self.skip_whitespace()
        arr = []
        if self.pos < self.len and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            if self.pos >= self.len:
                raise ParseError
            ch = self.text[self.pos]
            if ch == ']':
                self.pos += 1
                break
            elif ch == ',':
                self.pos += 1
            else:
                raise ParseError
        return arr

    def parse_string(self):
        self.pos += 1  # skip opening quote
        result = []
        while self.pos < self.len:
            ch = self.text[self.pos]
            if ch == '"':
                self.pos += 1
                return ''.join(result)
            elif ch == '\\':
                self.pos += 1
                if self.pos >= self.len:
                    raise ParseError
                esc = self.text[self.pos]
                if esc == 'u':
                    self.pos += 1
                    if self.pos + 3 >= self.len:
                        raise ParseError
                    hex_str = self.text[self.pos:self.pos + 4]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ParseError
                    code = int(hex_str, 16)
                    result.append(chr(code))
                    self.pos += 4
                else:
                    escape_map = {
                        '"': '"', '\\': '\\', '/': '/',
                        'b': '\b', 'f': '\f', 'n': '\n',
                        'r': '\r', 't': '\t'
                    }
                    if esc in escape_map:
                        result.append(escape_map[esc])
                        self.pos += 1
                    else:
                        raise ParseError
            else:
                if ord(ch) < 0x20:
                    raise ParseError
                result.append(ch)
                self.pos += 1
        raise ParseError  # unterminated string

    def parse_number(self):
        start = self.pos
        if self.text[self.pos] == '-':
            self.pos += 1
        if self.pos >= self.len:
            raise ParseError
        # integer part
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < self.len and self.text[self.pos].isdigit():
                raise ParseError
        else:
            if not self.text[self.pos].isdigit() or self.text[self.pos] == '0':
                raise ParseError
            self.pos += 1
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        # fraction
        has_frac = False
        if self.pos < self.len and self.text[self.pos] == '.':
            has_frac = True
            self.pos += 1
            if self.pos >= self.len or not self.text[self.pos].isdigit():
                raise ParseError
            self.pos += 1
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        # exponent
        has_exp = False
        if self.pos < self.len and self.text[self.pos] in 'eE':
            has_exp = True
            self.pos += 1
            if self.pos < self.len and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.len or not self.text[self.pos].isdigit():
                raise ParseError
            self.pos += 1
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        num_str = self.text[start:self.pos]
        if has_frac or has_exp:
            try:
                return float(num_str)
            except ValueError:
                raise ParseError
        else:
            try:
                return int(num_str)
            except ValueError:
                raise ParseError

    def parse_true(self):
        if self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        raise ParseError

    def parse_false(self):
        if self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        raise ParseError

    def parse_null(self):
        if self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        raise ParseError


def parse(text: str):
    parser = JSONParser(text)
    try:
        return parser.parse()
    except ParseError:
        return None
