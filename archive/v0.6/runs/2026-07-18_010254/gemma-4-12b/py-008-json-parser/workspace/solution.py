class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in ' \n\r\t\f\v':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= self.length:
            return None
        char = self.text[self.pos]
        if char == '{': return self.parse_object()
        if char == '[': return self.parse_array()
        if char == '"': return self.parse_string()
        if char == 't': return self.parse_true()
        if char == 'f': return self.parse_false()
        if char == 'n': return self.parse_null()
        if char == '-' or char.isdigit(): return self.parse_number()
        return None

    def parse_object(self):
        self.pos += 1  # skip '{'
        obj = {}
        self.skip_whitespace()
        if self.pos < self.length and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            key = self.parse_string()
            if key is None: return None
            self.skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] != ':':
                return None
            self.pos += 1  # skip ':'
            val = self.parse_value()
            if val is None: return None
            obj[key] = val
            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            if self.pos >= self.length or self.text[self.pos] != ',':
                return None
            self.pos += 1  # skip ','

    def parse_array(self):
        self.pos += 1  # skip '['
        arr = []
        self.skip_whitespace()
        if self.pos < self.length and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            val = self.parse_value()
            if val is None: return None
            arr.append(val)
            self.skip_whitespace()
            if self.pos < self.length and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            if self.pos >= self.length or self.text[self.pos] != ',':
                return None
            self.pos += 1  # skip ','

    def parse_string(self):
        if self.pos >= self.length or self.text[self.pos] != '"':
            return None
        self.pos += 1
        res = []
        while self.pos < self.length:
            char = self.text[self.pos]
            if char == '"':
                self.pos += 1
                return "".join(res)
            elif char == '\\':
                self.pos += 1
                if self.pos >= self.length: return None
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
                    hex_str = self.text[self.pos:self.pos+4]
                    if len(hex_str) < 4: return None
                    try:
                        res.append(chr(int(hex_str, 16)))
                    except ValueError: return None
                    self.pos += 4
                else: return None
                self.pos += 1
            else:
                res.append(char)
                self.pos += 1
        return None

    def parse_true(self):
        if self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        return None

    def parse_false(self):
        if self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        return None

    def parse_null(self):
        if self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        return None

    def parse_number(self):
        start = self.pos
        if self.pos < self.length and self.text[self.pos] == '-':
            self.pos += 1
        
        # Integer part
        if self.pos < self.length and self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < self.length and self.text[self.pos].isdigit():
                return None  # Leading zero: 0123
        elif self.pos < self.length and self.text[self.pos].isdigit():
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            return None

        # Fractional part
        has_fraction = False
        if self.pos < self.length and self.text[self.pos] == '.':
            self.pos += 1
            has_fraction = True
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                return None
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        
        # Exponent part
        has_exponent = False
        if self.pos < self.length and self.text[self.pos] in 'eE':
            self.pos += 1
            has_exponent = True
            if self.pos < self.length and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                return None
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        
        num_str = self.text[start:self.pos]
        try:
            val = float(num_str)
            if not has_fraction and not has_exponent:
                return int(val)
            if val == int(val):
                return int(val)
            return val
        except ValueError:
            return None

def parse(text: str):
    parser = JSONParser(text)
    try:
        result = parser.parse_value()
        # If result is None, it could be a valid 'null' or an invalid input.
        # We check if the parser actually consumed characters to distinguish.
        if result is None and parser.pos == 0:
            return None
        
        parser.skip_whitespace()
        if parser.pos != parser.length:
            return None  # Trailing garbage
        return result
    except Exception:
        return None
