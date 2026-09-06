def parse(text: str):
    try:
        p = _Parser(text)
        value = p.parse_value()
        p.skip_whitespace()
        if p.pos < len(p.text):
            raise ValueError("Trailing garbage")
        return value
    except Exception:
        return None


class _Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= self.length:
            raise ValueError("Unexpected end")
        c = self.text[self.pos]
        if c == '{':
            return self.parse_object()
        if c == '[':
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == '-' or c.isdigit():
            return self.parse_number()
        if c == 't' or c == 'f' or c == 'n':
            return self.parse_literal()
        raise ValueError("Unexpected character")

    def parse_object(self):
        self.pos += 1  # skip '{'
        d = {}
        self.skip_whitespace()
        if self.pos < self.length and self.text[self.pos] == '}':
            self.pos += 1
            return d
        while True:
            self.skip_whitespace()
            if self.pos >= self.length:
                raise ValueError("Unterminated object")
            if self.text[self.pos] != '"':
                raise ValueError("Key must be string")
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] != ':':
                raise ValueError("Missing colon")
            self.pos += 1
            value = self.parse_value()
            d[key] = value
            self.skip_whitespace()
            if self.pos >= self.length:
                raise ValueError("Unterminated object")
            if self.text[self.pos] == '}':
                self.pos += 1
                return d
            if self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise ValueError("Expected comma")

    def parse_array(self):
        self.pos += 1  # skip '['
        lst = []
        self.skip_whitespace()
        if self.pos < self.length and self.text[self.pos] == ']':
            self.pos += 1
            return lst
        while True:
            value = self.parse_value()
            lst.append(value)
            self.skip_whitespace()
            if self.pos >= self.length:
                raise ValueError("Unterminated array")
            if self.text[self.pos] == ']':
                self.pos += 1
                return lst
            if self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise ValueError("Expected comma")

    def parse_string(self):
        self.pos += 1  # skip '"'
        result = []
        while self.pos < self.length:
            c = self.text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(result)
            if c == '\\':
                self.pos += 1
                if self.pos >= self.length:
                    raise ValueError("Unterminated escape")
                c = self.text[self.pos]
                if c == '"':
                    result.append('"')
                elif c == '\\':
                    result.append('\\')
                elif c == '/':
                    result.append('/')
                elif c == 'b':
                    result.append('\b')
                elif c == 'f':
                    result.append('\f')
                elif c == 'n':
                    result.append('\n')
                elif c == 'r':
                    result.append('\r')
                elif c == 't':
                    result.append('\t')
                elif c == 'u':
                    self.pos += 1
                    if self.pos + 4 > self.length:
                        raise ValueError("Invalid unicode")
                    hex_str = self.text[self.pos:self.pos+4]
                    if not all(ch in '0123456789abcdefABCDEF' for ch in hex_str):
                        raise ValueError("Invalid unicode")
                    result.append(chr(int(hex_str, 16)))
                    self.pos += 3
                else:
                    raise ValueError("Invalid escape")
            else:
                result.append(c)
            self.pos += 1
        raise ValueError("Unterminated string")

    def parse_number(self):
        start = self.pos
        if self.text[self.pos] == '-':
            self.pos += 1
        if self.pos >= self.length:
            raise ValueError("Invalid number")
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < self.length and self.text[self.pos].isdigit():
                raise ValueError("Leading zeros not allowed")
        else:
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        is_float = False
        if self.pos < self.length and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise ValueError("Digits required after decimal")
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        if self.pos < self.length and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise ValueError("Digits required after exponent")
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        s = self.text[start:self.pos]
        return float(s) if is_float else int(s)

    def parse_literal(self):
        rest = self.text[self.pos:]
        if rest.startswith("true"):
            self.pos += 4
            return True
        if rest.startswith("false"):
            self.pos += 5
            return False
        if rest.startswith("null"):
            self.pos += 4
            return None
        raise ValueError("Invalid literal")
