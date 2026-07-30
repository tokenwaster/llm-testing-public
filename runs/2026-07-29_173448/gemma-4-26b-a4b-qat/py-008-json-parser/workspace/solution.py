class JSONParser:
    class ParseError(Exception):
        pass

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def error(self):
        raise self.ParseError()

    def skip_ws(self):
        while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse(self):
        try:
            self.skip_ws()
            if self.pos == self.length:
                return None
            val = self.parse_value()
            self.skip_ws()
            if self.pos < self.length:
                return None
            return val
        except (self.ParseError, ValueError, IndexError):
            return None

    def parse_value(self):
        self.skip_ws()
        if self.pos >= self.length:
            self.error()
        c = self.text[self.pos]
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
        elif c == '-' or c.isdigit():
            return self.parse_number()
        else:
            self.error()

    def parse_object(self):
        self.pos += 1
        obj = {}
        self.skip_ws()
        if self.pos < self.length and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_ws()
            if self.pos >= self.length or self.text[self.pos] != '"':
                self.error()
            key = self.parse_string()
            self.skip_ws()
            if self.pos >= self.length or self.text[self.pos] != ':':
                self.error()
            self.pos += 1
            val = self.parse_value()
            self.skip_ws()
            if self.pos < self.length and self.text[self.pos] == ',':
                self.pos += 1
                self.skip_ws()
                if self.pos < self.length and self.text[self.pos] == '}':
                    self.error()
            elif self.pos < self.length and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            else:
                self.error()

    def parse_array(self):
        self.pos += 1
        arr = []
        self.skip_ws()
        if self.pos < self.length and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            val = self.parse_value()
            self.skip_ws()
            if self.pos < self.length and self.text[self.pos] == ',':
                self.pos += 1
                self.skip_ws()
                if self.pos < self.length and self.text[self.pos] == ']':
                    self.error()
            elif self.pos < self.length and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            else:
                self.error()

    def parse_string(self):
        self.pos += 1
        res = []
        while self.pos < self.length:
            c = self.text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(res)
            elif c == '\\':
                self.pos += 1
                if self.pos >= self.length:
                    self.error()
                esc = self.text[self.pos]
                if esc == '"': res.append('"')
                elif esc == '\\': res.append('\\')
                elif esc == '/': res.append('/')
                elif esc == 'b': res.append('\b')
                elif esc == 'f': res.append('\f')
                elif esc == 'n': res.append('\n')
                elif esc == 'r': res.append('\r')
                elif esc == 't': res.append('\t')
                elif esc == 'u':
                    self.pos += 1
                    if self.pos + 4 > self.length:
                        self.error()
                    u_hex = self.text[self.pos : self.pos + 4]
                    try:
                        res.append(chr(int(u_hex, 16)))
                        self.pos += 4
                    except ValueError:
                        self.error()
                else:
                    self.error()
            elif ord(c) < 0x20:
                self.error()
            else:
                res.append(c)
                self.pos += 1
        self.error()

    def parse_literal(self, keyword, return_val):
        if self.text.startswith(keyword, self.pos):
            next_pos = self.pos + len(keyword)
            if next_pos < self.length and self.text[next_pos].isalnum():
                self.error()
            self.pos = next_pos
            return return_val
        else:
            self.error()

    def parse_number(self):
        start = self.pos
        if self.text[self.pos] == '-':
            self.pos += 1
        if self.pos < self.length and self.text[self.pos].isdigit():
            if self.text[self.pos] == '0':
                self.pos += 1
                if self.pos < self.length and self.text[self.pos].isdigit():
                    self.error()
            else:
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.pos += 1
        else:
            self.error()

        if self.pos < self.length and self.text[self.pos] == '.':
            self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                self.error()
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        
        if self.pos < self.length and self.text[self.pos] in 'eE':
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                self.error()
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        
        num_str = self.text[start:self.pos]
        if '.' in num_str or 'e' in num_str.lower():
            return float(num_str)
        else:
            return int(num_str)

def parse(text: str):
    return JSONParser(text).parse()
