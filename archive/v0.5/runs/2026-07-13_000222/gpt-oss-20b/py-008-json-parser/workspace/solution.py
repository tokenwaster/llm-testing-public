#!/usr/bin/env python3
"""
A minimal JSON parser that follows the full JSON grammar.
It returns Python objects (dict, list, str, int, float, True, False, None)
or None if the input is not valid JSON.
"""

import sys

def parse(text: str):
    """
    Parse a JSON document and return the corresponding Python object,
    or None if the input is invalid.
    """
    parser = _JSONParser(text)
    result = parser.parse()
    return result


class _JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.n = len(text)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def parse(self):
        try:
            value = self._parse_value()
            self._skip_whitespace()
            if self.i != self.n:          # trailing garbage
                return None
            return value
        except _JSONError:
            return None

    # ------------------------------------------------------------------
    # Parsing helpers
    # ------------------------------------------------------------------
    def _parse_value(self):
        self._skip_whitespace()
        if self.i >= self.n:
            raise _JSONError("Unexpected end of input")

        ch = self.text[self.i]
        if ch == '{':
            return self._parse_object()
        elif ch == '[':
            return self._parse_array()
        elif ch == '"':
            return self._parse_string()
        elif ch == 't':
            return self._expect_literal('true', True)
        elif ch == 'f':
            return self._expect_literal('false', False)
        elif ch == 'n':
            return self._expect_literal('null', None)
        elif ch == '-' or ch.isdigit():
            return self._parse_number()
        else:
            raise _JSONError(f"Unexpected character: {ch!r}")

    def _parse_object(self):
        obj = {}
        self.i += 1  # skip '{'
        self._skip_whitespace()

        if self._peek() == '}':
            self.i += 1
            return obj

        while True:
            self._skip_whitespace()
            if self._peek() != '"':
                raise _JSONError("Object keys must be strings")
            key = self._parse_string()

            self._skip_whitespace()
            if self._next_char() != ':':
                raise _JSONError("Missing ':' after object key")

            value = self._parse_value()
            obj[key] = value

            self._skip_whitespace()
            ch = self._peek()
            if ch == '}':
                self.i += 1
                break
            elif ch == ',':
                self.i += 1
                continue
            else:
                raise _JSONError("Expected ',' or '}' in object")
        return obj

    def _parse_array(self):
        arr = []
        self.i += 1  # skip '['
        self._skip_whitespace()

        if self._peek() == ']':
            self.i += 1
            return arr

        while True:
            value = self._parse_value()
            arr.append(value)

            self._skip_whitespace()
            ch = self._peek()
            if ch == ']':
                self.i += 1
                break
            elif ch == ',':
                self.i += 1
                continue
            else:
                raise _JSONError("Expected ',' or ']' in array")
        return arr

    def _parse_string(self):
        result = []
        self.i += 1  # skip opening quote
        while True:
            if self.i >= self.n:
                raise _JSONError("Unterminated string")

            ch = self.text[self.i]
            if ch == '"':
                self.i += 1
                return ''.join(result)
            elif ch == '\\':
                self.i += 1
                if self.i >= self.n:
                    raise _JSONError("Unterminated escape sequence")
                esc = self.text[self.i]
                if esc == '"':
                    result.append('"')
                elif esc == '\\':
                    result.append('\\')
                elif esc == '/':
                    result.append('/')
                elif esc == 'b':
                    result.append('\b')
                elif esc == 'f':
                    result.append('\f')
                elif esc == 'n':
                    result.append('\n')
                elif esc == 'r':
                    result.append('\r')
                elif esc == 't':
                    result.append('\t')
                elif esc == 'u':
                    hex_digits = self.text[self.i+1:self.i+5]
                    if len(hex_digits) != 4 or not all(c in "0123456789abcdefABCDEF" for c in hex_digits):
                        raise _JSONError("Invalid Unicode escape")
                    codepoint = int(hex_digits, 16)
                    result.append(chr(codepoint))
                    self.i += 4
                else:
                    raise _JSONError(f"Invalid escape character: \\{esc}")
            elif ord(ch) < 0x20:
                raise _JSONError("Control characters not allowed in strings")
            else:
                result.append(ch)
            self.i += 1

    def _parse_number(self):
        start = self.i
        ch = self.text[self.i]

        # sign
        if ch == '-':
            self.i += 1
            if self.i >= self.n or not self.text[self.i].isdigit():
                raise _JSONError("Invalid number format")

        # integer part
        if self.text[self.i] == '0':
            self.i += 1
        else:
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1

        # fraction part
        has_frac = False
        if self.i < self.n and self.text[self.i] == '.':
            has_frac = True
            self.i += 1
            if self.i >= self.n or not self.text[self.i].isdigit():
                raise _JSONError("Invalid number format")
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1

        # exponent part
        has_exp = False
        if self.i < self.n and self.text[self.i] in ('e', 'E'):
            has_exp = True
            self.i += 1
            if self.i < self.n and self.text[self.i] in ('+', '-'):
                self.i += 1
            if self.i >= self.n or not self.text[self.i].isdigit():
                raise _JSONError("Invalid number format")
            while self.i < self.n and self.text[self.i].isdigit():
                self.i += 1

        num_str = self.text[start:self.i]
        try:
            if has_frac or has_exp:
                return float(num_str)
            else:
                # disallow leading zeros except single zero
                if len(num_str.lstrip('-')) > 1 and num_str.lstrip('-').startswith('0'):
                    raise _JSONError("Leading zeros are not allowed")
                return int(num_str)
        except ValueError:
            raise _JSONError("Invalid number")

    def _expect_literal(self, literal: str, value):
        if self.text[self.i:self.i+len(literal)] != literal:
            raise _JSONError(f"Expected {literal}")
        self.i += len(literal)
        return value

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------
    def _skip_whitespace(self):
        while self.i < self.n and self.text[self.i] in ' \t\n\r':
            self.i += 1

    def _peek(self):
        if self.i >= self.n:
            return ''
        return self.text[self.i]

    def _next_char(self):
        ch = self._peek()
        self.i += 1
        return ch


class _JSONError(Exception):
    pass


# ----------------------------------------------------------------------
# If run as a script, provide simple CLI for testing
# ----------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python solution.py <json_file>")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        data = f.read()
    result = parse(data)
    print(result)
