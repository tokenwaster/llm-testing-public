import sys, re

# Increase recursion limit for deeply nested JSON structures if needed.
sys.setrecursionlimit(10**6)

NUMBER_PATTERN = re.compile(r'^-?(?:0|[1-9]\d*)(\.\d+)?([eE][+-]?\d+)?$')


class JSONParser:
    """A simple recursive-descent JSON parser."""

    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.end = len(text)

    # Skip whitespace characters (space, tab, newline, carriage return).
    def skip_ws(self):
        while self.pos < self.end and self.text[self.pos] in ' \t\r\n':
            self.pos += 1

    def peek_char(self):
        if self.pos >= self.end:
            return None
        return self.text[self.pos]

    def next_char(self):
        c = self.peek_char()
        if c is not None:
            self.pos += 1
        return c

    # Top-level entry point.
    def parse(self):
        self.skip_ws()
        if self.pos >= self.end:
            raise ValueError("Empty input")
        result = self.parse_value()
        self.skip_ws()
        if self.peek_char() is not None:
            raise ValueError("Trailing content after JSON value")
        return result

    # Parse a top-level value.
    def parse_value(self):
        self.skip_ws()
        c = self.peek_char()
        if c == '{':
            return self.parse_object()
        elif c == '[':
            return self.parse_array()
        elif c == '"':
            return self.parse_string()
        elif c in '-0123456789':
            return self.parse_number()
        else:
            # Check for literals (case-sensitive).
            rest = self.text[self.pos:]
            if rest.startswith('true'):
                self.pos += 4
                return True
            elif rest.startswith('false'):
                self.pos += 5
                return False
            elif rest.startswith('null'):
                self.pos += 4
                return None
        raise ValueError(f"Unexpected character: {c!r}")

    # Parse a JSON number.
    def parse_number(self):
        start = self.pos
        # Consume all characters that can be part of a JSON number.
        while True:
            c = self.peek_char()
            if c is None:
                break
            if c in '0123456789.-eE+-':
                self.next_char()
            else:
                break

        token = self.text[start:self.pos]
        if not token:
            raise ValueError("No digits for number")

        # Validate the numeric literal against JSON grammar.
        if not NUMBER_PATTERN.match(token):
            raise ValueError(f"Invalid number format: {token!r}")

        # Determine type: int or float based on presence of '.' or exponent indicator.
        has_fraction = '.' in token
        has_exponent = any(ch in token for ch in 'eE')
        if has_fraction or has_exponent:
            return float(token)
        else:
            return int(token)

    # Parse a JSON string with escape handling, including \uXXXX.
    def parse_string(self):
        if self.peek_char() != '"':
            raise ValueError("Expected opening double quote")
        self.next_char()  # consume "

        result = []
        while True:
            c = self.peek_char()
            if c is None:
                raise ValueError("Unterminated string")

            if c == '"':
                self.next_char()  # closing quote, done.
                break

            elif c == '\\':
                self.next_char()  # consume backslash
                esc = self.peek_char()
                if esc is None:
                    raise ValueError("Unexpected end of string after backslash")

                if esc in ('"', '/', '\\', 'b', 'f', 'n', 'r', 't'):
                    escape_map = {
                        '"': '"',
                        '/': '/',
                        '\\': '\\',
                        'b': '\b',
                        'f': '\f',
                        'n': '\n',
                        'r': '\r',
                        't': '\t'
                    }
                    result.append(escape_map[esc])
                    self.next_char()  # consume the escaped character itself

                elif esc == 'u':
                    self.next_char()  # consume 'u'
                    hex_digits = ""
                    for _ in range(4):
                        h = self.peek_char()
                        if h not in '0123456789abcdefABCDEF':
                            raise ValueError("Invalid unicode escape")
                        hex_digits += h
                        self.next_char()  # consume digit

                    try:
                        code_point = int(hex_digits, 16)
                    except Exception as e:
                        raise ValueError(f"Unicode conversion error: {e}")

                    if not (0 <= code_point <= 0x10FFFF):
                        raise ValueError("Invalid unicode escape range")
                    # Surrogate pairs are not supported.
                    if 0xD800 <= code_point <= 0xDFFF:
                        raise ValueError("Surrogate pair not allowed in JSON string")

                    result.append(chr(code_point))

                else:
                    raise ValueError(f"Unknown escape sequence \\{esc}")

            else:
                # Control characters must be escaped; raw ones are invalid.
                if ord(c) < 32 and c != ' ':
                    raise ValueError("Invalid unescaped control character in string")
                result.append(c)

        return ''.join(result)

    def parse_object(self):
        if self.peek_char() != '{':
            raise ValueError("Expected opening brace {")
        self.next_char()  # consume {

        obj = {}
        self.skip_ws()
        if self.peek_char() == '}':
            self.next_char()
            return obj

        while True:
            key = self.parse_string()
            self.skip_ws()
            if self.peek_char() != ':':
                raise ValueError("Expected colon")
            self.next_char()  # consume :
            value = self.parse_value()
            obj[key] = value

            self.skip_ws()
            c = self.peek_char()
            if c == '}':
                self.next_char()
                break
            elif c == ',':
                self.next_char()  # consume comma
                self.skip_ws()
                next_c = self.peek_char()
                if next_c == '}':
                    raise ValueError("Trailing comma not allowed")
                continue
            else:
                raise ValueError(f"Unexpected character in object: {c!r}")

        return obj

    def parse_array(self):
        if self.peek_char() != '[':
            raise ValueError("Expected opening bracket [")
        self.next_char()  # consume [

        arr = []
        self.skip_ws()
        if self.peek_char() == ']':
            self.next_char()
            return arr

        while True:
            value = self.parse_value()
            arr.append(value)

            self.skip_ws()
            c = self.peek_char()
            if c == ']':
                self.next_char()
                break
            elif c == ',':
                self.next_char()  # consume comma
                self.skip_ws()
                next_c = self.peek_char()
                if next_c == ']':
                    raise ValueError("Trailing comma not allowed")
                continue
            else:
                raise ValueError(f"Unexpected character in array: {c!r}")

        return arr


def parse(text):
    parser = JSONParser(text)
    try:
        return parser.parse()
    except Exception:
        # Any parsing error results in None.
        return None
