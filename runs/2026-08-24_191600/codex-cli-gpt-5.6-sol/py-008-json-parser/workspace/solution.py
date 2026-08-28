class _JSONError(Exception):
    pass


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
            raise _JSONError

        char = self.text[self.pos]
        if char == "{":
            return self.parse_object()
        if char == "[":
            return self.parse_array()
        if char == '"':
            return self.parse_string()
        if char == "-" or char.isdigit() and char.isascii():
            return self.parse_number()
        if self.text.startswith("true", self.pos):
            self.pos += 4
            return True
        if self.text.startswith("false", self.pos):
            self.pos += 5
            return False
        if self.text.startswith("null", self.pos):
            self.pos += 4
            return None
        raise _JSONError

    def parse_object(self):
        result = {}
        self.pos += 1
        self.skip_whitespace()

        if self.pos < self.length and self.text[self.pos] == "}":
            self.pos += 1
            return result

        while True:
            self.skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] != '"':
                raise _JSONError
            key = self.parse_string()

            self.skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] != ":":
                raise _JSONError
            self.pos += 1

            result[key] = self.parse_value()
            self.skip_whitespace()

            if self.pos >= self.length:
                raise _JSONError
            if self.text[self.pos] == "}":
                self.pos += 1
                return result
            if self.text[self.pos] != ",":
                raise _JSONError
            self.pos += 1

    def parse_array(self):
        result = []
        self.pos += 1
        self.skip_whitespace()

        if self.pos < self.length and self.text[self.pos] == "]":
            self.pos += 1
            return result

        while True:
            result.append(self.parse_value())
            self.skip_whitespace()

            if self.pos >= self.length:
                raise _JSONError
            if self.text[self.pos] == "]":
                self.pos += 1
                return result
            if self.text[self.pos] != ",":
                raise _JSONError
            self.pos += 1

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
                raise _JSONError
            if char != "\\":
                result.append(char)
                continue

            if self.pos >= self.length:
                raise _JSONError
            escape = self.text[self.pos]
            self.pos += 1

            if escape in escapes:
                result.append(escapes[escape])
            elif escape == "u":
                code = self.parse_hex_escape()

                if 0xD800 <= code <= 0xDBFF:
                    saved_pos = self.pos
                    if (
                        self.pos + 2 <= self.length
                        and self.text[self.pos:self.pos + 2] == "\\u"
                    ):
                        self.pos += 2
                        low = self.parse_hex_escape()
                        if 0xDC00 <= low <= 0xDFFF:
                            code = (
                                0x10000
                                + ((code - 0xD800) << 10)
                                + (low - 0xDC00)
                            )
                        else:
                            self.pos = saved_pos
                    result.append(chr(code))
                else:
                    result.append(chr(code))
            else:
                raise _JSONError

        raise _JSONError

    def parse_hex_escape(self):
        if self.pos + 4 > self.length:
            raise _JSONError
        digits = self.text[self.pos:self.pos + 4]
        if any(
            char not in "0123456789abcdefABCDEF"
            for char in digits
        ):
            raise _JSONError
        self.pos += 4
        return int(digits, 16)

    def parse_number(self):
        start = self.pos

        if self.text[self.pos] == "-":
            self.pos += 1
            if self.pos >= self.length:
                raise _JSONError

        if self.text[self.pos] == "0":
            self.pos += 1
            if (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                raise _JSONError
        elif (
            self.text[self.pos].isascii()
            and self.text[self.pos] in "123456789"
        ):
            while (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                self.pos += 1
        else:
            raise _JSONError

        is_float = False

        if self.pos < self.length and self.text[self.pos] == ".":
            is_float = True
            self.pos += 1
            fraction_start = self.pos
            while (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                self.pos += 1
            if self.pos == fraction_start:
                raise _JSONError

        if self.pos < self.length and self.text[self.pos] in "eE":
            is_float = True
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in "+-":
                self.pos += 1
            exponent_start = self.pos
            while (
                self.pos < self.length
                and self.text[self.pos].isascii()
                and self.text[self.pos].isdigit()
            ):
                self.pos += 1
            if self.pos == exponent_start:
                raise _JSONError

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
    except (ValueError, OverflowError, RecursionError, _JSONError):
        return None
