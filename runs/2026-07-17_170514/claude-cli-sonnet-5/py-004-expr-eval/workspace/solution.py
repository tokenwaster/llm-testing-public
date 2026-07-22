import re


class _Parser:
    _NUM_RE = re.compile(r'\d+\.\d+|\d+')
    _ID_RE = re.compile(r'[a-zA-Z_]\w*')
    _OPS = set('+-*/%^()')

    def __init__(self, expr, variables):
        self.variables = variables
        self.tokens = self._tokenize(expr)
        self.pos = 0

    def _tokenize(self, expr):
        tokens = []
        i, n = 0, len(expr)
        while i < n:
            c = expr[i]
            if c.isspace():
                i += 1
                continue
            m = self._NUM_RE.match(expr, i)
            if m:
                tokens.append(('NUM', m.group()))
                i = m.end()
                continue
            m = self._ID_RE.match(expr, i)
            if m:
                tokens.append(('ID', m.group()))
                i = m.end()
                continue
            if c in self._OPS:
                tokens.append((c, c))
                i += 1
                continue
            raise ValueError(f"Unexpected character {c!r} at position {i}")
        return tokens

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self):
        tok = self._peek()
        self.pos += 1
        return tok

    def parse(self):
        if not self.tokens:
            raise ValueError("Empty expression")
        value = self._parse_expr()
        if self.pos != len(self.tokens):
            tok = self._peek()
            raise ValueError(f"Unexpected trailing token {tok}")
        return value

    def _parse_expr(self):
        value = self._parse_term()
        while True:
            tok = self._peek()
            if tok is not None and tok[0] in ('+', '-'):
                self._advance()
                rhs = self._parse_term()
                if tok[0] == '+':
                    value = value + rhs
                else:
                    value = value - rhs
            else:
                break
        return value

    def _parse_term(self):
        value = self._parse_unary()
        while True:
            tok = self._peek()
            if tok is not None and tok[0] in ('*', '/', '%'):
                self._advance()
                rhs = self._parse_unary()
                if tok[0] == '*':
                    value = value * rhs
                elif tok[0] == '/':
                    if rhs == 0:
                        raise ValueError("Division by zero")
                    value = value / rhs
                else:
                    if rhs == 0:
                        raise ValueError("Modulo by zero")
                    value = value % rhs
            else:
                break
        return value

    def _parse_unary(self):
        tok = self._peek()
        if tok is not None and tok[0] == '-':
            self._advance()
            return -self._parse_unary()
        if tok is not None and tok[0] == '+':
            self._advance()
            return self._parse_unary()
        return self._parse_power()

    def _parse_power(self):
        base = self._parse_atom()
        tok = self._peek()
        if tok is not None and tok[0] == '^':
            self._advance()
            exponent = self._parse_unary()
            return base ** exponent
        return base

    def _parse_atom(self):
        tok = self._peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        kind, text = tok
        if kind == 'NUM':
            self._advance()
            return float(text)
        if kind == 'ID':
            self._advance()
            if text not in self.variables:
                raise ValueError(f"Unknown variable: {text}")
            return float(self.variables[text])
        if kind == '(':
            self._advance()
            value = self._parse_expr()
            tok = self._peek()
            if tok is None or tok[0] != ')':
                raise ValueError("Unbalanced parentheses")
            self._advance()
            return value
        raise ValueError(f"Unexpected token: {text}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    parser = _Parser(expr, variables)
    result = parser.parse()
    return float(result)
