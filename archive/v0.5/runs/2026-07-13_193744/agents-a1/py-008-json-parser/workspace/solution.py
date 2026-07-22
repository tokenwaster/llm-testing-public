def parse(text: str):
    class Parser:
        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.length = len(text)

        def skip_whitespace(self):
            while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
                self.pos += 1

        def is_eof(self):
            return self.pos >= self.length

        def parse(self):
            self.skip_whitespace()
            if self.is_eof():
                return None
            value = self.parse_value()
            if value is None and not self.is_eof():
                return None
            self.skip_whitespace()
            if self.pos < self.length:
                return None
            return value

        def parse_value(self):
            if self.is_eof():
                return None
            ch = self.text[self.pos]
            if ch == '"':
                return self.parse_string()
            elif ch == '{':
                return self.parse_object()
            elif ch == '[':
                return self.parse_array()
            elif ch == 't':
                return self.parse_true()
            elif ch == 'f':
                return self.parse_false()
            elif ch == 'n':
                return self.parse_null()
            elif ch == '-' or ch.isdigit():
                return self.parse_number()
            else:
                return None

        def parse_string(self):
            if self.text[self.pos] != '"':
                return None
            self.pos += 1  # consume opening quote
            result = []
            while True:
                if self.is_eof():
                    return None
                ch = self.text[self.pos]
                if ch == '"':
                    self.pos += 1
                    break
                elif ch == '\\':
                    self.pos += 1
                    if self.is_eof():
                        return None
                    esc = self.text[self.pos]
                    if esc == '"':
                        result.append('"')
                        self.pos += 1
                    elif esc == '\\':
                        result.append('\\')
                        self.pos += 1
                    elif esc == '/':
                        result.append('/')
                        self.pos += 1
                    elif esc == 'b':
                        result.append('\b')
                        self.pos += 1
                    elif esc == 'f':
                        result.append('\f')
                        self.pos += 1
                    elif esc == 'n':
                        result.append('\n')
                        self.pos += 1
                    elif esc == 'r':
                        result.append('\r')
                        self.pos += 1
                    elif esc == 't':
                        result.append('\t')
                        self.pos += 1
                    elif esc == 'u':
                        # consume 'u'
                        self.pos += 1
                        if self.pos + 4 > self.length:
                            return None
                        hex_str = self.text[self.pos:self.pos+4]
                        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                            return None
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        self.pos += 4
                    else:
                        return None
                else:
                    # control characters (U+0000 to U+001F) are not allowed unescaped
                    if ord(ch) < 32:
                        return None
                    result.append(ch)
                    self.pos += 1
            return ''.join(result)

        def parse_object(self):
            if self.text[self.pos] != '{':
                return None
            self.pos += 1
            self.skip_whitespace()
            obj = {}
            if self.is_eof():
                return None
            if self.text[self.pos] == '}':
                self.pos += 1
                return obj
            while True:
                self.skip_whitespace()
                if self.text[self.pos] != '"':
                    return None
                key = self.parse_string()
                if key is None:
                    return None
                self.skip_whitespace()
                if self.text[self.pos] != ':':
                    return None
                self.pos += 1
                self.skip_whitespace()
                value = self.parse_value()
                if value is None:
                    return None
                obj[key] = value
                self.skip_whitespace()
                if self.is_eof():
                    return None
                ch = self.text[self.pos]
                if ch == '}':
                    self.pos += 1
                    break
                elif ch == ',':
                    self.pos += 1
                else:
                    return None
            return obj

        def parse_array(self):
            if self.text[self.pos] != '[':
                return None
            self.pos += 1
            self.skip_whitespace()
            arr = []
            if self.is_eof():
                return None
            if self.text[self.pos] == ']':
                self.pos += 1
                return arr
            while True:
                self.skip_whitespace()
                value = self.parse_value()
                if value is None:
                    return None
                arr.append(value)
                self.skip_whitespace()
                if self.is_eof():
                    return None
                ch = self.text[self.pos]
                if ch == ']':
                    self.pos += 1
                    break
                elif ch == ',':
                    self.pos += 1
                else:
                    return None
            return arr

        def parse_true(self):
            if self.text[self.pos:self.pos+4] == 'true':
                self.pos += 4
                return True
            return None

        def parse_false(self):
            if self.text[self.pos:self.pos+5] == 'false':
                self.pos += 5
                return False
            return None

        def parse_null(self):
            if self.text[self.pos:self.pos+4] == 'null':
                self.pos += 4
                return None
            return None

        def parse_number(self):
            start = self.pos
            if self.text[self.pos] == '-':
                self.pos += 1
            # Must have at least one digit after optional sign
            if not self.text[self.pos].isdigit():
                return None
            # Handle integer part, including leading zero rule
            if self.text[self.pos] == '0':
                self.pos += 1
            else:
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.pos += 1
            # Fractional part
            if self.pos < self.length and self.text[self.pos] == '.':
                self.pos += 1
                if not self.text[self.pos].isdigit():
                    return None
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.pos += 1
            # Exponent part
            if self.pos < self.length and self.text[self.pos] in 'eE':
                self.pos += 1
                if self.pos < self.length and self.text[self.pos] in '+-':
                    self.pos += 1
                if not self.text[self.pos].isdigit():
                    return None
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.pos += 1
            num_str = self.text[start:self.pos]
            try:
                if '.' in num_str or 'e' in num_str or 'E' in num_str:
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                return None

    parser = Parser(text)
    return parser.parse()
