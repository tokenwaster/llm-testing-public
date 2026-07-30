class _Parser:
    def __init__(self, expr: str, variables: dict[str, float] | None) -> None:
        self.expr = expr
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def parse(self) -> float:
        value = self._parse_expression()
        self._skip_whitespace()
        if self.pos != len(self.expr):
            raise ValueError("Malformed syntax")
        return float(value)

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.expr) and self.expr[self.pos].isspace():
            self.pos += 1

    def _match(self, token: str) -> bool:
        self._skip_whitespace()
        if self.pos < len(self.expr) and self.expr[self.pos] == token:
            self.pos += 1
            return True
        return False

    def _parse_expression(self) -> float:
        value = self._parse_term()

        while True:
            if self._match("+"):
                value += self._parse_term()
            elif self._match("-"):
                value -= self._parse_term()
            else:
                return value

    def _parse_term(self) -> float:
        value = self._parse_unary()

        while True:
            if self._match("*"):
                value *= self._parse_unary()
            elif self._match("/"):
                divisor = self._parse_unary()
                if divisor == 0.0:
                    raise ValueError("Division by zero")
                value /= divisor
            elif self._match("%"):
                divisor = self._parse_unary()
                if divisor == 0.0:
                    raise ValueError("Modulo by zero")
                value %= divisor
            else:
                return value

    def _parse_unary(self) -> float:
        if self._match("-"):
            return -self._parse_unary()
        return self._parse_power()

    def _parse_power(self) -> float:
        base = self._parse_primary()

        if self._match("^"):
            exponent = self._parse_unary()
            try:
                result = base ** exponent
            except (ZeroDivisionError, OverflowError, ValueError) as exc:
                raise ValueError("Invalid exponentiation") from exc

            if isinstance(result, complex):
                raise ValueError("Expression has a non-real result")
            return float(result)

        return base

    def _parse_primary(self) -> float:
        self._skip_whitespace()

        if self.pos >= len(self.expr):
            raise ValueError("Unexpected end of expression")

        if self._match("("):
            value = self._parse_expression()
            if not self._match(")"):
                raise ValueError("Unbalanced parentheses")
            return value

        char = self.expr[self.pos]

        if "0" <= char <= "9":
            return self._parse_number()

        if self._is_identifier_start(char):
            return self._parse_variable()

        if char == ")":
            raise ValueError("Unbalanced parentheses")

        raise ValueError("Malformed syntax")

    def _parse_number(self) -> float:
        start = self.pos

        while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
            self.pos += 1

        if self.pos < len(self.expr) and self.expr[self.pos] == ".":
            self.pos += 1
            while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                self.pos += 1

        text = self.expr[start:self.pos]
        try:
            return float(text)
        except ValueError as exc:
            raise ValueError("Malformed number") from exc

    def _parse_variable(self) -> float:
        start = self.pos
        self.pos += 1

        while (
            self.pos < len(self.expr)
            and self._is_identifier_part(self.expr[self.pos])
        ):
            self.pos += 1

        name = self.expr[start:self.pos]
        if name not in self.variables:
            raise ValueError(f"Unknown variable: {name}")

        try:
            return float(self.variables[name])
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError(f"Invalid value for variable: {name}") from exc

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return (
            "a" <= char <= "z"
            or "A" <= char <= "Z"
            or char == "_"
        )

    @classmethod
    def _is_identifier_part(cls, char: str) -> bool:
        return cls._is_identifier_start(char) or "0" <= char <= "9"


def evaluate(
    expr: str,
    variables: dict[str, float] | None = None,
) -> float:
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")
    return _Parser(expr, variables).parse()
