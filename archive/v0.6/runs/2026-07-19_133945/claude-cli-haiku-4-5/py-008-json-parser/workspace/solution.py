def parse(text: str):
    try:
        parser = JSONParser(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != len(text):
            return None
        return result
    except:
        return None


class JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
    
    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1
    
    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= len(self.text):
            raise ValueError("Unexpected end of input")
        
        c = self.text[self.pos]
        
        if c == '{':
            return self.parse_object()
        elif c == '[':
            return self.parse_array()
        elif c == '"':
            return self.parse_string()
        elif c == 't':
            return self.parse_true()
        elif c == 'f':
            return self.parse_false()
        elif c == 'n':
            return self.parse_null()
        elif c == '-' or c.isdigit():
            return self.parse_number()
        else:
            raise ValueError("Unexpected character")
    
    def parse_object(self):
        obj = {}
        self.pos += 1
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
            
            if self.text[self.pos] == '}':
                self.pos += 1
                return obj
            elif self.text[self.pos] == ',':
                self.pos += 1
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    raise ValueError("Trailing comma")
            else:
                raise ValueError("Expected comma or brace")
    
    def parse_array(self):
        arr = []
        self.pos += 1
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
            
            if self.text[self.pos] == ']':
                self.pos += 1
                return arr
            elif self.text[self.pos] == ',':
                self.pos += 1
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == ']':
                    raise ValueError("Trailing comma")
            else:
                raise ValueError("Expected comma or bracket")
    
    def parse_string(self):
        self.pos += 1
        s = ""
        
        while self.pos < len(self.text):
            c = self.text[self.pos]
            
            if c == '"':
                self.pos += 1
                return s
            elif c == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    raise ValueError("Unterminated string")
                
                escape_char = self.text[self.pos]
                if escape_char == '"':
                    s += '"'
                elif escape_char == '\\':
                    s += '\\'
                elif escape_char == '/':
                    s += '/'
                elif escape_char == 'b':
                    s += '\b'
                elif escape_char == 'f':
                    s += '\f'
                elif escape_char == 'n':
                    s += '\n'
                elif escape_char == 'r':
                    s += '\r'
                elif escape_char == 't':
                    s += '\t'
                elif escape_char == 'u':
                    self.pos += 1
                    if self.pos + 3 >= len(self.text):
                        raise ValueError("Incomplete unicode escape")
                    hex_str = self.text[self.pos:self.pos+4]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ValueError("Invalid unicode escape")
                    code_point = int(hex_str, 16)
                    s += chr(code_point)
                    self.pos += 3
                else:
                    raise ValueError("Invalid escape sequence")
                
                self.pos += 1
            else:
                s += c
                self.pos += 1
        
        raise ValueError("Unterminated string")
    
    def parse_true(self):
        if self.text[self.pos:self.pos+4] == 'true':
            self.pos += 4
            return True
        raise ValueError("Invalid literal")
    
    def parse_false(self):
        if self.text[self.pos:self.pos+5] == 'false':
            self.pos += 5
            return False
        raise ValueError("Invalid literal")
    
    def parse_null(self):
        if self.text[self.pos:self.pos+4] == 'null':
            self.pos += 4
            return None
        raise ValueError("Invalid literal")
    
    def parse_number(self):
        start = self.pos
        
        if self.pos < len(self.text) and self.text[self.pos] == '-':
            self.pos += 1
        
        if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
            raise ValueError("Invalid number")
        
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos].isdigit():
                raise ValueError("Leading zero")
        else:
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
        is_float = False
        
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ValueError("Invalid decimal")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
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
