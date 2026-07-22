def parse(text: str):
    parser = JSONParser(text)
    try:
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(parser.text):
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
        
        char = self.text[self.pos]
        
        if char == '{':
            return self.parse_object()
        elif char == '[':
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char == 't':
            return self.parse_true()
        elif char == 'f':
            return self.parse_false()
        elif char == 'n':
            return self.parse_null()
        elif char == '-' or char.isdigit():
            return self.parse_number()
        else:
            raise ValueError(f"Unexpected character: {char}")
    
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
                raise ValueError("Expected string key")
            key = self.parse_string()
            
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                raise ValueError("Expected ':'")
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
                raise ValueError("Expected ',' or '}'")
    
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
                raise ValueError("Expected ',' or ']'")
    
    def parse_string(self):
        if self.pos >= len(self.text) or self.text[self.pos] != '"':
            raise ValueError("Expected '\"'")
        self.pos += 1
        result = []
        
        while self.pos < len(self.text):
            char = self.text[self.pos]
            
            if char == '"':
                self.pos += 1
                return ''.join(result)
            elif char == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    raise ValueError("Unterminated string escape")
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
                    if self.pos + 4 >= len(self.text):
                        raise ValueError("Incomplete unicode escape")
                    hex_str = self.text[self.pos+1:self.pos+5]
                    try:
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        self.pos += 5
                    except (ValueError, OverflowError):
                        raise ValueError("Invalid unicode escape")
                else:
                    raise ValueError(f"Invalid escape sequence: \\{escape_char}")
            else:
                result.append(char)
                self.pos += 1
        
        raise ValueError("Unterminated string")
    
    def parse_true(self):
        if self.text[self.pos:self.pos+4] == 'true':
            self.pos += 4
            return True
        else:
            raise ValueError("Invalid literal")
    
    def parse_false(self):
        if self.text[self.pos:self.pos+5] == 'false':
            self.pos += 5
            return False
        else:
            raise ValueError("Invalid literal")
    
    def parse_null(self):
        if self.text[self.pos:self.pos+4] == 'null':
            self.pos += 4
            return None
        else:
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
                raise ValueError("Leading zeros not allowed")
        else:
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
        is_float = False
        
        if self.pos < len(self.text) and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ValueError("Invalid number")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
        if self.pos < len(self.text) and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise ValueError("Invalid number")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        
        num_str = self.text[start:self.pos]
        
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            raise ValueError("Invalid number")
