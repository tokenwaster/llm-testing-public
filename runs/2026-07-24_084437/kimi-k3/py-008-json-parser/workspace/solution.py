"""solution.py -- a hand-written JSON parser.

Parses a JSON document into the equivalent Python object without using the
`json` module (or any other JSON library).  Invalid input yields ``None``.
"""

import sys

# Deeply nested documents need more than the default recursion head-room.
try:
    if sys.getrecursionlimit() < 10000:
        sys.setrecursionlimit(10000)
except Exception:
    pass


class _ParseError(Exception):
    """Internal signal raised when the input is not valid JSON."""


_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
_WHITESPACE = " \t\n\r"


class _Parser(object):
    __slots__ = ("text", "pos", "n")

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.n = len(text)

    # -- helpers ---------------------------------------------------------
    def skip_whitespace(self):
        text = self.text
        pos = self.pos
        n = self.n
        while pos < n and text[pos] in _WHITESPACE:
            pos += 1
        self.pos = pos

    def error(self, message):
        raise _ParseError(message)

    # -- values ----------------------------------------------------------
    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= self.n:
            self.error("unexpected end of input")
        ch = self.text[self.pos]
        if ch == "{":
            return self.parse_object()
        if ch == "[":
            return self.parse_array()
        if ch == '"':
            return self.parse_string()
        if ch == "t":
            self.expect_literal("true")
            return True
        if ch == "f":
            self.expect_literal("false")
            return False
        if ch == "n":
            self.expect_literal("null")
            return None
        if ch == "-" or "0" <= ch <= "9":
            return self.parse_number()
        self.error("unexpected character %r" % ch)

    def expect_literal(self, literal):
        if self.text.startswith(literal, self.pos):
            self.pos += len(literal)
        else:
            self.error("invalid literal")

    # -- strings ---------------------------------------------------------
    def parse_string(self):
        # Precondition: self.text[self.pos] == '"'
        text = self.text
        n = self.n
        pos = self.pos + 1
        parts = []
        start = pos
        while True:
            if pos >= n:
                self.error("unterminated string")
            ch = text[pos]
            if ch == '"':
                parts.append(text[start:pos])
                pos += 1
                break
            if ch == "\\":
                parts.append(text[start:pos])
                pos += 1
                if pos >= n:
                    self.error("unterminated escape")
                esc = text[pos]
                pos += 1
                if esc == '"':
                    parts.append('"')
                elif esc == "\\":
                    parts.append("\\")
                elif esc == "/":
                    parts.append("/")
                elif esc == "b":
                    parts.append("\b")
                elif esc == "f":
                    parts.append("\f")
                elif esc == "n":
                    parts.append("\n")
                elif esc == "r":
                    parts.append("\r")
                elif esc == "t":
                    parts.append("\t")
                elif esc == "u":
                    if pos + 4 > n:
                        self.error("truncated unicode escape")
                    digits = text[pos:pos + 4]
                    if any(c not in _HEX_DIGITS for c in digits):
                        self.error("invalid unicode escape")
                    code = int(digits, 16)
                    pos += 4
                    # Combine a UTF-16 surrogate pair into one character.
                    if 0xD800 <= code <= 0xDBFF and text[pos:pos + 2] == "\\u":
                        digits2 = text[pos + 2:pos + 6]
                        if len(digits2) == 4 and all(
                            c in _HEX_DIGITS for c in digits2
                        ):
                            code2 = int(digits2, 16)
                            if 0xDC00 <= code2 <= 0xDFFF:
                                code = (
                                    0x10000
                                    + ((code - 0xD800) << 10)
                                    + (code2 - 0xDC00)
                                )
                                pos += 6
                    parts.append(chr(code))
                else:
                    self.error("invalid escape %r" % esc)
                start = pos
            elif ord(ch) < 0x20:
                self.error("unescaped control character in string")
            else:
                pos += 1
        self.pos = pos
        return "".join(parts)

    # -- numbers ---------------------------------------------------------
    def parse_number(self):
        text = self.text
        n = self.n
        pos = self.pos
        start = pos

        if pos < n and text[pos] == "-":
            pos += 1

        # Integer part: either a single 0 or a non-zero digit followed by
        # more digits (leading zeros are not valid JSON).
        if pos >= n:
            self.error("invalid number")
        ch = text[pos]
        if ch == "0":
            pos += 1
            if pos < n and "0" <= text[pos] <= "9":
                self.error("leading zero in number")
        elif "1" <= ch <= "9":
            pos += 1
            while pos < n and "0" <= text[pos] <= "9":
                pos += 1
        else:
            self.error("invalid number")

        is_float = False

        # Fractional part.
        if pos < n and text[pos] == ".":
            is_float = True
            pos += 1
            if pos >= n or not ("0" <= text[pos] <= "9"):
                self.error("digits required after decimal point")
            while pos < n and "0" <= text[pos] <= "9":
                pos += 1

        # Exponent part.
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
        token = text[start:pos]
        try:
            if is_float:
                return float(token)
            return int(token)
        except ValueError:
            self.error("invalid number")

    # -- arrays ----------------------------------------------------------
    def parse_array(self):
        self.pos += 1  # consume '['
        items = []
        self.skip_whitespace()
        if self.pos < self.n and self.text[self.pos] == "]":
            self.pos += 1
            return items
        while True:
            items.append(self.parse_value())
            self.skip_whitespace()
            if self.pos >= self.n:
                self.error("unterminated array")
            ch = self.text[self.pos]
            if ch == ",":
                self.pos += 1
            elif ch == "]":
                self.pos += 1
                return items
            else:
                self.error("expected ',' or ']' in array")

    # -- objects ---------------------------------------------------------
    def parse_object(self):
        self.pos += 1  # consume '{'
        obj = {}
        self.skip_whitespace()
        if self.pos < self.n and self.text[self.pos] == "}":
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            if self.pos >= self.n or self.text[self.pos] != '"':
                self.error("expected string key in object")
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= self.n or self.text[self.pos] != ":":
                self.error("expected ':' in object")
            self.pos += 1
            obj[key] = self.parse_value()
            self.skip_whitespace()
            if self.pos >= self.n:
                self.error("unterminated object")
            ch = self.text[self.pos]
            if ch == ",":
                self.pos += 1
            elif ch == "}":
                self.pos += 1
                return obj
            else:
                self.error("expected ',' or '}' in object")


def parse(text):
    """Parse *text* as JSON.

    Returns the equivalent Python object (``dict`` / ``list`` / ``str`` /
    ``int`` / ``float`` / ``True`` / ``False`` / ``None``), or ``None``
    when *text* is not a valid JSON document.
    """
    if not isinstance(text, str):
        return None
    parser = _Parser(text)
    try:
        value = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != parser.n:
            return None  # trailing garbage after the document
        return value
    except _ParseError:
        return None
    except (ValueError, OverflowError, RecursionError):
        return None
