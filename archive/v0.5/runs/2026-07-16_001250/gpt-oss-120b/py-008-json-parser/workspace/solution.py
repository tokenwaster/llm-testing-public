# solution.py

def parse(text: str):
    """
    Parse a JSON document from *text* and return the corresponding Python
    object, or ``None`` if the input is not valid JSON.
    """
    parser = _JSONParser(text)
    return parser.parse()


class _JSONParser:
    def __init__(self, s: str):
        self.s = s
        self.i = 0
        self.n = len(s)

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #
    def parse(self):
        self._skip_ws()
        value = self._parse_value()
        if value is None:
            return None
        self._skip_ws()
        if self.i != self.n:
            return None
        return value

    # ------------------------------------------------------------------ #
    # Core parsing helpers
    # ------------------------------------------------------------------ #
    def _parse_value(self):
        if self.i >= self.n:
            return None
        ch = self.s[self.i]
        if ch == '"':
            return self._parse_string()
        if ch == '{':
            return self._parse_object()
        if ch == '[':
            return self._parse_array()
        if ch == 't':
            return self._parse_literal('true', True)
        if ch == 'f':
            return self._parse_literal('false', False)
        if ch == 'n':
            return self._parse_literal('null', None)
        if ch == '-' or ch.isdigit():
            return self._parse_number()
        return None

    # ------------------------------------------------------------------ #
    # Literals: true / false / null
    # ------------------------------------------------------------------ #
    def _parse_literal(self, literal: str, value):
        end = self.i + len(literal)
        if self.s.startswith(literal, self.i) and (end == self.n or not self.s[end].isalnum()):
            self.i = end
            return value
        return None

    # ------------------------------------------------------------------ #
    # Strings
    # ------------------------------------------------------------------ #
    def _parse_string(self):
        assert self.s[self.i] == '"'
        self.i += 1  # skip opening quote
        result = []
        while self.i < self.n:
            ch = self.s[self.i]
            if ch == '"':
                self.i += 1
                return ''.join(result)
            if ch == '\\':
                esc = self._parse_escape()
                if esc is None:
                    return None
                result.append(esc)
                continue
            # control characters are not allowed
            if ord(ch) < 0x20:
                return None
            result.append(ch)
            self.i += 1
        return None  # Unterminated string

    def _parse_escape(self):
        self.i += 1  # skip backslash
        if self.i >= self.n:
            return None
        ch = self.s[self.i]
        self.i += 1
        if ch == '"':
            return '"'
        if ch == '\\':
            return '\\'
        if ch == '/':
            return '/'
        if ch == 'b':
            return '\b'
        if ch == 'f':
            return '\f'
        if ch == 'n':
            return '\n'
        if ch == 'r':
            return '\r'
        if ch == 't':
            return '\t'
        if ch == 'u':
            return self._parse_unicode_escape()
        return None

    def _parse_unicode_escape(self):
        if self.i + 4 > self.n:
            return None
        hex_digits = self.s[self.i:self.i + 4]
        if not all(c in "0123456789abcdefABCDEF" for c in hex_digits):
            return None
        code_point = int(hex_digits, 16)
        self.i += 4
        # Handle surrogate pairs for completeness
        if 0xD800 <= code_point <= 0xDBFF:
            # high surrogate, expect a low surrogate next
            if self.s[self.i:self.i + 2] != '\\u':
                return chr(code_point)  # treat as isolated high surrogate
            self.i += 2
            low_hex = self.s[self.i:self.i + 4]
            if not all(c in "0123456789abcdefABCDEF" for c in low_hex):
                return None
            low = int(low_hex, 16)
            self.i += 4
            if not (0xDC00 <= low <= 0xDFFF):
                return None
            # combine to actual code point
            code_point = 0x10000 + ((code_point - 0xD800) << 10) + (low - 0xDC00)
        return chr(code_point)

    # ------------------------------------------------------------------ #
    # Numbers
    # ------------------------------------------------------------------ #
    def _parse_number(self):
        start = self.i
        # optional sign
        if self.s[self.i] == '-':
            self.i += 1
            if self.i >= self.n:
                return None

        # integer part
        if self.s[self.i] == '0':
            self.i += 1
            # leading zeros are forbidden
            if self.i < self.n and self.s[self.i].isdigit():
                return None
        elif self.s[self.i] in '123456789':
            while self.i < self.n and self.s[self.i].isdigit():
                self.i += 1
        else:
            return None

        is_float = False

        # fraction
        if self.i < self.n and self.s[self.i] == '.':
            is_float = True
            self.i += 1
            if self.i >= self.n or not self.s[self.i].isdigit():
                return None
            while self.i < self.n and self.s[self.i].isdigit():
                self.i += 1

        # exponent
        if self.i < self.n and self.s[self.i] in 'eE':
            is_float = True
            self.i += 1
            if self.i < self.n and self.s[self.i] in '+-':
                self.i += 1
            if self.i >= self.n or not self.s[self.i].isdigit():
                return None
            while self.i < self.n and self.s[self.i].isdigit():
                self.i += 1

        num_str = self.s[start:self.i]
        try:
            return float(num_str) if is_float else int(num_str)
        except ValueError:
            return None

    # ------------------------------------------------------------------ #
    # Arrays
    # ------------------------------------------------------------------ #
    def _parse_array(self):
        assert self.s[self.i] == '['
        self.i += 1
        self._skip_ws()
        if self.i < self.n and self.s[self.i] == ']':
            self.i += 1
            return []
        items = []
        while True:
            self._skip_ws()
            val = self._parse_value()
            if val is None:
                return None
            items.append(val)
            self._skip_ws()
            if self.i >= self.n:
                return None
            ch = self.s[self.i]
            if ch == ',':
                self.i += 1
                continue
            if ch == ']':
                self.i += 1
                return items
            return None  # unexpected character

    # ------------------------------------------------------------------ #
    # Objects
    # ------------------------------------------------------------------ #
    def _parse_object(self):
        assert self.s[self.i] == '{'
        self.i += 1
        self._skip_ws()
        if self.i < self.n and self.s[self.i] == '}':
            self.i += 1
            return {}
        obj = {}
        while True:
            self._skip_ws()
            if self.i >= self.n or self.s[self.i] != '"':
                return None
            key = self._parse_string()
            if key is None:
                return None
            self._skip_ws()
            if self.i >= self.n or self.s[self.i] != ':':
                return None
            self.i += 1
            self._skip_ws()
            value = self._parse_value()
            if value is None:
                return None
            obj[key] = value
            self._skip_ws()
            if self.i >= self.n:
                return None
            ch = self.s[self.i]
            if ch == ',':
                self.i += 1
                continue
            if ch == '}':
                self.i += 1
                return obj
            return None  # unexpected character

    # ------------------------------------------------------------------ #
    # Whitespace handling
    # ------------------------------------------------------------------ #
    def _skip_ws(self):
        while self.i < self.n and self.s[self.i] in ' \t\n\r':
            self.i += 1
