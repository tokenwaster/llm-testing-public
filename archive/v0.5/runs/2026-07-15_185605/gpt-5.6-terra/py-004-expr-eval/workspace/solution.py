class _ExpressionParser:
    def __init__(self, text: str, variables: dict[str, float] | None):
        self.text = text
        self.variables = {} if variables is None else variables
        self.pos = 0

    def parse(self) -> float:
        value = self._parse_expression()
        self._skip_whitespace()
        if self.pos != len(self.text):
            raise ValueError("malformed syntax")
        return float(value)

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def _parse_expression(self) -> float:
        value = self._parse_term()

        while True:
            self._skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] not in "+-":
                break

            operator = self.text[self.pos]
            self.pos += 1
            right = self._parse_term()

            if operator == "+":
                value += right
            else:
                value -= right

        return float(value)

    def _parse_term(self) -> float:
        value = self._parse_unary()

        while True:
            self._skip_whitespace()
            if self.pos >= len(self.text) or self.text[self.pos] not in "*/%":
                break

            operator = self.text[self.pos]
            self.pos += 1
            right = self._parse_unary()

            if right == 0:
                raise ValueError("division or modulo by zero")

            if operator == "*":
                value *= right
            elif operator == "/":
                value /= right
            else:
                value %= right

        return float(value)

    def _parse_unary(self) -> float:
        self._skip_whitespace()

        if self.pos < len(self.text) and self.text[self.pos] == "-":
            self.pos += 1
            return float(-self._parse_unary())

        return self._parse_power()

    def _parse_power(self) -> float:
        base = self._parse_primary()

        self._skip_whitespace()
        if self.pos < len(self.text) and self.text[self.pos] == "^":
            self.pos += 1
            exponent = self._parse_unary()

            try:
                result = base ** exponent
            except (ZeroDivisionError, OverflowError, ValueError):
                raise ValueError("invalid exponentiation") from None

            if isinstance(result, complex):
                raise ValueError("invalid exponentiation")

            return float(result)

        return float(base)

    def _parse_primary(self) -> float:
        self._skip_whitespace()

        if self.pos >= len(self.text):
            raise ValueError("malformed syntax")

        current = self.text[self.pos]

        if current == "(":
            self.pos += 1
            value = self._parse_expression()
            self._skip_whitespace()

            if self.pos >= len(self.text) or self.text[self.pos] != ")":
                raise ValueError("unbalanced parentheses")

            self.pos += 1
            return float(value)

        if current.isdigit():
            return self._parse_number()

        if current.isalpha() or current == "_":
            return self._parse_variable()

        raise ValueError("malformed syntax")

    def _parse_number(self) -> float:
        start = self.pos

        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1

        if self.pos < len(self.text) and self.text[self.pos] == ".":
            self.pos += 1
            decimal_start = self.pos

            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1

            if self.pos == decimal_start:
                raise ValueError("malformed syntax")

        return float(self.text[start:self.pos])

    def _parse_variable(self) -> float:
        start = self.pos
        self.pos += 1

        while self.pos < len(self.text):
            char = self.text[self.pos]
            if not (char.isalnum() or char == "_"):
                break
            self.pos += 1

        name = self.text[start:self.pos]

        if name not in self.variables:
            raise ValueError("unknown variable")

        try:
            return float(self.variables[name])
        except (TypeError, ValueError):
            raise ValueError("invalid variable value") from None


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if not isinstance(expr, str):
        raise ValueError("expression must be a string")

    return _ExpressionParser(expr, variables).parse()
