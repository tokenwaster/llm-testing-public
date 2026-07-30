class JSONParseError(Exception):
    pass

class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def parse(self):
        try:
            self.skip_ws()
            if self.pos >= self.length:
                return None
            val = self.parse_value()
            self.skip_ws()
            if self.pos < self.length:
                return None
            return val
        except JSONParseError:
            return None
        except Exception:
            return None

    def skip_ws(self):
        while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        if self.pos >= self.length:
            raise JSONParseError()
        ch = self.text[self.pos]
        if ch == '{':
            return self.parse_object()
        elif ch == '[':
            return self.parse_array()
        elif ch == '"':
            return self.parse_string()
        elif ch == '-' or ch in '0123456789':
            return self.parse_number()
        elif self.text[self.pos:self.pos+4] == 'true':
            self.pos += 4
            return True
        elif self.text[self.pos:self.pos+5] == 'false':
            self.pos += 5
            return False
        elif self.text[self.pos:self.pos+4] == 'null':
            self.pos += 4
            return None
        else:
            raise JSONParseError()

    def parse_object(self):
        self.pos += 1
        self.skip_ws()
        if self.pos < self.length and self.text[self.pos] == '}':
            self.pos += 1
            return {}
        
        obj = {}
        while True:
            self.skip_ws()
            if self.pos >= self.length or self.text[self.pos] != '"':
                raise JSONParseError()
            key = self.parse_string()
            
            self.skip_ws()
            if self.pos >= self.length or self.text[self.pos] != ':':
                raise JSONParseError()
            self.pos += 1
            
            self.skip_ws()
            val = self.parse_value()
            obj[key] = val
            
            self.skip_ws()
            if self.pos >= self.length:
                raise JSONParseError()
            if self.text[self.pos] == '}':
                self.pos += 1
                return obj
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise JSONParseError()

    def parse_array(self):
        self.pos += 1
        self.skip_ws()
        if self.pos < self.length and self.text[self.pos] == ']':
            self.pos += 1
            return []
        
        arr = []
        while True:
            self.skip_ws()
            val = self.parse_value()
            arr.append(val)
            
            self.skip_ws()
            if self.pos >= self.length:
                raise JSONParseError()
            if self.text[self.pos] == ']':
                self.pos += 1
                return arr
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise JSONParseError()

    def parse_string(self):
        if self.pos >= self.length or self.text[self.pos] != '"':
            raise JSONParseError()
        self.pos += 1
        chars = []
        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch == '"':
                self.pos += 1
                return ''.join(chars)
            elif ch == '\\':
                self.pos += 1
                if self.pos >= self.length:
                    raise JSONParseError()
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
                    if self.pos + 5 > self.length:
                        raise JSONParseError()
                    hex_str = self.text[self.pos+1:self.pos+5]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise JSONParseError()
                    code_point = int(hex_str, 16)
                    self.pos += 5
                    if 0xD800 <= code_point <= 0xDBFF:
                        if self.pos + 6 > self.length or self.text[self.pos] != '\\' or self.text[self.pos+1] != 'u':
                            raise JSONParseError()
                        low_hex = self.text[self.pos+2:self.pos+6]
                        if not all(c in '0123456789abcdefABCDEF' for c in low_hex):
                            raise JSONParseError()
                        low_code = int(low_hex, 16)
                        if 0xDC00 <= low_code <= 0xDFFF:
                            code_point = 0x10000 + (code_point - 0xD800) * 0x400 + (low_code - 0xDC00)
                            self.pos += 6
                        else:
                            raise JSONParseError()
                    chars.append(chr(code_point))
                else:
                    raise JSONParseError()
                self.pos += 1
            elif ord(ch) < 0x20:
                raise JSONParseError()
            else:
                chars.append(ch)
                self.pos += 1
        raise JSONParseError()

    def parse_number(self):
        start = self.pos
        if self.pos < self.length and self.text[self.pos] == '-':
            self.pos += 1
        if self.pos >= self.length:
            raise JSONParseError()
        
        if self.text[self.pos] == '0':
            self.pos += 1
        elif self.text[self.pos] in '0123456789':
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.pos += 1
        else:
            raise JSONParseError()
            
        is_float = False
        if self.pos < self.length and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= self.length or self.text[self.pos] not in '0123456789':
                raise JSONParseError()
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.pos += 1
                
        if self.pos < self.length and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.length or self.text[self.pos] not in '0123456789':
                raise JSONParseError()
            while self.pos < self.length and self.text[self.pos] in '0123456789':
                self.pos += 1
                
        num_str = self.text[start:self.pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)

def parse(text: str):
    parser = JSONParser(text)
    return parser.parse()
