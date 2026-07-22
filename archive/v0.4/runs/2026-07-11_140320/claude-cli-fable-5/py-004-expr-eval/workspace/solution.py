"""Arithmetic expression evaluator with a hand-written recursive-descent parser.

Grammar (in precedence order, loosest first):

    expr    := term (('+' | '-') term)*
    term    := unary (('*' | '/' | '%') unary)*
    unary   := '-' unary | power
    power   := atom ('^' unary)?          # right-associative; exponent may
                                          # itself carry unary minus (2^-3)
    atom    := NUMBER | NAME | '(' expr ')'

Unary minus binds looser than '^', so -2^2 == -(2^2) == -4.
"""


def _tokenize(expr: str) -> list[tuple[str, str]]:
    """Convert the input string into a list of (kind, text) tokens."""
    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in "+-*/%^()":
            tokens.append(("op", c))
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            if j < n and expr[j] == ".":
                j += 1
                if j >= n or not expr[j].isdigit():
                    raise ValueError(
                        f"malformed number at position {i}: {expr[i:j]!r}"
                    )
                while j < n and expr[j].isdigit():
                    j += 1
            tokens.append(("num", expr[i:j]))
            i = j
            continue
        if c.isalpha() or c == "_":
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append(("name", expr[i:j]))
            i = j
            continue
        raise ValueError(f"unexpected character {c!r} at position {i}")
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
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def at_op(self, *ops: str) -> bool:
        tok = self.peek()
        return tok is not None and tok[0] == "op" and tok[1] in ops

    def parse(self) -> float:
        value = self.expr()
        if self.pos != len(self.tokens):
            raise ValueError(f"unexpected token {self.tokens[self.pos][1]!r}")
        return value

    def expr(self) -> float:
        value = self.term()
        while self.at_op("+", "-"):
            op = self.advance()[1]
            rhs = self.term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def term(self) -> float:
        value = self.unary()
        while self.at_op("*", "/", "%"):
            op = self.advance()[1]
            rhs = self.unary()
            if op == "*":
                value = value * rhs
            else:
                if rhs == 0:
                    raise ValueError(
                        "division by zero" if op == "/" else "modulo by zero"
                    )
                value = value / rhs if op == "/" else value % rhs
        return value

    def unary(self) -> float:
        if self.at_op("-"):
            self.advance()
            return -self.unary()
        return self.power()

    def power(self) -> float:
        base = self.atom()
        if self.at_op("^"):
            self.advance()
            exponent = self.unary()  # right-associative, allows 2^-3
            try:
                return float(base ** exponent)
            except ZeroDivisionError:
                raise ValueError("zero raised to a negative power") from None
            except (OverflowError, TypeError) as e:
                raise ValueError(f"invalid exponentiation: {e}") from None
        return base

    def atom(self) -> float:
        tok = self.peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        kind, text = tok
        if kind == "num":
            self.advance()
            return float(text)
        if kind == "name":
            self.advance()
            if text not in self.variables:
                raise ValueError(f"unknown variable {text!r}")
            return float(self.variables[text])
        if kind == "op" and text == "(":
            self.advance()
            value = self.expr()
            if not self.at_op(")"):
                raise ValueError("unbalanced parentheses: missing ')'")
            self.advance()
            return value
        raise ValueError(f"unexpected token {text!r}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("empty expression")
    result = _Parser(tokens, variables or {}).parse()
    if isinstance(result, complex):
        raise ValueError("expression produced a non-real result")
    return float(result)
