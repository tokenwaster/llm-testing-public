class _JSONParseError(Exception):
    pass


class _Parser:
    _WS = " \t\n\r"
    _ESCAPE = {
        '"': '"',
        '\\': '\\',
        '/': '/',
        'b': '\b',
        'f': '\f',
        'n': '\n',
        'r': '\r',
        't': '\t',
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.n = len(text)

    def skip_ws(self) -> None:
        while self.pos < self.n and self.text[self.pos] in self._WS:
            self.pos += 1

    def parse_value(self):
        self.skip_ws()
        if self.pos >= self.n:
            raise _JSONParseError
        c = self.text[self.pos]
        if c == '{':
            return self.parse_object()
        if c == '[':
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == '-' or ('0' <= c <= '9'):
            return self.parse_number()
        if self.text.startswith('true', self.pos):
            self.pos += 4
            return True
        if self.text.startswith('false', self.pos):
            self.pos += 5
            return False
        if self.text.startswith('null', self.pos):
            self.pos += 4
            return None
        raise _JSONParseError

    def parse_string(self) -> str:
        t = self.text
        n = self.n
        i = self.pos
        if i >= n or t[i] != '"':
            raise _JSONParseError
        i += 1
        parts = []
        while i < n:
            c = t[i]
            if c == '"':
                i += 1
                self.pos = i
                return self._combine_surrogates(''.join(parts))
            if c == '\\':
                i += 1
                if i >= n:
                    raise _JSONParseError
                esc = t[i]
                if esc == 'u':
                    start = i + 1
                    end = start + 4
                    if end > n:
                        raise _JSONParseError
                    try:
                        code = int(t[start:end], 16)
                    except ValueError:
                        raise _JSONParseError
                    parts.append(chr(code))
                    i = end
                elif esc in self._ESCAPE:
                    parts.append(self._ESCAPE[esc])
                    i += 1
                else:
                    raise _JSONParseError
                continue
            if ord(c) < 32:
                raise _JSONParseError
            parts.append(c)
            i += 1
        raise _JSONParseError

    @staticmethod
    def _is_digit(c: str) -> bool:
        return '0' <= c <= '9'

    def parse_number(self):
        t = self.text
        n = self.n
        i = self.pos
        start = i
        is_float = False

        if t[i] == '-':
            i += 1
            if i >= n or not self._is_digit(t[i]):
                raise _JSONParseError

        first = t[i]
        if not self._is_digit(first):
            raise _JSONParseError
        if first == '0':
            i += 1
            if i < n and self._is_digit(t[i]):
                raise _JSONParseError
        else:
            i += 1
            while i < n and self._is_digit(t[i]):
                i += 1

        if i < n and t[i] == '.':
            is_float = True
            i += 1
            if i >= n or not self._is_digit(t[i]):
                raise _JSONParseError
            while i < n and self._is_digit(t[i]):
                i += 1

        if i < n and t[i] in ('e', 'E'):
            is_float = True
            i += 1
            if i < n and t[i] in ('+', '-'):
                i += 1
            if i >= n or not self._is_digit(t[i]):
                raise _JSONParseError
            while i < n and self._is_digit(t[i]):
                i += 1

        num_str = t[start:i]
        self.pos = i
        if is_float:
            return float(num_str)
        return int(num_str)

    def parse_array(self):
        t = self.text
        i = self.pos
        if i >= self.n or t[i] != '[':
            raise _JSONParseError
        i += 1
        self.pos = i
        self.skip_ws()
        result = []
        if self.pos < self.n and self.text[self.pos] == ']':
            self.pos += 1
            return result
        while True:
            value = self.parse_value()
            result.append(value)
            self.skip_ws()
            if self.pos >= self.n:
                raise _JSONParseError
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
                self.skip_ws()
                if self.pos < self.n and self.text[self.pos] == ']':
                    raise _JSONParseError
                continue
            if c == ']':
                self.pos += 1
                return result
            raise _JSONParseError

    def parse_object(self):
        t = self.text
        i = self.pos
        if i >= self.n or t[i] != '{':
            raise _JSONParseError
        i += 1
        self.pos = i
        self.skip_ws()
        result = {}
        if self.pos < self.n and self.text[self.pos] == '}':
            self.pos += 1
            return result
        while True:
            self.skip_ws()
            key = self.parse_string()
            self.skip_ws()
            if self.pos >= self.n or self.text[self.pos] != ':':
                raise _JSONParseError
            self.pos += 1
            value = self.parse_value()
            result[key] = value
            self.skip_ws()
            if self.pos >= self.n:
                raise _JSONParseError
            c = self.text[self.pos]
            if c == ',':
                self.pos += 1
                self.skip_ws()
                if self.pos < self.n and self.text[self.pos] == '}':
                    raise _JSONParseError
                continue
            if c == '}':
                self.pos += 1
                return result
            raise _JSONParseError

    @staticmethod
    def _combine_surrogates(s: str) -> str:
        res = []
        i = 0
        n = len(s)
        while i < n:
            cp = ord(s[i])
            if 0xD800 <= cp <= 0xDBFF and i + 1 < n:
                nxt = ord(s[i + 1])
                if 0xDC00 <= nxt <= 0xDFFF:
                    combined = 0x10000 + ((cp & 0x3FF) << 10) + (nxt & 0x3FF)
                    res.append(chr(combined))
                    i += 2
                    continue
            res.append(s[i])
            i += 1
        return ''.join(res)


def parse(text: str):
    if not isinstance(text, str):
        return None
    parser = _Parser(text)
    try:
        value = parser.parse_value()
        parser.skip_ws()
        if parser.pos != parser.n:
            return None
        return value
    except _JSONParseError:
        return None
