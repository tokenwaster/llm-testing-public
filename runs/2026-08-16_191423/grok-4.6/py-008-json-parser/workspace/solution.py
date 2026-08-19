class _ParseError(Exception):
    pass


class _Parser:
    def __init__(self, text):
        self.text = text
        self.n = len(text)
        self.pos = 0

    def peek(self):
        if self.pos < self.n:
            return self.text[self.pos]
        return None

    def skip_ws(self):
        while self.pos < self.n and self.text[self.pos] in " \t\n\r":
            self.pos += 1

    def parse_value(self):
        self.skip_ws()
        c = self.peek()
        if c is None:
            raise _ParseError()
        if c == "{":
            return self.parse_object()
        if c == "[":
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == "t":
            return self.parse_literal("true", True)
        if c == "f":
            return self.parse_literal("false", False)
        if c == "n":
            return self.parse_literal("null", None)
        if c == "-" or c.isdigit():
            return self.parse_number()
        raise _ParseError()

    def parse_literal(self, lit, value):
        end = self.pos + len(lit)
        if self.text[self.pos:end] != lit:
            raise _ParseError()
        self.pos = end
        return value

    def parse_object(self):
        self.pos += 1
        self.skip_ws()
        obj = {}
        if self.peek() == "}":
            self.pos += 1
            return obj
        while True:
            self.skip_ws()
            if self.peek() != '"':
                raise _ParseError()
            key = self.parse_string()
            self.skip_ws()
            if self.peek() != ":":
                raise _ParseError()
            self.pos += 1
            obj[key] = self.parse_value()
            self.skip_ws()
            c = self.peek()
            if c == ",":
                self.pos += 1
                self.skip_ws()
                if self.peek() == "}":
                    raise _ParseError()
                continue
            if c == "}":
                self.pos += 1
                return obj
            raise _ParseError()

    def parse_array(self):
        self.pos += 1
        self.skip_ws()
        arr = []
        if self.peek() == "]":
            self.pos += 1
            return arr
        while True:
            arr.append(self.parse_value())
            self.skip_ws()
            c = self.peek()
            if c == ",":
                self.pos += 1
                self.skip_ws()
                if self.peek() == "]":
                    raise _ParseError()
                continue
            if c == "]":
                self.pos += 1
                return arr
            raise _ParseError()

    def parse_hex4(self):
        if self.pos + 4 > self.n:
            raise _ParseError()
        hexd = self.text[self.pos:self.pos + 4]
        for ch in hexd:
            if ch not in "0123456789abcdefABCDEF":
                raise _ParseError()
        self.pos += 4
        return int(hexd, 16)

    def parse_string(self):
        self.pos += 1
        out = []
        while self.pos < self.n:
            c = self.text[self.pos]
            if c == '"':
                self.pos += 1
                return "".join(out)
            if c == "\\":
                self.pos += 1
                if self.pos >= self.n:
                    raise _ParseError()
                e = self.text[self.pos]
                mapping = {
                    '"': '"',
                    "\\": "\\",
                    "/": "/",
                    "b": "\b",
                    "f": "\f",
                    "n": "\n",
                    "r": "\r",
                    "t": "\t",
                }
                if e in mapping:
                    out.append(mapping[e])
                    self.pos += 1
                elif e == "u":
                    self.pos += 1
                    code = self.parse_hex4()
                    if 0xD800 <= code <= 0xDBFF:
                        if (
                            self.pos + 6 <= self.n
                            and self.text[self.pos:self.pos + 2] == "\\u"
                        ):
                            saved = self.pos
                            self.pos += 2
                            try:
                                low = self.parse_hex4()
                            except _ParseError:
                                self.pos = saved
                            else:
                                if 0xDC00 <= low <= 0xDFFF:
                                    code = (
                                        0x10000
                                        + ((code - 0xD800) << 10)
                                        + (low - 0xDC00)
                                    )
                                else:
                                    self.pos = saved
                    out.append(chr(code))
                else:
                    raise _ParseError()
            else:
                if ord(c) < 0x20:
                    raise _ParseError()
                out.append(c)
                self.pos += 1
        raise _ParseError()

    def parse_number(self):
        start = self.pos
        if self.peek() == "-":
            self.pos += 1
        c = self.peek()
        if c is None or not c.isdigit():
            raise _ParseError()
        if c == "0":
            self.pos += 1
            nxt = self.peek()
            if nxt is not None and nxt.isdigit():
                raise _ParseError()
        else:
            while True:
                nxt = self.peek()
                if nxt is None or not nxt.isdigit():
                    break
                self.pos += 1
        is_float = False
        if self.peek() == ".":
            is_float = True
            self.pos += 1
            nxt = self.peek()
            if nxt is None or not nxt.isdigit():
                raise _ParseError()
            while True:
                nxt = self.peek()
                if nxt is None or not nxt.isdigit():
                    break
                self.pos += 1
        if self.peek() in ("e", "E"):
            is_float = True
            self.pos += 1
            if self.peek() in ("+", "-"):
                self.pos += 1
            nxt = self.peek()
            if nxt is None or not nxt.isdigit():
                raise _ParseError()
            while True:
                nxt = self.peek()
                if nxt is None or not nxt.isdigit():
                    break
                self.pos += 1
        raw = self.text[start:self.pos]
        if is_float:
            return float(raw)
        return int(raw)


def parse(text: str):
    if not isinstance(text, str):
        return None
    try:
        p = _Parser(text)
        result = p.parse_value()
        p.skip_ws()
        if p.pos != p.n:
            return None
        return result
    except _ParseError:
        return None
