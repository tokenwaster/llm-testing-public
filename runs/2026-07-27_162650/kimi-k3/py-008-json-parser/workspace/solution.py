"""A hand-written JSON parser.

parse(text) returns the equivalent Python object, or None if the text is
not valid JSON.  No JSON libraries are used.
"""

# Unique sentinel used internally to signal a parse failure.  This is kept
# distinct from None so that the valid JSON document "null" (which maps to
# Python's None) is not confused with an error.
_FAIL = object()

_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")

_SIMPLE_ESCAPES = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}


def _is_digit(ch):
    # Only ASCII digits are valid in JSON numbers (str.isdigit() would also
    # accept various non-ASCII digits, which JSON does not allow).
    return "0" <= ch <= "9"


class _Parser:
    __slots__ = ("text", "pos", "n")

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.n = len(text)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def skip_ws(self):
        # JSON whitespace is exactly: space, tab, LF, CR.
        text = self.text
        n = self.n
        pos = self.pos
        while pos < n and text[pos] in " \t\n\r":
            pos += 1
        self.pos = pos

    def _read_hex4(self, start):
        """Read exactly four hex digits starting at index `start`.

        Returns the integer value, or None if not possible.
        """
        if start + 4 > self.n:
            return None
        s = self.text[start:start + 4]
        for ch in s:
            if ch not in _HEX_DIGITS:
                return None
        return int(s, 16)

    # ------------------------------------------------------------------
    # Grammar productions
    # ------------------------------------------------------------------
    def parse_value(self):
        self.skip_ws()
        if self.pos >= self.n:
            return _FAIL
        c = self.text[self.pos]
        if c == "{":
            return self.parse_object()
        if c == "[":
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == "t":
            return self.parse_literal("true", True)
        if c == "f":
            return self.parse_literal("false", False)
        if c == "n":
            return self.parse_literal("null", None)
        if c == "-" or _is_digit(c):
            return self.parse_number()
        return _FAIL

    def parse_literal(self, word, value):
        if self.text.startswith(word, self.pos):
            self.pos += len(word)
            return value
        return _FAIL

    def parse_string(self):
        # Precondition: self.text[self.pos] == '"'
        text = self.text
        n = self.n
        self.pos += 1
        parts = []
        while self.pos < n:
            c = text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(parts)
            if c == "\\":
                if self.pos + 1 >= n:
                    return _FAIL
                esc = text[self.pos + 1]
                if esc in _SIMPLE_ESCAPES:
                    parts.append(_SIMPLE_ESCAPES[esc])
                    self.pos += 2
                elif esc == "u":
                    code = self._read_hex4(self.pos + 2)
                    if code is None:
                        return _FAIL
                    self.pos += 6
                    # Combine a UTF-16 surrogate pair into one character.
                    if 0xD800 <= code <= 0xDBFF:
                        if text[self.pos:self.pos + 2] == "\\u":
                            low = self._read_hex4(self.pos + 2)
                            if low is not None and 0xDC00 <= low <= 0xDFFF:
                                self.pos += 6
                                code = (0x10000
                                        + ((code - 0xD800) << 10)
                                        + (low - 0xDC00))
                    parts.append(chr(code))
                else:
                    # Invalid escape sequence.
                    return _FAIL
            elif ord(c) < 0x20:
                # Control characters must be escaped in JSON strings.
                return _FAIL
            else:
                parts.append(c)
                self.pos += 1
        # Unterminated string.
        return _FAIL

    def parse_number(self):
        # JSON number grammar:
        #   -?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?
        text = self.text
        n = self.n
        start = self.pos

        if self.pos < n and text[self.pos] == "-":
            self.pos += 1

        if self.pos >= n:
            return _FAIL

        # Integer part: either a single 0, or a non-zero digit followed
        # by any digits (this rejects leading zeros such as 007).
        if text[self.pos] == "0":
            self.pos += 1
            if self.pos < n and _is_digit(text[self.pos]):
                return _FAIL
        elif _is_digit(text[self.pos]):
            while self.pos < n and _is_digit(text[self.pos]):
                self.pos += 1
        else:
            return _FAIL

        is_float = False

        # Fractional part.
        if self.pos < n and text[self.pos] == ".":
            is_float = True
            self.pos += 1
            if self.pos >= n or not _is_digit(text[self.pos]):
                return _FAIL
            while self.pos < n and _is_digit(text[self.pos]):
                self.pos += 1

        # Exponent part.
        if self.pos < n and text[self.pos] in "eE":
            is_float = True
            self.pos += 1
            if self.pos < n and text[self.pos] in "+-":
                self.pos += 1
            if self.pos >= n or not _is_digit(text[self.pos]):
                return _FAIL
            while self.pos < n and _is_digit(text[self.pos]):
                self.pos += 1

        token = text[start:self.pos]
        try:
            return float(token) if is_float else int(token)
        except ValueError:
            return _FAIL

    def parse_array(self):
        # Precondition: self.text[self.pos] == '['
        self.pos += 1
        result = []
        self.skip_ws()
        if self.pos < self.n and self.text[self.pos] == "]":
            self.pos += 1
            return result
        while True:
            value = self.parse_value()
            if value is _FAIL:
                return _FAIL
            result.append(value)
            self.skip_ws()
            if self.pos >= self.n:
                return _FAIL
            c = self.text[self.pos]
            if c == ",":
                self.pos += 1
                continue
            if c == "]":
                self.pos += 1
                return result
            return _FAIL

    def parse_object(self):
        # Precondition: self.text[self.pos] == '{'
        self.pos += 1
        result = {}
        self.skip_ws()
        if self.pos < self.n and self.text[self.pos] == "}":
            self.pos += 1
            return result
        while True:
            self.skip_ws()
            if self.pos >= self.n or self.text[self.pos] != '"':
                return _FAIL
            key = self.parse_string()
            if key is _FAIL:
                return _FAIL
            self.skip_ws()
            if self.pos >= self.n or self.text[self.pos] != ":":
                return _FAIL
            self.pos += 1
            value = self.parse_value()
            if value is _FAIL:
                return _FAIL
            result[key] = value
            self.skip_ws()
            if self.pos >= self.n:
                return _FAIL
            c = self.text[self.pos]
            if c == ",":
                self.pos += 1
                continue
            if c == "}":
                self.pos += 1
                return result
            return _FAIL


def parse(text: str):
    """Parse a JSON document.

    Returns the equivalent Python object, or None if `text` is not valid
    JSON.
    """
    if not isinstance(text, str):
        return None
    parser = _Parser(text)
    try:
        value = parser.parse_value()
    except RecursionError:
        # Pathologically deep nesting: treat as unparseable rather than
        # crashing.
        return None
    if value is _FAIL:
        return None
    parser.skip_ws()
    if parser.pos != parser.n:
        # Trailing garbage after an otherwise valid document.
        return None
    return value
