class JSONParseError(Exception):
    pass


class JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.length = len(text)
        self.pos = 0

    def skip_ws(self):
        while self.pos < self.length and self.text[self.pos] in " \t\n\r":
            self.pos += 1

    def parse(self):
        self.skip_ws()
        if self.pos >= self.length:
            return None
        try:
            val = self.parse_value()
            self.skip_ws()
            if self.pos != self.length:
                return None
            return val
        except JSONParseError:
            return None

    def parse_value(self):
        self.skip_ws()
        if self.pos >= self.length:
            raise JSONParseError("Unexpected EOF")
        ch = self.text[self.pos]
        if ch == '"':
            return self.parse_string()
        elif ch == "{":
            return self.parse_object()
        elif ch == "[":
            return self.parse_array()
        elif ch == "t":
            return self.parse_true()
        elif ch == "f":
            return self.parse_false()
        elif ch == "n":
            return self.parse_null()
        elif ch == "-" or ch.isdigit():
            return self.parse_number()
        else:
            raise JSONParseError(f"Unexpected character: {ch!r}")

    def parse_true(self):
        if self.text.startswith("true", self.pos):
            self.pos += 4
            return True
        raise JSONParseError("Expected 'true'")

    def parse_false(self):
        if self.text.startswith("false", self.pos):
            self.pos += 5
            return False
        raise JSONParseError("Expected 'false'")

    def parse_null(self):
        if self.text.startswith("null", self.pos):
            self.pos += 4
            return None
        raise JSONParseError("Expected 'null'")

    def parse_string(self):
        if self.text[self.pos] != '"':
            raise JSONParseError("Expected '\"'")
        self.pos += 1
        res = []
        while self.pos < self.length:
            ch = self.text[self.pos]
            if ch == '"':
                self.pos += 1
                return "".join(res)
            elif ch == "\\":
                self.pos += 1
                if self.pos >= self.length:
                    raise JSONParseError("Unterminated escape sequence")
                esc = self.text[self.pos]
                self.pos += 1
                if esc == '"':
                    res.append('"')
                elif esc == "\\":
                    res.append("\\")
                elif esc == "/":
                    res.append("/")
                elif esc == "b":
                    res.append("\b")
                elif esc == "f":
                    res.append("\f")
                elif esc == "n":
                    res.append("\n")
                elif esc == "r":
                    res.append("\r")
                elif esc == "t":
                    res.append("\t")
                elif esc == "u":
                    if self.pos + 4 > self.length:
                        raise JSONParseError("Incomplete unicode escape")
                    hex_str = self.text[self.pos : self.pos + 4]
                    if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
                        raise JSONParseError("Invalid hex in unicode escape")
                    self.pos += 4
                    code_point = int(hex_str, 16)

                    # Handle UTF-16 surrogate pairs
                    if 0xD800 <= code_point <= 0xDBFF:
                        if (
                            self.pos + 6 <= self.length
                            and self.text[self.pos : self.pos + 2] == "\\u"
                        ):
                            hex_str2 = self.text[self.pos + 2 : self.pos + 6]
                            if all(
                                c in "0123456789abcdefABCDEF" for c in hex_str2
                            ):
                                code_point2 = int(hex_str2, 16)
                                if 0xDC00 <= code_point2 <= 0xDFFF:
                                    self.pos += 6
                                    code_point = (
                                        0x10000
                                        + ((code_point - 0xD800) << 10)
                                        + (code_point2 - 0xDC00)
                                    )
                    res.append(chr(code_point))
                else:
                    raise JSONParseError(f"Invalid escape sequence '\\{esc}'")
            else:
                if ord(ch) < 0x20:
                    raise JSONParseError("Unescaped control character")
                res.append(ch)
                self.pos += 1
        raise JSONParseError("Unterminated string")

    def parse_number(self):
        start = self.pos
        if self.text[self.pos] == "-":
            self.pos += 1
            if self.pos >= self.length:
                raise JSONParseError("Unexpected end after '-'")

        if self.text[self.pos] == "0":
            self.pos += 1
            if self.pos < self.length and self.text[self.pos].isdigit():
                raise JSONParseError("Leading zero not allowed")
        elif "1" <= self.text[self.pos] <= "9":
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise JSONParseError("Expected digit in number")

        is_float = False

        if self.pos < self.length and self.text[self.pos] == ".":
            is_float = True
            self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise JSONParseError("Expected digit after decimal point")
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

        if self.pos < self.length and self.text[self.pos] in "eE":
            is_float = True
            self.pos += 1
            if self.pos < self.length and self.text[self.pos] in "+-":
                self.pos += 1
            if self.pos >= self.length or not self.text[self.pos].isdigit():
                raise JSONParseError("Expected digit in exponent")
            while self.pos < self.length and self.text[self.pos].isdigit():
                self.pos += 1

        num_str = self.text[start : self.pos]
        if is_float:
            return float(num_str)
        else:
            return int(num_str)

    def parse_array(self):
        if self.text[self.pos] != "[":
            raise JSONParseError("Expected '['")
        self.pos += 1
        self.skip_ws()
        res = []
        if self.pos < self.length and self.text[self.pos] == "]":
            self.pos += 1
            return res

        while True:
            val = self.parse_value()
            res.append(val)
            self.skip_ws()
            if self.pos >= self.length:
                raise JSONParseError("Unterminated array")
            if self.text[self.pos] == "]":
                self.pos += 1
                return res
            elif self.text[self.pos] == ",":
                self.pos += 1
                self.skip_ws()
                if self.pos < self.length and self.text[self.pos] == "]":
                    raise JSONParseError("Trailing comma in array")
            else:
                raise JSONParseError("Expected ',' or ']' in array")

    def parse_object(self):
        if self.text[self.pos] != "{":
            raise JSONParseError("Expected '{'")
        self.pos += 1
        self.skip_ws()
        res = {}
        if self.pos < self.length and self.text[self.pos] == "}":
            self.pos += 1
            return res

        while True:
            self.skip_ws()
            if self.pos >= self.length or self.text[self.pos] != '"':
                raise JSONParseError("Expected string key in object")
            key = self.parse_string()
            self.skip_ws()
            if self.pos >= self.length or self.text[self.pos] != ":":
                raise JSONParseError("Expected ':' after key in object")
            self.pos += 1
            val = self.parse_value()
            res[key] = val
            self.skip_ws()
            if self.pos >= self.length:
                raise JSONParseError("Unterminated object")
            if self.text[self.pos] == "}":
                self.pos += 1
                return res
            elif self.text[self.pos] == ",":
                self.pos += 1
                self.skip_ws()
                if self.pos < self.length and self.text[self.pos] == "}":
                    raise JSONParseError("Trailing comma in object")
            else:
                raise JSONParseError("Expected ',' or '}' in object")


def parse(text: str):
    if not isinstance(text, str):
        return None
    return JSONParser(text).parse()
