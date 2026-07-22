def parse(text: str):
    if not isinstance(text, str):
        return None

    class ParseError(Exception):
        pass

    class Parser:
        def __init__(self, source):
            self.source = source
            self.length = len(source)
            self.pos = 0

        def skip_whitespace(self):
            while self.pos < self.length and self.source[self.pos] in " \t\r\n":
                self.pos += 1

        def parse_value(self):
            self.skip_whitespace()

            if self.pos >= self.length:
                raise ParseError

            ch = self.source[self.pos]

            if ch == '"':
                return self.parse_string()
            if ch == "{":
                return self.parse_object()
            if ch == "[":
                return self.parse_array()
            if ch == "t":
                return self.parse_literal("true", True)
            if ch == "f":
                return self.parse_literal("false", False)
            if ch == "n":
                return self.parse_literal("null", None)
            if ch == "-" or ch.isdigit():
                return self.parse_number()

            raise ParseError

        def parse_literal(self, literal, value):
            if self.source.startswith(literal, self.pos):
                self.pos += len(literal)
                return value
            raise ParseError

        def parse_string(self):
            if self.source[self.pos] != '"':
                raise ParseError

            self.pos += 1
            result = []

            while self.pos < self.length:
                ch = self.source[self.pos]
                self.pos += 1

                if ch == '"':
                    return "".join(result)

                if ord(ch) < 0x20:
                    raise ParseError

                if ch != "\\":
                    result.append(ch)
                    continue

                if self.pos >= self.length:
                    raise ParseError

                escape = self.source[self.pos]
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
                    raise ParseError

                code_unit = self.parse_unicode_escape()

                if (
                    0xD800 <= code_unit <= 0xDBFF
                    and self.pos + 6 <= self.length
                    and self.source[self.pos:self.pos + 2] == "\\u"
                ):
                    saved_pos = self.pos
                    self.pos += 2
                    try:
                        low = self.parse_unicode_escape()
                    except ParseError:
                        self.pos = saved_pos
                        result.append(chr(code_unit))
                        continue

                    if 0xDC00 <= low <= 0xDFFF:
                        codepoint = 0x10000 + ((code_unit - 0xD800) << 10) + (low - 0xDC00)
                        result.append(chr(codepoint))
                    else:
                        self.pos = saved_pos
                        result.append(chr(code_unit))
                else:
                    result.append(chr(code_unit))

            raise ParseError

        def parse_unicode_escape(self):
            if self.pos + 4 > self.length:
                raise ParseError

            digits = self.source[self.pos:self.pos + 4]
            if any(ch not in "0123456789abcdefABCDEF" for ch in digits):
                raise ParseError

            self.pos += 4
            return int(digits, 16)

        def parse_number(self):
            start = self.pos

            if self.source[self.pos] == "-":
                self.pos += 1
                if self.pos >= self.length:
                    raise ParseError

            if self.pos >= self.length:
                raise ParseError

            if self.source[self.pos] == "0":
                self.pos += 1
                if self.pos < self.length and self.source[self.pos].isdigit():
                    raise ParseError
            elif "1" <= self.source[self.pos] <= "9":
                while self.pos < self.length and self.source[self.pos].isdigit():
                    self.pos += 1
            else:
                raise ParseError

            is_float = False

            if self.pos < self.length and self.source[self.pos] == ".":
                is_float = True
                self.pos += 1

                if self.pos >= self.length or not self.source[self.pos].isdigit():
                    raise ParseError

                while self.pos < self.length and self.source[self.pos].isdigit():
                    self.pos += 1

            if self.pos < self.length and self.source[self.pos] in "eE":
                is_float = True
                self.pos += 1

                if self.pos < self.length and self.source[self.pos] in "+-":
                    self.pos += 1

                if self.pos >= self.length or not self.source[self.pos].isdigit():
                    raise ParseError

                while self.pos < self.length and self.source[self.pos].isdigit():
                    self.pos += 1

            number = self.source[start:self.pos]

            try:
                return float(number) if is_float else int(number)
            except (ValueError, OverflowError):
                raise ParseError

        def parse_array(self):
            self.pos += 1
            result = []

            self.skip_whitespace()
            if self.pos < self.length and self.source[self.pos] == "]":
                self.pos += 1
                return result

            while True:
                result.append(self.parse_value())
                self.skip_whitespace()

                if self.pos >= self.length:
                    raise ParseError

                if self.source[self.pos] == "]":
                    self.pos += 1
                    return result

                if self.source[self.pos] != ",":
                    raise ParseError

                self.pos += 1
                self.skip_whitespace()

        def parse_object(self):
            self.pos += 1
            result = {}

            self.skip_whitespace()
            if self.pos < self.length and self.source[self.pos] == "}":
                self.pos += 1
                return result

            while True:
                self.skip_whitespace()

                if self.pos >= self.length or self.source[self.pos] != '"':
                    raise ParseError

                key = self.parse_string()
                self.skip_whitespace()

                if self.pos >= self.length or self.source[self.pos] != ":":
                    raise ParseError

                self.pos += 1
                value = self.parse_value()
                result[key] = value

                self.skip_whitespace()

                if self.pos >= self.length:
                    raise ParseError

                if self.source[self.pos] == "}":
                    self.pos += 1
                    return result

                if self.source[self.pos] != ",":
                    raise ParseError

                self.pos += 1
                self.skip_whitespace()

    try:
        parser = Parser(text)
        value = parser.parse_value()
        parser.skip_whitespace()

        if parser.pos != parser.length:
            return None

        return value
    except (ParseError, RecursionError, ValueError, OverflowError):
        return None
