class JSONParser:
    def __init__(self, text):
        self.text = text
        self.pos = 0

    def error(self):
        raise ValueError("Invalid JSON")

    def skip_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= len(self.text):
            self.error()
        char = self.text[self.pos]
        if char == '{':
            return self.parse_object()
        elif char == '[':
            return self.parse_array()
        elif char == '"':
            return self.parse_string()
        elif char in ('t', 'f', 'n'):
            return self.parse_literal()
        elif char == '-' or char.isdigit():
            return self.parse_number()
        else:
            self.error()

    def parse_object(self):
        self.pos += 1  # skip {
        obj = {}
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == '}':
            self.pos += 1
            return obj

        while True:
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                self.error()
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] != ':':
                self.error()
            self.pos += 1  # skip :
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            elif self.pos < len(self.text) and self.text[self.pos] == ',':
                self.pos += 1
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    self.error()  # Trailing comma error
            else:
                self.error()

    def parse_array(self):
        self.pos += 1  # skip [
        arr = []
        self.skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == ']':
            self.pos += 1
            return arr

        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            elif self.pos < len(self.text) and self.text[self.pos] == ',':
                self.pos += 1
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == ']':
                    self.error()  # Trailing comma error
            else:
                self.error()

    def parse_string(self):
        self.pos += 1  # skip opening "
        res = []
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            char = self.text[self.pos]
            if char == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    self.error()
                esc = self.text[self.pos]
                if esc == '"': res.append('"')
                elif esc == '\\': res.append('\\')
                elif esc == '/': res.append('/')
                elif esc == 'b': res.append('\b')
                elif esc == 'f': res.append('\f')
                elif esc == 'n': res.append('\n')
                elif esc == 'r': res.append('\rot') # wait, \r is carriage return
                elif esc == '\r': res.append('\r') # correction:
                # Let's rewrite the escape logic properly
                pass 
            # Re-writing escapes correctly below...
        return ""

    def parse_string_fixed(self):
        self.pos += 1  # skip opening "
        res = []
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            char = self.text[self.pos]
            if char == '\\':
                self.pos += 1
                if self.pos >= len(self.text):
                    self.error()
                esc = self.text[self.pos]
                if esc == '"': res.append('"')
                elif esc == '\\': res.append('\\')
                elif esc == '/': res.append('/')
                elif esc == 'b': res.append('\b')
                elif esc == 'f': res.append('\f')
                elif esc == 'n': res.append('\n')
                elif esc == 'r': res.append('\r')
                elif esc == 't': res.append('\t')
                elif esc == 'u':
                    hex_str = ""
                    for _ in range(4):
                        if self.pos >= len(self.text) or not self._is_hex(self.text[self.pos]):
                            self.error()
                        hex_str += self.text[self.pos]
                        self.pos += 1
                    res.append(chr(int(hex_str, 16)))
                else:
                    self.error()
            else:
                res.append(char)
            self.pos += 1
        if self.pos >= len(self.text) or self.text[self.pos] != '"':
            self.error()
        self.pos += 1  # skip closing "
        return "".join(res)

    def _is_hex(self, c):
        return '0' <= c <= '9' or 'a' <= c <= 'f' or 'A' <= c <= 'F'

    def parse_literal(self):
        if self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        elif self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        elif self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        else:
            self.error()

    def parse_number(self):
        start = self.pos
        if self.text[self.pos] == '-':
            self.pos += 1
        
        if self.pos >= len(self.text) or (not self.text[self.pos].isdigit() and self.text[self.pos] != '.'):
            self.error()

        if self.text[self.pos] == '0':
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.error()
        elif self.pos < len(self.text) and self.text[self.pos].isdigit():
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            self.error()

        if self.pos < len(self.text) and self.text[self.pos] == '.':
            self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                self.error()
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1

        if self.pos < len(self.text) and self.text[self.pos] in ('e', 'E'):
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] in ('+', '-'):
                self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                self.error()
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1

        num_str = self.text[start:self.pos]
        try:
            if '.' in num_str or 'e' in num_str.lower():
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            self.error()

