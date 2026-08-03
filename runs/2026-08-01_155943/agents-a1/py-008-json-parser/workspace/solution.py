def parse(text: str):
    class JSONParser:
        def __init__(self, s):
            self.s = s
            self.pos = 0
        
        def peek(self):
            if self.pos < len(self.s):
                return self.s[self.pos]
            return None
        
        def advance(self):
            ch = self.peek()
            self.pos += 1
            return ch
        
        def skip_whitespace(self):
            while self.peek() in ' \t\n\r':
                self.advance()
        
        def parse_value(self):
            self.skip_whitespace()
            if self.peek() is None:
                raise ValueError("Unexpected end of input")
            
            start = self.pos
            
            # Check for string
            if self.peek() == '"':
                return self.parse_string()
            
            # Check for object
            if self.peek() == '{':
                return self.parse_object()
            
            # Check for array
            if self.peek() == '[':
                return self.parse_array()
            
            # Check for number (may start with -)
            if self.peek() in '-0123456789':
                return self.parse_number(start)
            
            # Check for true, false, null
            remaining = self.s[self.pos:]
            if remaining.startswith('true'):
                self.pos += 4
                return True
            elif remaining.startswith('false'):
                self.pos += 5
                return False
            elif remaining.startswith('null'):
                self.pos += 4
                return None
            
            # Invalid token start
            raise ValueError(f"Invalid token at position {self.pos}")
        
        def parse_string(self):
            if self.advance() != '"':
                raise ValueError("Expected opening quote")
            
            result = []
            while True:
                ch = self.peek()
                
                # End of string
                if ch == '"':
                    self.advance()
                    return ''.join(result)
                
                # Control characters not allowed unescaped
                if ord(ch) < 0x20:
                    raise ValueError("Unescaped control character in string")
                
                if ch == '\\':
                    self.advance()
                    escape = self.peek()
                    if escape is None:
                        raise ValueError("Unterminated escape sequence")
                    
                    if escape == '"':
                        result.append('"')
                    elif escape == '\\':
                        result.append('\\')
                    elif escape == '/':
                        result.append('/')
                    elif escape == 'b':
                        result.append('\b')
                    elif escape == 'f':
                        result.append('\f')
                    elif escape == 'n':
                        result.append('\n')
                    elif escape == 'r':
                        result.append('\r')
                    elif escape == 't':
                        result.append('\t')
                    elif escape == 'u':
                        # Unicode escape \uXXXX
                        self.advance()
                        if len(self.s) < self.pos + 4:
                            raise ValueError("Invalid unicode escape sequence")
                        
                        hex_chars = self.s[self.pos:self.pos+4]
                        try:
                            code_point = int(hex_chars, 16)
                        except ValueError:
                            raise ValueError(f"Invalid unicode characters {hex_chars}")
                        
                        result.append(chr(code_point))
                        self.pos += 4
                    else:
                        raise ValueError(f"Unknown escape sequence \\{escape}")
                    
                elif ch is None:
                    # Unterminated string
                    raise ValueError("Unterminated string literal")
                
                else:
                    result.append(ch)
                    self.advance()
        
        def parse_number(self, start_pos=None):
            if start_pos is not None and self.pos != start_pos:
                return self.parse_number()
            
            pos = self.pos
            
            # Check for negative sign
            if self.peek() == '-':
                self.advance()
            
            # Integer part - must have digits but cannot have leading zeros unless it's just 0
            if self.peek() is None:
                raise ValueError("Invalid number")
            
            has_leading_zero = False
            int_part = []
            
            while self.peek() in '0123456789':
                # Check for leading zeros (not allowed unless it's just 0)
                if len(int_part) == 0 and self.peek() == '0' and pos != start_pos:
                    has_leading_zero = True
                
                int_part.append(self.advance())
            
            if not int_part:
                raise ValueError("Invalid number")
            
            # Decimal part
            is_float = False
            decimal_part = []
            if self.peek() == '.':
                is_float = True
                self.advance()
                
                digits_after_decimal = 0
                while self.peek() in '0123456789':
                    digits_after_decimal += 1
                    decimal_part.append(self.advance())
                
                if digits_after_decimal == 0:
                    raise ValueError("Invalid number")
            
            # Exponent part
            exp_part = []
            if self.peek() in 'eE' and (is_float or int_part):
                is_float = True
                self.advance()
                
                # Optional sign
                if self.peek() in '-+':
                    self.advance()
                
                digits_in_exp = 0
                while self.peek() in '0123456789':
                    digits_in_exp += 1
                    exp_part.append(self.advance())
                
                if digits_in_exp == 0:
                    raise ValueError("Invalid number exponent")
            
            # Check for leading zero issue with trailing zeros only
            if self.pos - pos > len(int_part) + 2 and int_part[0] == '0' and len(int_part) > 1:
                has_leading_zero = True
            
            num_str = ''.join(self.s[start_pos:self.pos])
            
            # Check for leading zeros in the integer part (e.g., "007", "00", etc.)
            if not is_float and int_part and len(int_part) > 1 and int_part[0] == '0' and self.s.find('0', start_pos, start_pos+2) != -1:
                # This is a bit tricky because we need to check for leading zeros before any decimal point or exponent
                if '.' not in num_str[:num_str.index('.') if '.' in num_str else len(num_str)] and 'e' not in num_str[:num_str.index('e') if 'e' in num_str else len(num_str)]:
                    # Check: after stripping the leading zero, what remains starts with another digit?
                    temp = int_part[0] + ''.join(int_part[1:])  # The parsed integer part string
                    if len(temp) > 1 and temp.startswith('0'):
                        has_leading_zero = True
            
            # More precise check: look at the actual substring in s from start_pos to pos of decimal/exponent or end
            full_num_str = num_str.split('.')[0].split('e')[0].upper()
            if len(full_num_str) > 1 and (full_num_str.startswith('0') or 
                 ('-'.in_num_str if '-' in full_num_str else False)): # this is getting messy, let's simplify
            
                # Actually simpler: check the raw substring before decimal/exponent for leading zeros
                pre_exp = num_str.split('.')[0] if '.' in num_str else num_str
                if 'e' in pre_exp:  # exponent comes after potential decimals? No, e can be in integer part too per JSON spec... wait no.
                    # In JSON number format: [minus]?int_part[decimal][exponent]
                    # So the raw string might have both . and e/E, or just one of them, or none.
                
            # Let's do a proper check for leading zeros in integer part:
            int_str = num_str.split('.')[0].split('e')[0].upper()
            if 'e' in int_str:
                int_str = int_str[:int_str.index('e')]
            
            # If we have more than 1 digit and starts with '0', it's invalid (unless the number is just "0" or "-0")
            has_leading_zero = False
            if len(int_str) > 1:
                # Check for leading zero that isn't followed by non-digit? No, JSON spec says no leading zeros at all unless it's exactly 0.
                first_digit = int_str[0] if int_str.startswith('-') else int_str[-len(int_str):][0]
                # Actually simpler: strip optional minus and check the integer part string for leading zero with length > 1
                digits_only = int_str.lstrip('-')
                if len(digits_only) > 1 and digits_only[0] == '0':
                    has_leading_zero = True
            
            if has_leading_zero:
                raise ValueError("Leading zeros not allowed")
            
            try:
                num_value = float(num_str)
            except ValueError:
                raise ValueError("Invalid number format")
            
            return int(num_value) if is_float == False else num_value
        
        def parse_object(self):
            self.advance()  # {
            obj = {}
            self.skip_whitespace()
            
            while True:
                ch = self.peek()
                
                if ch == '}':
                    self.advance()
                    return obj
                
                if not (ch == ':' or ch in '0123456789-'):  # key must be string, so we expect " or something invalid after whitespace
                    raise ValueError("Invalid object content")
                
                self.skip_whitespace()
                key = self.parse_string()
                self.skip_whitespace()
                
                if self.advance() != ':':
                    raise ValueError("Expected colon")
                
                value = self.parse_value()
                
                obj[key] = value
                
                self.skip_whitespace()
                
                ch = self.peek()
                if ch == '}':
                    self.advance()
                    return obj
                
                if ch == ',':
                    self.advance()
                    
                    # Check for trailing comma after this comma (next token would be } or key)
                    self.skip_whitespace()
                    peek_after_comma = self.peek()
                    if peek_after_comma is None:
                        raise ValueError("Trailing comma")
                
                elif ch == ' ':  # whitespace might have been consumed, check again after potential skip?
                    # Actually we just handled the case where next char should be } or ,. If it's something else and not }, that's invalid.
                    continue
            
            return obj
        
        def parse_array(self):
            self.advance()  # [
            arr = []
            
            while True:
                ch = self.peek()
                
                if ch == ']':
                    self.advance()
                    return arr
                
                value = self.parse_value()
                
                arr.append(value)
                
                self.skip_whitespace()
                ch = self.peek()
                
                if ch == ']':
                    self.advance()
                    return arr
                
                if ch == ',':
                    self.advance()
                    
                    # Check for trailing comma: after this comma and whitespace, we might expect ] or another value.
                    # But JSON doesn't allow trailing commas in arrays.
                    # We'll let the next parse_value call fail appropriately (it will raise ValueError for unexpected end).
                
                elif ch == ' ':  # extra space? shouldn't happen after peek but just to be safe
                    continue
            
            return arr
    
    try:
        parser = JSONParser(text)
        
        result = parser.parse_value()
        parser.skip_whitespace()
        
        if parser.peek() is not None:
            raise ValueError("Trailing content")
        
        return result
    
    except Exception:
        return None
