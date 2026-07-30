"""A small, dependency-free JSON parser.

`parse(text)` returns the equivalent Python object, or `None` when the input
is not a valid JSON document.
"""

WHITESPACE = " \t\n\r"

ESCAPES = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}

DIGITS = "0123456789"
HEXDIGITS = "0123456789abcdefABCDEF"


class _JSONError(Exception):
    """Raised internally whenever the document turns out to be malformed."""


class _Parser:
    def __init__(self, text):
        self.text = text
        self.i = 0
        self.n = len(text)

    # -- low level helpers -------------------------------------------------

    def peek(self):
        if self.i < self.n:
            return self.text[self.i]
        return ""

    def advance(self):
        ch = self.peek()
        if not ch:
            raise _JSONError("unexpected end of input")
        self.i += 1
        return ch

    def expect(self, ch):
        if self.peek() != ch:
            raise _JSONError("expected %r" % ch)
        self.i += 1

    def skip_ws(self):
        while self.i < self.n and self.text[self.i] in WHITESPACE:
            self.i += 1

    # -- grammar -----------------------------------------------------------

    def parse_document(self):
        self.skip_ws()
        value = self.parse_value()
        self.skip_ws()
        if self.i != self.n:
            raise _JSONError("trailing garbage")
        return value

    def parse_value(self):
        ch = self.peek()
        if ch == "{":
            return self.parse_object()
        if ch == "[":
            return self.parse_array()
        if ch == '"':
            return self.parse_string()
        if ch == "t":
            self.parse_literal("true")
            return True
        if ch == "f":
            self.parse_literal("false")
            return False
        if ch == "n":
            self.parse_literal("null")
            return None
        if ch == "-" or ch in DIGITS:
            return self.parse_number()
        raise _JSONError("unexpected character %r" % ch)

    def parse_literal(self, word):
        if self.text[self.i:self.i + len(word)] != word:
            raise _JSONError("bad literal")
        self.i += len(word)

    def parse_object(self):
        self.expect("{")
        result = {}
        self.skip_ws()
        if self.peek() == "}":
            self.i += 1
            return result
        while True:
            self.skip_ws()
            if self.peek() != '"':
                raise _JSONError("object key must be a string")
            key = self.parse_string()
            self.skip_ws()
            self.expect(":")
            self.skip_ws()
            result[key] = self.parse_value()
            self.skip_ws()
            ch = self.peek()
            if ch == ",":
                self.i += 1
                continue
            if ch == "}":
                self.i += 1
                return result
            raise _JSONError("expected ',' or '}'")

    def parse_array(self):
        self.expect("[")
        result = []
        self.skip_ws()
        if self.peek() == "]":
            self.i += 1
            return result
        while True:
            self.skip_ws()
            result.append(self.parse_value())
            self.skip_ws()
            ch = self.peek()
            if ch == ",":
                self.i += 1
                continue
            if ch == "]":
                self.i += 1
                return result
            raise _JSONError("expected ',' or ']'")

    def parse_string(self):
        self.expect('"')
        out = []
        while True:
            ch = self.advance()
            if ch == '"':
                return "".join(out)
            if ch == "\\":
                esc = self.advance()
                if esc in ESCAPES:
                    out.append(ESCAPES[esc])
                elif esc == "u":
                    out.append(self.parse_unicode_escape())
                else:
                    raise _JSONError("bad escape %r" % esc)
            elif ch < "\x20":
                raise _JSONError("unescaped control character")
            else:
                out.append(ch)

    def parse_unicode_escape(self):
        code = self.read_hex4()
        # Combine surrogate pairs when both halves are present.
        if 0xD800 <= code <= 0xDBFF and self.text[self.i:self.i + 2] == "\\u":
            save = self.i
            self.i += 2
            low = self.read_hex4()
            if 0xDC00 <= low <= 0xDFFF:
                code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
            else:
                self.i = save
        return chr(code)

    def read_hex4(self):
        digits = self.text[self.i:self.i + 4]
        if len(digits) != 4 or any(d not in HEXDIGITS for d in digits):
            raise _JSONError("bad unicode escape")
        self.i += 4
        return int(digits, 16)

    def parse_number(self):
        start = self.i
        if self.peek() == "-":
            self.i += 1
        # int part: either a lone 0 or a non-zero-leading run of digits.
        if self.peek() == "0":
            self.i += 1
        elif self.peek() in DIGITS[1:]:
            while self.peek() in DIGITS:
                self.i += 1
        else:
            raise _JSONError("bad number")

        is_float = False
        if self.peek() == ".":
            is_float = True
            self.i += 1
            if self.peek() not in DIGITS:
                raise _JSONError("bad fraction")
            while self.peek() in DIGITS:
                self.i += 1

        if self.peek() in "eE":
            is_float = True
            self.i += 1
            if self.peek() in "+-":
                self.i += 1
            if self.peek() not in DIGITS:
                raise _JSONError("bad exponent")
            while self.peek() in DIGITS:
                self.i += 1

        raw = self.text[start:self.i]
        if is_float:
            value = float(raw)
            # An exponent can still land on a whole number (1e2 -> 100.0);
            # JSON says that is a float, so keep it one.
            return value
        return int(raw)


def parse(text):
    """Parse `text` as JSON, returning the Python equivalent or None."""
    if not isinstance(text, str):
        return None
    try:
        return _Parser(text).parse_document()
    except (_JSONError, ValueError, RecursionError):
        return None
