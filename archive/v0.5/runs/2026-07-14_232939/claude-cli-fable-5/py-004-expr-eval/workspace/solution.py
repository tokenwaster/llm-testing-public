import re


_TOKEN_RE = re.compile(
    r"\s*(?:"
    r"(?P<number>\d+(?:\.\d+)?|\.\d+)"
    r"|(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)"
    r"|(?P<op>[+\-*/%^()])"
    r")"
)


def _tokenize(expr: str) -> list[tuple[str, str]]:
    tokens = []
    pos = 0
    while pos < len(expr):
        match = _TOKEN_RE.match(expr, pos)
        if match is None:
            # Nothing matched here; either trailing whitespace or a bad char.
            rest = expr[pos:]
            if rest.strip() == "":
                break
            raise ValueError(f"unexpected character at position {pos}: {rest.lstrip()[0]!r}")
        if match.lastgroup is None:
            # Matched only whitespace at the end of the string.
            pos = match.end()
            continue
        kind = match.lastgroup
        tokens.append((kind, match.group(kind)))
        pos = match.end()
    return tokens


class _Parser:
    def __init__(self, tokens: list[tuple[str, str]], variables: dict[str, float]):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self) -> tuple[str, str] | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def next(self) -> tuple[str, str]:
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        self.pos += 1
        return tok

    def match_op(self, *ops: str) -> str | None:
        tok = self.peek()
        if tok is not None and tok[0] == "op" and tok[1] in ops:
            self.pos += 1
            return tok[1]
        return None

    def parse(self) -> float:
        value = self.expr()
        if self.pos != len(self.tokens):
            kind, text = self.tokens[self.pos]
            raise ValueError(f"unexpected token {text!r}")
        return value

    def expr(self) -> float:
        value = self.term()
        while True:
            op = self.match_op("+", "-")
            if op is None:
                return value
            rhs = self.term()
            value = value + rhs if op == "+" else value - rhs

    def term(self) -> float:
        value = self.factor()
        while True:
            op = self.match_op("*", "/", "%")
            if op is None:
                return value
            rhs = self.factor()
            if op == "*":
                value = value * rhs
            elif op == "/":
                if rhs == 0:
                    raise ValueError("division by zero")
                value = value / rhs
            else:
                if rhs == 0:
                    raise ValueError("modulo by zero")
                value = value % rhs

    def factor(self) -> float:
        # Unary minus binds looser than ^, so -2^2 == -(2^2).
        if self.match_op("-"):
            return -self.factor()
        return self.power()

    def power(self) -> float:
        base = self.atom()
        if self.match_op("^"):
            # Right-associative; exponent may carry its own unary minus (2^-3).
            exponent = self.factor()
            try:
                result = base ** exponent
            except ZeroDivisionError:
                raise ValueError("zero raised to a negative power") from None
            except OverflowError:
                raise ValueError("result too large") from None
            if isinstance(result, complex):
                raise ValueError("complex result from exponentiation")
            return float(result)
        return base

    def atom(self) -> float:
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        kind, text = tok
        if kind == "number":
            self.pos += 1
            return float(text)
        if kind == "name":
            self.pos += 1
            if text not in self.variables:
                raise ValueError(f"unknown variable: {text!r}")
            return float(self.variables[text])
        if kind == "op" and text == "(":
            self.pos += 1
            value = self.expr()
            if self.match_op(")") is None:
                raise ValueError("unbalanced parentheses: expected ')'")
            return value
        raise ValueError(f"unexpected token {text!r}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("empty expression")
    return float(_Parser(tokens, variables).parse())
