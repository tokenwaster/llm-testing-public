class ParseError(Exception):
    pass


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
            raise ParseError("EOF")
        
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
            raise ParseError(f"Unexpected character")
    
    def parse_object(self):
        self.pos += 1
        obj = {}
        
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == '}':
            self.pos += 1
            return obj
        
        while True:
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                raise ParseError("Expected key")
            
            key = self.parse_string()
            
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                raise ParseError("Expected colon")
            self.pos += 1
            
            value = self.parse_value()
            obj[key] = value
            
            self.skip_whitespace()
            if self.pos >= len(self.text):
                raise ParseError("EOF in object")
            
            if self.text[self.pos] == '}':
                self.pos += 1
                return obj
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise ParseError("Expected , or }")
    
    def parse_array(self):
        self.pos += 1
        arr = []
        
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == ']':
            self.pos += 1
            return arr
        
        while True:
            value = self.parse_value()
            arr.append(value)
            
            self.skip_whitespace()
            if self.pos >= len(self.text):
                raise ParseError("EOF in array")
            
            if self.text[self.pos] == ']':
                self.pos += 1
                return arr
            elif self.text[self.pos] == ',':
                self.pos += 1
            else:
                raise ParseError("Expected , or ]")
    
    def parse_string(self):
        if self.pos >= len(self.text) or self.text[self.pos] != '"':
            raise ParseError("Expected string")
        
        self.pos += 1
        result = []
        
        while self.pos < len(self.text):
            c = self.text[self.pos]
            
            if c == '"':
                self.pos += 1
                return ''.join(result)
            elif c == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    raise ParseError("Unterminated escape")
                
                escape_char = self.text[self.pos]
                if escape_char == '"':
                    result.append('"')
                    self.pos += 1
                elif escape_char == '\\':
                    result.append('\\')
                    self.pos += 1
                elif escape_char == '/':
                    result.append('/')
                    self.pos += 1
                elif escape_char == 'b':
                    result.append('\b')
                    self.pos += 1
                elif escape_char == 'f':
                    result.append('\f')
                    self.pos += 1
                elif escape_char == 'n':
                    result.append('\n')
                    self.pos += 1
                elif escape_char == 'r':
                    result.append('\r')
                    self.pos += 1
                elif escape_char == 't':
                    result.append('\t')
                    self.pos += 1
                elif escape_char == 'u':
                    self.pos += 1
                    if self.pos + 3 >= len(self.text):
                        raise ParseError("Invalid unicode escape")
                    hex_str = self.text[self.pos:self.pos+4]
                    if not all(ch in '0123456789abcdefABCDEF' for ch in hex_str):
                        raise ParseError("Invalid unicode escape")
                    code_point = int(hex_str, 16)
                    result.append(chr(code_point))
                    self.pos += 4
                else:
                    raise ParseError("Invalid escape")
            elif ord(c) < 0x20:
                raise ParseError("Control character in string")
            else:
                result.append(c)
                self.pos += 1
        
        raise ParseError("Unterminated string")
    
    def parse_number(self):
        start = self.pos
        
        if self.pos < len(self.text) and self.text[self.pos] == '-':
            self.pos += 1
        
        if self.pos >= len(self.text):
            raise ParseError("Invalid number")
        
        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos].isdigit():
                raise ParseError("Leading zero")
        elif self.text[self.pos].isdigit():
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise ParseError("Invalid number")
        
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ParseError("Invalid fraction")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
        if self.pos < len(self.text) and self.text[self.pos] in 'eE':
            self.pos += 1
            if self.pos >= len(self.text):
                raise ParseError("Invalid exponent")
            if self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ParseError("Invalid exponent")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
        num_str = self.text[start:self.pos]
        if '.' in num_str or 'e' in num_str or 'E' in num_str:
            return float(num_str)
        else:
            return int(num_str)
    
    def parse_true(self):
        if self.text[self.pos:self.pos+4] == 'true':
            self.pos += 4
            return True
        raise ParseError("Invalid literal")
    
    def parse_false(self):
        if self.text[self.pos:self.pos+5] == 'false':
            self.pos += 5
            return False
        raise ParseError("Invalid literal")
    
    def parse_null(self):
        if self.text[self.pos:self.pos+4] == 'null':
            self.pos += 4
            return None
        raise ParseError("Invalid literal")


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
