class _InvalidJSON(Exception):
    pass


_ESCAPES = {
    '"': '"',
    '\\': '\\',
    '/': '/',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
}


class _Parser:
    def __init__(self, text):
        self.text = text
        self.n = len(text)
        self.pos = 0

    def error(self):
        raise _InvalidJSON()

    def eof(self):
        return self.pos >= self.n

    def peek(self):
        return self.text[self.pos] if self.pos < self.n else ''

    def skip_ws(self):
        while self.pos < self.n and self.text[self.pos] in ' \t\r\n':
            self.pos += 1

    def expect(self, ch):
        if self.peek() != ch:
            self.error()
        self.pos += 1

    def parse_document(self):
        value = self.parse_value()
        self.skip_ws()
        if not self.eof():
            self.error()
        return value

    def parse_value(self):
        stack = []
        result = None
        have_result = False

        while True:
            if not have_result:
                if stack:
                    frame = stack[-1]
                    if frame['kind'] == 'object':
                        state = frame['state']
                        if state == 'key_or_end':
                            self.skip_ws()
                            if self.eof():
                                self.error()
                            if self.peek() == '}':
                                self.pos += 1
                                result = frame['value']
                                stack.pop()
                                have_result = True
                                continue
                            frame['key'] = self.parse_string()
                            self.skip_ws()
                            self.expect(':')
                            frame['state'] = 'value'
                            continue
                        if state == 'key':
                            self.skip_ws()
                            if self.eof():
                                self.error()
                            frame['key'] = self.parse_string()
                            self.skip_ws()
                            self.expect(':')
                            frame['state'] = 'value'
                            continue
                    else:
                        if frame['state'] == 'value_or_end':
                            self.skip_ws()
                            if self.eof():
                                self.error()
                            if self.peek() == ']':
                                self.pos += 1
                                result = frame['value']
                                stack.pop()
                                have_result = True
                                continue
                            frame['state'] = 'value'
                            continue

                self.skip_ws()
                if self.eof():
                    self.error()
                ch = self.peek()
                if ch == '{':
                    self.pos += 1
                    stack.append({
                        'kind': 'object',
                        'value': {},
                        'state': 'key_or_end',
                        'key': None,
                    })
                    continue
                if ch == '[':
                    self.pos += 1
                    stack.append({
                        'kind': 'array',
                        'value': [],
                        'state': 'value_or_end',
                    })
                    continue
                result = self.parse_scalar()
                have_result = True
                continue

            if not stack:
                return result

            frame = stack[-1]
            if frame['kind'] == 'array':
                if frame['state'] != 'value':
                    self.error()
                frame['value'].append(result)
                have_result = False
                self.skip_ws()
                if self.eof():
                    self.error()
                ch = self.peek()
                if ch == ',':
                    self.pos += 1
                    frame['state'] = 'value'
                elif ch == ']':
                    self.pos += 1
                    result = frame['value']
                    stack.pop()
                    have_result = True
                else:
                    self.error()
            else:
                if frame['state'] != 'value':
                    self.error()
                frame['value'][frame['key']] = result
                frame['key'] = None
                have_result = False
                self.skip_ws()
                if self.eof():
                    self.error()
                ch = self.peek()
                if ch == ',':
                    self.pos += 1
                    frame['state'] = 'key'
                elif ch == '}':
                    self.pos += 1
                    result = frame['value']
                    stack.pop()
                    have_result = True
                else:
                    self.error()

    def parse_scalar(self):
        ch = self.peek()
        if ch == '"':
            return self.parse_string()
        if ch == 't':
            return self.literal('true', True)
        if ch == 'f':
            return self.literal('false', False)
        if ch == 'n':
            return self.literal('null', None)
        if ch == '-' or ('0' <= ch <= '9'):
            return self.parse_number()
        self.error()

    def literal(self, word, value):
        if not self.text.startswith(word, self.pos):
            self.error()
        self.pos += len(word)
        return value

    def parse_string(self):
        if self.peek() != '"':
            self.error()
        self.pos += 1
        parts = []
        while True:
            if self.pos >= self.n:
                self.error()
            ch = self.text[self.pos]
            self.pos += 1
            if ch == '"':
                return ''.join(parts)
            if ch == '\\':
                if self.pos >= self.n:
                    self.error()
                esc = self.text[self.pos]
                self.pos += 1
                if esc == 'u':
                    parts.append(self.unicode_escape())
                else:
                    try:
                        parts.append(_ESCAPES[esc])
                    except KeyError:
                        self.error()
            elif ord(ch) < 0x20:
                self.error()
            else:
                parts.append(ch)

    def read_hex4(self):
        if self.pos + 4 > self.n:
            self.error()
        code = 0
        for ch in self.text[self.pos:self.pos + 4]:
            o = ord(ch)
            if 48 <= o <= 57:
                digit = o - 48
            elif 65 <= o <= 70:
                digit = o - 55
            elif 97 <= o <= 102:
                digit = o - 87
            else:
                self.error()
            code = code * 16 + digit
        self.pos += 4
        return code

    def hex4_at(self, i):
        if i + 4 > self.n:
            return None
        code = 0
        for ch in self.text[i:i + 4]:
            o = ord(ch)
            if 48 <= o <= 57:
                digit = o - 48
            elif 65 <= o <= 70:
                digit = o - 55
            elif 97 <= o <= 102:
                digit = o - 87
            else:
                return None
            code = code * 16 + digit
        return code

    def unicode_escape(self):
        code = self.read_hex4()
        if 0xD800 <= code <= 0xDBFF and self.text.startswith('\\u', self.pos):
            low = self.hex4_at(self.pos + 2)
            if low is not None and 0xDC00 <= low <= 0xDFFF:
                self.pos += 6
                return chr(0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00))
        return chr(code)

    def parse_number(self):
        start = self.pos
        if self.peek() == '-':
            self.pos += 1
        if self.pos >= self.n:
            self.error()

        ch = self.text[self.pos]
        if ch == '0':
            self.pos += 1
        elif '1' <= ch <= '9':
            self.pos += 1
            while self.pos < self.n and '0' <= self.text[self.pos] <= '9':
                self.pos += 1
        else:
            self.error()

        is_float = False
        if self.pos < self.n and self.text[self.pos] == '.':
            is_float = True
            self.pos += 1
            if self.pos >= self.n or not ('0' <= self.text[self.pos] <= '9'):
                self.error()
            while self.pos < self.n and '0' <= self.text[self.pos] <= '9':
                self.pos += 1

        if self.pos < self.n and self.text[self.pos] in 'eE':
            is_float = True
            self.pos += 1
            if self.pos < self.n and self.text[self.pos] in '+-':
                self.pos += 1
            if self.pos >= self.n or not ('0' <= self.text[self.pos] <= '9'):
                self.error()
            while self.pos < self.n and '0' <= self.text[self.pos] <= '9':
                self.pos += 1

        s = self.text[start:self.pos]
        if is_float:
            try:
                return float(s)
            except OverflowError:
                return float('-inf') if s[0] == '-' else float('inf')
        try:
            return int(s)
        except ValueError:
            return self.int_from_digits(s)

    def int_from_digits(self, s):
        negative = s[0] == '-'
        if negative:
            s = s[1:]
        value = 0
        i = 0
        n = len(s)
        while i < n:
            j = i + 9
            if j > n:
                j = n
            value = value * (10 ** (j - i)) + int(s[i:j])
            i = j
        return -value if negative else value


def parse(text: str):
    if not isinstance(text, str):
        return None
    try:
        return _Parser(text).parse_document()
    except _InvalidJSON:
        return None
