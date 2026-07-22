class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.length = len(text)
        self.pos = 0

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def parse_value(self):
        self.skip_whitespace()

        if self.pos >= self.length:
            raise _ParseError

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
        if char == "-" or char.isdigit() and char.isascii():
            return self.parse_number()

        raise _ParseError

    def parse_literal(self, literal, value):
        end = self.pos + len(literal)
        if self.text[self.pos:end] != literal:
            raise _ParseError
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
                raise _ParseError

            if char != "\\":
                result.append(char)
                continue

            if self.pos >= self.length:
                raise _ParseError

            escape = self.text[self.pos]
            self.pos += 1

            if escape in escapes:
                result.append(escapes[escape])
            elif escape == "u":
                code = self.parse_unicode_escape()

                # Combine an escaped UTF-16 surrogate pair when present.
                if (
                    0xD800 <= code <= 0xDBFF
                    and self.pos + 6 <= self.length
                    and self.text[self.pos:self.pos + 2] == "\\u"
                ):
                    digits = self.text[self.pos + 2:self.pos + 6]
                    if all(c in "0123456789abcdefABCDEF" for c in digits):
                        low = int(digits, 16)
                        if 0xDC00 <= low <= 0xDFFF:
                            self.pos += 6
                            code = (
                                0x10000
                                + ((code - 0xD800) << 10)
                                + (low - 0xDC00)
                            )

                result.append(chr(code))
            else:
                raise _ParseError

        raise _ParseError

    def parse_unicode_escape(self):
        if self.pos + 4 > self.length:
            raise _ParseError

        digits = self.text[self.pos:self.pos + 4]
        if not all(c in "0123456789abcdefABCDEF" for c in digits):
            raise _ParseError

        self.pos += 4
        return int(digits, 16)

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
                raise _ParseError

            char = self.text[self.pos]
            if char == "]":
                self.pos += 1
                return result
            if char != ",":
                raise _ParseError

            self.pos += 1
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] == "]":
                raise _ParseError

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
                raise _ParseError

            key = self.parse_string()
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] != ":":
                raise _ParseError

            self.pos += 1
            result[key] = self.parse_value()
            self.skip_whitespace()

            if self.pos >= self.length:
                raise _ParseError

            char = self.text[self.pos]
            if char == "}":
                self.pos += 1
                return result
            if char != ",":
                raise _ParseError

            self.pos += 1
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] == "}":
                raise _ParseError

    def parse_number(self):
        start = self.pos

        if self.text[self.pos] == "-":
            self.pos += 1
            if self.pos >= self.length:
                raise _ParseError

        if self.text[self.pos] == "0":
            self.pos += 1
            if (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                raise _ParseError
        elif (
            self.text[self.pos].isascii()
            and self.text[self.pos] in "123456789"
        ):
            self.pos += 1
            while (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                self.pos += 1
        else:
            raise _ParseError

        is_float = False

        if self.pos < self.length and self.text[self.pos] == ".":
            is_float = True
            self.pos += 1

            if (
                self.pos >= self.length
                or not self.text[self.pos].isascii()
                or not self.text[self.pos].isdigit()
            ):
                raise _ParseError

            while (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                self.pos += 1

        if self.pos < self.length and self.text[self.pos] in "eE":
            is_float = True
            self.pos += 1

            if self.pos < self.length and self.text[self.pos] in "+-":
                self.pos += 1

            if (
                self.pos >= self.length
                or not self.text[self.pos].isascii()
                or not self.text[self.pos].isdigit()
            ):
                raise _ParseError

            while (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                self.pos += 1

        number = self.text[start:self.pos]
        return float(number) if is_float else int(number)


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
    except (ValueError, OverflowError, RecursionError, _ParseError):
        return None
