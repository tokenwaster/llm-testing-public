"""Arithmetic expression evaluator with a hand-written recursive-descent parser.

No use of eval/exec/ast or any parsing library — tokenizer and parser are
implemented directly.
"""


def _tokenize(expr):
    """Convert the source string into a list of tokens.

    Each token is a tuple (type, value) where type is one of:
    'num', 'name', 'op', 'lparen', 'rparen'.
    """
    tokens = []
    i = 0
    n = len(expr)
    operators = set("+-*/%^")

    while i < n:
        c = expr[i]

        # Whitespace anywhere between tokens is skipped.
        if c.isspace():
            i += 1
            continue

        # Numbers: integers and decimals (digits with an optional single dot).
        if c.isdigit() or c == ".":
            start = i
            dot_seen = False
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    if dot_seen:
                        raise ValueError(f"malformed number at position {start}")
                    dot_seen = True
                i += 1
            text = expr[start:i]
            # A lone dot is not a valid number.
            if text == ".":
                raise ValueError(f"malformed number at position {start}")
            tokens.append(("num", float(text)))
            continue

        # Variable names: [a-zA-Z_][a-zA-Z0-9_]*
        if c.isalpha() or c == "_":
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(("name", expr[start:i]))
            continue

        if c in operators:
            tokens.append(("op", c))
            i += 1
            continue

        if c == "(":
            tokens.append(("lparen", c))
            i += 1
            continue

        if c == ")":
            tokens.append(("rparen", c))
            i += 1
            continue

        raise ValueError(f"unexpected character {c!r} at position {i}")

    return tokens


class _Parser:
    """Recursive-descent parser / evaluator.

    Grammar (lowest to highest precedence):

        expr    := add
        add     := mul (('+' | '-') mul)*
        mul     := unary (('*' | '/' | '%') unary)*
        unary   := '-' unary | power
        power   := atom ('^' unary)?          # right-associative, RHS is unary
        atom    := number | name | '(' expr ')'

    Unary minus binds looser than '^' (so -2^2 == -4), which is achieved by
    having power's base be an atom while its exponent recurses into unary.
    """

    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return (None, None)

    def _advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self):
        value = self._parse_add()
        if self.pos != len(self.tokens):
            raise ValueError("unexpected trailing tokens")
        return value

    def _parse_add(self):
        value = self._parse_mul()
        while True:
            typ, val = self._peek()
            if typ == "op" and val in ("+", "-"):
                self._advance()
                rhs = self._parse_mul()
                value = value + rhs if val == "+" else value - rhs
            else:
                break
        return value

    def _parse_mul(self):
        value = self._parse_unary()
        while True:
            typ, val = self._peek()
            if typ == "op" and val in ("*", "/", "%"):
                self._advance()
                rhs = self._parse_unary()
                if val == "*":
                    value = value * rhs
                elif val == "/":
                    if rhs == 0:
                        raise ValueError("division by zero")
                    value = value / rhs
                else:  # '%'
                    if rhs == 0:
                        raise ValueError("modulo by zero")
                    value = value % rhs
            else:
                break
        return value

    def _parse_unary(self):
        typ, val = self._peek()
        if typ == "op" and val == "-":
            self._advance()
            return -self._parse_unary()
        return self._parse_power()

    def _parse_power(self):
        base = self._parse_atom()
        typ, val = self._peek()
        if typ == "op" and val == "^":
            self._advance()
            # Right-associative; exponent recurses into unary so that
            # constructs like 2^-3 and 2^3^2 parse correctly.
            exponent = self._parse_unary()
            try:
                return float(base ** exponent)
            except (OverflowError, ValueError):
                raise ValueError("invalid exponentiation")
        return base

    def _parse_atom(self):
        typ, val = self._peek()

        if typ is None:
            raise ValueError("unexpected end of expression")

        if typ == "num":
            self._advance()
            return float(val)

        if typ == "name":
            self._advance()
            if val not in self.variables:
                raise ValueError(f"unknown variable {val!r}")
            return float(self.variables[val])

        if typ == "lparen":
            self._advance()
            value = self._parse_add()
            ntyp, _ = self._peek()
            if ntyp != "rparen":
                raise ValueError("unbalanced parentheses")
            self._advance()
            return value

        raise ValueError(f"unexpected token {val!r}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("empty expression")
    parser = _Parser(tokens, variables)
    return float(parser.parse())
