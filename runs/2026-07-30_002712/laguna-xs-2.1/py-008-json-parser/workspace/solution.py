import re

def parse(text: str):
    """Parse a JSON document and return the equivalent Python object."""
    
    class Parser:
        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.length = len(text)
        
        def peek(self):
            if self.pos < self.length:
                return self.text[self.pos]
            return None
        
        def consume(self):
            char = self.peek()
            if char is not None:
                self.pos += 1
            return char
        
        def skip_whitespace(self):
            while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
                self.pos += 1
        
        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= self.length:
                return None
            
            char = self.peek()
            
            if char == '"':
                return self.parse_string()
            elif char == '{':
                return self.parse_object()
            elif char == '[':
                return self.parse_array()
            elif char == 't':
                return self.parse_true()
            elif char == 'f':
                return self.parse_false()
            elif char == 'n':
                return self.parse_null()
            elif char == '-' or char.isdigit():
                return self.parse_number()
            else:
                return None
        
        def parse_string(self):
            if not self.consume() == '"':
                return None
            
            result = []
            while True:
                if self.pos >= self.length:
                    return None
                
                char = self.consume()
                
                if char == '"':
                    break
                elif char == '\\':
                    if self.pos >= self.length:
                        return None
                    
                    escaped = self.consume()
                    if escaped == '"':
                        result.append('"')
                    elif escaped == '\\':
                        result.append('\\')
                    elif escaped == '/':
                        result.append('/')
                    elif escaped == 'b':
                        result.append('\b')
                    elif escaped == 'f':
                        result.append('\f')
                    elif escaped == 'n':
                        result.append('\n')
                    elif escaped == 'r':
                        result.append('\r')
                    elif escaped == 't':
                        result.append('\t')
                    elif escaped == 'u':
                        if self.pos + 4 > self.length:
                            return None
                        hex_str = self.text[self.pos:self.pos + 4]
                        self.pos += 4
                        try:
                            code_point = int(hex_str, 16)
                            result.append(chr(code_point))
                        except ValueError:
                            return None
                    else:
                        return None
                elif ord(char) < 32:
                    return None
                else:
                    result.append(char)
            
            return ''.join(result)
        
        def parse_number(self):
            start = self.pos
            
            if self.peek() == '-':
                self.consume()
            
            if self.pos >= self.length:
                return None
            
            char = self.peek()
            if char not in '0123456789':
                return None
            
            # Check for leading zero
            if char == '0':
                self.consume()
                if self.pos < self.length and self.text[self.pos].isdigit():
                    return None  # Leading zero like "01" is invalid
            else:
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.consume()
            
            has_exponent = False
            
            if self.pos < self.length and self.peek() == '.':
                self.consume()
                if self.pos >= self.length or not self.text[self.pos].isdigit():
                    pass  # Decimal point must be followed by digit in valid JSON
                else:
                    while self.pos < self.length and self.text[self.pos].isdigit():
                        self.consume()
            
            if self.pos < self.length and (self.peek() == 'e' or self.peek() == 'E'):
                has_exponent = True
                self.consume()
                if self.pos < self.length and (self.peek() == '+' or self.peek() == '-'):
                    self.consume()
                if self.pos >= self.length or not self.text[self.pos].isdigit():
                    pass  # Exponent must have digits
                
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.consume()
            
            num_str = self.text[start:self.pos]
            try:
                if has_exponent or '.' in num_str:
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                return None
        
        def parse_object(self):
            if not self.consume() == '{':
                return None
            
            result = {}
            self.skip_whitespace()
            
            if self.peek() == '}':
                self.consume()
                return result
            
            while True:
                key_str = self.parse_string()
                if key_str is None:
                    return None
                
                self.skip_whitespace()
                if not self.peek() == ':':
                    return None
                self.consume()
                
                value = self.parse_value()
                if value is None and self.pos > 0:
                    # Check if we're at a valid position for parsing a value
                    pass
                
                result[key_str] = value
                
                self.skip_whitespace()
                char = self.peek()
                if char == '}':
                    self.consume()
                    return result
                elif char != ',':
                    return None
                
                self.consume()
                self.skip_whitespace()
        
        def parse_array(self):
            if not self.consume() == '[':
                return None
            
            result = []
            self.skip_whitespace()
            
            if self.peek() == ']':
                self.consume()
                return result
            
            while True:
                value = self.parse_value()
                # Need to check if parsing succeeded
                start_pos = self.pos  # We'll track this differently
                
                result.append(value)
                
                self.skip_whitespace()
                char = self.peek()
                if char == ']':
                    self.consume()
                    return result
                elif char != ',':
                    return None
                
                self.consume()
                self.skip_whitespace()
        
        def parse_true(self):
            if self.text[self.pos:self.pos + 4] == 'true':
                self.pos += 4
                return True
            return None
        
        def parse_false(self):
            if self.text[self.pos:self.pos + 5] == 'false':
                self.pos += 5
                return False
            return None
        
        def parse_null(self):
            if self.text[self.pos:self.pos + 4] == 'null':
                self.pos += 4
                return None
            return None
    
    # Create parser and attempt to parse
    parser = Parser(text)
    result = parser.parse_value()
    
    # Check for trailing garbage
    parser.skip_whitespace()
    if parser.pos < len(text):
        return None
    
    return result


