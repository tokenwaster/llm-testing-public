class _Parser:
    def __init__(self, expr: str, variables: dict[str, float] | None):
        self.expr = expr
        self.variables = variables or {}
        self.pos = 0

    def skip_whitespace(self) -> None:
        while self.pos < len(self.expr) and self.expr[self.pos].isspace():
            self.pos += 1

    def peek(self) -> str | None:
        self.skip_whitespace()
        if self.pos >= len(self.expr):
            return None
        return self.expr[self.pos]

    def consume(self, char: str) -> bool:
        if self.peek() == char:
            self.pos += 1
            return True
        return False

    def parse(self) -> float:
        value = self.parse_additive()
        if self.peek() is not None:
            raise ValueError("malformed syntax")
        return float(value)

    def parse_additive(self) -> float:
        value = self.parse_multiplicative()

        while True:
            if self.consume("+"):
                value += self.parse_multiplicative()
            elif self.consume("-"):
                value -= self.parse_multiplicative()
            else:
                return value

    def parse_multiplicative(self) -> float:
        value = self.parse_unary()

        while True:
            if self.consume("*"):
                value *= self.parse_unary()
            elif self.consume("/"):
                right = self.parse_unary()
                if right == 0:
                    raise ValueError("division by zero")
                value /= right
            elif self.consume("%"):
                right = self.parse_unary()
                if right == 0:
                    raise ValueError("modulo by zero")
                value %= right
            else:
                return value

    def parse_unary(self) -> float:
        if self.consume("-"):
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self) -> float:
        value = self.parse_primary()

        if self.consume("^"):
            value = value ** self.parse_unary()

        return value

    def parse_primary(self) -> float:
        token = self.peek()

        if token is None:
            raise ValueError("malformed syntax")

        if self.consume("("):
            value = self.parse_additive()
            if not self.consume(")"):
                raise ValueError("unbalanced parentheses")
            return value

        if token.isdigit():
            start = self.pos
            while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                self.pos += 1

            if self.pos < len(self.expr) and self.expr[self.pos] == ".":
                self.pos += 1
                while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                    self.pos += 1

            try:
                return float(self.expr[start:self.pos])
            except ValueError:
                raise ValueError("malformed syntax")

        if token.isalpha() or token == "_":
            start = self.pos
            self.pos += 1

            while self.pos < len(self.expr):
                char = self.expr[self.pos]
                if not (char.isalnum() or char == "_"):
                    break
                self.pos += 1

            name = self.expr[start:self.pos]
            if name not in self.variables:
                raise ValueError(f"unknown variable: {name}")
            return float(self.variables[name])

        raise ValueError("malformed syntax")


def evaluate(
    expr: str,
    variables: dict[str, float] | None = None,
) -> float:
    return _Parser(expr, variables).parse()
