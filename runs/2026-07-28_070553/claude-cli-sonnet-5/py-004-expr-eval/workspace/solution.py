import re


_TOKEN_RE = re.compile(
    r"\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<id>[a-zA-Z_][a-zA-Z0-9_]*)|(?P<op>[+\-*/%^()]))"
)


def _tokenize(expr: str):
    tokens = []
    pos = 0
    length = len(expr)
    while pos < length:
        m = _TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            if expr[pos:].strip() == "":
                break
            raise ValueError(f"Unexpected character at position {pos}: {expr[pos:pos+1]!r}")
        pos = m.end()
        if m.group("num") is not None:
            tokens.append(("num", m.group("num")))
        elif m.group("id") is not None:
            tokens.append(("id", m.group("id")))
        elif m.group("op") is not None:
            tokens.append(("op", m.group("op")))
    return tokens


class _Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect_op(self, op):
        tok = self.peek()
        if tok is None or tok[0] != "op" or tok[1] != op:
            raise ValueError(f"Expected '{op}' but found {tok!r}")
        self.advance()

    def parse(self):
        result = self.parse_expr()
        if self.peek() is not None:
            raise ValueError(f"Unexpected trailing token: {self.peek()!r}")
        return result

    def parse_expr(self):
        value = self.parse_term()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "op" and tok[1] in ("+", "-"):
                self.advance()
                rhs = self.parse_term()
                if tok[1] == "+":
                    value = value + rhs
                else:
                    value = value - rhs
            else:
                break
        return value

    def parse_term(self):
        value = self.parse_unary()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "op" and tok[1] in ("*", "/", "%"):
                self.advance()
                rhs = self.parse_unary()
                if tok[1] == "*":
                    value = value * rhs
                elif tok[1] == "/":
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

    def parse_unary(self):
        tok = self.peek()
        if tok is not None and tok[0] == "op" and tok[1] == "-":
            self.advance()
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        base = self.parse_primary()
        tok = self.peek()
        if tok is not None and tok[0] == "op" and tok[1] == "^":
            self.advance()
            exponent = self.parse_unary()
            return base ** exponent
        return base

    def parse_primary(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if tok[0] == "num":
            self.advance()
            return float(tok[1])
        if tok[0] == "id":
            self.advance()
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        if tok[0] == "op" and tok[1] == "(":
            self.advance()
            value = self.parse_expr()
            self.expect_op(")")
            return value
        raise ValueError(f"Unexpected token: {tok!r}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")
    parser = _Parser(tokens, variables)
    result = parser.parse()
    return float(result)
