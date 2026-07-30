import re


_TOKEN_RE = re.compile(
    r"""
    \s*(?:
        (?P<number>\d+\.\d+|\.\d+|\d+)
      | (?P<ident>[a-zA-Z_][a-zA-Z0-9_]*)
      | (?P<op>[+\-*/%^()])
    )
    """,
    re.VERBOSE,
)


def _tokenize(expr: str):
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
        if m.group("number") is not None:
            tokens.append(("number", m.group("number")))
        elif m.group("ident") is not None:
            tokens.append(("ident", m.group("ident")))
        else:
            tokens.append(("op", m.group("op")))
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

    def expect_op(self, value):
        tok = self.peek()
        if tok is None or tok[0] != "op" or tok[1] != value:
            raise ValueError(f"Expected {value!r} at position {self.pos}")
        self.advance()

    def parse(self):
        result = self.parse_expr()
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected trailing tokens starting at {self.tokens[self.pos]}")
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
        value = self.parse_factor()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "op" and tok[1] in ("*", "/", "%"):
                self.advance()
                rhs = self.parse_factor()
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

    def parse_factor(self):
        tok = self.peek()
        if tok is not None and tok[0] == "op" and tok[1] == "-":
            self.advance()
            return -self.parse_factor()
        return self.parse_power()

    def parse_power(self):
        base = self.parse_atom()
        tok = self.peek()
        if tok is not None and tok[0] == "op" and tok[1] == "^":
            self.advance()
            exponent = self.parse_factor()
            return base ** exponent
        return base

    def parse_atom(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        kind, value = tok
        if kind == "number":
            self.advance()
            return float(value)
        if kind == "ident":
            self.advance()
            if value not in self.variables:
                raise ValueError(f"Unknown variable: {value!r}")
            return float(self.variables[value])
        if kind == "op" and value == "(":
            self.advance()
            result = self.parse_expr()
            tok2 = self.peek()
            if tok2 is None or tok2[0] != "op" or tok2[1] != ")":
                raise ValueError("Unbalanced parentheses")
            self.advance()
            return result
        raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr: str, variables: "dict[str, float] | None" = None) -> float:
    if not isinstance(expr, str) or not expr.strip():
        raise ValueError("Expression must be a non-empty string")
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")
    parser = _Parser(tokens, variables)
    try:
        result = parser.parse()
    except IndexError:
        raise ValueError("Malformed expression")
    return float(result)
