def parse(text: str):
    class Parser:
        def __init__(self, source):
            self.source = source
            self.index = 0

        def whitespace(self):
            while self.index < len(self.source) and self.source[self.index] in " \t\r\n":
                self.index += 1

        def value(self):
            self.whitespace()
            if self.index >= len(self.source):
                raise ValueError

            char = self.source[self.index]

            if char == '"':
                return self.string()
            if char == "{":
                return self.object()
            if char == "[":
                return self.array()
            if self.source.startswith("true", self.index):
                self.index += 4
                return True
            if self.source.startswith("false", self.index):
                self.index += 5
                return False
            if self.source.startswith("null", self.index):
                self.index += 4
                return None
            if char == "-" or char.isdigit():
                return self.number()

            raise ValueError

        def string(self):
            self.index += 1
            result = []

            while self.index < len(self.source):
                char = self.source[self.index]
                self.index += 1

                if char == '"':
                    return "".join(result)

                if char == "\\":
                    if self.index >= len(self.source):
                        raise ValueError

                    escape = self.source[self.index]
                    self.index += 1

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
                        if self.index + 4 > len(self.source):
                            raise ValueError
                        digits = self.source[self.index:self.index + 4]
                        if any(digit not in "0123456789abcdefABCDEF" for digit in digits):
                            raise ValueError
                        result.append(chr(int(digits, 16)))
                        self.index += 4
                    else:
                        raise ValueError
                else:
                    if ord(char) < 0x20:
                        raise ValueError
                    result.append(char)

            raise ValueError

        def number(self):
            start = self.index

            if self.source[self.index] == "-":
                self.index += 1
                if self.index >= len(self.source):
                    raise ValueError

            if self.source[self.index] == "0":
                self.index += 1
                if self.index < len(self.source) and self.source[self.index].isdigit():
                    raise ValueError
            elif self.source[self.index] in "123456789":
                while self.index < len(self.source) and self.source[self.index].isdigit():
                    self.index += 1
            else:
                raise ValueError

            is_float = False

            if self.index < len(self.source) and self.source[self.index] == ".":
                is_float = True
                self.index += 1
                fraction_start = self.index
                while self.index < len(self.source) and self.source[self.index].isdigit():
                    self.index += 1
                if self.index == fraction_start:
                    raise ValueError

            if self.index < len(self.source) and self.source[self.index] in "eE":
                is_float = True
                self.index += 1

                if self.index < len(self.source) and self.source[self.index] in "+-":
                    self.index += 1

                exponent_start = self.index
                while self.index < len(self.source) and self.source[self.index].isdigit():
                    self.index += 1
                if self.index == exponent_start:
                    raise ValueError

            number_text = self.source[start:self.index]
            return float(number_text) if is_float else int(number_text)

        def array(self):
            self.index += 1
            result = []
            self.whitespace()

            if self.index < len(self.source) and self.source[self.index] == "]":
                self.index += 1
                return result

            while True:
                result.append(self.value())
                self.whitespace()

                if self.index >= len(self.source):
                    raise ValueError
                if self.source[self.index] == "]":
                    self.index += 1
                    return result
                if self.source[self.index] != ",":
                    raise ValueError

                self.index += 1
                self.whitespace()
                if self.index < len(self.source) and self.source[self.index] == "]":
                    raise ValueError

        def object(self):
            self.index += 1
            result = {}
            self.whitespace()

            if self.index < len(self.source) and self.source[self.index] == "}":
                self.index += 1
                return result

            while True:
                self.whitespace()
                if self.index >= len(self.source) or self.source[self.index] != '"':
                    raise ValueError

                key = self.string()
                self.whitespace()

                if self.index >= len(self.source) or self.source[self.index] != ":":
                    raise ValueError

                self.index += 1
                result[key] = self.value()
                self.whitespace()

                if self.index >= len(self.source):
                    raise ValueError
                if self.source[self.index] == "}":
                    self.index += 1
                    return result
                if self.source[self.index] != ",":
                    raise ValueError

                self.index += 1
                self.whitespace()
                if self.index < len(self.source) and self.source[self.index] == "}":
                    raise ValueError

    try:
        parser = Parser(text)
        result = parser.value()
        parser.whitespace()

        if parser.index != len(text):
            return None
        return result
    except (ValueError, TypeError, OverflowError, RecursionError):
        return None
