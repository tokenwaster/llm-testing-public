class _JSONParseError(Exception):
    pass


class _Parser:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    def skip_whitespace(self):
        while self.pos < self.length and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def parse_document(self):
        self.skip_whitespace()
        value = self.parse_value()
        self.skip_whitespace()
        if self.pos != self.length:
            raise _JSONParseError
        return value

    def parse_value(self):
        self.skip_whitespace()

        if self.pos >= self.length:
            raise _JSONParseError

        ch = self.text[self.pos]

        if ch == '"':
            return self.parse_string()
        if ch == "{":
            return self.parse_object()
        if ch == "[":
            return self.parse_array()
        if ch == "-" or ch.isdigit():
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

        raise _JSONParseError

    def parse_string(self):
        if self.text[self.pos] != '"':
            raise _JSONParseError

        self.pos += 1
        result = []

        while self.pos < self.length:
            ch = self.text[self.pos]
            self.pos += 1

            if ch == '"':
                return "".join(result)

            if ord(ch) < 0x20:
                raise _JSONParseError

            if ch != "\\":
                result.append(ch)
                continue

            if self.pos >= self.length:
                raise _JSONParseError

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
            elif escape == "u":
                code_unit = self.parse_unicode_escape()

                # Combine valid UTF-16 surrogate pairs into one Python character.
                if 0xD800 <= code_unit <= 0xDBFF:
                    saved_pos = self.pos
                    if (
                        self.pos + 6 <= self.length
                        and self.text[self.pos] == "\\"
                        and self.text[self.pos + 1] == "u"
                    ):
                        self.pos += 2
                        try:
                            low_surrogate = self.parse_unicode_escape()
                        except _JSONParseError:
                            self.pos = saved_pos
                            result.append(chr(code_unit))
                            continue

                        if 0xDC00 <= low_surrogate <= 0xDFFF:
                            codepoint = (
                                0x10000
                                + ((code_unit - 0xD800) << 10)
                                + (low_surrogate - 0xDC00)
                            )
                            result.append(chr(codepoint))
                        else:
                            self.pos = saved_pos
                            result.append(chr(code_unit))
                    else:
                        result.append(chr(code_unit))
                else:
                    result.append(chr(code_unit))
            else:
                raise _JSONParseError

        raise _JSONParseError

    def parse_unicode_escape(self):
        if self.pos + 4 > self.length:
            raise _JSONParseError

        digits = self.text[self.pos:self.pos + 4]
        if any(ch not in "0123456789abcdefABCDEF" for ch in digits):
            raise _JSONParseError

        self.pos += 4
        return int(digits, 16)

    def parse_number(self):
        start = self.pos

        if self.text[self.pos] == "-":
            self.pos += 1
            if self.pos >= self.length:
                raise _JSONParseError

        if self.pos >= self.length:
            raise _JSONParseError

        if self.text[self.pos] == "0":
            self.pos += 1
            if self.pos < self.length and self.text[self.pos].isdigit():
                raise _JSONParseError
        elif self.text[self.pos] in "123456789":
            self.pos += 1
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise _JSONParseError

        is_float = False

        if self.pos < self.length and self.text[self.pos] == ".":
            is_float = True
            self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise _JSONParseError
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

        if self.pos < self.length and self.text[self.pos] in "eE":
            is_float = True
            self.pos += 1

            if self.pos < self.length and self.text[self.pos] in "+-":
                self.pos += 1

            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise _JSONParseError

            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

        number_text = self.text[start:self.pos]
        return float(number_text) if is_float else int(number_text)

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
                raise _JSONParseError

            if self.text[self.pos] == "]":
                self.pos += 1
                return result

            if self.text[self.pos] != ",":
                raise _JSONParseError

            self.pos += 1
            self.skip_whitespace()

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
                raise _JSONParseError

            key = self.parse_string()
            self.skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] != ":":
                raise _JSONParseError

            self.pos += 1
            value = self.parse_value()
            result[key] = value

            self.skip_whitespace()
            if self.pos >= self.length:
                raise _JSONParseError

            if self.text[self.pos] == "}":
                self.pos += 1
                return result

            if self.text[self.pos] != ",":
                raise _JSONParseError

            self.pos += 1
            self.skip_whitespace()


def parse(text: str):
    try:
        if not isinstance(text, str):
            return None
        return _Parser(text).parse_document()
    except (ValueError, OverflowError, _JSONParseError):
        return None
