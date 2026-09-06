import re
import sys

if hasattr(sys, "set_int_max_str_digits"):
    try:
        sys.set_int_max_str_digits(0)
    except Exception:
        pass

NUMBER_RE = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?")


class JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.n = len(text)
        self.idx = 0

    def skip_whitespace(self):
        text = self.text
        n = self.n
        idx = self.idx
        while idx < n and text[idx] in " \t\n\r":
            idx += 1
        self.idx = idx

    def parse_string(self) -> str:
        self.idx += 1
        chars = []
        text = self.text
        n = self.n
        while self.idx < n:
            c = text[self.idx]
            if c == '"':
                self.idx += 1
                return "".join(chars)
            elif c == "\\":
                self.idx += 1
                if self.idx >= n:
                    raise ValueError("Unterminated escape")
                esc = text[self.idx]
                self.idx += 1
                if esc == '"':
                    chars.append('"')
                elif esc == "\\":
                    chars.append("\\")
                elif esc == "/":
                    chars.append("/")
                elif esc == "b":
                    chars.append("\b")
                elif esc == "f":
                    chars.append("\f")
                elif esc == "n":
                    chars.append("\n")
                elif esc == "r":
                    chars.append("\r")
                elif esc == "t":
                    chars.append("\t")
                elif esc == "u":
                    if self.idx + 4 > n:
                        raise ValueError("Incomplete unicode escape")
                    hex_str = text[self.idx : self.idx + 4]
                    if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
                        raise ValueError("Invalid unicode escape")
                    self.idx += 4
                    code = int(hex_str, 16)
                    if 0xD800 <= code <= 0xDBFF:
                        if self.idx + 6 <= n and text[self.idx : self.idx + 2] == "\\u":
                            hex_str2 = text[self.idx + 2 : self.idx + 6]
                            if all(c in "0123456789abcdefABCDEF" for c in hex_str2):
                                code2 = int(hex_str2, 16)
                                if 0xDC00 <= code2 <= 0xDFFF:
                                    code = 0x10000 + ((code - 0xD800) << 10) + (code2 - 0xDC00)
                                    self.idx += 6
                    chars.append(chr(code))
                else:
                    raise ValueError(f"Invalid escape sequence \\{esc}")
            else:
                if ord(c) < 0x20:
                    raise ValueError("Unescaped control character in string")
                chars.append(c)
                self.idx += 1
        raise ValueError("Unterminated string")

    def parse_number(self):
        match = NUMBER_RE.match(self.text, self.idx)
        if not match:
            raise ValueError("Invalid number format")
        end = match.end()
        if end < self.n and self.text[end] not in " \t\n\r,]}":
            raise ValueError("Unexpected character after number")
        num_str = match.group(0)
        self.idx = end
        if "." in num_str or "e" in num_str or "E" in num_str:
            return float(num_str)
        return int(num_str)

    def parse_object(self) -> dict:
        self.idx += 1
        self.skip_whitespace()
        if self.idx < self.n and self.text[self.idx] == "}":
            self.idx += 1
            return {}

        obj = {}
        while True:
            self.skip_whitespace()
            if self.idx >= self.n or self.text[self.idx] != '"':
                raise ValueError("Expected string key in object")
            key = self.parse_string()
            self.skip_whitespace()
            if self.idx >= self.n or self.text[self.idx] != ":":
                raise ValueError("Expected ':' after object key")
            self.idx += 1
            val = self.parse_value()
            obj[key] = val
            self.skip_whitespace()
            if self.idx >= self.n:
                raise ValueError("Unterminated object")
            c = self.text[self.idx]
            if c == "}":
                self.idx += 1
                return obj
            elif c == ",":
                self.idx += 1
                self.skip_whitespace()
                if self.idx < self.n and self.text[self.idx] == "}":
                    raise ValueError("Trailing comma in object")
            else:
                raise ValueError("Expected ',' or '}' in object")

    def parse_array(self) -> list:
        self.idx += 1
        self.skip_whitespace()
        if self.idx < self.n and self.text[self.idx] == "]":
            self.idx += 1
            return []

        arr = []
        while True:
            val = self.parse_value()
            arr.append(val)
            self.skip_whitespace()
            if self.idx >= self.n:
                raise ValueError("Unterminated array")
            c = self.text[self.idx]
            if c == "]":
                self.idx += 1
                return arr
            elif c == ",":
                self.idx += 1
                self.skip_whitespace()
                if self.idx < self.n and self.text[self.idx] == "]":
                    raise ValueError("Trailing comma in array")
            else:
                raise ValueError("Expected ',' or ']' in array")

    def parse_value(self):
        self.skip_whitespace()
        if self.idx >= self.n:
            raise ValueError("Unexpected end of input")

        c = self.text[self.idx]
        if c == '"':
            return self.parse_string()
        elif c == "{":
            return self.parse_object()
        elif c == "[":
            return self.parse_array()
        elif c == "t":
            if self.text.startswith("true", self.idx):
                self.idx += 4
                if self.idx < self.n and self.text[self.idx] not in " \t\n\r,]}":
                    raise ValueError("Unexpected character after true")
                return True
            raise ValueError("Invalid literal")
        elif c == "f":
            if self.text.startswith("false", self.idx):
                self.idx += 5
                if self.idx < self.n and self.text[self.idx] not in " \t\n\r,]}":
                    raise ValueError("Unexpected character after false")
                return False
            raise ValueError("Invalid literal")
        elif c == "n":
            if self.text.startswith("null", self.idx):
                self.idx += 4
                if self.idx < self.n and self.text[self.idx] not in " \t\n\r,]}":
                    raise ValueError("Unexpected character after null")
                return None
            raise ValueError("Invalid literal")
        elif c == "-" or c.isdigit():
            return self.parse_number()
        else:
            raise ValueError(f"Unexpected character: {c}")


def parse(text: str):
    if not isinstance(text, str):
        return None
    parser = JSONParser(text)
    try:
        val = parser.parse_value()
        parser.skip_whitespace()
        if parser.idx != parser.n:
            return None
        return val
    except Exception:
        return None
