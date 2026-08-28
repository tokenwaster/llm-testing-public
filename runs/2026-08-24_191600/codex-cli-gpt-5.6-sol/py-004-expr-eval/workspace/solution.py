from __future__ import annotations


class _Parser:
    def __init__(self, expr: str, variables: dict[str, float] | None):
        if not isinstance(expr, str):
            raise ValueError("Expression must be a string")
        self.expr = expr
        self.variables = variables or {}
        self.pos = 0

    def parse(self) -> float:
        try:
            value = self._expression()
            self._skip_whitespace()
            if self.pos != len(self.expr):
                raise ValueError("Malformed syntax")
            return float(value)
        except ZeroDivisionError:
            raise ValueError("Division or modulo by zero") from None
        except (OverflowError, TypeError):
            raise ValueError("Invalid arithmetic operation") from None

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.expr) and self.expr[self.pos].isspace():
            self.pos += 1

    def _consume(self, character: str) -> bool:
        self._skip_whitespace()
        if self.pos < len(self.expr) and self.expr[self.pos] == character:
            self.pos += 1
            return True
        return False

    def _expression(self) -> float:
        value = self._term()
        while True:
            if self._consume("+"):
                value += self._term()
            elif self._consume("-"):
                value -= self._term()
            else:
                return value

    def _term(self) -> float:
        value = self._unary()
        while True:
            if self._consume("*"):
                value *= self._unary()
            elif self._consume("/"):
                divisor = self._unary()
                if divisor == 0:
                    raise ValueError("Division by zero")
                value /= divisor
            elif self._consume("%"):
                divisor = self._unary()
                if divisor == 0:
                    raise ValueError("Modulo by zero")
                value %= divisor
            else:
                return value

    def _unary(self) -> float:
        if self._consume("-"):
            return -self._unary()
        return self._power()

    def _power(self) -> float:
        value = self._primary()
        if self._consume("^"):
            value = value ** self._unary()
            if isinstance(value, complex):
                raise ValueError("Complex results are not supported")
        return value

    def _primary(self) -> float:
        self._skip_whitespace()

        if self._consume("("):
            value = self._expression()
            if not self._consume(")"):
                raise ValueError("Unbalanced parentheses")
            return value

        self._skip_whitespace()
        if self.pos >= len(self.expr):
            raise ValueError("Malformed syntax")

        character = self.expr[self.pos]
        if character.isdigit():
            return self._number()
        if character.isalpha() or character == "_":
            return self._variable()
        if character == ")":
            raise ValueError("Unbalanced parentheses")
        raise ValueError("Malformed syntax")

    def _number(self) -> float:
        start = self.pos

        while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
            self.pos += 1

        if self.pos < len(self.expr) and self.expr[self.pos] == ".":
            self.pos += 1
            decimal_start = self.pos
            while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                self.pos += 1
            if self.pos == decimal_start:
                raise ValueError("Malformed number")

        return float(self.expr[start:self.pos])

    def _variable(self) -> float:
        start = self.pos
        self.pos += 1

        while self.pos < len(self.expr):
            character = self.expr[self.pos]
            if not (character.isalnum() or character == "_"):
                break
            self.pos += 1

        name = self.expr[start:self.pos]
        if name not in self.variables:
            raise ValueError(f"Unknown variable: {name}")

        try:
            return float(self.variables[name])
        except (TypeError, ValueError):
            raise ValueError(f"Invalid value for variable: {name}") from None


def evaluate(
    expr: str,
    variables: dict[str, float] | None = None,
) -> float:
    return _Parser(expr, variables).parse()
