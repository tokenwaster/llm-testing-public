import math
from typing import Any


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables)
    return parser.parse()


def _tokenize(s: str) -> list[tuple[str, Any]]:
    tokens: list[tuple[str, Any]] = []
    i = 0
    n = len(s)

    while i < n:
        c = s[i]

        if c.isspace():
            i += 1
            continue

        if c.isdigit() or c == '.':
            start = i
            if c == '.':
                i += 1
                while i < n and s[i].isdigit():
                    i += 1
                num_str = s[start:i]
                if num_str == '.':
                    raise ValueError("malformed number")
            else:
                while i < n and s[i].isdigit():
                    i += 1
                if i < n and s[i] == '.':
                    i += 1
                    while i < n and s[i].isdigit():
                        i += 1
                num_str = s[start:i]

            try:
                value = float(num_str)
            except ValueError:
                raise ValueError("malformed number")

            tokens.append(('NUMBER', value))
            continue

        if c.isalpha() or c == '_':
            start = i
            while i < n and (s[i].isalnum() or s[i] == '_'):
                i += 1
            tokens.append(('NAME', s[start:i]))
            continue

        if c in '+-*/%^()':
            tokens.append((c, c))
            i += 1
            continue

        raise ValueError(f"invalid character: {c!r}")

    tokens.append(('EOF', None))
    return tokens


class _Parser:
    def __init__(self, tokens: list[tuple[str, Any]], variables: dict[str, float]):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def _current(self) -> tuple[str, Any]:
        return self.tokens[self.pos]

    def _consume(self, expected: str | None = None) -> tuple[str, Any]:
        tok = self._current()
        if expected is not None and tok[0] != expected:
            raise ValueError("unexpected token")
        self.pos += 1
        return tok

    def parse(self) -> float:
        result = self._expr()
        if self._current()[0] != 'EOF':
            raise ValueError("unexpected token after complete expression")
        return float(result)

    def _expr(self) -> float:
        value = self._term()
        while self._current()[0] in ('+', '-'):
            op = self._consume()[0]
            right = self._term()
            if op == '+':
                value = value + right
            else:
                value = value - right
        return float(value)

    def _term(self) -> float:
        value = self._unary()
        while self._current()[0] in ('*', '/', '%'):
            op = self._consume()[0]
            right = self._unary()
            if op == '*':
                value = value * right
            elif op == '/':
                if right == 0.0:
                    raise ValueError("division by zero")
                value = value / right
            else:  # '%'
                if right == 0.0:
                    raise ValueError("modulo by zero")
                value = value % right
        return float(value)

    def _unary(self) -> float:
        if self._current()[0] == '-':
            self._consume()
            return -self._unary()
        return self._power()

    def _power(self) -> float:
        value = self._primary()
        if self._current()[0] == '^':
            self._consume()
            exponent = self._unary()
            try:
                value = math.pow(value, exponent)
            except ValueError as exc:
                raise ValueError(f"invalid exponentiation: {exc}")
        return float(value)

    def _primary(self) -> float:
        tok_type, tok_val = self._current()

        if tok_type == 'NUMBER':
            self._consume()
            return float(tok_val)

        if tok_type == 'NAME':
            self._consume()
            if tok_val not in self.variables:
                raise ValueError(f"unknown variable: {tok_val}")
            return float(self.variables[tok_val])

        if tok_type == '(':
            self._consume()
            value = self._expr()
            if self._current()[0] != ')':
                raise ValueError("unbalanced parentheses")
            self._consume()
            return value

        raise ValueError("unexpected token")
