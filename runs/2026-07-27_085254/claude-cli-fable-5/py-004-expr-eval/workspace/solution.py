import re


_TOKEN_RE = re.compile(
    r"\s*(?:"
    r"(?P<num>\d+(?:\.\d+)?)"
    r"|(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)"
    r"|(?P<op>[+\-*/%^()])"
    r")"
)


def _tokenize(expr: str) -> list[tuple[str, str]]:
    tokens = []
    pos = 0
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos and not m.group(0):
            # nothing matched at this position (after optional whitespace)
            raise ValueError(f"Invalid character at position {pos}: {expr[pos]!r}")
        if m.lastgroup is None:
            # matched only trailing whitespace
            pos = m.end()
            if pos >= len(expr):
                break
            raise ValueError(f"Invalid character at position {pos}: {expr[pos]!r}")
        kind = m.lastgroup
        tokens.append((kind, m.group(kind)))
        pos = m.end()
    return tokens


class _Parser:
    def __init__(self, tokens: list[tuple[str, str]], variables: dict[str, float]):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return (None, None)

    def next(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect_op(self, op: str):
        kind, val = self.next()
        if kind != "op" or val != op:
            raise ValueError(f"Expected {op!r}, got {val!r}")

    # expr := term (('+' | '-') term)*
    def parse_expr(self) -> float:
        value = self.parse_term()
        while True:
            kind, val = self.peek()
            if kind == "op" and val in ("+", "-"):
                self.next()
                rhs = self.parse_term()
                value = value + rhs if val == "+" else value - rhs
            else:
                return value

    # term := unary (('*' | '/' | '%') unary)*
    def parse_term(self) -> float:
        value = self.parse_unary()
        while True:
            kind, val = self.peek()
            if kind == "op" and val in ("*", "/", "%"):
                self.next()
                rhs = self.parse_unary()
                if val == "*":
                    value = value * rhs
                else:
                    if rhs == 0:
                        raise ValueError("Division by zero")
                    value = value / rhs if val == "/" else value % rhs
            else:
                return value

    # unary := '-' unary | power
    def parse_unary(self) -> float:
        kind, val = self.peek()
        if kind == "op" and val == "-":
            self.next()
            return -self.parse_unary()
        return self.parse_power()

    # power := atom ('^' unary)?   (right-associative; rhs may carry unary minus)
    def parse_power(self) -> float:
        base = self.parse_atom()
        kind, val = self.peek()
        if kind == "op" and val == "^":
            self.next()
            exponent = self.parse_unary()
            try:
                result = base ** exponent
            except (ZeroDivisionError, OverflowError) as e:
                raise ValueError(f"Invalid exponentiation: {e}") from e
            if isinstance(result, complex):
                raise ValueError("Exponentiation produced a complex result")
            return float(result)
        return base

    # atom := number | name | '(' expr ')'
    def parse_atom(self) -> float:
        kind, val = self.next()
        if kind == "num":
            return float(val)
        if kind == "name":
            if val not in self.variables:
                raise ValueError(f"Unknown variable: {val!r}")
            return float(self.variables[val])
        if kind == "op" and val == "(":
            value = self.parse_expr()
            self.expect_op(")")
            return value
        raise ValueError(f"Unexpected token: {val!r}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")
    parser = _Parser(tokens, variables or {})
    result = parser.parse_expr()
    if parser.pos != len(parser.tokens):
        raise ValueError(f"Unexpected trailing token: {parser.peek()[1]!r}")
    return float(result)
