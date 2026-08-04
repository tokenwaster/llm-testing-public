def parse(text: str):
    """
    Parses a JSON string and returns the corresponding Python object.
    Returns None if the input is not valid JSON.
    """
    if not isinstance(text, str):
        return None
    
    # We'll use an index pointer to walk through the string
    index = 0
    length = len(text)
    
    def skip_whitespace():
        nonlocal index
        while index < length and text[index] in ' \t\n\r':
            index += 1
    
    def parse_value():
        nonlocal index
        skip_whitespace()
        if index >= length:
            return None
        
        ch = text[index]
        if ch == '{':
            return parse_object()
        elif ch == '[':
            return parse_array()
        elif ch == '"':
            return parse_string()
        elif ch in '-0123456789':
            return parse_number()
        elif text.startswith('true', index):
            index += 4
            return True
        elif text.startswith('false', index):
            index += 5
            return False
        elif text.startswith('null', index):
            index += 4
            return None
        else:
            return None
    
    def parse_object():
        nonlocal index
        # index is at '{'
        index += 1  # consume '{'
        obj = {}
        skip_whitespace()
        if index < length and text[index] == '}':
            index += 1
            return obj
        
        while True:
            skip_whitespace()
            if index >= length:
                return None
            # Expect a string key
            if text[index] != '"':
                return None
            key = parse_string()
            if key is None:
                return None
            skip_whitespace()
            if index >= length or text[index] != ':':
                return None
            index += 1  # consume ':'
            value = parse_value()
            if value is None and index < length:
                # Could be that parse_value returned None for valid null, but we need to check
                # Actually parse_value returns None for null, which is valid.
                # But if parse_value returns None because of error, we need to detect.
                # We'll handle by checking if we actually parsed null.
                # Since parse_value returns None for both null and error, we need to differentiate.
                # We'll store a flag or check the original text.
                # Better: let parse_value return a sentinel for error? But spec says return None for invalid.
                # We'll rely on the fact that after parse_value, if it was null, index advanced.
                # If parse_value returns None and index didn't advance, it's an error.
                # But parse_value for null advances index by 4. So we can check if index advanced.
                # However, we don't have the old index. Let's restructure: we'll have parse_value return a special marker for error.
                # Simpler: we'll check if the value is None and the next char is not a valid separator, but that's messy.
                # Let's implement parse_value to return (value, success) or use exceptions.
                # To keep it simple, we'll use a helper that returns a tuple (value, error_flag).
                pass
            # Actually, let's redesign: we'll use a different approach.
            # For now, assume parse_value works correctly.
            # But we need to handle the case where parse_value returns None due to invalid input.
            # We'll check if index didn't move? Not reliable.
            # Let's implement parse_value to raise an exception on error, and catch it.
            # But the spec says return None, not raise.
            # We'll use a global error flag.
            # Let's refactor: we'll use a class with state.
            # Since we're in a function, we'll use a list to hold error state.
            pass
        
        # The above is incomplete. Let's rewrite properly.
        # I'll restart with a cleaner implementation.
    
    # Given the complexity, I'll implement a proper recursive descent parser
    # with error handling via returning None and checking index progress.
    
    # Let's redo the whole function properly.
    
    # We'll use a class to hold state.
    class Parser:
        def __init__(self, s):
            self.s = s
            self.pos = 0
            self.len = len(s)
        
        def skip_ws(self):
            while self.pos < self.len and self.s[self.pos] in ' \t\n\r':
                self.pos += 1
        
        def peek(self):
            if self.pos < self.len:
                return self.s[self.pos]
            return None
        
        def consume(self, ch):
            if self.pos < self.len and self.s[self.pos] == ch:
                self.pos += 1
                return True
            return False
        
        def parse(self):
            self.skip_ws()
            val = self.parse_value()
            if val is None:
                return None
            self.skip_ws()
            # Check for trailing garbage
            if self.pos != self.len:
                return None
            return val
        
        def parse_value(self):
            self.skip_ws()
            ch = self.peek()
            if ch is None:
                return None
            if ch == '{':
                return self.parse_object()
            elif ch == '[':
                return self.parse_array()
            elif ch == '"':
                return self.parse_string()
            elif ch in '-0123456789':
                return self.parse_number()
            elif self.s.startswith('true', self.pos):
                self.pos += 4
                return True
            elif self.s.startswith('false', self.pos):
                self.pos += 5
                return False
            elif self.s.startswith('null', self.pos):
                self.pos += 4
                return None
            else:
                return None
        
        def parse_object(self):
            # consume '{'
            if not self.consume('{'):
                return None
            obj = {}
            self.skip_ws()
            if self.consume('}'):
                return obj
            while True:
                self.skip_ws()
                if self.peek() != '"':
                    return None
                key = self.parse_string()
                if key is None:
                    return None
                self.skip_ws()
                if not self.consume(':'):
                    return None
                val = self.parse_value()
                if val is None:
                    # Could be null, but parse_value returns None for null too.
                    # We need to differentiate. Let's check if we actually parsed null.
                    # We'll store the position before parsing and see if it moved.
                    # But easier: we'll have parse_value return a special marker for error.
                    # Let's use a sentinel object.
                    pass
                # Actually, let's handle null properly: parse_value returns None for null,
                # but also for error. We'll check if the next character is valid after null.
                # Since we can't distinguish, we'll change approach: parse_value will return
                # a tuple (value, success). But that changes the interface.
                # Let's instead use a different method: we'll have parse_value return None on error,
                # but we'll also check if the position advanced. If it didn't, it's an error.
                # For null, position advances by 4. So we can check.
                # We'll save position before calling parse_value.
                pos_before = self.pos
                val = self.parse_value()
                if val is None and self.pos == pos_before:
                    # parse_value didn't advance, so it's an error (not null)
                    return None
                # For null, val is None but pos advanced, so it's fine.
                obj[key] = val
                self.skip_ws()
                if self.consume(','):
                    continue
                elif self.consume('}'):
                    return obj
                else:
                    return None
        
        def parse_array(self):
            if not self.consume('['):
                return None
            arr = []
            self.skip_ws()
            if self.consume(']'):
                return arr
            while True:
                self.skip_ws()
                pos_before = self.pos
                val = self.parse_value()
                if val is None and self.pos == pos_before:
                    return None
                arr.append(val)
                self.skip_ws()
                if self.consume(','):
                    continue
                elif self.consume(']'):
                    return arr
                else:
                    return None
        
        def parse_string(self):
            if not self.consume('"'):
                return None
            result = []
            while self.pos < self.len:
                ch = self.s[self.pos]
                if ch == '"':
                    self.pos += 1
                    return ''.join(result)
                elif ch == '\\':
                    self.pos += 1
                    if self.pos >= self.len:
                        return None
                    esc = self.s[self.pos]
                    self.pos += 1
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
                        # parse 4 hex digits
                        if self.pos + 4 > self.len:
                            return None
                        hex_str = self.s[self.pos:self.pos+4]
                        if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                            return None
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        self.pos += 4
                    else:
                        return None
                else:
                    # Regular character
                    # JSON strings cannot contain control characters (0x00-0x1F) except as escapes
                    if ord(ch) < 0x20:
                        return None
                    result.append(ch)
                    self.pos += 1
            # Unterminated string
            return None
        
        def parse_number(self):
            start = self.pos
            # Handle optional minus
            if self.peek() == '-':
                self.pos += 1
            # Integer part
            if self.pos >= self.len:
                return None
            if self.s[self.pos] == '0':
                self.pos += 1
                # After leading zero, next char must be '.' or 'e' or 'E' or end of number
                # But we need to check that there is no digit after leading zero (like 007)
                # We'll handle by checking after we parse the number.
            elif '1' <= self.s[self.pos] <= '9':
                self.pos += 1
                while self.pos < self.len and '0' <= self.s[self.pos] <= '9':
                    self.pos += 1
            else:
                return None
            
            # Fractional part
            is_float = False
            if self.pos < self.len and self.s[self.pos] == '.':
                is_float = True
                self.pos += 1
                if self.pos >= self.len or not ('0' <= self.s[self.pos] <= '9'):
                    return None
                while self.pos < self.len and '0' <= self.s[self.pos] <= '9':
                    self.pos += 1
            
            # Exponent part
            if self.pos < self.len and self.s[self.pos] in 'eE':
                is_float = True
                self.pos += 1
                if self.pos < self.len and self.s[self.pos] in '+-':
                    self.pos += 1
                if self.pos >= self.len or not ('0' <= self.s[self.pos] <= '9'):
                    return None
                while self.pos < self.len and '0' <= self.s[self.pos] <= '9':
                    self.pos += 1
            
            # Now extract the substring
            num_str = self.s[start:self.pos]
            # Check for leading zeros in integer part (if not float)
            if not is_float:
                # If number starts with '-0' and has more digits, invalid
                if num_str.startswith('-0') and len(num_str) > 2 and num_str[2].isdigit():
                    return None
                if num_str.startswith('0') and len(num_str) > 1 and num_str[1].isdigit():
                    return None
            # Convert
            try:
                if is_float:
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                return None
    
    parser = Parser(text)
    return parser.parse()
