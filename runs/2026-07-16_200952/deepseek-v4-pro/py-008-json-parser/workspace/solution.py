class JSONParseError(Exception):
    pass

class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def skip_whitespace(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def peek(self) -> str | None:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def next_char(self) -> str:
        if self.pos >= len(self.text):
            raise JSONParseError("Unexpected end of input")
        ch = self.text[self.pos]
        self.pos += 1
        return ch

    def expect_char(self, expected: str) -> str:
        ch = self.next_char()
        if ch != expected:
            raise JSONParseError(f"Expected '{expected}', got '{ch}'")
        return ch

    def parse_value(self):
        self.skip_whitespace()
        ch = self.peek()
        if ch is None:
            raise JSONParseError("Empty input")
        if ch == '{':
            return self.parse_object()
        elif ch == '[':
            return self.parse_array()
        elif ch == '"':
            return self.parse_string()
        elif ch == 't' or ch == 'f':
            return self.parse_literal()
        elif ch == 'n':
            return self.parse_literal()
        elif ch == '-' or ch.isdigit():
            return self.parse_number()
        else:
            raise JSONParseError(f"Unexpected character: {ch}")

    def parse_object(self) -> dict:
        self.expect_char('{')
        self.skip_whitespace()
        obj = {}
        if self.peek() == '}':
            self.next_char()
            return obj
        while True:
            self.skip_whitespace()
            key = self.parse_string()
            self.skip_whitespace()
            self.expect_char(':')
            self.skip_whitespace()
            val = self.parse_value()
            obj[key] = val
            self.skip_whitespace()
            ch = self.next_char()
            if ch == '}':
                return obj
            elif ch != ',':
                raise JSONParseError("Expected ',' or '}' in object")
            self.skip_whitespace()
            if self.peek() == '}':
                raise JSONParseError("Trailing comma in object")

    def parse_array(self) -> list:
        self.expect_char('[')
        self.skip_whitespace()
        arr = []
        if self.peek() == ']':
            self.next_char()
            return arr
        while True:
            self.skip_whitespace()
            val = self.parse_value()
            arr.append(val)
            self.skip_whitespace()
            ch = self.next_char()
            if ch == ']':
                return arr
            elif ch != ',':
                raise JSONParseError("Expected ',' or ']' in array")
            self.skip_whitespace()
            if self.peek() == ']':
                raise JSONParseError("Trailing comma in array")

    def parse_string(self) -> str:
        self.expect_char('"')
        result = []
        while True:
            ch = self.next_char()
            if ch == '"':
                return ''.join(result)
            elif ch == '\\':
                esc = self.next_char()
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
                    hex_str = self.text[self.pos:self.pos+4]
                    if len(hex_str) < 4:
                        raise JSONParseError("Incomplete unicode escape")
                    try:
                        code = int(hex_str, 16)
                    except ValueError:
                        raise JSONParseError("Invalid unicode escape")
                    self.pos += 4
                    if 0xD800 <= code <= 0xDBFF:  # high surrogate
                        if self.pos < len(self.text) and self.text[self.pos:self.pos+2] == '\\u':
                            if self.pos + 6 > len(self.text):
                                raise JSONParseError("Incomplete surrogate pair")
                            hex2 = self.text[self.pos+2:self.pos+6]
                            try:
                                code2 = int(hex2, 16)
                            except ValueError:
                                raise JSONParseError("Invalid surrogate pair")
                            if 0xDC00 <= code2 <= 0xDFFF:
                                codepoint = 0x10000 + (code - 0xD800) * 0x400 + (code2 - 0xDC00)
                                result.append(chr(codepoint))
                                self.pos += 6
                            else:
                                raise JSONParseError("Invalid low surrogate")
                        else:
                            raise JSONParseError("Lone high surrogate")
                    elif 0xDC00 <= code <= 0xDFFF:  # low surrogate without high
                        raise JSONParseError("Lone low surrogate")
                    else:
                        result.append(chr(code))
                else:
                    raise JSONParseError(f"Invalid escape: \\{esc}")
            else:
                if ord(ch) <= 0x1F:
                    raise JSONParseError("Unescaped control character in string")
                result.append(ch)

    def parse_number(self) -> int | float:
        start = self.pos
        if self.peek() == '-':
            self.pos += 1
        if self.peek() is None:
            raise JSONParseError("Incomplete number")
        if self.peek() == '0':
            self.pos += 1
        elif self.peek().isdigit() and self.peek() != '0':
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise JSONParseError("Invalid number")
        if self.pos < len(self.text) and self.peek() == '.':
            self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise JSONParseError("Invalid fraction")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        if self.pos < len(self.text) and self.peek() in 'eE':
            self.pos += 1
            if self.pos < len(self.text) and self.peek() in '+-':
                self.pos += 1
            if self.pos >= len(self.text) or not self.text[self.pos].isdigit():
                raise JSONParseError("Invalid exponent")
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        num_str = self.text[start:self.pos]
        try:
            if '.' in num_str or 'e' in num_str or 'E' in num_str:
                return float(num_str)
            else:
                return int(num_str)
        except ValueError:
            raise JSONParseError("Invalid number format")

    def parse_literal(self):
        self.skip_whitespace()
        if self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        elif self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        elif self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        else:
            raise JSONParseError("Invalid literal")


def parse(text: str):
    try:
        parser = _Parser(text)
        val = parser.parse_value()
        parser.skip_whitespace()
        if parser.pos != len(parser.text):
            raise JSONParseError("Trailing garbage after document")
        return val
    except Exception:
        return None
