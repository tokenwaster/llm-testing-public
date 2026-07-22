def parse(text: str):
    class Parser:
        def __init__(self, s):
            self.s = s
            self.pos = 0

        def skip_ws(self):
            while self.pos < len(self.s) and self.s[self.pos] in ' \t\n\r':
                self.pos += 1

        def parse_value(self):
            self.skip_ws()
            if self.pos >= len(self.s):
                raise ValueError("Unexpected end of input")
            c = self.s[self.pos]
            if c == '{':
                return self.parse_object()
            if c == '[':
                return self.parse_array()
            if c == '"':
                return self.parse_string()
            if c == 't':
                return self.parse_literal('true', True)
            if c == 'f':
                return self.parse_literal('false', False)
            if c == 'n':
                return self.parse_literal('null', None)
            if c == '-' or c.isdigit():
                return self.parse_number()
            raise ValueError(f"Unexpected character: {c!r}")

        def parse_literal(self, word, value):
            if self.s[self.pos:self.pos + len(word)] == word:
                self.pos += len(word)
                return value
            raise ValueError(f"Invalid literal at pos {self.pos}")

        def parse_object(self):
            self.pos += 1  # skip '{'
            result = {}
            self.skip_ws()
            if self.pos < len(self.s) and self.s[self.pos] == '}':
                self.pos += 1
                return result
            while True:
                self.skip_ws()
                if self.pos >= len(self.s) or self.s[self.pos] != '"':
                    raise ValueError("Expected string key")
                key = self.parse_string()
                self.skip_ws()
                if self.pos >= len(self.s) or self.s[self.pos] != ':':
                    raise ValueError("Expected ':'")
                self.pos += 1
                value = self.parse_value()
                result[key] = value
                self.skip_ws()
                if self.pos >= len(self.s):
                    raise ValueError("Unterminated object")
                ch = self.s[self.pos]
                if ch == '}':
                    self.pos += 1
                    return result
                if ch == ',':
                    self.pos += 1
                    self.skip_ws()
                    if self.pos < len(self.s) and self.s[self.pos] == '}':
                        raise ValueError("Trailing comma in object")
                else:
                    raise ValueError("Expected ',' or '}'")

        def parse_array(self):
            self.pos += 1  # skip '['
            result = []
            self.skip_ws()
            if self.pos < len(self.s) and self.s[self.pos] == ']':
                self.pos += 1
                return result
            while True:
                value = self.parse_value()
                result.append(value)
                self.skip_ws()
                if self.pos >= len(self.s):
                    raise ValueError("Unterminated array")
                ch = self.s[self.pos]
                if ch == ']':
                    self.pos += 1
                    return result
                if ch == ',':
                    self.pos += 1
                    self.skip_ws()
                    if self.pos < len(self.s) and self.s[self.pos] == ']':
                        raise ValueError("Trailing comma in array")
                else:
                    raise ValueError("Expected ',' or ']'")

        def parse_string(self):
            self.pos += 1  # skip opening '"'
            chars = []
            while self.pos < len(self.s):
                c = self.s[self.pos]
                if c == '"':
                    self.pos += 1
                    return ''.join(chars)
                if c == '\\':
                    self.pos += 1
                    if self.pos >= len(self.s):
                        raise ValueError("Unexpected end in escape")
                    e = self.s[self.pos]
                    if e == '"':
                        chars.append('"')
                    elif e == '\\':
                        chars.append('\\')
                    elif e == '/':
                        chars.append('/')
                    elif e == 'b':
                        chars.append('\b')
                    elif e == 'f':
                        chars.append('\f')
                    elif e == 'n':
                        chars.append('\n')
                    elif e == 'r':
                        chars.append('\r')
                    elif e == 't':
                        chars.append('\t')
                    elif e == 'u':
                        self.pos += 1
                        cp = self._parse_hex4()
                        if 0xD800 <= cp <= 0xDBFF:
                            if (self.pos + 1 < len(self.s) and
                                    self.s[self.pos] == '\\' and self.s[self.pos + 1] == 'u'):
                                self.pos += 2
                                low = self._parse_hex4()
                                if not (0xDC00 <= low <= 0xDFFF):
                                    raise ValueError("Invalid low surrogate")
                                cp = 0x10000 + ((cp - 0xD800) << 10) + (low - 0xDC00)
                            else:
                                raise ValueError("Missing low surrogate")
                        elif 0xDC00 <= cp <= 0xDFFF:
                            raise ValueError("Unexpected low surrogate")
                        chars.append(chr(cp))
                        continue
                    else:
                        raise ValueError(f"Invalid escape: \\{e}")
                    self.pos += 1
                elif ord(c) < 0x20:
                    raise ValueError("Unescaped control character in string")
                else:
                    chars.append(c)
                    self.pos += 1
            raise ValueError("Unterminated string")

        def _parse_hex4(self):
            if self.pos + 4 > len(self.s):
                raise ValueError("Incomplete unicode escape")
            h = self.s[self.pos:self.pos + 4]
            if not all(c in '0123456789abcdefABCDEF' for c in h):
                raise ValueError("Invalid hex in unicode escape")
            self.pos += 4
            return int(h, 16)

        def parse_number(self):
            start = self.pos
            is_float = False

            if self.pos < len(self.s) and self.s[self.pos] == '-':
                self.pos += 1

            if self.pos >= len(self.s):
                raise ValueError("Expected digit")

            if self.s[self.pos] == '0':
                self.pos += 1
                if self.pos < len(self.s) and self.s[self.pos].isdigit():
                    raise ValueError("Leading zeros not allowed")
            elif self.s[self.pos].isdigit():
                while self.pos < len(self.s) and self.s[self.pos].isdigit():
                    self.pos += 1
            else:
                raise ValueError("Expected digit")

            if self.pos < len(self.s) and self.s[self.pos] == '.':
                is_float = True
                self.pos += 1
                if self.pos >= len(self.s) or not self.s[self.pos].isdigit():
                    raise ValueError("Expected digit after '.'")
                while self.pos < len(self.s) and self.s[self.pos].isdigit():
                    self.pos += 1

            if self.pos < len(self.s) and self.s[self.pos] in 'eE':
                is_float = True
                self.pos += 1
                if self.pos < len(self.s) and self.s[self.pos] in '+-':
                    self.pos += 1
                if self.pos >= len(self.s) or not self.s[self.pos].isdigit():
                    raise ValueError("Expected digit in exponent")
                while self.pos < len(self.s) and self.s[self.pos].isdigit():
                    self.pos += 1

            num_str = self.s[start:self.pos]
            return float(num_str) if is_float else int(num_str)

    try:
        p = Parser(text)
        value = p.parse_value()
        p.skip_ws()
        if p.pos != len(text):
            return None
        return value
    except Exception:
        return None
