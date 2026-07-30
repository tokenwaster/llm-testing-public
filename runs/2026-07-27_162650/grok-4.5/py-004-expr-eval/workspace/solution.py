from __future__ import annotations


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables)
    result = parser.parse_expr()
    if parser.pos < len(parser.tokens):
        raise ValueError("malformed syntax: unexpected trailing tokens")
    return float(result)


def _tokenize(expr: str) -> list:
    tokens: list = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in "+-*/%^()":
            tokens.append(c)
            i += 1
            continue
        if c.isdigit() or c == ".":
            start = i
            seen_dot = c == "."
            i += 1
            while i < n:
                ch = expr[i]
                if ch.isdigit():
                    i += 1
                elif ch == ".":
                    if seen_dot:
                        raise ValueError("malformed number")
                    seen_dot = True
                    i += 1
                else:
                    break
            num_str = expr[start:i]
            if num_str == "." or num_str.count(".") > 1:
                raise ValueError("malformed number")
            # reject leading-dot-only forms that are empty of digits handled above;
            # also reject trailing dot-only like "3." — float accepts it, allow it
            try:
                tokens.append(float(num_str))
            except ValueError:
                raise ValueError("malformed number") from None
            continue
        if c.isalpha() or c == "_":
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(("var", expr[start:i]))
            continue
        raise ValueError(f"malformed syntax: unexpected character {c!r}")
    return tokens


class _Parser:
    def __init__(self, tokens: list, variables: dict[str, float]) -> None:
        self.tokens = tokens
        self.variables = variables
        self.pos = 0

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self):
        tok = self._peek()
        if tok is None:
            raise ValueError("malformed syntax: unexpected end of expression")
        self.pos += 1
        return tok

    def parse_expr(self) -> float:
        left = self.parse_term()
        while True:
            op = self._peek()
            if op == "+" or op == "-":
                self._consume()
                right = self.parse_term()
                if op == "+":
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    def parse_term(self) -> float:
        left = self.parse_unary()
        while True:
            op = self._peek()
            if op == "*" or op == "/" or op == "%":
                self._consume()
                right = self.parse_unary()
                if op == "*":
                    left = left * right
                elif op == "/":
                    if right == 0.0:
                        raise ValueError("division by zero")
                    left = left / right
                else:
                    if right == 0.0:
                        raise ValueError("modulo by zero")
                    left = left % right
            else:
                break
        return left

    def parse_unary(self) -> float:
        if self._peek() == "-":
            self._consume()
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self) -> float:
        base = self.parse_primary()
        if self._peek() == "^":
            self._consume()
            # right-associative: exponent is unary (can be negative / another power)
            exp = self.parse_unary()
            return base ** exp
        return base

    def parse_primary(self) -> float:
        tok = self._peek()
        if tok is None:
            raise ValueError("malformed syntax: unexpected end of expression")
        if isinstance(tok, float):
            self._consume()
            return tok
        if isinstance(tok, tuple) and tok[0] == "var":
            self._consume()
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"unknown variable: {name}")
            return float(self.variables[name])
        if tok == "(":
            self._consume()
            val = self.parse_expr()
            if self._peek() != ")":
                raise ValueError("unbalanced parentheses")
            self._consume()
            return val
        raise ValueError("malformed syntax")
