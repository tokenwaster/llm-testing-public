# solution.py
from __future__ import annotations

class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.n = len(text)
        self.i = 0

    # ------------------------------------------------------------------ utils
    def _skip_ws(self):
        while self.i < self.n and self.text[self.i] in " \t\r\n":
            self.i += 1

    def _peek(self) -> str | None:
        self._skip_ws()
        return self.text[self.i] if self.i < self.n else None

    def _consume(self, ch: str):
        self._skip_ws()
        if self.i < self.n and self.text[self.i] == ch:
            self.i += 1
        else:
            raise _ParseError(f"Expected '{ch}'")

    # ----------------------------------------------------------------- literals
    def _parse_literal(self, literal: str, value):
        end = self.i + len(literal)
        if self.text[self.i:end] == literal:
            self.i = end
            return value
        raise _ParseError(f"Expected literal {literal}")

    # ------------------------------------------------------------------- value
    def parse_value(self):
        self._skip_ws()
        if self.i >= self.n:
            raise _ParseError("Unexpected end of input")
        ch = self.text[self.i]

        if ch == '"':
            return self._parse_string()
        elif ch == '{':
            return self._parse_object()
        elif ch == '[':
            return self._parse_array()
        elif ch == 't':
            return self._parse_literal('true', True)
        elif ch == 'f':
            return self._parse_literal('false', False)
        elif ch == 'n':
            return self._parse_literal('null', None)
        elif ch == '-' or ch.isdigit():
            return self._parse_number()
        else:
            raise _ParseError(f"Unexpected character {ch}")

    # ------------------------------------------------------------------- array
    def _parse_array(self):
        self._consume('[')
        arr = []
        self._skip_ws()
        if self._peek() == ']':
            self._consume(']')
            return arr
        while True:
            arr.append(self.parse_value())
            self._skip_ws()
            nxt = self._peek()
            if nxt == ',':
                self._consume(',')
                continue
            elif nxt == ']':
                self._consume(']')
                break
            else:
                raise _ParseError("Expected ',' or ']' in array")
        return arr

    # ------------------------------------------------------------------- object
    def _parse_object(self):
        self._consume('{')
        obj = {}
        self._skip_ws()
        if self._peek() == '}':
            self._consume('}')
            return obj
        while True:
            self._skip_ws()
            if self._peek() != '"':
                raise _ParseError("Object keys must be strings")
            key = self._parse_string()
            self._skip_ws()
            self._consume(':')
            val = self.parse_value()
            obj[key] = val
            self._skip_ws()
            nxt = self._peek()
            if nxt == ',':
                self._consume(',')
                continue
            elif nxt == '}':
                self._consume('}')
                break
            else:
                raise _ParseError("Expected ',' or '}' in object")
        return obj

    # ------------------------------------------------------------------- string
    def _parse_string(self):
        self._consume('"')
        sb = []
        while True:
            if self.i >= self.n:
                raise _ParseError("Unterminated string")
            ch = self.text[self.i]
            if ch == '"':
                self.i += 1
                break
            if ch == '\\':
                self.i += 1
                if self.i >= self.n:
                    raise _ParseError("Unterminated escape")
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
                    # expect exactly 4 hex digits
                    if self.i + 4 > self.n:
                        raise _ParseError("Incomplete \\u escape")
                    hex_digits = self.text[self.i:self.i + 4]
                    if not all(c in "0123456789abcdefABCDEF" for c in hex_digits):
                        raise _ParseError("Invalid hex in \\u escape")
                    code_point = int(hex_digits, 16)
                    sb.append(chr(code_point))
                    self.i += 4
                else:
                    raise _ParseError(f"Invalid escape character \\{esc}")
            else:
                # JSON strings cannot contain control characters (U+0000-001F)
                if ord(ch) < 0x20:
                    raise _ParseError("Invalid control character in string")
                sb.append(ch)
                self.i += 1
        return ''.join(sb)

    # ------------------------------------------------------------------- number
    def _parse_number(self):
        start = self.i
        # optional minus
        if self.text[self.i] == '-':
            self.i += 1
            if self.i >= self.n:
                raise _ParseError("Invalid number")
        # integer part
        if self.text[self.i] == '0':
            self.i += 1
        elif self.text[self.i] in '123456789':
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        else:
            raise _ParseError("Invalid number")
        # fraction
        if self.i < self.n and self.text[self.i] == '.':
            self.i += 1
            if self.i >= self.n or not self.text[self.i].isdigit():
                raise _ParseError("Invalid fraction")
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        # exponent
        if self.i < self.n and self.text[self.i] in 'eE':
            self.i += 1
            if self.i < self.n and self.text[self.i] in '+-':
                self.i += 1
            if self.i >= self.n or not self.text[self.i].isdigit():
                raise _ParseError("Invalid exponent")
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1
        num_str = self.text[start:self.i]
        # Determine int vs float
        if any(c in num_str for c in '.eE'):
            try:
                return float(num_str)
            except ValueError:
                raise _ParseError("Invalid float")
        else:
            # No leading zeros allowed except single zero (already enforced)
            try:
                return int(num_str)
            except ValueError:
                raise _ParseError("Invalid int")


def parse(text: str):
    """
    Parse a JSON document and return the corresponding Python object.
    Returns None if the input is not valid JSON.
    """
    try:
        parser = _Parser(text)
        result = parser.parse_value()
        parser._skip_ws()
        if parser.i != parser.n:
            # trailing non‑whitespace characters
            raise _ParseError("Trailing garbage")
        return result
    except _ParseError:
        return None
