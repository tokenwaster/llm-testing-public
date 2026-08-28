def parse(text: str):
    if not isinstance(text, str):
        return None

    class Parser:
        def __init__(self, source):
            self.s = source
            self.i = 0
            self.n = len(source)

        def whitespace(self):
            while self.i < self.n and self.s[self.i] in " \t\r\n":
                self.i += 1

        def value(self):
            self.whitespace()
            if self.i >= self.n:
                raise ValueError

            ch = self.s[self.i]
            if ch == '"':
                return self.string()
            if ch == "{":
                return self.object()
            if ch == "[":
                return self.array()
            if ch == "-" or ch.isdigit():
                return self.number()
            if self.s.startswith("true", self.i):
                self.i += 4
                return True
            if self.s.startswith("false", self.i):
                self.i += 5
                return False
            if self.s.startswith("null", self.i):
                self.i += 4
                return None
            raise ValueError

        def string(self):
            self.i += 1
            result = []

            while self.i < self.n:
                ch = self.s[self.i]
                self.i += 1

                if ch == '"':
                    return "".join(result)
                if ord(ch) < 0x20:
                    raise ValueError

                if ch != "\\":
                    result.append(ch)
                    continue

                if self.i >= self.n:
                    raise ValueError
                esc = self.s[self.i]
                self.i += 1
                escapes = {
                    '"': '"', "\\": "\\", "/": "/",
                    "b": "\b", "f": "\f", "n": "\n",
                    "r": "\r", "t": "\t",
                }
                if esc in escapes:
                    result.append(escapes[esc])
                elif esc == "u":
                    result.append(self.unicode_escape())
                else:
                    raise ValueError

            raise ValueError

        def unicode_escape(self):
            if self.i + 4 > self.n:
                raise ValueError
            digits = self.s[self.i:self.i + 4]
            if any(ch not in "0123456789abcdefABCDEF" for ch in digits):
                raise ValueError
            self.i += 4
            code = int(digits, 16)

            if 0xD800 <= code <= 0xDBFF:
                if not self.s.startswith("\\u", self.i):
                    raise ValueError
                self.i += 2
                if self.i + 4 > self.n:
                    raise ValueError
                low_digits = self.s[self.i:self.i + 4]
                if any(ch not in "0123456789abcdefABCDEF" for ch in low_digits):
                    raise ValueError
                self.i += 4
                low = int(low_digits, 16)
                if not 0xDC00 <= low <= 0xDFFF:
                    raise ValueError
                code = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
            elif 0xDC00 <= code <= 0xDFFF:
                raise ValueError

            return chr(code)

        def number(self):
            start = self.i

            if self.s[self.i] == "-":
                self.i += 1
                if self.i >= self.n:
                    raise ValueError

            if self.i >= self.n or not self.s[self.i].isdigit():
                raise ValueError

            if self.s[self.i] == "0":
                self.i += 1
                if self.i < self.n and self.s[self.i].isdigit():
                    raise ValueError
            else:
                while self.i < self.n and self.s[self.i].isdigit():
                    self.i += 1

            is_float = False
            if self.i < self.n and self.s[self.i] == ".":
                is_float = True
                self.i += 1
                digit_start = self.i
                while self.i < self.n and self.s[self.i].isdigit():
                    self.i += 1
                if self.i == digit_start:
                    raise ValueError

            if self.i < self.n and self.s[self.i] in "eE":
                is_float = True
                self.i += 1
                if self.i < self.n and self.s[self.i] in "+-":
                    self.i += 1
                digit_start = self.i
                while self.i < self.n and self.s[self.i].isdigit():
                    self.i += 1
                if self.i == digit_start:
                    raise ValueError

            token = self.s[start:self.i]
            return float(token) if is_float else int(token)

        def array(self):
            self.i += 1
            result = []
            self.whitespace()

            if self.i < self.n and self.s[self.i] == "]":
                self.i += 1
                return result

            while True:
                result.append(self.value())
                self.whitespace()
                if self.i >= self.n:
                    raise ValueError
                if self.s[self.i] == "]":
                    self.i += 1
                    return result
                if self.s[self.i] != ",":
                    raise ValueError
                self.i += 1
                self.whitespace()
                if self.i >= self.n or self.s[self.i] == "]":
                    raise ValueError

        def object(self):
            self.i += 1
            result = {}
            self.whitespace()

            if self.i < self.n and self.s[self.i] == "}":
                self.i += 1
                return result

            while True:
                self.whitespace()
                if self.i >= self.n or self.s[self.i] != '"':
                    raise ValueError
                key = self.string()

                self.whitespace()
                if self.i >= self.n or self.s[self.i] != ":":
                    raise ValueError
                self.i += 1

                result[key] = self.value()
                self.whitespace()
                if self.i >= self.n:
                    raise ValueError
                if self.s[self.i] == "}":
                    self.i += 1
                    return result
                if self.s[self.i] != ",":
                    raise ValueError
                self.i += 1
                self.whitespace()
                if self.i >= self.n or self.s[self.i] == "}":
                    raise ValueError

    try:
        parser = Parser(text)
        result = parser.value()
        parser.whitespace()
        return result if parser.i == parser.n else None
    except (ValueError, OverflowError):
        return None