# More robust implementation
def parse(text: str):
    """Parse a JSON document and return the equivalent Python object."""
    
    class Parser:
        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.length = len(text)
        
        def peek(self):
            if self.pos < self.length:
                return self.text[self.pos]
            return None
        
        def consume_char(self):
            char = self.peek()
            if char is not None:
                self.pos += 1
            return char
        
        def skip_whitespace(self):
            while self.pos < self.length and self.text[self.pos] in ' \t\n\r':
                self.pos += 1
        
        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= self.length:
                return None, False
            
            char = self.peek()
            
            if char == '"':
                val = self.parse_string()
                return val, True
            elif char == '{':
                val = self.parse_object()
                return val, True
            elif char == '[':
                val = self.parse_array()
                return val, True
            elif char == 't':
                val = self.parse_true()
                return val, True
            elif char == 'f':
                val = self.parse_false()
                return val, True
            elif char == 'n':
                val = self.parse_null()
                return val, True
            elif char == '-' or (char and char.isdigit()):
                val = self.parse_number()
                return val, True
            else:
                return None, False
        
        def parse_string(self):
            if not self.consume_char() == '"':
                return None
            
            result = []
            while True:
                if self.pos >= self.length:
                    return None
                
                char = self.consume_char()
                
                if char == '"':
                    break
                elif char == '\\':
                    if self.pos >= self.length:
                        return None
                    
                    escaped = self.consume_char()
                    if escaped == '"':
                        result.append('"')
                    elif escaped == '\\':
                        result.append('\\')
                    elif escaped == '/':
                        result.append('/')
                    elif escaped == 'b':
                        result.append('\b')
                    elif escaped == 'f':
                        result.append('\f')
                    elif escaped == 'n':
                        result.append('\n')
                    elif escaped == 'r':
                        result.append('\r')
                    elif escaped == 't':
                        result.append('\t')
                    elif escaped == 'u':
                        if self.pos + 4 > self.length:
                            return None
                        hex_str = self.text[self.pos:self.pos + 4]
                        try:
                            code_point = int(hex_str, 16)
                            self.pos += 4
                            result.append(chr(code_point))
                        except ValueError:
                            return None
                    else:
                        return None
                elif ord(char) < 32:
                    return None
                else:
                    result.append(char)
            
            return ''.join(result)
        
        def parse_number(self):
            start = self.pos
            
            if self.peek() == '-':
                self.consume_char()
            
            # Parse integer part
            char = self.peek()
            if not char or not (char.isdigit()):
                return None
            
            # Check for leading zero
            if char == '0':
                self.consume_char()
                next_char = self.peek()
                if next_char and next_char.isdigit():
                    return None  # Leading zero like "01" is invalid
            else:
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.consume_char()
            
            has_decimal = False
            has_exponent = False
            
            if self.pos < self.length and self.peek() == '.':
                has_decimal = True
                self.consume_char()
                char = self.peek()
                if not char or not char.isdigit():
                    pass  # Invalid but we continue for parsing
                else:
                    while self.pos < self.length and self.text[self.pos].isdigit():
                        self.consume_char()
            
            if self.pos < self.length and (self.peek() == 'e' or self.peek() == 'E'):
                has_exponent = True
                self.consume_char()
                char = self.peek()
                if char in ('+', '-'):
                    self.consume_char()
                char = self.peek()
                if not char or not char.isdigit():
                    pass  # Invalid but we continue for parsing
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.consume_char()
            
            num_str = self.text[start:self.pos]
            try:
                if has_decimal or has_exponent:
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                return None
        
        def parse_object(self):
            if not self.consume_char() == '{':
                return None
            
            result = {}
            self.skip_whitespace()
            
            if self.peek() == '}':
                self.consume_char()
                return result
            
            while True:
                key_str = self.parse_string()
                if key_str is None:
                    return None
                
                self.skip_whitespace()
                if not self.peek() == ':':
                    return None
                self.consume_char()
                
                value, success = self.parse_value()
                if not success:
                    return None
                
                result[key_str] = value
                
                self.skip_whitespace()
                char = self.peek()
                if char == '}':
                    self.consume_char()
                    return result
                elif char != ',':
                    return None
                
                self.consume_char()
                self.skip_whitespace()
        
        def parse_array(self):
            if not self.consume_char() == '[':
                return None
            
            result = []
            self.skip_whitespace()
            
            if self.peek() == ']':
                self.consume_char()
                return result
            
            while True:
                value, success = self.parse_value()
                if not success:
                    return None
                
                result.append(value)
                
                self.skip_whitespace()
                char = self.peek()
                if char == ']':
                    self.consume_char()
                    return result
                elif char != ',':
                    return None
                
                self.consume_char()
                self.skip_whitespace()
        
        def parse_true(self):
            if self.text[self.pos:self.pos + 4] == 'true':
                self.pos += 4
                return True
            return None
        
        def parse_false(self):
            if self.text[self.pos:self.pos + 5] == 'false':
                self.pos += 5
                return False
            return None
        
        def parse_null(self):
            if self.text[self.pos:self.pos + 4] == 'null':
                self.pos += 4
                return None
            return None
    
    parser = Parser(text)
    result, success = parser.parse_value()
    
    if not success:
        return None
    
    # Check for trailing garbage
    parser.skip_whitespace()
    if parser.pos < len(text):
        return None
    
    return result
