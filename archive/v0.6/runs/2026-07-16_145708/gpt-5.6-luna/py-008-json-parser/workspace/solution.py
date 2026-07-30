class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()

        if self.pos >= self.length:
            raise _ParseError()

        char = self.text[self.pos]

        if char == "{":
            return self.parse_object()
        if char == "[":
            return self.parse_array()
        if char == '"':
            return self.parse_string()
        if char == "t":
            return self.parse_literal("true", True)
        if char == "f":
            return self.parse_literal("false", False)
        if char == "n":
            return self.parse_literal("null", None)
        if char == "-" or char.isdigit():
            return self.parse_number()

        raise _ParseError()

    def parse_literal(self, literal, value):
        if not self.text.startswith(literal, self.pos):
            raise _ParseError()
        self.pos += len(literal)
        return value

    def parse_string(self):
        if self.pos >= self.length or self.text[self.pos] != '"':
            raise _ParseError()

        self.pos += 1
        result = []

        while self.pos < self.length:
            char = self.text[self.pos]

            if char == '"':
                self.pos += 1
                return "".join(result)

            if ord(char) < 0x20:
                raise _ParseError()

            if char != "\\":
                result.append(char)
                self.pos += 1
                continue

            self.pos += 1
            if self.pos >= self.length:
                raise _ParseError()

            escape = self.text[self.pos]
            self.pos += 1

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

            if escape in escapes:
                result.append(escapes[escape])
                continue

            if escape != "u":
                raise _ParseError()

            if self.pos + 4 > self.length:
                raise _ParseError()

            digits = self.text[self.pos:self.pos + 4]
            if any(d not in "0123456789abcdefABCDEF" for d in digits):
                raise _ParseError()

            codepoint = int(digits, 16)
            self.pos += 4

            # Combine adjacent UTF-16 surrogate escapes into one code point.
            if 0xD800 <= codepoint <= 0xDBFF:
                if (
                    self.pos + 6 <= self.length
                    and self.text[self.pos:self.pos + 2] == "\\u"
                ):
                    low_digits = self.text[self.pos + 2:self.pos + 6]
                    if all(
                        d in "0123456789abcdefABCDEF"
                        for d in low_digits
                    ):
                        low = int(low_digits, 16)
                        if 0xDC00 <= low <= 0xDFFF:
                            codepoint = (
                                0x10000
                                + ((codepoint - 0xD800) << 10)
                                + (low - 0xDC00)
                            )
                            self.pos += 6

            result.append(chr(codepoint))

        raise _ParseError()

    def parse_number(self):
        start = self.pos

        if self.text[self.pos] == "-":
            self.pos += 1
            if self.pos >= self.length:
                raise _ParseError()

        if self.text[self.pos] == "0":
            self.pos += 1
            if self.pos < self.length and self.text[self.pos].isdigit():
                raise _ParseError()
        elif "1" <= self.text[self.pos] <= "9":
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise _ParseError()

        is_float = False

        if self.pos < self.length and self.text[self.pos] == ".":
            is_float = True
            self.pos += 1
            fraction_start = self.pos

            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

            if self.pos == fraction_start:
                raise _ParseError()

        if self.pos < self.length and self.text[self.pos] in "eE":
            is_float = True
            self.pos += 1

            if self.pos < self.length and self.text[self.pos] in "+-":
                self.pos += 1

            exponent_start = self.pos
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

            if self.pos == exponent_start:
                raise _ParseError()

        number_text = self.text[start:self.pos]

        try:
            return float(number_text) if is_float else int(number_text)
        except ValueError:
            raise _ParseError()

    def parse_array(self):
        self.pos += 1
        result = []

        self.skip_whitespace()
        if self.pos < self.length and self.text[self.pos] == "]":
            self.pos += 1
            return result

        while True:
            result.append(self.parse_value())
            self.skip_whitespace()

            if self.pos >= self.length:
                raise _ParseError()

            if self.text[self.pos] == "]":
                self.pos += 1
                return result

            if self.text[self.pos] != ",":
                raise _ParseError()

            self.pos += 1
            self.skip_whitespace()

            if self.pos < self.length and self.text[self.pos] == "]":
                raise _ParseError()

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
                raise _ParseError()

            key = self.parse_string()
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] != ":":
                raise _ParseError()

            self.pos += 1
            result[key] = self.parse_value()
            self.skip_whitespace()

            if self.pos >= self.length:
                raise _ParseError()

            if self.text[self.pos] == "}":
                self.pos += 1
                return result

            if self.text[self.pos] != ",":
                raise _ParseError()

            self.pos += 1
            self.skip_whitespace()

            if self.pos < self.length and self.text[self.pos] == "}":
                raise _ParseError()


def parse(text: str):
    if not isinstance(text, str):
        return None

    try:
        parser = _Parser(text)
        value = parser.parse_value()
        parser.skip_whitespace()

        if parser.pos != parser.length:
            return None

        return value
    except (IndexError, RecursionError, _ParseError):
        return None
