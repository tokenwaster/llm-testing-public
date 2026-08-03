class Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def parse(self):
        try:
            value = self.parse_value()
            self.skip_whitespace()
            if self.pos != len(self.text):
                return None
            return value
        except Exception:
            return None

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= len(self.text):
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
        if self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        if self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        if self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        raise ValueError("Unexpected character")

    def parse_object(self):
        obj = {}
        self.pos += 1  # skip {
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                raise ValueError("Expected string key")
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                raise ValueError("Expected colon")
            self.pos += 1
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("Unterminated object")
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
                continue
            if c == '}':
                self.pos += 1
                return obj
            raise ValueError("Expected , or }")

    def parse_array(self):
        arr = []
        self.pos += 1  # skip [
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("Unterminated array")
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
                continue
            if c == ']':
                self.pos += 1
                return arr
            raise ValueError("Expected , or ]")

    def parse_string(self):
        self.pos += 1  # skip opening "
        result = []
        while self.pos < len(self.text):
            c = self.text[self.pos]
            if c == '"':
                self.pos += 1
                return ''.join(result)
            if c == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    raise ValueError("Unterminated string escape")
                e = self.text[self.pos]
                if e == '"': result.append('"')
                elif e == '\\': result.append('\\')
                elif e == '/': result.append('/')
                elif e == 'b': result.append('\b')
                elif e == 'f': result.append('\f')
                elif e == 'n': result.append('\n')
                elif e == 'r': result.append('\r')
                elif e == 't': result.append('\t')
                elif e == 'u':
                    hex_digits = self.text[self.pos+1:self.pos+5]
                    if len(hex_digits) != 4 or not all(h in '0123456789abcdefABCDEF' for h in hex_digits):
                        raise ValueError("Invalid unicode escape")
                    result.append(chr(int(hex_digits, 16)))
                    self.pos += 4
                else:
                    raise ValueError("Invalid escape")
                self.pos += 1
            else:
                result.append(c)
                self.pos += 1
        raise ValueError("Unterminated string")

    def parse_number(self):
        start = self.pos
        if self.text[self.pos] == '-':
            self.pos += 1
        if self.pos >= len(self.text):
            raise ValueError("Invalid number")
        # integer part
        if self.text[self.pos] == '0':
            self.pos += 1
        elif self.text[self.pos] in '123456789':
            self.pos += 1
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise ValueError("Invalid number")
        is_float = False
        # fractional part
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ValueError("Invalid fraction")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        # exponent
        if self.pos < len(self.text) and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ValueError("Invalid exponent")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        num_str = self.text[start:self.pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)


def parse(text: str):
    parser = Parser(text)
    return parser.parse()
