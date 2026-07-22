def parse(text: str):
    """Parse a JSON document and return the equivalent Python object."""
    
    # Sentinel to distinguish parsing error from null value
    PARSE_ERROR = object()
    
    class Tokenizer:
        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.length = len(text)
        
        def peek(self):
            if self.pos >= self.length:
                return None
            return self.text[self.pos]
        
        def advance(self):
            self.pos += 1
        
        def skip_whitespace(self):
            while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
                self.pos += 1
        
        def read_string(self):
            if self.peek() != '"':
                return PARSE_ERROR
            self.advance()
            
            result = []
            while self.pos < self.length:
                ch = self.text[self.pos]
                if ch == '"':
                    self.advance()
                    return ''.join(result)
                elif ch == '\\':
                    self.advance()
                    if self.pos >= self.length:
                        return PARSE_ERROR
                    esc = self.text[self.pos]
                    if esc == '"':
                        result.append('"')
                    elif esc == '\\':
                        result.append('\\')
                    elif esc == '/':
                        result.append('/')
                    elif esc == 'b':
                        result.append('\b')
                    elif esc == 'f':
                        result.append('\f')
                    elif esc == 'n':
                        result.append('\n')
                    elif esc == 'r':
                        result.append('\r')
                    elif esc == 't':
                        result.append('\t')
                    elif esc == 'u':
                        self.advance()
                        hex_str = self.text[self.pos:self.pos+4]
                        if len(hex_str) < 4:
                            return PARSE_ERROR
                        try:
                            code_point = int(hex_str, 16)
                            result.append(chr(code_point))
                            self.pos += 3
                        except:
                            return PARSE_ERROR
                    else:
                        return PARSE_ERROR
                    self.advance()
                else:
                    if ord(ch) < 0x20:
                        return PARSE_ERROR
                    result.append(ch)
                    self.advance()
            
            return PARSE_ERROR
        
        def read_number(self):
            start = self.pos
            
            if self.peek() == '-':
                self.advance()
            
            if self.peek() == '0':
                self.advance()
                if self.peek() and self.peek().isdigit():
                    return PARSE_ERROR
            elif self.peek() and self.peek().isdigit():
                while self.peek() and self.peek().isdigit():
                    self.advance()
            else:
                return PARSE_ERROR
            
            is_float = False
            
            if self.peek() == '.':
                is_float = True
                self.advance()
                if not self.peek() or not self.peek().isdigit():
                    return PARSE_ERROR
                while self.peek() and self.peek().isdigit():
                    self.advance()
            
            if self.peek() and self.peek() in 'eE':
                is_float = True
                self.advance()
                if self.peek() and self.peek() in '+-':
                    self.advance()
                if not self.peek() or not self.peek().isdigit():
                    return PARSE_ERROR
                while self.peek() and self.peek().isdigit():
                    self.advance()
            
            num_str = self.text[start:self.pos]
            try:
                if is_float:
                    return float(num_str)
                else:
                    return int(num_str)
            except:
                return PARSE_ERROR
    
    def parse_value(tokenizer):
        tokenizer.skip_whitespace()
        
        ch = tokenizer.peek()
        if ch is None:
            return PARSE_ERROR
        
        if ch == '"':
            return tokenizer.read_string()
        elif ch == '{':
            return parse_object(tokenizer)
        elif ch == '[':
            return parse_array(tokenizer)
        elif ch == 't':
            if tokenizer.text[tokenizer.pos:tokenizer.pos+4] == 'true':
                tokenizer.pos += 4
                return True
            return PARSE_ERROR
        elif ch == 'f':
            if tokenizer.text[tokenizer.pos:tokenizer.pos+5] == 'false':
                tokenizer.pos += 5
                return False
            return PARSE_ERROR
        elif ch == 'n':
            if tokenizer.text[tokenizer.pos:tokenizer.pos+4] == 'null':
                tokenizer.pos += 4
                return None
            return PARSE_ERROR
        elif ch == '-' or ch.isdigit():
            return tokenizer.read_number()
        else:
            return PARSE_ERROR
    
    def parse_object(tokenizer):
        if tokenizer.peek() != '{':
            return PARSE_ERROR
        tokenizer.advance()
        
        obj = {}
        tokenizer.skip_whitespace()
        
        if tokenizer.peek() == '}':
            tokenizer.advance()
            return obj
        
        while True:
            tokenizer.skip_whitespace()
            
            if tokenizer.peek() != '"':
                return PARSE_ERROR
            key = tokenizer.read_string()
            if key is PARSE_ERROR:
                return PARSE_ERROR
            
            tokenizer.skip_whitespace()
            
            if tokenizer.peek() != ':':
                return PARSE_ERROR
            tokenizer.advance()
            
            value = parse_value(tokenizer)
            if value is PARSE_ERROR:
                return PARSE_ERROR
            
            obj[key] = value
            
            tokenizer.skip_whitespace()
            
            ch = tokenizer.peek()
            if ch == '}':
                tokenizer.advance()
                return obj
            elif ch == ',':
                tokenizer.advance()
                tokenizer.skip_whitespace()
                if tokenizer.peek() == '}':
                    return PARSE_ERROR
            else:
                return PARSE_ERROR
    
    def parse_array(tokenizer):
        if tokenizer.peek() != '[':
            return PARSE_ERROR
        tokenizer.advance()
        
        arr = []
        tokenizer.skip_whitespace()
        
        if tokenizer.peek() == ']':
            tokenizer.advance()
            return arr
        
        while True:
            value = parse_value(tokenizer)
            if value is PARSE_ERROR:
                return PARSE_ERROR
            
            arr.append(value)
            
            tokenizer.skip_whitespace()
            
            ch = tokenizer.peek()
            if ch == ']':
                tokenizer.advance()
                return arr
            elif ch == ',':
                tokenizer.advance()
                tokenizer.skip_whitespace()
                if tokenizer.peek() == ']':
                    return PARSE_ERROR
            else:
                return PARSE_ERROR
    
    try:
        tokenizer = Tokenizer(text)
        result = parse_value(tokenizer)
        if result is PARSE_ERROR:
            return None
        
        tokenizer.skip_whitespace()
        
        if tokenizer.pos != tokenizer.length:
            return None
        
        return result
    except:
        return None
