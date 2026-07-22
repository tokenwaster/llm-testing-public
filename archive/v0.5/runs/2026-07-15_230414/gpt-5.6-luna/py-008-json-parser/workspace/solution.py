def parse(text: str):
    if not isinstance(text, str):
        return None

    class Parser:
        def __init__(self, source):
            self.text = source
            self.length = len(source)
            self.pos = 0

        def skip_whitespace(self):
            while self.pos < self.length and self.text[self.pos] in " \t\r\n":
                self.pos += 1

        def parse_document(self):
            self.skip_whitespace()
            ok, value = self.parse_value()
            if not ok:
                return None
            self.skip_whitespace()
            if self.pos != self.length:
                return None
            return value

        def parse_value(self):
            self.skip_whitespace()
            if self.pos >= self.length:
                return False, None

            char = self.text[self.pos]

            if char == '"':
                return self.parse_string()
            if char == "{":
                return self.parse_object()
            if char == "[":
                return self.parse_array()
            if char == "-" or ("0" <= char <= "9"):
                return self.parse_number()

            for word, value in (
                ("true", True),
                ("false", False),
                ("null", None),
            ):
                if self.text.startswith(word, self.pos):
                    self.pos += len(word)
                    return True, value

            return False, None

        def parse_string(self):
            if self.pos >= self.length or self.text[self.pos] != '"':
                return False, None

            self.pos += 1
            chars = []

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
                    return True, "".join(chars)

                if ord(char) < 0x20:
                    return False, None

                if char != "\\":
                    chars.append(char)
                    continue

                if self.pos >= self.length:
                    return False, None

                escape = self.text[self.pos]
                self.pos += 1

                if escape in escapes:
                    chars.append(escapes[escape])
                    continue

                if escape != "u":
                    return False, None

                if self.pos + 4 > self.length:
                    return False, None

                digits = self.text[self.pos:self.pos + 4]
                if any(
                    digit not in "0123456789abcdefABCDEF"
                    for digit in digits
                ):
                    return False, None

                codepoint = int(digits, 16)
                self.pos += 4

                if 0xD800 <= codepoint <= 0xDBFF:
                    if (
                        self.pos + 6 <= self.length
                        and self.text[self.pos:self.pos + 2] == "\\u"
                    ):
                        low_digits = self.text[self.pos + 2:self.pos + 6]
                        if all(
                            digit in "0123456789abcdefABCDEF"
                            for digit in low_digits
                        ):
                            low = int(low_digits, 16)
                            if 0xDC00 <= low <= 0xDFFF:
                                codepoint = (
                                    0x10000
                                    + ((codepoint - 0xD800) << 10)
                                    + (low - 0xDC00)
                                )
                                self.pos += 6

                chars.append(chr(codepoint))

            return False, None

        def parse_number(self):
            start = self.pos

            if self.pos < self.length and self.text[self.pos] == "-":
                self.pos += 1

            if self.pos >= self.length:
                return False, None

            if self.text[self.pos] == "0":
                self.pos += 1
                if (
                    self.pos < self.length
                    and "0" <= self.text[self.pos] <= "9"
                ):
                    return False, None
            elif "1" <= self.text[self.pos] <= "9":
                while (
                    self.pos < self.length
                    and "0" <= self.text[self.pos] <= "9"
                ):
                    self.pos += 1
            else:
                return False, None

            is_float = False

            if self.pos < self.length and self.text[self.pos] == ".":
                is_float = True
                self.pos += 1
                fraction_start = self.pos

                while (
                    self.pos < self.length
                    and "0" <= self.text[self.pos] <= "9"
                ):
                    self.pos += 1

                if self.pos == fraction_start:
                    return False, None

            if self.pos < self.length and self.text[self.pos] in "eE":
                is_float = True
                self.pos += 1

                if (
                    self.pos < self.length
                    and self.text[self.pos] in "+-"
                ):
                    self.pos += 1

                exponent_start = self.pos
                while (
                    self.pos < self.length
                    and "0" <= self.text[self.pos] <= "9"
                ):
                    self.pos += 1

                if self.pos == exponent_start:
                    return False, None

            number_text = self.text[start:self.pos]
            try:
                return True, float(number_text) if is_float else int(number_text)
            except (ValueError, OverflowError):
                return False, None

        def parse_array(self):
            self.pos += 1
            result = []
            self.skip_whitespace()

            if self.pos < self.length and self.text[self.pos] == "]":
                self.pos += 1
                return True, result

            while True:
                ok, value = self.parse_value()
                if not ok:
                    return False, None
                result.append(value)

                self.skip_whitespace()
                if self.pos >= self.length:
                    return False, None

                if self.text[self.pos] == "]":
                    self.pos += 1
                    return True, result

                if self.text[self.pos] != ",":
                    return False, None

                self.pos += 1
                self.skip_whitespace()

                if self.pos < self.length and self.text[self.pos] == "]":
                    return False, None

        def parse_object(self):
            self.pos += 1
            result = {}
            self.skip_whitespace()

            if self.pos < self.length and self.text[self.pos] == "}":
                self.pos += 1
                return True, result

            while True:
                self.skip_whitespace()
                if self.pos >= self.length or self.text[self.pos] != '"':
                    return False, None

                ok, key = self.parse_string()
                if not ok:
                    return False, None

                self.skip_whitespace()
                if self.pos >= self.length or self.text[self.pos] != ":":
                    return False, None

                self.pos += 1
                ok, value = self.parse_value()
                if not ok:
                    return False, None
                result[key] = value

                self.skip_whitespace()
                if self.pos >= self.length:
                    return False, None

                if self.text[self.pos] == "}":
                    self.pos += 1
                    return True, result

                if self.text[self.pos] != ",":
                    return False, None

                self.pos += 1
                self.skip_whitespace()

                if self.pos < self.length and self.text[self.pos] == "}":
                    return False, None

    try:
        return Parser(text).parse_document()
    except (RecursionError, UnicodeError):
        return None
