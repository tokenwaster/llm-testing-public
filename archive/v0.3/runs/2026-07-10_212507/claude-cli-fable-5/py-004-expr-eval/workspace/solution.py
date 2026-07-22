import re


_TOKEN_RE = re.compile(
    r"\s*(?:"
    r"(?P<number>\d+(?:\.\d*)?)"
    r"|(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)"
    r"|(?P<op>[-+*/%^()])"
    r")"
)


def _tokenize(expr: str) -> list[tuple[str, str]]:
    tokens = []
    pos = 0
    while pos < len(expr):
        match = _TOKEN_RE.match(expr, pos)
        if match is None:
            # Nothing but trailing whitespace is fine; anything else is an error.
            if expr[pos:].strip() == "":
                break
            raise ValueError(f"unexpected character at position {pos}: {expr[pos:]!r}")
        pos = match.end()
        if match.lastgroup == "number":
            tokens.append(("number", match.group("number")))
        elif match.lastgroup == "name":
            tokens.append(("name", match.group("name")))
        elif match.lastgroup == "op":
            tokens.append(("op", match.group("op")))
        else:
            # Matched only whitespace at end of string.
            break
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

    def advance(self) -> tuple[str, str]:
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        self.pos += 1
        return tok

    def expect_op(self, op: str) -> None:
        tok = self.peek()
        if tok is None or tok != ("op", op):
            raise ValueError(f"expected {op!r}")
        self.pos += 1

    # expression := additive
    def parse_expression(self) -> float:
        return self.parse_additive()

    # additive := multiplicative (('+' | '-') multiplicative)*
    def parse_additive(self) -> float:
        value = self.parse_multiplicative()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "op" and tok[1] in "+-":
                self.advance()
                rhs = self.parse_multiplicative()
                value = value + rhs if tok[1] == "+" else value - rhs
            else:
                return value

    # multiplicative := unary (('*' | '/' | '%') unary)*
    def parse_multiplicative(self) -> float:
        value = self.parse_unary()
        while True:
            tok = self.peek()
            if tok is not None and tok[0] == "op" and tok[1] in "*/%":
                self.advance()
                rhs = self.parse_unary()
                if tok[1] == "*":
                    value = value * rhs
                else:
                    if rhs == 0:
                        raise ValueError(
                            "division by zero" if tok[1] == "/" else "modulo by zero"
                        )
                    value = value / rhs if tok[1] == "/" else value % rhs
            else:
                return value

    # unary := '-' unary | power
    # Unary minus binds looser than '^', so -2^2 parses as -(2^2).
    def parse_unary(self) -> float:
        tok = self.peek()
        if tok == ("op", "-"):
            self.advance()
            return -self.parse_unary()
        return self.parse_power()

    # power := atom ('^' unary)?   (right-associative; exponent may be negated)
    def parse_power(self) -> float:
        base = self.parse_atom()
        tok = self.peek()
        if tok == ("op", "^"):
            self.advance()
            exponent = self.parse_unary()
            try:
                result = base ** exponent
            except (OverflowError, ZeroDivisionError) as exc:
                raise ValueError(f"invalid exponentiation: {exc}") from exc
            if isinstance(result, complex):
                raise ValueError("exponentiation produced a complex result")
            return float(result)
        return base

    # atom := number | name | '(' expression ')'
    def parse_atom(self) -> float:
        tok = self.advance()
        kind, text = tok
        if kind == "number":
            return float(text)
        if kind == "name":
            if text not in self.variables:
                raise ValueError(f"unknown variable: {text!r}")
            return float(self.variables[text])
        if kind == "op" and text == "(":
            value = self.parse_expression()
            self.expect_op(")")
            return value
        raise ValueError(f"unexpected token: {text!r}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("empty expression")
    parser = _Parser(tokens, variables or {})
    result = parser.parse_expression()
    if parser.peek() is not None:
        raise ValueError(f"unexpected token: {parser.peek()[1]!r}")
    return float(result)
