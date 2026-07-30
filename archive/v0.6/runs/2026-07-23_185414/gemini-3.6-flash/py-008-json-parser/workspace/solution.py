import re


class ParseError(Exception):
    pass


NUMBER_RE = re.compile(r'-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?')


class JSONParser:
    def __init__(self, text: str):
        self.text = text
        self.len = len(text)
        self.idx = 0

    def parse(self):
        try:
            self.skip_ws()
            if self.idx >= self.len:
                raise ParseError()
            val = self.parse_value()
            self.skip_ws()
            if self.idx != self.len:
                raise ParseError()
            return val
        except ParseError:
            return None

    def skip_ws(self):
        while self.idx < self.len and self.text[self.idx] in ' \t\n\r':
            self.idx += 1

    def peek(self):
        if self.idx < self.len:
            return self.text[self.idx]
        return None

    def parse_value(self):
        ch = self.peek()
        if ch is None:
            raise ParseError()
        if ch == '"':
            return self.parse_string()
        elif ch == '{':
            return self.parse_object()
        elif ch == '[':
            return self.parse_array()
        elif ch in 'tfn':
            return self.parse_literal()
        elif ch == '-' or ch.isdigit():
            return self.parse_number()
        else:
            raise ParseError()

    def parse_literal(self):
        if self.text.startswith('true', self.idx):
            self.idx += 4
            return True
        elif self.text.startswith('false', self.idx):
            self.idx += 5
            return False
        elif self.text.startswith('null', self.idx):
            self.idx += 4
            return None
        else:
            raise ParseError()

    def parse_number(self):
        match = NUMBER_RE.match(self.text, self.idx)
        if not match:
            raise ParseError()
        num_str = match.group(0)
        self.idx += len(num_str)
        if '.' in num_str or 'e' in num_str or 'E' in num_str:
            return float(num_str)
        else:
            return int(num_str)

    def parse_string(self):
        if self.idx >= self.len or self.text[self.idx] != '"':
            raise ParseError()
        self.idx += 1
        chars = []

        while self.idx < self.len:
            ch = self.text[self.idx]
            if ch == '"':
                self.idx += 1
                return "".join(chars)
            elif ch == '\\':
                self.idx += 1
                if self.idx >= self.len:
                    raise ParseError()
                esc = self.text[self.idx]
                if esc == '"':
                    chars.append('"')
                elif esc == '\\':
                    chars.append('\\')
                elif esc == '/':
                    chars.append('/')
                elif esc == 'b':
                    chars.append('\b')
                elif esc == 'f':
                    chars.append('\f')
                elif esc == 'n':
                    chars.append('\n')
                elif esc == 'r':
                    chars.append('\r')
                elif esc == 't':
                    chars.append('\t')
                elif esc == 'u':
                    if self.idx + 4 >= self.len:
                        raise ParseError()
                    hex_str = self.text[self.idx + 1 : self.idx + 5]
                    if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                        raise ParseError()
                    val = int(hex_str, 16)
                    self.idx += 4

                    if 0xD800 <= val <= 0xDBFF:
                        if (
                            self.idx + 6 < self.len
                            and self.text[self.idx + 1] == '\\'
                            and self.text[self.idx + 2] == 'u'
                        ):
                            hex_str2 = self.text[self.idx + 3 : self.idx + 7]
                            if all(
                                c in '0123456789abcdefABCDEF' for c in hex_str2
                            ):
                                val2 = int(hex_str2, 16)
                                if 0xDC00 <= val2 <= 0xDFFF:
                                    val = (
                                        0x10000
                                        + ((val - 0xD800) << 10)
                                        + (val2 - 0xDC00)
                                    )
                                    self.idx += 6
                    chars.append(chr(val))
                else:
                    raise ParseError()
                self.idx += 1
            else:
                if ord(ch) < 0x20:
                    raise ParseError()
                chars.append(ch)
                self.idx += 1

        raise ParseError()

    def parse_array(self):
        if self.idx >= self.len or self.text[self.idx] != '[':
            raise ParseError()
        self.idx += 1
        self.skip_ws()

        res = []
        if self.idx < self.len and self.text[self.idx] == ']':
            self.idx += 1
            return res

        while True:
            val = self.parse_value()
            res.append(val)
            self.skip_ws()
            if self.idx >= self.len:
                raise ParseError()
            ch = self.text[self.idx]
            if ch == ']':
                self.idx += 1
                return res
            elif ch == ',':
                self.idx += 1
                self.skip_ws()
                if self.idx < self.len and self.text[self.idx] == ']':
                    raise ParseError()
            else:
                raise ParseError()

    def parse_object(self):
        if self.idx >= self.len or self.text[self.idx] != '{':
            raise ParseError()
        self.idx += 1
        self.skip_ws()

        res = {}
        if self.idx < self.len and self.text[self.idx] == '}':
            self.idx += 1
            return res

        while True:
            if self.idx >= self.len or self.text[self.idx] != '"':
                raise ParseError()
            key = self.parse_string()
            self.skip_ws()
            if self.idx >= self.len or self.text[self.idx] != ':':
                raise ParseError()
            self.idx += 1
            self.skip_ws()
            val = self.parse_value()
            res[key] = val
            self.skip_ws()
            if self.idx >= self.len:
                raise ParseError()
            ch = self.text[self.idx]
            if ch == '}':
                self.idx += 1
                return res
            elif ch == ',':
                self.idx += 1
                self.skip_ws()
                if self.idx < self.len and self.text[self.idx] == '}':
                    raise ParseError()
            else:
                raise ParseError()


def parse(text: str):
    if not isinstance(text, str):
        return None
    return JSONParser(text).parse()
