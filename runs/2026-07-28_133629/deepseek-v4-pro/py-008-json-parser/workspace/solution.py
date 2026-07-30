FAIL = object()

class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= len(self.text):
            return FAIL
        ch = self.text[self.pos]
        if ch == '{':
            return self.parse_object()
        elif ch == '[':
            return self.parse_array()
        elif ch == '"':
            return self.parse_string()
        elif ch == '-' or ('0' <= ch <= '9'):
            return self.parse_number()
        elif ch == 't':
            return self.parse_literal('true', True)
        elif ch == 'f':
            return self.parse_literal('false', False)
        elif ch == 'n':
            return self.parse_literal('null', None)
        else:
            return FAIL

    def parse_object(self):
        if self.text[self.pos] != '{':
            return FAIL
        self.pos += 1
        obj = {}
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            if self.pos >= len(self.text):
                return FAIL
            key = self.parse_string()
            if key is FAIL:
                return FAIL
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                return FAIL
            self.pos += 1
            self.skip_whitespace()
            val = self.parse_value()
            if val is FAIL:
                return FAIL
            obj[key] = val
            self.skip_whitespace()
            if self.pos >= len(self.text):
                return FAIL
            if self.text[self.pos] == '}':
                self.pos += 1
                return obj
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                return FAIL

    def parse_array(self):
        if self.text[self.pos] != '[':
            return FAIL
        self.pos += 1
        arr = []
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            self.skip_whitespace()
            if self.pos >= len(self.text):
                return FAIL
            val = self.parse_value()
            if val is FAIL:
                return FAIL
            arr.append(val)
            self.skip_whitespace()
            if self.pos >= len(self.text):
                return FAIL
            if self.text[self.pos] == ']':
                self.pos += 1
                return arr
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                return FAIL

    def parse_string(self):
        if self.text[self.pos] != '"':
            return FAIL
        self.pos += 1
        chars = []
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch == '"':
                self.pos += 1
                return ''.join(chars)
            elif ch == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    return FAIL
                esc = self.text[self.pos]
                if esc == '"':
                    chars.append('"')
                elif esc == '\\':
                    chars.append('\\')
                elif esc == '/':
                    chars.append('/')
                elif esc == 'b':
                    chars.append('\b')
                elif esc == 'f':
                    chars.append('\f')
                elif esc == 'n':
                    chars.append('\n')
                elif esc == 'r':
                    chars.append('\r')
                elif esc == 't':
                    chars.append('\t')
                elif esc == 'u':
                    if self.pos + 4 >= len(self.text):
                        return FAIL
                    hex_str = self.text[self.pos+1:self.pos+5]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        return FAIL
                    code_point = int(hex_str, 16)
                    chars.append(chr(code_point))
                    self.pos += 4
                else:
                    return FAIL
                self.pos += 1
            else:
                if ord(ch) < 0x20:
                    return FAIL
                chars.append(ch)
                self.pos += 1
        return FAIL

    def parse_number(self):
        start = self.pos
        if self.pos < len(self.text) and self.text[self.pos] == '-':
            self.pos += 1
        if self.pos >= len(self.text) or not ('0' <= self.text[self.pos] <= '9'):
            return FAIL
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                return FAIL
        else:
            while self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
        is_float = False
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            if self.pos >= len(self.text) or not ('0' <= self.text[self.pos] <= '9'):
                return FAIL
            while self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
            is_float = True
        if self.pos < len(self.text) and self.text[self.pos] in ('e', 'E'):
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] in ('+', '-'):
                self.pos += 1
            if self.pos >= len(self.text) or not ('0' <= self.text[self.pos] <= '9'):
                return FAIL
            while self.pos < len(self.text) and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
            is_float = True
        if start == self.pos:
            return FAIL
        num_str = self.text[start:self.pos]
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            return FAIL

    def parse_literal(self, literal, value):
        end = self.pos + len(literal)
        if end > len(self.text):
            return FAIL
        if self.text[self.pos:end] == literal:
            if end < len(self.text) and self.text[end].isalnum():
                return FAIL
            self.pos = end
            return value
        return FAIL


def parse(text: str):
    parser = JSONParser(text)
    val = parser.parse_value()
    if val is FAIL:
        return None
    parser.skip_whitespace()
    if parser.pos != len(text):
        return None
    return val
