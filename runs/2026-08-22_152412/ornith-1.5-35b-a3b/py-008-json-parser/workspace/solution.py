"""A from-scratch JSON parser (does not use the json module)."""


class _Sentinel:
    def __repr__(self):
        return "<JSON_PARSE_FAILED>"


_FAIL = _Sentinel()


class _Parser:
    WS = " \t\n\r"

    def __init__(self, text):
        self.text = text
        self.pos = 0

    # ---- entry point ----
    def parse(self):
        self.skip_ws()
        if self.pos >= len(self.text):
            return _FAIL
        value = self.parse_value()
        if value is _FAIL:
            return _FAIL
        self.skip_ws()
        if self.pos != len(self.text):  # reject trailing garbage
            return _FAIL
        return value

    # ---- whitespace ----
    def skip_ws(self):
        text, n = self.text, len(self.text)
        while self.pos < n and text[self.pos] in self.WS:
            self.pos += 1

    # ---- value dispatch ----
    def parse_value(self):
        if self.pos >= len(self.text):
            return _FAIL
        c = self.text[self.pos]
        if c == "{":
            return self.parse_object()
        if c == "[":
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == "-" or "0" <= c <= "9":
            return self.parse_number()
        if c in "tfn":
            return self.parse_literal()
        return _FAIL

    # ---- object ----
    def parse_object(self):
        text, n = self.text, len(self.text)
        self.pos += 1  # consume '{'
        result = {}
        self.skip_ws()
        if self.pos < n and text[self.pos] == "}":
            self.pos += 1
            return result
        while True:
            self.skip_ws()
            if self.pos >= n or text[self.pos] != '"':
                return _FAIL
            key = self.parse_string()
            if key is _FAIL:
                return _FAIL
            self.skip_ws()
            if self.pos >= n or text[self.pos] != ":":
                return _FAIL
            self.pos += 1  # consume ':'
            value = self.parse_value()
            if value is _FAIL:
                return _FAIL
            result[key] = value
            self.skip_ws()
            if self.pos >= n:
                return _FAIL
            c = text[self.pos]
            if c == ",":
                self.pos += 1
            elif c == "}":
                self.pos += 1
                return result
            else:
                return _FAIL

    # ---- array ----
    def parse_array(self):
        text, n = self.text, len(self.text)
        self.pos += 1  # consume '['
        result = []
        self.skip_ws()
        if self.pos < n and text[self.pos] == "]":
            self.pos += 1
            return result
        while True:
            value = self.parse_value()
            if value is _FAIL:
                return _FAIL
            result.append(value)
            self.skip_ws()
            if self.pos >= n:
                return _FAIL
            c = text[self.pos]
            if c == ",":
                self.pos += 1
            elif c == "]":
                self.pos += 1
                return result
            else:
                return _FAIL

    # ---- string ----
    def parse_string(self):
        text, n = self.text, len(self.text)
        self.pos += 1  # consume opening quote
        chars = []
        simple = {
            '"': '"',
            '\\': '\\',
            '/': '/',
            'b': '\b',
            'f': '\f',
            'n': '\n',
            'r': '\r',
            't': '\t',
        }
        while True:
            if self.pos >= n:
                return _FAIL
            c = text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(chars)
            if c == "\\":
                self.pos += 1
                if self.pos >= n:
                    return _FAIL
                esc = text[self.pos]
                if esc in simple:
                    chars.append(simple[esc])
                    self.pos += 1
                elif esc == "u":
                    code = self._read_hex4()
                    if code is _FAIL:
                        return _FAIL
                    if 0xD800 <= code <= 0xDBFF:
                        # high surrogate must be followed by a low surrogate
                        if text[self.pos:self.pos + 2] == "\\u":
                            self.pos += 1  # move past backslash onto 'u'
                            code2 = self._read_hex4()
                            if code2 is _FAIL or not (0xDC00 <= code2 <= 0xDFFF):
                                return _FAIL
                            combined = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
                            chars.append(chr(combined))
                        else:
                            return _FAIL
                    else:
                        chars.append(chr(code))
                else:
                    return _FAIL
            elif ord(c) < 0x20:
                return _FAIL
            else:
                chars.append(c)
                self.pos += 1

    def _read_hex4(self):
        text = self.text
        u_pos = self.pos  # position of 'u'
        if u_pos + 5 > len(text):
            return _FAIL
        hexstr = text[u_pos + 1:u_pos + 5]
        if len(hexstr) != 4:
            return _FAIL
        for ch in hexstr:
            if ch not in "0123456789abcdefABCDEF":
                return _FAIL
        self.pos = u_pos + 5  # advance past 'u' and the four hex digits
        return int(hexstr, 16)

    # ---- number ----
    def parse_number(self):
        text, n = self.text, len(self.text)
        start = self.pos
        if text[self.pos] == "-":
            self.pos += 1
        if self.pos >= n:
            return _FAIL
        c = text[self.pos]
        if c == "0":
            self.pos += 1
            if self.pos < n and text[self.pos].isdigit():
                return _FAIL  # leading zeros not allowed
        elif "1" <= c <= "9":
            self.pos += 1
            while self.pos < n and text[self.pos].isdigit():
                self.pos += 1
        else:
            return _FAIL
        is_float = False
        if self.pos < n and text[self.pos] == ".":
            is_float = True
            self.pos += 1
            if self.pos >= n or not text[self.pos].isdigit():
                return _FAIL
            while self.pos < n and text[self.pos].isdigit():
                self.pos += 1
        if self.pos < n and text[self.pos] in "eE":
            is_float = True
            self.pos += 1
            if self.pos < n and text[self.pos] in "+-":
                self.pos += 1
            if self.pos >= n or not text[self.pos].isdigit():
                return _FAIL
            while self.pos < n and text[self.pos].isdigit():
                self.pos += 1
        numstr = text[start:self.pos]
        try:
            return float(numstr) if is_float else int(numstr)
        except ValueError:
            return _FAIL

    # ---- literals ----
    def parse_literal(self):
        text = self.text
        for literal, value in (("true", True), ("false", False), ("null", None)):
            end = self.pos + len(literal)
            if text[self.pos:end] == literal and not self._followed_by_ident(end):
                self.pos = end
                return value
        return _FAIL

    def _followed_by_ident(self, pos):
        if pos >= len(self.text):
            return False
        c = self.text[pos]
        return c.isalnum() or c == "_"


def parse(text: str):
    result = _Parser(text).parse()
    if result is _FAIL:
        return None
    return result
