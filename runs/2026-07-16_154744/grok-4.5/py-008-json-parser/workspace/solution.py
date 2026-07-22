class _Parser:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.n = len(text)

    def skip_whitespace(self) -> None:
        while self.pos < self.n and self.text[self.pos] in ' \t\n\r':
            self.pos += 1

    def peek(self):
        if self.pos < self.n:
            return self.text[self.pos]
        return None

    def consume(self, expected=None):
        c = self.peek()
        if c is None:
            raise ValueError('unexpected end of input')
        if expected is not None and c != expected:
            raise ValueError(f'expected {expected!r}')
        self.pos += 1
        return c

    def parse_value(self):
        self.skip_whitespace()
        c = self.peek()
        if c is None:
            raise ValueError('empty value')
        if c == '{':
            return self.parse_object()
        if c == '[':
            return self.parse_array()
        if c == '"':
            return self.parse_string()
        if c == 't':
            return self.parse_literal('true', True)
        if c == 'f':
            return self.parse_literal('false', False)
        if c == 'n':
            return self.parse_literal('null', None)
        if c == '-' or c.isdigit():
            return self.parse_number()
        raise ValueError('invalid value')

    def parse_object(self):
        self.consume('{')
        self.skip_whitespace()
        obj = {}
        if self.peek() == '}':
            self.consume('}')
            return obj
        while True:
            self.skip_whitespace()
            if self.peek() != '"':
                raise ValueError('object key must be string')
            key = self.parse_string()
            self.skip_whitespace()
            self.consume(':')
            value = self.parse_value()
            obj[key] = value
            self.skip_whitespace()
            c = self.peek()
            if c == '}':
                self.consume('}')
                return obj
            if c == ',':
                self.consume(',')
                self.skip_whitespace()
                if self.peek() == '}':
                    raise ValueError('trailing comma in object')
                continue
            raise ValueError('expected , or } in object')

    def parse_array(self):
        self.consume('[')
        self.skip_whitespace()
        arr = []
        if self.peek() == ']':
            self.consume(']')
            return arr
        while True:
            value = self.parse_value()
            arr.append(value)
            self.skip_whitespace()
            c = self.peek()
            if c == ']':
                self.consume(']')
                return arr
            if c == ',':
                self.consume(',')
                self.skip_whitespace()
                if self.peek() == ']':
                    raise ValueError('trailing comma in array')
                continue
            raise ValueError('expected , or ] in array')

    def parse_string(self):
        self.consume('"')
        parts = []
        while True:
            c = self.peek()
            if c is None:
                raise ValueError('unterminated string')
            if c == '"':
                self.consume('"')
                return ''.join(parts)
            if c == '\\':
                self.consume('\\')
                esc = self.consume()
                if esc == '"':
                    parts.append('"')
                elif esc == '\\':
                    parts.append('\\')
                elif esc == '/':
                    parts.append('/')
                elif esc == 'b':
                    parts.append('\b')
                elif esc == 'f':
                    parts.append('\f')
                elif esc == 'n':
                    parts.append('\n')
                elif esc == 'r':
                    parts.append('\r')
                elif esc == 't':
                    parts.append('\t')
                elif esc == 'u':
                    hex_digits = []
                    for _ in range(4):
                        h = self.consume()
                        if h not in '0123456789abcdefABCDEF':
                            raise ValueError('invalid unicode escape')
                        hex_digits.append(h)
                    parts.append(chr(int(''.join(hex_digits), 16)))
                else:
                    raise ValueError('invalid escape sequence')
            else:
                if ord(c) < 0x20:
                    raise ValueError('unescaped control character in string')
                parts.append(self.consume())

    def parse_literal(self, literal: str, value):
        for ch in literal:
            self.consume(ch)
        return value

    def parse_number(self):
        start = self.pos
        if self.peek() == '-':
            self.consume('-')
        # integer part
        c = self.peek()
        if c == '0':
            self.consume('0')
            if self.peek() is not None and self.peek().isdigit():
                raise ValueError('leading zeros not allowed')
        elif c is not None and c.isdigit():
            while self.peek() is not None and self.peek().isdigit():
                self.consume()
        else:
            raise ValueError('invalid number')
        is_float = False
        # fractional part
        if self.peek() == '.':
            is_float = True
            self.consume('.')
            if self.peek() is None or not self.peek().isdigit():
                raise ValueError('invalid fraction')
            while self.peek() is not None and self.peek().isdigit():
                self.consume()
        # exponent
        if self.peek() in ('e', 'E'):
            is_float = True
            self.consume()
            if self.peek() in ('+', '-'):
                self.consume()
            if self.peek() is None or not self.peek().isdigit():
                raise ValueError('invalid exponent')
            while self.peek() is not None and self.peek().isdigit():
                self.consume()
        num_str = self.text[start:self.pos]
        if is_float:
            return float(num_str)
        return int(num_str)


def parse(text: str):
    if not isinstance(text, str):
        return None
    try:
        p = _Parser(text)
        result = p.parse_value()
        p.skip_whitespace()
        if p.pos != p.n:
            return None
        return result
    except Exception:
        return None
