"""solution.py — a hand-written JSON parser (no json module)."""


class _ParseError(Exception):
    """Raised internally whenever the input is not valid JSON."""


_HEX_DIGITS = "0123456789abcdefABCDEF"


class _Parser:
    """Recursive-descent parser over the input text."""

    __slots__ = ("text", "pos", "n")

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.n = len(text)

    # -- helpers ---------------------------------------------------------

    def error(self, msg="invalid JSON"):
        raise _ParseError(msg)

    def skip_ws(self):
        text, n = self.text, self.n
        pos = self.pos
        while pos < n and text[pos] in " \t\n\r":
            pos += 1
        self.pos = pos

    def expect_literal(self, word):
        if self.text.startswith(word, self.pos):
            self.pos += len(word)
        else:
            self.error("invalid literal")

    # -- values ----------------------------------------------------------

    def parse_value(self):
        self.skip_ws()
        if self.pos >= self.n:
            self.error("unexpected end of input")
        c = self.text[self.pos]
        if c == "{":
            return self.parse_object()
        if c == "[":
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == "t":
            self.expect_literal("true")
            return True
        if c == "f":
            self.expect_literal("false")
            return False
        if c == "n":
            self.expect_literal("null")
            return None
        if c == "-" or "0" <= c <= "9":
            return self.parse_number()
        self.error("unexpected character %r" % c)

    # -- strings ---------------------------------------------------------

    def parse_string(self):
        text, n = self.text, self.n
        self.pos += 1  # consume opening quote
        parts = []
        while True:
            if self.pos >= n:
                self.error("unterminated string")
            c = text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(parts)
            if c == "\\":
                self.pos += 1
                if self.pos >= n:
                    self.error("unterminated escape")
                e = text[self.pos]
                self.pos += 1
                if e == '"':
                    parts.append('"')
                elif e == "\\":
                    parts.append("\\")
                elif e == "/":
                    parts.append("/")
                elif e == "b":
                    parts.append("\b")
                elif e == "f":
                    parts.append("\f")
                elif e == "n":
                    parts.append("\n")
                elif e == "r":
                    parts.append("\r")
                elif e == "t":
                    parts.append("\t")
                elif e == "u":
                    parts.append(self.parse_unicode_escape())
                else:
                    self.error("invalid escape \\%s" % e)
            elif ord(c) < 0x20:
                self.error("unescaped control character in string")
            else:
                parts.append(c)
                self.pos += 1

    def read_hex4(self):
        if self.pos + 4 > self.n:
            self.error("truncated \\u escape")
        s = self.text[self.pos:self.pos + 4]
        for ch in s:
            if ch not in _HEX_DIGITS:
                self.error("non-hex digit in \\u escape")
        self.pos += 4
        return int(s, 16)

    def parse_unicode_escape(self):
        # self.pos sits just past the "u" of a "\uXXXX" escape.
        code = self.read_hex4()
        if 0xD800 <= code <= 0xDBFF:
            # High surrogate: combine only if directly followed by a valid
            # low-surrogate escape; otherwise leave it as-is (like json does).
            save = self.pos
            if self.text[self.pos:self.pos + 2] == "\\u":
                self.pos += 2
                try:
                    low = self.read_hex4()
                except _ParseError:
                    low = None
                if low is not None and 0xDC00 <= low <= 0xDFFF:
                    combined = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
                    return chr(combined)
                self.pos = save
        return chr(code)

    # -- numbers ---------------------------------------------------------

    def parse_number(self):
        text, n = self.text, self.n
        start = self.pos
        pos = self.pos

        if pos < n and text[pos] == "-":
            pos += 1

        # Integer part: "0" or [1-9][0-9]* (leading zeros are illegal).
        if pos >= n:
            self.error("bad number")
        c = text[pos]
        if c == "0":
            pos += 1
            if pos < n and "0" <= text[pos] <= "9":
                self.error("leading zero in number")
        elif "1" <= c <= "9":
            pos += 1
            while pos < n and "0" <= text[pos] <= "9":
                pos += 1
        else:
            self.error("bad number")

        is_float = False

        # Fractional part: "." followed by at least one digit.
        if pos < n and text[pos] == ".":
            is_float = True
            pos += 1
            if pos >= n or not ("0" <= text[pos] <= "9"):
                self.error("digits required after decimal point")
            while pos < n and "0" <= text[pos] <= "9":
                pos += 1

        # Exponent part: [eE][+-]?digits
        if pos < n and text[pos] in "eE":
            is_float = True
            pos += 1
            if pos < n and text[pos] in "+-":
                pos += 1
            if pos >= n or not ("0" <= text[pos] <= "9"):
                self.error("digits required in exponent")
            while pos < n and "0" <= text[pos] <= "9":
                pos += 1

        self.pos = pos
        s = text[start:pos]
        return float(s) if is_float else int(s)

    # -- arrays / objects -------------------------------------------------

    def parse_array(self):
        self.pos += 1  # consume '['
        items = []
        self.skip_ws()
        if self.pos < self.n and self.text[self.pos] == "]":
            self.pos += 1
            return items
        while True:
            items.append(self.parse_value())
            self.skip_ws()
            if self.pos >= self.n:
                self.error("unterminated array")
            c = self.text[self.pos]
            if c == ",":
                self.pos += 1
            elif c == "]":
                self.pos += 1
                return items
            else:
                self.error("expected ',' or ']' in array")

    def parse_object(self):
        self.pos += 1  # consume '{'
        obj = {}
        self.skip_ws()
        if self.pos < self.n and self.text[self.pos] == "}":
            self.pos += 1
            return obj
        while True:
            self.skip_ws()
            if self.pos >= self.n or self.text[self.pos] != '"':
                self.error("expected string key in object")
            key = self.parse_string()
            self.skip_ws()
            if self.pos >= self.n or self.text[self.pos] != ":":
                self.error("expected ':' in object")
            self.pos += 1
            obj[key] = self.parse_value()
            self.skip_ws()
            if self.pos >= self.n:
                self.error("unterminated object")
            c = self.text[self.pos]
            if c == ",":
                self.pos += 1
            elif c == "}":
                self.pos += 1
                return obj
            else:
                self.error("expected ',' or '}' in object")


def parse(text):
    """Parse *text* as JSON.

    Returns the equivalent Python object, or None if the input is not
    valid JSON (note: the valid document "null" also yields None).
    """
    if not isinstance(text, str):
        return None
    try:
        parser = _Parser(text)
        value = parser.parse_value()
        parser.skip_ws()
        if parser.pos != parser.n:
            return None  # trailing garbage after the document
        return value
    except (_ParseError, RecursionError, ValueError, OverflowError):
        return None
