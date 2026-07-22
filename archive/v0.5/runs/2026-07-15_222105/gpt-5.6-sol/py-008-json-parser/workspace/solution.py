_INVALID = object()


class _Parser:
    def __init__(self, text):
        self.text = text
        self.length = len(text)
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()

        if self.pos >= self.length:
            return _INVALID

        char = self.text[self.pos]

        if char == '"':
            return self.parse_string()
        if char == "{":
            return self.parse_object()
        if char == "[":
            return self.parse_array()
        if char == "t":
            return self.parse_literal("true", True)
        if char == "f":
            return self.parse_literal("false", False)
        if char == "n":
            return self.parse_literal("null", None)
        if char == "-" or char.isdigit():
            return self.parse_number()

        return _INVALID

    def parse_literal(self, literal, value):
        end = self.pos + len(literal)
        if self.text[self.pos:end] != literal:
            return _INVALID
        self.pos = end
        return value

    def parse_string(self):
        self.pos += 1
        result = []

        escapes = {
            '"': '"',
            "\\": "\\",
            "/": "/",
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
        }

        while self.pos < self.length:
            char = self.text[self.pos]
            self.pos += 1

            if char == '"':
                return "".join(result)

            if ord(char) < 0x20:
                return _INVALID

            if char != "\\":
                result.append(char)
                continue

            if self.pos >= self.length:
                return _INVALID

            escape = self.text[self.pos]
            self.pos += 1

            if escape in escapes:
                result.append(escapes[escape])
                continue

            if escape != "u":
                return _INVALID

            codepoint = self.parse_unicode_escape()
            if codepoint is _INVALID:
                return _INVALID

            # Combine a UTF-16 surrogate pair when present.
            if (
                0xD800 <= codepoint <= 0xDBFF
                and self.pos + 6 <= self.length
                and self.text[self.pos:self.pos + 2] == "\\u"
            ):
                hex_digits = self.text[self.pos + 2:self.pos + 6]
                if self.is_hex_sequence(hex_digits):
                    low = int(hex_digits, 16)
                    if 0xDC00 <= low <= 0xDFFF:
                        self.pos += 6
                        codepoint = (
                            0x10000
                            + ((codepoint - 0xD800) << 10)
                            + (low - 0xDC00)
                        )

            result.append(chr(codepoint))

        return _INVALID

    def parse_unicode_escape(self):
        if self.pos + 4 > self.length:
            return _INVALID

        digits = self.text[self.pos:self.pos + 4]
        if not self.is_hex_sequence(digits):
            return _INVALID

        self.pos += 4
        return int(digits, 16)

    @staticmethod
    def is_hex_sequence(text):
        return all(
            "0" <= char <= "9"
            or "a" <= char <= "f"
            or "A" <= char <= "F"
            for char in text
        )

    def parse_number(self):
        start = self.pos

        if self.text[self.pos] == "-":
            self.pos += 1
            if self.pos >= self.length:
                return _INVALID

        if self.text[self.pos] == "0":
            self.pos += 1
            if self.pos < self.length and self.text[self.pos].isdigit():
                return _INVALID
        elif "1" <= self.text[self.pos] <= "9":
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            return _INVALID

        is_float = False

        if self.pos < self.length and self.text[self.pos] == ".":
            is_float = True
            self.pos += 1

            fraction_start = self.pos
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

            if self.pos == fraction_start:
                return _INVALID

        if self.pos < self.length and self.text[self.pos] in "eE":
            is_float = True
            self.pos += 1

            if self.pos < self.length and self.text[self.pos] in "+-":
                self.pos += 1

            exponent_start = self.pos
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

            if self.pos == exponent_start:
                return _INVALID

        token = self.text[start:self.pos]

        if is_float:
            try:
                return float(token)
            except (ValueError, OverflowError):
                return _INVALID

        negative = token.startswith("-")
        digits = token[1:] if negative else token

        # Build manually to avoid Python's configurable integer-string limit.
        value = 0
        for digit in digits:
            value = value * 10 + (ord(digit) - ord("0"))

        return -value if negative else value

    def parse_array(self):
        self.pos += 1
        result = []
        self.skip_whitespace()

        if self.pos < self.length and self.text[self.pos] == "]":
            self.pos += 1
            return result

        while True:
            value = self.parse_value()
            if value is _INVALID:
                return _INVALID
            result.append(value)

            self.skip_whitespace()
            if self.pos >= self.length:
                return _INVALID

            char = self.text[self.pos]
            if char == "]":
                self.pos += 1
                return result
            if char != ",":
                return _INVALID

            self.pos += 1
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] == "]":
                return _INVALID

    def parse_object(self):
        self.pos += 1
        result = {}
        self.skip_whitespace()

        if self.pos < self.length and self.text[self.pos] == "}":
            self.pos += 1
            return result

        while True:
            self.skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] != '"':
                return _INVALID

            key = self.parse_string()
            if key is _INVALID:
                return _INVALID

            self.skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] != ":":
                return _INVALID

            self.pos += 1
            value = self.parse_value()
            if value is _INVALID:
                return _INVALID

            result[key] = value

            self.skip_whitespace()
            if self.pos >= self.length:
                return _INVALID

            char = self.text[self.pos]
            if char == "}":
                self.pos += 1
                return result
            if char != ",":
                return _INVALID

            self.pos += 1
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] == "}":
                return _INVALID


def parse(text: str):
    if not isinstance(text, str):
        return None

    try:
        parser = _Parser(text)
        result = parser.parse_value()

        if result is _INVALID:
            return None

        parser.skip_whitespace()
        if parser.pos != parser.length:
            return None

        return result
    except (ValueError, OverflowError, RecursionError):
        return None
