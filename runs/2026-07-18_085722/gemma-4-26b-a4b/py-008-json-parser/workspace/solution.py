def parse(text: str):
    class Parser:
        def __init__(self, text):
            self.text = text
            self.pos = 0

        def skip_whitespace(self):
            while self.pos < len(self.text) and self.text[self.pos].isspace():
                self.pos += 1

        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= len(self.text):
                raise ValueError("Empty input")
            char = self.text[self.pos]
            if char == '{':
                return self.parse_object()
            elif char == '[':
                return self.parse_array()
            elif char == '"':
                return self.parse_string()
            elif char in '-0123456789':
                return self.parse_number()
            elif self.text.startswith('true', self.pos):
                next_p = self.pos + 4
                if next_p == len(self.text) or not self.text[next_p].isalnum():
                    self.pos = next_p
                    return True
            elif self.text.startswith('false', self.pos):
                next_p = self.pos + 5
                if next_p == len(self.text) or not self.text[next::next_p].isalnum(): # wait, typo in logic
                    pass # let's rewrite this part cleanly below
            # Re-writing the literal check to be safer and cleaner:
            elif self.text.startswith('true', self.pos):
                self.pos += 4
                if self.pos < len(self.text) and self.text[self.pos].isalnum():
                    raise ValueError("Invalid literal")
                return True
            elif self.text.startswith('false', self.pos):
                self.pos += 5
                if self.pos < len(self.text) and self.text[self.pos].isalnum():
                    raise ValueError("Invalid literal")
                return False
            elif self.text.startswith('null', self.pos):
                self.pos += 4
                if self.pos < len(self.text) and self.text[self.pos].isalnum():
                    raise ValueError("Invalid literal")
                return None
            raise ValueError("Invalid value start")

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
                    raise ValueError("Key must be string")
                key = self.parse_string()
                self.skip_whitespace()
                if self.pos >= len(self.text) or self.text[self.pos] != ':':
                    raise ValueError("Expected :")
                self.pos += 1  # skip :
                val = self.parse_value()
                obj[key] = val
                self.skip_whitespace()
                if self.pos < len(self.text) and self.text[self.pos] == '}':
                    self.pos += 1
                    return obj
                elif self.pos < len(self.text) and self.text[self.pos] == ',':
                    self.pos += 1
                    self.skip_whitespace()
                    if self.pos < len(self.text) and self.text[self.pos] == '}':
                        raise ValueError("Trailing comma")
                else:
                    raise ValueError("Expected , or }")

        def parse_array(self):
            self.pos += 1  # skip [
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
                    if self.pos < len(self.text) and self.text[self.pos] == ']':
                        raise ValueError("Trailing comma")
                else:
                    raise ValueError("Expected , or ]")

        def parse_string(self):
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                raise ValueError("Expected \"")
            self.pos += 1  # skip opening "
            res = []
            while self.pos < len(self.text):
                char = self.text[self.pos]
                if char == '"':
                    self.pos += 1
                    return "".join(res)
                elif char == '\\':
                    self.pos += 1
                    if self.pos >= len(self.text):
                        raise ValueError("Unterminated escape")
                    esc = self.text[self.pos]
                    if esc == 'u':
                        h = ""
                        for _ in range(4):
                            if self.pos >= len(self.text):
                                raise ValueError("Unterminated unicode")
                            c = self.text[self.pos]
                            if c in "0123456789abcdefABCDEF":
                                h += c
                                self.pos += 1
                            else:
                                raise ValueError("Invalid hex digit")
                        res.append(chr(int(h, 16)))
                    else:
                        mapping = {'"': '"', '\\': '\\', '/': '/', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t'}
                        if esc in mapping:
                            res.append(mapping[esc])
                            self.pos += 1
                        else:
                            raise ValueError("Invalid escape")
                elif ord(char) < 0x20:
                    raise ValueError("Control character not escaped")
                else:
                    res.append(char)
                    self.pos += 1
            raise ValueError("Unterminated string")

        def parse_number(self):
            start = self.pos
            if self.text[self.pos] == '-':
                self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos] == '0':
                self.pos += 1
                if self.pos < len(self.text) and self.text[self.pos].isdigit():
                    raise ValueError("Leading zero")
            elif self.pos < len(self.text) and self.text[self.pos].isdigit():
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1
            else:
                raise ValueError("Invalid number")

            if self.pos < len(self.text) and self.text[self.pos] == '.':
                self.pos += 1
                if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                    raise ValueError("Invalid fraction")
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1

            if self.pos < len(self.text) and self.text[self.pos] in 'eE':
                self.pos += 1
                if self.pos < len(self.text) and self.text[self.pos] in '+-':
                    self.pos += 1
                if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                    raise ValueError("Invalid exponent")
                while self.pos < len(self.text) and self.text[self.pos].isdigit():
                    self.pos += 1

            num_str = self.text[start:self.pos]
            if '.' in num_str or 'e' in num_str.lower():
                return float(num_str)
            else:
                return int(num_str)

    try:
        parser = Parser(text)
        result = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos < len(parser.text):
            return None
        return result
    except Exception:
        return None
