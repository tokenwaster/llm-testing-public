def parse(text):
    if not isinstance(text, str):
        return None
    parser = _JSONParser(text)
    try:
        result = parser._parse_value()
        parser._skip_ws()
        if parser._pos != len(parser._text):
            return None
        return result
    except _JSONError:
        return None


class _JSONError(Exception):
    pass


class _JSONParser:
    _DIGITS = '0123456789'
    _HEX = '0123456789abcdefABCDEF'
    _WS = ' \t\n\r'

    def __init__(self, text):
        self._text = text
        self._pos = 0
        self._n = len(text)

    def _peek(self):
        if self._pos >= self._n:
            raise _JSONError()
        return self._text[self._pos]

    def _expect(self, c):
        if self._pos >= self._n or self._text[self._pos] != c:
            raise _JSONError()
        self._pos += 1

    def _skip_ws(self):
        while self._pos < self._n and self._text[self._pos] in self._WS:
            self._pos += 1

    def _parse_value(self):
        self._skip_ws()
        c = self._peek()
        if c == '{':
            return self._parse_object()
        if c == '[':
            return self._parse_array()
        if c == '"':
            return self._parse_string()
        if c == 't':
            return self._parse_literal('true', True)
        if c == 'f':
            return self._parse_literal('false', False)
        if c == 'n':
            return self._parse_literal('null', None)
        if c == '-' or c in self._DIGITS:
            return self._parse_number()
        raise _JSONError()

    def _parse_literal(self, literal, value):
        end = self._pos + len(literal)
        if end > self._n or self._text[self._pos:end] != literal:
            raise _JSONError()
        self._pos = end
        return value

    def _parse_string(self):
        self._expect('"')
        out = []
        while self._pos < self._n:
            c = self._text[self._pos]
            if c == '"':
                self._pos += 1
                return ''.join(out)
            if c == '\\':
                self._pos += 1
                if self._pos >= self._n:
                    raise _JSONError()
                esc = self._text[self._pos]
                if esc == '"':
                    out.append('"')
                    self._pos += 1
                elif esc == '\\':
                    out.append('\\')
                    self._pos += 1
                elif esc == '/':
                    out.append('/')
                    self._pos += 1
                elif esc == 'b':
                    out.append('\b')
                    self._pos += 1
                elif esc == 'f':
                    out.append('\f')
                    self._pos += 1
                elif esc == 'n':
                    out.append('\n')
                    self._pos += 1
                elif esc == 'r':
                    out.append('\r')
                    self._pos += 1
                elif esc == 't':
                    out.append('\t')
                    self._pos += 1
                elif esc == 'u':
                    if self._pos + 4 >= self._n:
                        raise _JSONError()
                    hex_str = self._text[self._pos+1:self._pos+5]
                    for ch in hex_str:
                        if ch not in self._HEX:
                            raise _JSONError()
                    code = int(hex_str, 16)
                    self._pos += 4
                    # Surrogate pair handling
                    if 0xD800 <= code <= 0xDBFF:
                        if (self._pos + 6 < self._n
                                and self._text[self._pos+1] == '\\'
                                and self._text[self._pos+2] == 'u'):
                            hex_str2 = self._text[self._pos+3:self._pos+7]
                            if all(ch in self._HEX for ch in hex_str2):
                                code2 = int(hex_str2, 16)
                                if 0xDC00 <= code2 <= 0xDFFF:
                                    code = 0x10000 + (code - 0xD800) * 0x400 + (code2 - 0xDC00)
                                    self._pos += 6
                    out.append(chr(code))
                    self._pos += 1
                else:
                    raise _JSONError()
            else:
                if ord(c) < 0x20:
                    raise _JSONError()
                out.append(c)
                self._pos += 1
        raise _JSONError()

    def _parse_number(self):
        start = self._pos
        if self._text[self._pos] == '-':
            self._pos += 1
            if self._pos >= self._n:
                raise _JSONError()
        if self._text[self._pos] == '0':
            self._pos += 1
        elif self._text[self._pos] in self._DIGITS:
            while self._pos < self._n and self._text[self._pos] in self._DIGITS:
                self._pos += 1
        else:
            raise _JSONError()
        is_float = False
        if self._pos < self._n and self._text[self._pos] == '.':
            is_float = True
            self._pos += 1
            if self._pos >= self._n or self._text[self._pos] not in self._DIGITS:
                raise _JSONError()
            while self._pos < self._n and self._text[self._pos] in self._DIGITS:
                self._pos += 1
        if self._pos < self._n and self._text[self._pos] in 'eE':
            is_float = True
            self._pos += 1
            if self._pos < self._n and self._text[self._pos] in '+-':
                self._pos += 1
            if self._pos >= self._n or self._text[self._pos] not in self._DIGITS:
                raise _JSONError()
            while self._pos < self._n and self._text[self._pos] in self._DIGITS:
                self._pos += 1
        s = self._text[start:self._pos]
        if is_float:
            return float(s)
        return int(s)

    def _parse_object(self):
        self._expect('{')
        result = {}
        self._skip_ws()
        if self._pos < self._n and self._text[self._pos] == '}':
            self._pos += 1
            return result
        while True:
            self._skip_ws()
            if self._pos >= self._n or self._text[self._pos] != '"':
                raise _JSONError()
            key = self._parse_string()
            self._skip_ws()
            self._expect(':')
            value = self._parse_value()
            result[key] = value
            self._skip_ws()
            if self._pos >= self._n:
                raise _JSONError()
            ch = self._text[self._pos]
            if ch == ',':
                self._pos += 1
                continue
            if ch == '}':
                self._pos += 1
                return result
            raise _JSONError()

    def _parse_array(self):
        self._expect('[')
        result = []
        self._skip_ws()
        if self._pos < self._n and self._text[self._pos] == ']':
            self._pos += 1
            return result
        while True:
            value = self._parse_value()
            result.append(value)
            self._skip_ws()
            if self._pos >= self._n:
                raise _JSONError()
            ch = self._text[self._pos]
            if ch == ',':
                self._pos += 1
                continue
            if ch == ']':
                self._pos += 1
                return result
            raise _JSONError()
