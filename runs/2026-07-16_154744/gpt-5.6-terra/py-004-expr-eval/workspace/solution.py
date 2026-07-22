def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    class Parser:
        def __init__(self, text: str, values: dict[str, float] | None):
            self.text = text
            self.variables = values if values is not None else {}
            self.pos = 0

        def error(self) -> None:
            raise ValueError("malformed expression")

        def skip_whitespace(self) -> None:
            while self.pos < len(self.text) and self.text[self.pos].isspace():
                self.pos += 1

        def peek(self) -> str | None:
            self.skip_whitespace()
            if self.pos >= len(self.text):
                return None
            return self.text[self.pos]

        @staticmethod
        def is_digit(char: str) -> bool:
            return "0" <= char <= "9"

        @staticmethod
        def is_identifier_start(char: str) -> bool:
            return ("a" <= char <= "z") or ("A" <= char <= "Z") or char == "_"

        @staticmethod
        def is_identifier_part(char: str) -> bool:
            return (
                ("a" <= char <= "z")
                or ("A" <= char <= "Z")
                or ("0" <= char <= "9")
                or char == "_"
            )

        def parse(self) -> float:
            result = self.parse_expression()
            if self.peek() is not None:
                self.error()
            return float(result)

        def parse_expression(self) -> float:
            value = self.parse_term()

            while True:
                char = self.peek()
                if char == "+":
                    self.pos += 1
                    value += self.parse_term()
                elif char == "-":
                    self.pos += 1
                    value -= self.parse_term()
                else:
                    return value

        def parse_term(self) -> float:
            value = self.parse_unary()

            while True:
                char = self.peek()
                if char == "*":
                    self.pos += 1
                    value *= self.parse_unary()
                elif char == "/":
                    self.pos += 1
                    divisor = self.parse_unary()
                    if divisor == 0:
                        raise ValueError("division by zero")
                    value /= divisor
                elif char == "%":
                    self.pos += 1
                    divisor = self.parse_unary()
                    if divisor == 0:
                        raise ValueError("modulo by zero")
                    value %= divisor
                else:
                    return value

        def parse_unary(self) -> float:
            if self.peek() == "-":
                self.pos += 1
                return -self.parse_unary()
            return self.parse_power()

        def parse_power(self) -> float:
            value = self.parse_primary()

            if self.peek() == "^":
                self.pos += 1
                exponent = self.parse_unary()
                try:
                    value = value ** exponent
                except (ZeroDivisionError, OverflowError, ValueError):
                    raise ValueError("invalid exponentiation") from None

                if isinstance(value, complex):
                    raise ValueError("invalid exponentiation")

            return value

        def parse_primary(self) -> float:
            char = self.peek()

            if char is None:
                self.error()

            if char == "(":
                self.pos += 1
                value = self.parse_expression()
                if self.peek() != ")":
                    self.error()
                self.pos += 1
                return value

            if char is not None and self.is_digit(char):
                return self.parse_number()

            if char is not None and self.is_identifier_start(char):
                return self.parse_identifier()

            self.error()

        def parse_number(self) -> float:
            start = self.pos

            while self.pos < len(self.text) and self.is_digit(self.text[self.pos]):
                self.pos += 1

            if self.pos < len(self.text) and self.text[self.pos] == ".":
                self.pos += 1
                decimal_start = self.pos

                while self.pos < len(self.text) and self.is_digit(self.text[self.pos]):
                    self.pos += 1

                if self.pos == decimal_start:
                    self.error()

            return float(self.text[start:self.pos])

        def parse_identifier(self) -> float:
            start = self.pos
            self.pos += 1

            while (
                self.pos < len(self.text)
                and self.is_identifier_part(self.text[self.pos])
            ):
                self.pos += 1

            name = self.text[start:self.pos]

            if name not in self.variables:
                raise ValueError(f"unknown variable: {name}")

            try:
                return float(self.variables[name])
            except (TypeError, ValueError, OverflowError):
                raise ValueError(f"invalid value for variable: {name}") from None

    try:
        return Parser(expr, variables).parse()
    except RecursionError:
        raise ValueError("expression is too deeply nested") from None
