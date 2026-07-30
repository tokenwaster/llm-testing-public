# solution.py

import sys
from typing import Any, Optional

class JSONParseError(Exception):
    pass


class Parser:
    def __init__(self, text: str) -> None:
        self.text = text
        self.i = 0
        self.n = len(text)

    # ---------- utilities ----------
    def skip_ws(self) -> None:
        while self.i < self.n and self.text[self.i] in " \t\n\r":
            self.i += 1

    def peek(self) -> str:
        if self.i >= self.n:
            return ""
        return self.text[self.i]

    def consume(self, expected: Optional[str] = None) -> str:
        if self.i >= self.n:
            raise JSONParseError("Unexpected end of input")
        ch = self.text[self.i]
        if expected is not None and ch != expected:
            raise JSONParseError(f"Expected '{expected}', got '{ch}'")
        self.i += 1
        return ch

    def expect(self, s: str) -> None:
        for ch in s:
            self.consume(ch)

    # ---------- parsing ----------
    def parse_value(self) -> Any:
        self.skip_ws()
        if self.peek() == '"':
            return self.parse_string()
        elif self.peek() == '{':
            return self.parse_object()
        elif self.peek() == '[':
            return self.parse_array()
        elif self.text.startswith("true", self.i):
            self.i += 4
            return True
        elif self.text.startswith("false", self.i):
            self.i += 5
            return False
        elif self.text.startswith("null", self.i):
            self.i += 4
            return None
        else:
            return self.parse_number()

    def parse_object(self) -> dict:
        obj = {}
        self.expect("{")
        self.skip_ws()
        if self.peek() == "}":
            self.consume("}")
            return obj
        while True:
            self.skip_ws()
            if self.peek() != '"':
                raise JSONParseError("Object keys must be strings")
            key = self.parse_string()
            self.skip_ws()
            self.expect(":")
            value = self.parse_value()
            obj[key] = value
            self.skip_ws()
            ch = self.consume()
            if ch == "}":
                break
            elif ch != ",":
                raise JSONParseError("Expected ',' or '}' in object")
        return obj

    def parse_array(self) -> list:
        arr = []
        self.expect("[")
        self.skip_ws()
        if self.peek() == "]":
            self.consume("]")
            return arr
        while True:
            val = self.parse_value()
            arr.append(val)
            self.skip_ws()
            ch = self.consume()
            if ch == "]":
                break
            elif ch != ",":
                raise JSONParseError("Expected ',' or ']' in array")
        return arr

    def parse_string(self) -> str:
        result = []
        self.expect('"')
        while True:
            if self.i >= self.n:
                raise JSONParseError("Unterminated string")
            ch = self.consume()
            if ch == '"':
                break
            if ch == '\\':
                esc = self.consume()
                if esc == '"' or esc == '\\' or esc == '/':
                    result.append(esc)
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
                    hex_digits = self.text[self.i:self.i+4]
                    if len(hex_digits) != 4 or not all(c in "0123456789abcdefABCDEF" for c in hex_digits):
                        raise JSONParseError("Invalid unicode escape")
                    codepoint = int(hex_digits, 16)
                    result.append(chr(codepoint))
                    self.i += 4
                else:
                    raise JSONParseError(f"Invalid escape character '\\{esc}'")
            elif ord(ch) < 0x20:
                # control characters not allowed in JSON strings
                raise JSONParseError("Control character in string")
            else:
                result.append(ch)
        return "".join(result)

    def parse_number(self) -> Any:
        start = self.i
        if self.peek() == '-':
            self.consume()
        digits_start = self.i
        if self.peek() == '0':
            self.consume()
            # leading zeros not allowed unless single zero
            if self.peek().isdigit():
                raise JSONParseError("Leading zeros are not allowed")
        else:
            if not self.peek().isdigit():
                raise JSONParseError("Invalid number format")
            while self.peek().isdigit():
                self.consume()
        is_float = False
        if self.peek() == '.':
            is_float = True
            self.consume()
            if not self.peek().isdigit():
                raise JSONParseError("Digits required after decimal point")
            while self.peek().isdigit():
                self.consume()
        if self.peek() in ('e', 'E'):
            is_float = True
            self.consume()
            if self.peek() in ('+', '-'):
                self.consume()
            if not self.peek().isdigit():
                raise JSONParseError("Digits required in exponent")
            while self.peek().digit():
                self.consume()
        num_str = self.text[start:self.i]
        try:
            if is_float:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            raise JSONParseError("Invalid number value")


def parse(text: str) -> Optional[Any]:
    """
    Parse a JSON document and return the corresponding Python object.
    Return None if the input is not valid JSON.
    """
    try:
        parser = Parser(text)
        result = parser.parse_value()
        parser.skip_ws()
        if parser.i != parser.n:
            # trailing garbage
            return None
        return result
    except JSONParseError:
        return None


# If run as a script, provide simple CLI for testing
if __name__ == "__main__":
    import json
    data = sys.stdin.read()
    obj = parse(data)
    if obj is None:
        print("Invalid JSON")
    else:
        print(json.dumps(obj, indent=2))