def parse(text: str):
    # Re-injecting the fixed string method into a clean class structure for final output
    class Parser:
        def __init__(self, text):
            self.text = text
            self.pos = 0
        def error(self): raise ValueError()
        def skip_whitespace(self):
            while self.pos < len(self.text) and self.text[self.pos].isspace():
                self.pos += 1
        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= len(self.text): self.error()
            c = self.text[self.pos]
            if c == '{': return self.parse_object()
            if c == '[': return self.parse_array()
            if c == '"': return self.parse_string()
            if c in ('t', 'f', 'n'): return self.parse_literal()
            if c == '-' or c.isdigit(): return self.parse_number()
            self.error()
        def parse_object(self):
            self.pos += 1
            obj = {}
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            while True:
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != '"': self.error()
                key = self.parse_string()
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != ':': self.error()
                self.pos += 1
                val = self.parse_value()
                obj[key] = val
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    self.pos += 1
                    return obj
                elif self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.pos < len(self.text) and self.text[self.pos] == '}': self.error()
                else: self.error()
        def parse_array(self):
            self.pos += 1
            arr = []
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            while True:
                val = self.parse_value()
                arr.append(val)
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == ']':
                    self.pos += 1
                    return arr
                elif self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.pos < len(self.text) and self.text[self.pos] == ']': self.error()
                else: self.error()
        def parse_string(self):
            self.pos += 1
            res = []
            while self.pos < len(self.text) and self.pos < len(self.text) and self.text[self.pos] != '"':
                if self.text[self.pos] == '\\':
                    self.pos += 1
                    if self.pos >= len(self.text): self.error()
                    esc = self.text[self.pos]
                    if esc == '"': res.append('"')
                    elif esc == '\\': res.append('\\')
                    elif esc == '/': res.append('/')
                    elif esc == 'b': res.append('\b')
                    elif esc == 'f': res.append('\f')
                    elif esc == 'n': res.append('\n')
                    elif esc == 'r': res.append('\r')
                    elif esc == 't': res.append('\t')
                    elif esc == 'u':
                        h = ""
                        for _ in range(4):
                            if self.pos >= len(self.text) or not ('0' <= self.text[self.pos] <= '9' or 'a' <= self.text[self.pos].lower() <= 'f'):
                                self.error()
                            h += self.text[self.pos]
                            self.pos += 1
                        res.append(chr(int(h, 16)))
                    else: self.error()
                else:
                    res.append(self.text[self.pos])
                self.pos += 1
            if self.pos >= len(self.text) or self.text[self.pos] != '"': self.error()
            self.pos += 1
            return "".join(res)
        def parse_literal(self):
            if self.text.startswith('true', self.pos): self.pos += 4; return True
            if self.text.startswith('false', self.pos): self.pos += 5; return False
            if self.text.startswith('null', self.pos): self.pos += 4; return None
            self.error()
        def parse_number(self):
            start = self.pos
            if self.text[self.pos] == '-': self.pos += 1
            if self.pos >= len(self.int_check_bounds()) or (not self.text[self.pos].isdigit() and self.text[self.pos] != '.'):
                # Wait, I need to fix the logic for checking bounds in parse_number
                pass
            # Let's use a simpler approach for number parsing within the class structure
            return self._parse_num_logic(start)
        def int_check_bounds(self): return self.text # dummy
        def _parse_num_logic(self, start):
            p = self.pos
            if p >= len(self.text) or (not self.text[p].isdigit() and self.text[p] != '.'): self.error()
            if self.text[p] == '0':
                p += 1
                if p < len(self.text) and self.text[p].isdigit(): self.error()
            elif p < len(self.text) and self.text[p].isdigit():
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            else: self.error()
            if p < len(self.text) and self.text[p] == '.':
                p += 1
                if p >= len(self.text) or not self.text[p].isdigit(): self.error()
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            if p < len(self.text) and self.text[p] in ('e', 'E'):
                p += 1
                if p < len(self.text) and self.text[p] in ('+', '-'): p += 1
                if p >= len(self.text) or not self.text[p].isdigit(): self.error()
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            self.pos = p
            s = self.text[start:p]
            try: return float(s) if ('.' in s or 'e' in s.lower()) else int(s)
            except: self.error()

    # Final attempt at a clean, single-class implementation
    class JSONParserFinal:
        def __init__(self, text):
            self.text = text
            self.pos = 0
        def error(self): raise ValueError()
        def skip_whitespace(self):
            while self.pos < len(self.text) and self.text[self.pos].isspace(): self.pos += 1
        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= len(self.text): self.error()
            c = self.text[self.pos]
            if c == '{': return self.parse_object()
            if c == '[': return self.parse_array()
            if c == '"': return self.parse_string()
            if c in ('t', 'f', 'n'): return self.parse_literal()
            if c == '-' or c.isdigit(): return self.parse_number()
            self.error()
        def parse_object(self):
            self.pos += 1
            obj = {}
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            while True:
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != '"': self.error()
                key = self.parse_string()
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != ':': self.error()
                self.pos += 1
                val = self.parse_value()
                obj[key] = val
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    self.pos += 1
                    return obj
                elif self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.pos < len(self.text) and self.text[self.pos] == '}': self.error()
                else: self.error()
        def parse_array(self):
            self.pos += 1
            arr = []
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            while True:
                val = self.parse_value()
                arr.append(val)
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == ']':
                    self.pos += 1
                    return arr
                elif self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.pos < len(self.text) and self.text[self.pos] == ']': self.error()
                else: self.error()
        def parse_string(self):
            self.pos += 1
            res = []
            while self.pos < len(self.text) and self.text[self.pos] != '"':
                if self.text[self.pos] == '\\':
                    self.pos += 1
                    if self.pos >= len(self.text): self.error()
                    esc = self.text[self.pos]
                    if esc == '"': res.append('"')
                    elif esc == '\\': res.append('\\')
                    elif esc == '/': res.append('/')
                    elif esc == 'b': res.append('\b')
                    elif esc == 'f': res.append('\f')
                    elif esc == 'n': res.append('\n')
                    elif esc == 'r': res.append('\r')
                    elif esc == 't': res.append('\t')
                    elif esc == 'u':
                        h = ""
                        for _ in range(4):
                            if self.pos >= len(self.text) or not ('0' <= self.text[self.pos].lower() <= 'z' and (self.text[self.pos].isdigit() or 'a' <= self.text[self.pos].lower() <= 'f')):
                                self.error()
                            h += self.text[self.pos]
                            self.pos += 1
                        res.append(chr(int(h, 16)))
                    else: self.error()
                else:
                    res.append(self.text[self.pos])
                self.pos += 1
            if self.pos >= len(self.text) or self.text[self.pos] != '"': self.error()
            self.pos += 1
            return "".join(res)
        def parse_literal(self):
            if self.text.startswith('true', self.pos): self.pos += 4; return True
            if self.text.startswith('false', self.pos): self.pos += 5; return False
            if self.text.startswith('null', self.pos): self.pos += 4; return None
            self.error()
        def parse_number(self):
            start = self.pos
            if self.text[self.pos] == '-': self.pos += 1
            p = self.pos
            if p >= len(self.text) or (not self.text[p].isdigit() and self.text[p] != '.'): self.error()
            if self.text[p] == '0':
                p += 1
                if p < len(self.text) and self.text[p].isdigit(): self.error()
            elif p < len(self.text) and self.text[p].isdigit():
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            else: self.error()
            if p < len(self.text) and self.text[p] == '.':
                p += 1
                if p >= len(self.text) or not self.text[p].isdigit(): self.error()
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            if p < len(self.text) and self.text[p] in ('e', 'E'):
                p += 1
                if p < len(self.text) and self.text[p] in ('+', '-'): p += 1
                if p >= len(self.text) or not self.text[p].isdigit(): self.error()
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            self.pos = p
            s = self.text[start:p]
            try: return float(s) if ('.' in s or 'e' in s.lower()) else int(s)
            except: self.error()

    try:
        parser = JSONParserFinal(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(parser.text): return None
        return result
    except:
        return None

# Redefining the function to be clean and standalone as required by the prompt
def parse(text: str):
    class JSONParserFinal:
        def __init__(self, text):
            self.text = text
            self.pos = 0
        def error(self): raise ValueError()
        def skip_whitespace(self):
            while self.pos < len(self.text) and self.text[self.pos].isspace(): self.pos += 1
        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= len(self.text): self.error()
            c = self.text[self.pos]
            if c == '{': return self.parse_object()
            if c == '[': return self.parse_array()
            if c == '"': return self.parse_string()
            if c in ('t', 'f', 'n'): return self.parse_literal()
            if c == '-' or c.isdigit(): return self.parse_number()
            self.error()
        def parse_object(self):
            self.pos += 1
            obj = {}
            self.skip_whitespace()
            if self.pos < len(self.text) and self.text[self.pos] == '}':
                self.pos += 1
                return obj
            while True:
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != '"': self.error()
                key = self.parse_string()
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != ':': self.error()
                self.pos += 1
                val = self.parse_value()
                obj[key] = val
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    self.pos += 1
                    return obj
                elif self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.pos < len(self.text) and self.text[self.pos] == '}': self.error()
                else: self.error()
        def parse_array(self):
            self.pos += 1
            arr = []
            self.skip_whitespace()
            if self.pos < len(self.text) and self.pos < len(self.text) and self.text[self.pos] == ']':
                self.pos += 1
                return arr
            while True:
                val = self.parse_value()
                arr.append(val)
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == ']':
                    self.pos += 1
                    return arr
                elif self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.pos < len(self.text) and self.text[self.pos] == ']': self.error()
                else: self.error()
        def parse_string(self):
            self.pos += 1
            res = []
            while self.pos < len(self.text) and self.text[self.pos] != '"':
                if self.text[self.pos] == '\\':
                    self.pos += 1
                    if self.pos >= len(self.text): self.error()
                    esc = self.text[self.pos]
                    if esc == '"': res.append('"')
                    elif esc == '\\': res.append('\\')
                    elif esc == '/': res.append('/')
                    elif esc == 'b': res.append('\b')
                    elif esc == 'f': res.append('\f')
                    elif esc == 'n': res.append('\n')
                    elif esc == 'r': res.append('\r')
                    elif esc == 't': res.append('\t')
                    elif esc == 'u':
                        h = ""
                        for _ in range(4):
                            if self.pos >= len(self.text) or not ('0' <= self.text[self.pos].lower() <= 'z' and (self.text[self.pos].isdigit() or 'a' <= self.text[self.pos].lower() <= 'f')):
                                self.error()
                            h += self.text[self.pos]
                            self.pos += 1
                        res.append(chr(int(h, 16)))
                    else: self.error()
                else:
                    res.append(self.text[self.pos])
                self.pos += 1
            if self.pos >= len(self.text) or self.text[self.pos] != '"': self.error()
            self.pos += 1
            return "".join(res)
        def parse_literal(self):
            if self.text.startswith('true', self.pos): self.pos += 4; return True
            if self.text.startswith('false', self.pos): self.pos += 5; return False
            if self.text.startswith('null', self.pos): self.pos += 4; return None
            self.error()
        def parse_number(self):
            start = self.pos
            if self.text[self.pos] == '-': self.pos += 1
            p = self.pos
            if p >= len(self.text) or (not self.text[p].isdigit() and self.text[p] != '.'): self.error()
            if self.text[p] == '0':
                p += 1
                if p < len(self.text) and self.text[p].isdigit(): self.error()
            elif p < len(self.text) and self.text[p].isdigit():
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            else: self.error()
            if p < len(self.text) and self.text[p] == '.':
                p += 1
                if p >= len(self.text) or not self.text[p].isdigit(): self.error()
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            if p < len(self.text) and self.text[p] in ('e', 'E'):
                p += 1
                if p < len(self.text) and self.text[p] in ('+', '-'): p += 1
                if p >= len(self.text) or not self.text[p].isdigit(): self.error()
                while p < len(self.text) and self.text[p].isdigit(): p += 1
            self.pos = p
            s = self.text[start:p]
            try: return float(s) if ('.' in s or 'e' in s.lower()) else int(s)
            except: self.error()

    try:
        parser = JSONParserFinal(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(parser.text): return None
        return result
    except:
        return None
