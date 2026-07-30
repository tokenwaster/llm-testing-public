# solution.py
from __future__ import annotations

class _ParseError(Exception):
    """Internal exception used to abort parsing when encountering invalid JSON."""
    pass


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.len = len(text)
        self.i = 0

    # ---------- utility ----------
    def _skip_ws(self):
        while self.i < self.len and self.text[self.i] in " \t\r\n":
            self.i += 1

    def _peek(self) -> str | None:
        return self.text[self.i] if self.i < self.len else None

    def _consume(self, ch: str):
        if self._peek() != ch:
            raise _ParseError(f"Expected '{ch}'")
        self.i += 1

    # ---------- entry ----------
    def parse(self):
        self._skip_ws()
        value = self._value()
        self._skip_ws()
        if self.i != self.len:
            raise _ParseError("Trailing data after JSON value")
        return value

    # ---------- value ----------
    def _value(self):
        c = self._peek()
        if c == '"':
            return self._string()
        elif c == '{':
            return self._object()
        elif c == '[':
            return self._array()
        elif c == '-' or (c is not None and c.isdigit()):
            return self._number()
        elif c is None:
            raise _ParseError("Unexpected end of input")
        else:
            # literals true, false, null
            return self._literal()

    # ---------- literals ----------
    def _literal(self):
        remaining = self.text[self.i : self.i + 5]  # longest literal is 'false'
        if remaining.startswith('true'):
            self.i += 4
            return True
        if remaining.startswith('false'):
            self.i += 5
            return False
        if remaining[:4] == 'null':
            self.i += 4
            return None
        raise _ParseError("Invalid literal")

    # ---------- object ----------
    def _object(self):
        obj = {}
        self._consume('{')
        self._skip_ws()
        if self._peek() == '}':
            self._consume('}')
            return obj
        while True:
            self._skip_ws()
            if self._peek() != '"':
                raise _ParseError("Object keys must be strings")
            key = self._string()
            self._skip_ws()
            self._consume(':')
            self._skip_ws()
            val = self._value()
            obj[key] = val
            self._skip_ws()
            nxt = self._peek()
            if nxt == ',':
                self._consume(',')
                self._skip_ws()
                continue
            elif nxt == '}':
                self._consume('}')
                break
            else:
                raise _ParseError("Expected ',' or '}' in object")
        return obj

    # ---------- array ----------
    def _array(self):
        arr = []
        self._consume('[')
        self._skip_ws()
        if self._peek() == ']':
            self._consume(']')
            return arr
        while True:
            self._skip_ws()
            arr.append(self._value())
            self._skip_ws()
            nxt = self._peek()
            if nxt == ',':
                self._consume(',')
                self._skip_ws()
                continue
            elif nxt == ']':
                self._consume(']')
                break
            else:
                raise _ParseError("Expected ',' or ']' in array")
        return arr

    # ---------- string ----------
    def _string(self):
        self._consume('"')
        sb = []
        while True:
            if self.i >= self.len:
                raise _ParseError("Unterminated string")
            ch = self.text[self.i]
            self.i += 1
            if ch == '"':
                break
            if ch == '\\':
                if self.i >= self.len:
                    raise _ParseError("Unterminated escape sequence")
                esc = self.text[self.i]
                self.i += 1
                if esc == '"':
                    sb.append('"')
                elif esc == '\\':
                    sb.append('\\')
                elif esc == '/':
                    sb.append('/')
                elif esc == 'b':
                    sb.append('\b')
                elif esc == 'f':
                    sb.append('\f')
                elif esc == 'n':
                    sb.append('\n')
                elif esc == 'r':
                    sb.append('\r')
                elif esc == 't':
                    sb.append('\t')
                elif esc == 'u':
                    if self.i + 4 > self.len:
                        raise _ParseError("Incomplete Unicode escape")
                    hex_digits = self.text[self.i:self.i + 4]
                    if any(c not in "0123456789abcdefABCDEF" for c in hex_digits):
                        raise _ParseError("Invalid Unicode escape")
                    code_point = int(hex_digits, 16)
                    sb.append(chr(code_point))
                    self.i += 4
                else:
                    raise _ParseError(f"Invalid escape character '\\{esc}'")
            else:
                # Disallow control characters (U+0000 through U+001F)
                if ord(ch) < 0x20:
                    raise _ParseError("Control character in string")
                sb.append(ch)
        return ''.join(sb)

    # ---------- number ----------
    def _number(self):
        start = self.i
        # optional minus
        if self._peek() == '-':
            self.i += 1
        # integer part
        if self._peek() == '0':
            self.i += 1
            # leading zero must not be followed by another digit
            if self.i < self.len and self.text[self.i].isdigit():
                raise _ParseError("Leading zeros are not allowed")
        else:
            if not (self._peek() and self._peek().isdigit()):
                raise _ParseError("Invalid number")
            while self.i < self.len and self.text[self.i].isdigit():
                self.i += 1
        # fractional part
        if self._peek() == '.':
            self.i += 1
            if self.i >= self.len or not self.text[self.i].isdigit():
                raise _ParseError("Digits required after decimal point")
            while self.i < self.len and self.text[self.i].isdigit():
                self.i += 1
        # exponent part
        if self._peek() in ('e', 'E'):
            self.i += 1
            if self._peek() in ('+', '-'):
                self.i += 1
            if self.i >= self.len or not self.text[self.i].isdigit():
                raise _ParseError("Exponent requires at least one digit")
            while self.i < self.len and self.text[self.i].isdigit():
                self.i += 1
        num_str = self.text[start:self.i]
        # Determine type
        if any(c in num_str for c in '.eE'):
            try:
                return float(num_str)
            except ValueError:
                raise _ParseError("Invalid float representation")
        else:
            try:
                return int(num_str)
            except ValueError:
                raise _ParseError("Invalid int representation")


def parse(text: str):
    """
    Parses *text* as JSON and returns the corresponding Python object.
    Returns ``None`` if *text* is not a valid JSON document.
    """
    try:
        parser = _Parser(text)
        return parser.parse()
    except _ParseError:
        return None
