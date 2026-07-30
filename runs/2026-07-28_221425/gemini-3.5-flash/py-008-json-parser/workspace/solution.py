class JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.len = len(text)

    def error(self):
        raise ValueError("Invalid JSON")

    def skip_ws(self):
        while self.pos < self.len and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse(self):
        self.skip_ws()
        if self.pos == self.len:
            self.error()
        val = self.parse_value()
        self.skip_ws()
        if self.pos != self.len:
            self.error()
        return val

    def parse_value(self):
        if self.pos >= self.len:
            self.error()
        char = self.text[self.pos]
        if char == '{':
            return self.parse_object()
        elif char == '[':
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char == 't':
            return self.parse_keyword('true', True)
        elif char == 'f':
            return self.parse_keyword('false', False)
        elif char == 'n':
            return self.parse_keyword('null', None)
        elif char in '-0123456789':
            return self.parse_number()
        else:
            self.error()

    def parse_keyword(self, keyword, value):
        k_len = len(keyword)
        if self.text[self.pos:self.pos+k_len] == keyword:
            self.pos += k_len
            return value
        self.error()

    def parse_string(self):
        if self.pos >= self.len or self.text[self.pos] != '"':
            self.error()
        self.pos += 1  # skip '"'
        
        chars = []
        while self.pos < self.len:
            c = self.text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(chars)
            elif c == '\\':
                if self.pos + 1 >= self.len:
                    self.error()
                esc = self.text[self.pos+1]
                if esc == '"':
                    chars.append('"')
                    self.pos += 2
                elif esc == '\\':
                    chars.append('\\')
                    self.pos += 2
                elif esc == '/':
                    chars.append('/')
                    self.pos += 2
                elif esc == 'b':
                    chars.append('\b')
                    self.pos += 2
                elif esc == 'f':
                    chars.append('\f')
                    self.pos += 2
                elif esc == 'n':
                    chars.append('\n')
                    self.pos += 2
                elif esc == 'r':
                    chars.append('\r')
                    self.pos += 2
                elif esc == 't':
                    chars.append('\t')
                    self.pos += 2
                elif esc == 'u':
                    if self.pos + 5 >= self.len:
                        self.error()
                    hex_str = self.text[self.pos+2:self.pos+6]
                    if len(hex_str) != 4 or not all(h in '0123456789abcdefABCDEF' for h in hex_str):
                        self.error()
                    val = int(hex_str, 16)
                    if 0xD800 <= val <= 0xDBFF:
                        if self.pos + 11 < self.len and self.text[self.pos+6:self.pos+8] == '\\u':
                            next_hex = self.text[self.pos+8:self.pos+12]
                            if len(next_hex) == 4 and all(h in '0123456789abcdefABCDEF' for h in next_hex):
                                val2 = int(next_hex, 16)
                                if 0xDC00 <= val2 <= 0xDFFF:
                                    codepoint = 0x10000 + ((val - 0xD800) << 10) + (val2 - 0xDC00)
                                    chars.append(chr(codepoint))
                                    self.pos += 12
                                    continue
                        self.error()
                    elif 0xDC00 <= val <= 0xDFFF:
                        self.error()
                    else:
                        chars.append(chr(val))
                        self.pos += 6
                else:
                    self.error()
            else:
                if ord(c) < 0x20:
                    self.error()
                chars.append(c)
                self.pos += 1
        self.error()

    def parse_number(self):
        start = self.pos
        if self.pos < self.len and self.text[self.pos] == '-':
            self.pos += 1
        
        if self.pos >= self.len:
            self.error()
        
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < self.len and self.text[self.pos].isdigit():
                self.error()
        elif self.text[self.pos] in '123456789':
            self.pos += 1
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            self.error()
        
        is_float = False
        if self.pos < self.len and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= self.len or not self.text[self.pos].isdigit():
                self.error()
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        
        if self.pos < self.len and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < self.len and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.len or not self.text[self.pos].isdigit():
                self.error()
            while self.pos < self.len and self.text[self.pos].isdigit():
                self.pos += 1
        
        num_str = self.text[start:self.pos]
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except (ValueError, OverflowError):
            self.error()

    def parse_array(self):
        if self.pos >= self.len or self.text[self.pos] != '[':
            self.error()
        self.pos += 1
        self.skip_ws()
        
        arr = []
        if self.pos < self.len and self.text[self.pos] == ']':
            self.pos += 1
            return arr
            
        while True:
            val = self.parse_value()
            arr.append(val)
            self.skip_ws()
            if self.pos < self.len and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            elif self.pos < self.len and self.text[self.pos] == ',':
                self.pos += 1
                self.skip_ws()
            else:
                self.error()

    def parse_object(self):
        if self.pos >= self.len or self.text[self.pos] != '{':
            self.error()
        self.pos += 1
        self.skip_ws()
        
        obj = {}
        if self.pos < self.len and self.text[self.pos] == '}':
            self.pos += 1
            return obj
            
        while True:
            if self.pos >= self.len or self.text[self.pos] != '"':
                self.error()
            key = self.parse_string()
            self.skip_ws()
            
            if self.pos >= self.len or self.text[self.pos] != ':':
                self.error()
            self.pos += 1
            self.skip_ws()
            
            val = self.parse_value()
            obj[key] = val
            self.skip_ws()
            
            if self.pos < self.len and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            elif self.pos < self.len and self.text[self.pos] == ',':
                self.pos += 1
                self.skip_ws()
            else:
                self.error()

def parse(text: str):
    if not isinstance(text, str):
        return None
    try:
        return JSONParser(text).parse()
    except ValueError:
        return None
