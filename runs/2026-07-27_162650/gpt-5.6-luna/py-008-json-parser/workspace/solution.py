class _JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def parse(self):
        self.skip_whitespace()
        value = self.parse_value()
        self.skip_whitespace()
        if self.pos != self.length:
            raise ValueError
        return value

    def parse_value(self):
        self.skip_whitespace()
        if self.pos >= self.length:
            raise ValueError

        char = self.text[self.pos]

        if char == '"':
            return self.parse_string()
        if char == "{":
            return self.parse_object()
        if char == "[":
            return self.parse_array()
        if char == "t" and self.text.startswith("true", self.pos):
            self.pos += 4
            return True
        if char == "f" and self.text.startswith("false", self.pos):
            self.pos += 5
            return False
        if char == "n" and self.text.startswith("null", self.pos):
            self.pos += 4
            return None
        if char == "-" or char.isdigit():
            return self.parse_number()

        raise ValueError

    def parse_string(self):
        if self.text[self.pos] != '"':
            raise ValueError

        self.pos += 1
        result = []

        while self.pos < self.length:
            char = self.text[self.pos]
            self.pos += 1

            if char == '"':
                return "".join(result)

            if char == "\\":
                if self.pos >= self.length:
                    raise ValueError

                escape = self.text[self.pos]
                self.pos += 1

                simple_escapes = {
                    '"': '"',
                    "\\": "\\",
                    "/": "/",
                    "b": "\b",
                    "f": "\f",
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                }

                if escape in simple_escapes:
                    result.append(simple_escapes[escape])
                elif escape == "u":
                    if self.pos + 4 > self.length:
                        raise ValueError

                    digits = self.text[self.pos:self.pos + 4]
                    if any(d not in "0123456789abcdefABCDEF" for d in digits):
                        raise ValueError

                    codepoint = int(digits, 16)
                    self.pos += 4

                    # Combine UTF-16 surrogate pairs when present.
                    if 0xD800 <= codepoint <= 0xDBFF:
                        if (
                            self.text.startswith("\\u", self.pos)
                            and self.pos + 6 <= self.length
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
                else:
                    raise ValueError
            else:
                if ord(char) < 0x20:
                    raise ValueError
                result.append(char)

        raise ValueError

    def parse_number(self):
        start = self.pos

        if self.pos < self.length and self.text[self.pos] == "-":
            self.pos += 1

        if self.pos >= self.length:
            raise ValueError

        if self.text[self.pos] == "0":
            self.pos += 1
            if self.pos < self.length and self.text[self.pos].isdigit():
                raise ValueError
        elif "1" <= self.text[self.pos] <= "9":
            self.pos += 1
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise ValueError

        is_float = False

        if self.pos < self.length and self.text[self.pos] == ".":
            is_float = True
            self.pos += 1
            fraction_start = self.pos

            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

            if self.pos == fraction_start:
                raise ValueError

        if self.pos < self.length and self.text[self.pos] in "eE":
            is_float = True
            self.pos += 1

            if self.pos < self.length and self.text[self.pos] in "+-":
                self.pos += 1

            exponent_start = self.pos
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

            if self.pos == exponent_start:
                raise ValueError

        number_text = self.text[start:self.pos]
        return float(number_text) if is_float else int(number_text)

    def parse_array(self):
        if self.text[self.pos] != "[":
            raise ValueError

        self.pos += 1
        self.skip_whitespace()
        result = []

        if self.pos < self.length and self.text[self.pos] == "]":
            self.pos += 1
            return result

        while True:
            result.append(self.parse_value())
            self.skip_whitespace()

            if self.pos >= self.length:
                raise ValueError

            if self.text[self.pos] == "]":
                self.pos += 1
                return result

            if self.text[self.pos] != ",":
                raise ValueError

            self.pos += 1
            self.skip_whitespace()

            if self.pos < self.length and self.text[self.pos] == "]":
                raise ValueError

    def parse_object(self):
        if self.text[self.pos] != "{":
            raise ValueError

        self.pos += 1
        self.skip_whitespace()
        result = {}

        if self.pos < self.length and self.text[self.pos] == "}":
            self.pos += 1
            return result

        while True:
            self.skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] != '"':
                raise ValueError

            key = self.parse_string()
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] != ":":
                raise ValueError

            self.pos += 1
            result[key] = self.parse_value()
            self.skip_whitespace()

            if self.pos >= self.length:
                raise ValueError

            if self.text[self.pos] == "}":
                self.pos += 1
                return result

            if self.text[self.pos] != ",":
                raise ValueError

            self.pos += 1
            self.skip_whitespace()

            if self.pos < self.length and self.text[self.pos] == "}":
                raise ValueError


def parse(text: str):
    if not isinstance(text, str):
        return None

    try:
        return _JSONParser(text).parse()
    except Exception:
        return None
