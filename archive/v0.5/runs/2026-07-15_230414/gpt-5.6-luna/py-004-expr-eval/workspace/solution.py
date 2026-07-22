class _Parser:
    def __init__(self, expr: str, variables: dict[str, float] | None):
        self.expr = expr
        self.variables = variables or {}
        self.pos = 0

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.expr) and self.expr[self.pos].isspace():
            self.pos += 1

    def _match(self, char: str) -> bool:
        self._skip_whitespace()
        if self.pos < len(self.expr) and self.expr[self.pos] == char:
            self.pos += 1
            return True
        return False

    def _parse_number(self) -> float:
        self._skip_whitespace()
        start = self.pos

        while self.pos < len(self.expr) and "0" <= self.expr[self.pos] <= "9":
            self.pos += 1

        if self.pos < len(self.expr) and self.expr[self.pos] == ".":
            self.pos += 1
            while self.pos < len(self.expr) and "0" <= self.expr[self.pos] <= "9":
                self.pos += 1

        if self.pos == start:
            raise ValueError("Expected number")

        try:
            return float(self.expr[start:self.pos])
        except ValueError as exc:
            raise ValueError("Malformed number") from exc

    def _parse_identifier(self) -> float:
        self._skip_whitespace()
        start = self.pos

        if self.pos >= len(self.expr):
            raise ValueError("Expected identifier")

        char = self.expr[self.pos]
        if not (char.isascii() and (char.isalpha() or char == "_")):
            raise ValueError("Expected identifier")

        self.pos += 1
        while self.pos < len(self.expr):
            char = self.expr[self.pos]
            if not (char.isascii() and (char.isalnum() or char == "_")):
                break
            self.pos += 1

        name = self.expr[start:self.pos]
        if name not in self.variables:
            raise ValueError(f"Unknown variable: {name}")

        try:
            return float(self.variables[name])
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Invalid value for variable: {name}") from exc

    def _parse_primary(self) -> float:
        self._skip_whitespace()

        if self.pos >= len(self.expr):
            raise ValueError("Unexpected end of expression")

        char = self.expr[self.pos]

        if char == "(":
            self.pos += 1
            value = self._parse_expression()
            if not self._match(")"):
                raise ValueError("Unbalanced parentheses")
            return value

        if "0" <= char <= "9":
            return self._parse_number()

        if char.isascii() and (char.isalpha() or char == "_"):
            return self._parse_identifier()

        raise ValueError("Malformed syntax")

    def _parse_power(self) -> float:
        left = self._parse_primary()

        if self._match("^"):
            right = self._parse_unary()
            try:
                result = left ** right
            except (ArithmeticError, TypeError, ValueError) as exc:
                raise ValueError("Invalid exponentiation") from exc

            if isinstance(result, complex):
                raise ValueError("Complex results are not supported")
            return float(result)

        return left

    def _parse_unary(self) -> float:
        if self._match("-"):
            return -self._parse_unary()
        return self._parse_power()

    def _parse_multiplicative(self) -> float:
        value = self._parse_unary()

        while True:
            if self._match("*"):
                try:
                    value *= self._parse_unary()
                except (ArithmeticError, TypeError, ValueError) as exc:
                    raise ValueError("Invalid multiplication") from exc
            elif self._match("/"):
                divisor = self._parse_unary()
                try:
                    value /= divisor
                except (ArithmeticError, TypeError, ValueError) as exc:
                    raise ValueError("Division by zero or invalid division") from exc
            elif self._match("%"):
                divisor = self._parse_unary()
                try:
                    value %= divisor
                except (ArithmeticError, TypeError, ValueError) as exc:
                    raise ValueError("Modulo by zero or invalid modulo") from exc
            else:
                break

        return value

    def _parse_expression(self) -> float:
        value = self._parse_multiplicative()

        while True:
            if self._match("+"):
                value += self._parse_multiplicative()
            elif self._match("-"):
                value -= self._parse_multiplicative()
            else:
                break

        return value

    def parse(self) -> float:
        value = self._parse_expression()
        self._skip_whitespace()

        if self.pos != len(self.expr):
            raise ValueError("Malformed syntax")

        return float(value)


def evaluate(
    expr: str,
    variables: dict[str, float] | None = None,
) -> float:
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")
    return _Parser(expr, variables).parse()
