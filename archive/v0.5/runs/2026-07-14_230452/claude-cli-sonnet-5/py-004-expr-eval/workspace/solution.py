import re


_TOKEN_RE = re.compile(
    r"""
    \s*(?:
        (?P<NUMBER>\d+\.\d+|\d+\.|\.\d+|\d+)
      | (?P<IDENT>[a-zA-Z_][a-zA-Z0-9_]*)
      | (?P<OP>[+\-*/%^()])
    )
    """,
    re.VERBOSE,
)


def _tokenize(expr):
    tokens = []
    pos = 0
    length = len(expr)
    while pos < length:
        if expr[pos].isspace():
            pos += 1
            continue
        m = _TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            raise ValueError(f"Unexpected character at position {pos}: {expr[pos]!r}")
        if m.group("NUMBER") is not None:
            tokens.append(("NUMBER", m.group("NUMBER")))
        elif m.group("IDENT") is not None:
            tokens.append(("IDENT", m.group("IDENT")))
        else:
            tokens.append(("OP", m.group("OP")))
        pos = m.end()
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
        if tok is None or tok[0] != "OP" or tok[1] != op:
            raise ValueError(f"Expected '{op}' but found {tok}")
        self.advance()

    def parse(self):
        result = self.parse_expression()
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected trailing tokens: {self.tokens[self.pos:]}")
        return result

    def parse_expression(self):
        value = self.parse_term()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "OP" and tok[1] in ("+", "-"):
                op = self.advance()[1]
                rhs = self.parse_term()
                if op == "+":
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
            if tok is not None and tok[0] == "OP" and tok[1] in ("*", "/", "%"):
                op = self.advance()[1]
                rhs = self.parse_unary()
                if op == "*":
                    value = value * rhs
                elif op == "/":
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
        if tok is not None and tok[0] == "OP" and tok[1] == "-":
            self.advance()
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        base = self.parse_primary()
        tok = self.peek()
        if tok is not None and tok[0] == "OP" and tok[1] == "^":
            self.advance()
            exponent = self.parse_unary()
            return base ** exponent
        return base

    def parse_primary(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if tok[0] == "NUMBER":
            self.advance()
            return float(tok[1])
        if tok[0] == "IDENT":
            self.advance()
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        if tok[0] == "OP" and tok[1] == "(":
            self.advance()
            value = self.parse_expression()
            self.expect_op(")")
            return value
        raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")
    parser = _Parser(tokens, variables)
    try:
        result = parser.parse()
    except IndexError:
        raise ValueError("Malformed expression")
    return float(result)
