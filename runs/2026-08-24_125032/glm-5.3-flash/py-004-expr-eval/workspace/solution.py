import sys

# Allow deeply nested parentheses without hitting the default recursion cap.
sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float.

    Implements a hand-written tokenizer + recursive-descent parser.
    Supported: numbers (int/decimal), + - * / % ^ (right-assoc),
    repeated unary minus (binding looser than ^), parentheses,
    variables resolved from `variables`, whitespace between tokens.
    """
    tokens = _tokenize(expr)
    env = variables if variables is not None else {}
    parser = _Parser(tokens, env)
    return parser.parse()


def _tokenize(expr):
    tokens = []
    i, n = 0, len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if "0" <= ch <= "9":
            start = i
            while i < n and "0" <= expr[i] <= "9":
                i += 1
            if i < n and expr[i] == ".":
                i += 1
                if i >= n or not ("0" <= expr[i] <= "9"):
                    raise ValueError(f"malformed number at position {start}")
                while i < n and "0" <= expr[i] <= "9":
                    i += 1
            tokens.append(("num", float(expr[start:i])))
            continue
        if ch == "_" or "a" <= ch <= "z" or "A" <= ch <= "Z":
            start = i
            while i < n and (
                expr[i] == "_"
                or "a" <= expr[i] <= "z"
                or "A" <= expr[i] <= "Z"
                or "0" <= expr[i] <= "9"
            ):
                i += 1
            tokens.append(("name", expr[start:i]))
            continue
        if ch in "+-*/%^()":
            tokens.append((ch, ch))
            i += 1
            continue
        raise ValueError(f"unexpected character {ch!r} at position {i}")
    return tokens


class _Parser:
    """
    Grammar:
        expr   := term  (('+' | '-') term)*          left-assoc
        term   := factor (('*' | '/' | '%') factor)* left-assoc
        factor := '-' factor | power                 unary minus (looser than ^)
        power  := atom ('^' factor)?                 right-assoc
        atom   := NUMBER | NAME | '(' expr ')'
    """

    def __init__(self, tokens, env):
        self.tokens = tokens
        self.env = env
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos][0] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self):
        if not self.tokens:
            raise ValueError("empty expression")
        value = self.expr()
        if self.pos != len(self.tokens):
            raise ValueError(f"unexpected token {self.tokens[self.pos][0]!r}")
        return float(value)

    def expr(self):
        value = self.term()
        while self.peek() in ("+", "-"):
            op = self.advance()[0]
            rhs = self.term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def term(self):
        value = self.factor()
        while self.peek() in ("*", "/", "%"):
            op = self.advance()[0]
            rhs = self.factor()
            if op == "*":
                value = value * rhs
            else:
                if rhs == 0:
                    raise ValueError(
                        "division by zero" if op == "/" else "modulo by zero"
                    )
                value = value / rhs if op == "/" else value % rhs
        return value

    def factor(self):
        if self.peek() == "-":
            self.advance()
            return -self.factor()
        return self.power()

    def power(self):
        base = self.atom()
        if self.peek() == "^":
            self.advance()
            exponent = self.factor()
            try:
                result = base ** exponent
            except OverflowError:
                raise ValueError("overflow in exponentiation")
            except ZeroDivisionError:
                raise ValueError("zero raised to a negative power")
            if isinstance(result, complex):
                raise ValueError("invalid exponentiation (complex result)")
            return float(result)
        return base

    def atom(self):
        kind = self.peek()
        if kind == "num":
            return self.advance()[1]
        if kind == "name":
            name = self.advance()[1]
            if name not in self.env:
                raise ValueError(f"unknown variable {name!r}")
            return float(self.env[name])
        if kind == "(":
            self.advance()
            value = self.expr()
            if self.peek() != ")":
                raise ValueError("unbalanced parentheses: expected ')'")
            self.advance()
            return value
        if kind is None:
            raise ValueError("unexpected end of expression")
        raise ValueError(f"unexpected token {kind!r}")
