def parse(text: str):
    class JSONParser:
        def __init__(self, text):
            self.text = text
            self.pos = 0
            self.length = len(text)

        def skip_whitespace(self):
            while self.pos < self.length and self.text[self.pos] in " \n\r\t":
                self.pos += 1

        def peek(self):
            return self.text[self.pos] if self.pos < self.length else None

        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= self.length:
                return None
            char = self.peek()
            if char == '{':
                return self._parse_object()
            elif char == '[':
                return self._parse_array()
            elif char == '"':
                return self._parse_string()
            elif char == 't' and self.text.startswith('true', self.pos):
                self.pos += 4
                self.skip_whitespace()
                if self.pos < self.length and self.text[self.pos] not in ',]}': return None
                return True
            elif char == 'f' and self.text.startswith('false', self.pos):
                self.pos += 5
                self.skip_whitespace()
                if self.pos < self.length and self.text[self.pos] not in ',]}': return None
                return False
            elif char == 'n' and self.text.startswith('null', self.pos):
                self.pos += 4
                self.skip_whitespace()
                if self.pos < self.length and self.text[self.pos] not in ',]}': return None
                return None
            elif char == '-' or (char is not None and char.isdigit()):
                res = self._parse_number()
                if res is None: return None
                # Ensure no garbage immediately after number like "123abc"
                self.skip_whitespace()
                if self.pos < self.length and self.text[self.pos] not in ',]}': return None
                return res
            else:
                return None

        def _parse_object(self):
            obj = {}
            self.pos += 1  # {
            self.skip_whitespace()
            if self.peek() == '}':
                self.pos += 1
                return obj
            while True:
                self.skip_whitespace()
                key = self._parse_string()
                if key is None: return None
                self.skip_whitespace()
                if self.peek() != ':': return None
                self.pos += 1  # :
                val = self.parse_value()
                if val is None: return None
                obj[key] = val
                self.skip_whitespace()
                char = self.peek()
                if char == '}':
                    self.pos += 1
                    return obj
                elif char == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.peek() == '}': return None  # Trailing comma error
                else:
                    return None

        def _parse_array(self):
            arr = []
            self.pos += 1  # [
            self.skip_whitespace()
            if self.peek() == ']':
                self.pos += 1
                return arr
            while True:
                val = self.parse_value()
                if val is None: return None
                arr.append(val)
                self.skip_whitespace()
                char = self.peek()
                if char == ']':
                    self.pos += 1
                    return arr
                elif char == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.peek() == ']': return None  # Trailing comma error
                else:
                    return None

        def _parse_string(self):
            self.pos += 1  # "
            res = []
            while self.pos < self.length:
                char = self.text[self.pos]
                if char == '"':
                    self.pos += 1
                    return "".join(res)
                elif char == '\\':
                    self.pos += 1
                    esc = self.text[self.pos] if self.pos < self.length else None
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
                        if len(hex_str) < 4 or not all(c in "0123456789abcdefABCDEF" for c in hex_str):
                            return None
                        res.append(chr(int(hex_str, 16)))
                        self.pos += 4
                    else: return None  # Invalid escape sequence
                    self.pos += 1
                elif ord(char) < 32:  # Control characters not allowed in JSON strings
                    return None
                else:
                    res.append(char)
                    self.pos += 1
            return None

        def _parse_number(self):
            start = self.pos
            if self.peek() == '-':
                self.pos += 1
            if self.pos >= self.length: return None
            
            if self.text[self.pos] == '0':
                self.pos += 1
                if self.pos < self.length and self.text[self.pos].isdigit():
                    return None  # Leading zero (e.g., "07")
            else:
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.pos += 1
                if self.pos == start or (self.pos == start + 1 and self.text[start] == '-'):
                    return None  # No digits found

            if self.peek() == '.':
                self.pos += 1
                if self.pos >= self.length or not self.text[self.pos].isdigit():
                    return None
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.pos += 1
            
            if self.peek() in 'eE':
                self.pos += 1
                if self.peek() in '+-':
                    self.pos += 1
                if self.pos >= self.length or not self.text[self.pos].isdigit():
                    return None
                while self.pos < self.length and self.text[self.pos].isdigit():
                    self.pos += 1

            num_str = self.text[start:self.pos]
            try:
                if '.' in num_str or 'e' in num_str.lower():
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                return None

        def parse(self):
            self.skip_whitespace()
            if self.pos >= self.length: return None
            try:
                result = self.parse_value()
                self.skip_whitespace()
                if self.pos < self.length: return None  # Trailing garbage after document
                return result
            except:
                return None

    parser = JSONParser(text)
    return parser.parse()
