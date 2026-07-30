#!/usr/bin/env python3
"""
A minimal JSON parser that satisfies the requirements of the exercise.
"""

import re

# Regular expressions for number parsing (to detect integer vs float)
_NUMBER_RE = re.compile(r'^[+-]?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?$')
_INT_RE = re.compile(r'^[+-]?(?:0|[1-9]\d*)$')


class JSONParseError(Exception):
    """Raised when the input is not valid JSON."""
    pass


def parse(text: str):
    """
    Parse a JSON string and return the corresponding Python object.
    Return None if the input is not valid JSON.
    """
    try:
        parser = _Parser(text)
        value = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != len(parser.s):
            # Trailing garbage
            raise JSONParseError("Trailing characters")
        return value
    except JSONParseError:
        return None


class _Parser:
    def __init__(self, s: str):
        self.s = s
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < len(self.s) and self.s[self.pos] in ' \t\n\r':
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= len(self.s):
            raise JSONParseError("Unexpected end of input")
        ch = self.s[self.pos]
        if ch == '{':
            return self.parse_object()
        elif ch == '[':
            return self.parse_array()
        elif ch == '"':
            return self.parse_string()
        elif ch in '-0123456789':
            return self.parse_number()
        elif self.s.startswith('true', self.pos):
            self.pos += 4
            return True
        elif self.s.startswith('false', self.pos):
            self.pos += 5
            return False
        elif self.s.startswith('null', self.pos):
            self.pos += 4
            return None
        else:
            raise JSONParseError(f"Unexpected character {ch!r}")

    def parse_object(self):
        obj = {}
        assert self.s[self.pos] == '{'
        self.pos += 1
        self.skip_whitespace()
        if self.pos < len(self.s) and self.s[self.pos] == '}':
            self.pos += 1
            return obj
        while True:
            self.skip_whitespace()
            if self.pos >= len(self.s) or self.s[self.pos] != '"':
                raise JSONParseError("Expected string key")
            key = self.parse_string()
            self.skip_whitespace()
            if self.pos >= len(self.s) or self.s[self.pos] != ':':
                raise JSONParseError("Expected ':' after key")
            self.pos += 1
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            if self.pos >= len(self.s):
                raise JSONParseError("Unterminated object")
            ch = self.s[self.pos]
            if ch == '}':
                self.pos += 1
                break
            elif ch == ',':
                self.pos += 1
                continue
            else:
                raise JSONParseError(f"Unexpected character in object: {ch!r}")
        return obj

    def parse_array(self):
        arr = []
        assert self.s[self.pos] == '['
        self.pos += 1
        self.skip_whitespace()
        if self.pos < len(self.s) and self.s[self.pos] == ']':
            self.pos += 1
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            if self.pos >= len(self.s):
                raise JSONParseError("Unterminated array")
            ch = self.s[self.pos]
            if ch == ']':
                self.pos += 1
                break
            elif ch == ',':
                self.pos += 1
                continue
            else:
                raise JSONParseError(f"Unexpected character in array: {ch!r}")
        return arr

    def parse_string(self):
        assert self.s[self.pos] == '"'
        self.pos += 1
        chars = []
        while True:
            if self.pos >= len(self.s):
                raise JSONParseError("Unterminated string")
            ch = self.s[self.pos]
            if ch == '"':
                self.pos += 1
                break
            if ch == '\\':
                self.pos += 1
                if self.pos >= len(self.s):
                    raise JSONParseError("Unterminated escape sequence")
                esc = self.s[self.pos]
                self.pos += 1
                if esc == '"':
                    chars.append('"')
                elif esc == '\\':
                    chars.append('\\')
                elif esc == '/':
                    chars.append('/')
                elif esc == 'b':
                    chars.append('\b')
                elif esc == 'f':
                    chars.append('\f')
                elif esc == 'n':
                    chars.append('\n')
                elif esc == 'r':
                    chars.append('\r')
                elif esc == 't':
                    chars.append('\t')
                elif esc == 'u':
                    hex_digits = self.s[self.pos:self.pos+4]
                    if len(hex_digits) != 4 or not all(c in "0123456789abcdefABCDEF" for c in hex_digits):
                        raise JSONParseError("Invalid Unicode escape")
                    codepoint = int(hex_digits, 16)
                    chars.append(chr(codepoint))
                    self.pos += 4
                else:
                    raise JSONParseError(f"Invalid escape character: \\{esc}")
            else:
                if ord(ch) < 0x20:
                    raise JSONParseError("Control characters not allowed in strings")
                chars.append(ch)
                self.pos += 1
        return ''.join(chars)

    def parse_number(self):
        start = self.pos
        # Consume sign
        if self.s[self.pos] in '+-':
            self.pos += 1
        # Integer part
        if self.pos >= len(self.s):
            raise JSONParseError("Invalid number")
        if self.s[self.pos] == '0':
            self.pos += 1
        elif '1' <= self.s[self.pos] <= '9':
            while self.pos < len(self.s) and self.s[self.pos].isdigit():
                self.pos += 1
        else:
            raise JSONParseError("Invalid number")
        # Fractional part
        if self.pos < len(self.s) and self.s[self.pos] == '.':
            self.pos += 1
            if self.pos >= len(self.s) or not self.s[self.pos].isdigit():
                raise JSONParseError("Invalid fractional part")
            while self.pos < len(self.s) and self.s[self.pos].isdigit():
                self.pos += 1
        # Exponent part
        if self.pos < len(self.s) and self.s[self.pos] in 'eE':
            self.pos += 1
            if self.pos < len(self.s) and self.s[self.pos] in '+-':
                self.pos += 1
            if self.pos >= len(self.s) or not self.s[self.pos].isdigit():
                raise JSONParseError("Invalid exponent")
            while self.pos < len(self.s) and self.s[self.pos].isdigit():
                self.pos += 1
        num_str = self.s[start:self.pos]
        # Validate with regex to catch leading zeros like 007
        if not _NUMBER_RE.match(num_str):
            raise JSONParseError("Invalid number format")
        # Determine int vs float
        if _INT_RE.match(num_str):
            return int(num_str)
        else:
            return float(num_str)
