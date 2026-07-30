class _Parser:
    def __init__(self, text: str, variables: dict[str, float] | None):
        self.text = text
        self.variables = variables or {}
        self.pos = 0
        self.length = len(text)

    def _skip_whitespace(self) -> None:
        while self.pos < self.length and self.text[self.pos].isspace():
            self.pos += 1

    def _error(self, message: str = "Malformed expression") -> None:
        raise ValueError(message)

    def parse(self) -> float:
        value = self._parse_additive()
        self._skip_whitespace()
        if self.pos != self.length:
            self._error()
        return float(value)

    def _parse_additive(self) -> float:
        value = self._parse_multiplicative()

        while True:
            self._skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] not in "+-":
                return value

            operator = self.text[self.pos]
            self.pos += 1
            right = self._parse_multiplicative()

            if operator == "+":
                value = value + right
            else:
                value = value - right

    def _parse_multiplicative(self) -> float:
        value = self._parse_unary()

        while True:
            self._skip_whitespace()
            if self.pos >= self.length or self.text[self.pos] not in "*/%":
                return value

            operator = self.text[self.pos]
            self.pos += 1
            right = self._parse_unary()

            if operator == "*":
                value = value * right
            elif right == 0.0:
                self._error("Division or modulo by zero")
            elif operator == "/":
                value = value / right
            else:
                value = value % right

    def _parse_unary(self) -> float:
        self._skip_whitespace()

        if self.pos < self.length and self.text[self.pos] == "-":
            self.pos += 1
            return -self._parse_unary()

        return self._parse_power()

    def _parse_power(self) -> float:
        value = self._parse_primary()
        self._skip_whitespace()

        if self.pos < self.length and self.text[self.pos] == "^":
            self.pos += 1
            exponent = self._parse_unary()
            try:
                value = value ** exponent
            except (OverflowError, TypeError, ValueError, ZeroDivisionError):
                self._error("Invalid exponentiation")

            if isinstance(value, complex):
                self._error("Invalid exponentiation")

            value = float(value)

        return value

    def _parse_primary(self) -> float:
        self._skip_whitespace()

        if self.pos >= self.length:
            self._error()

        character = self.text[self.pos]

        if character == "(":
            self.pos += 1
            value = self._parse_additive()
            self._skip_whitespace()

            if self.pos >= self.length or self.text[self.pos] != ")":
                self._error("Unbalanced parentheses")

            self.pos += 1
            return value

        if "0" <= character <= "9":
            return self._parse_number()

        if ("a" <= character <= "z" or
                "A" <= character <= "Z" or
                character == "_"):
            return self._parse_variable()

        self._error()

    def _parse_number(self) -> float:
        start = self.pos

        while self.pos < self.length and "0" <= self.text[self.pos] <= "9":
            self.pos += 1

        if self.pos < self.length and self.text[self.pos] == ".":
            self.pos += 1
            while self.pos < self.length and "0" <= self.text[self.pos] <= "9":
                self.pos += 1

        literal = self.text[start:self.pos]
        try:
            return float(literal)
        except (TypeError, ValueError, OverflowError):
            self._error("Invalid number")

    def _parse_variable(self) -> float:
        start = self.pos
        self.pos += 1

        while self.pos < self.length:
            character = self.text[self.pos]
            if ("a" <= character <= "z" or
                    "A" <= character <= "Z" or
                    "0" <= character <= "9" or
                    character == "_"):
                self.pos += 1
            else:
                break

        name = self.text[start:self.pos]
        if name not in self.variables:
            self._error(f"Unknown variable: {name}")

        try:
            return float(self.variables[name])
        except (TypeError, ValueError, OverflowError):
            self._error(f"Invalid value for variable: {name}")


def evaluate(
    expr: str,
    variables: dict[str, float] | None = None
) -> float:
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")
    return _Parser(expr, variables).parse()
