import math


class _Parser:
    def __init__(self, expr: str, variables: dict[str, float] | None) -> None:
        self.tokens = self._tokenize(expr)
        self.pos = 0
        self.variables = variables if variables is not None else {}

    @staticmethod
    def _tokenize(expr: str) -> list[tuple[str, str]]:
        tokens: list[tuple[str, str]] = []
        i = 0

        while i < len(expr):
            ch = expr[i]

            if ch.isspace():
                i += 1
                continue

            if "0" <= ch <= "9":
                start = i
                while i < len(expr) and "0" <= expr[i] <= "9":
                    i += 1

                if i < len(expr) and expr[i] == ".":
                    i += 1
                    while i < len(expr) and "0" <= expr[i] <= "9":
                        i += 1

                tokens.append(("NUMBER", expr[start:i]))
                continue

            if (
                "a" <= ch <= "z"
                or "A" <= ch <= "Z"
                or ch == "_"
            ):
                start = i
                i += 1
                while i < len(expr):
                    current = expr[i]
                    if not (
                        "a" <= current <= "z"
                        or "A" <= current <= "Z"
                        or "0" <= current <= "9"
                        or current == "_"
                    ):
                        break
                    i += 1
                tokens.append(("NAME", expr[start:i]))
                continue

            if ch in "+-*/%^()":
                tokens.append((ch, ch))
                i += 1
                continue

            raise ValueError(f"invalid character: {ch!r}")

        tokens.append(("EOF", ""))
        return tokens

    def _current_kind(self) -> str:
        return self.tokens[self.pos][0]

    def _consume(self, kind: str) -> tuple[str, str]:
        token = self.tokens[self.pos]
        if token[0] != kind:
            raise ValueError("malformed expression")
        self.pos += 1
        return token

    def parse(self) -> float:
        result = self._parse_expression()
        if self._current_kind() != "EOF":
            raise ValueError("malformed expression")
        return float(result)

    def _parse_expression(self) -> float:
        result = self._parse_term()

        while self._current_kind() in ("+", "-"):
            operator = self._current_kind()
            self.pos += 1
            right = self._parse_term()

            if operator == "+":
                result += right
            else:
                result -= right

        return result

    def _parse_term(self) -> float:
        result = self._parse_unary()

        while self._current_kind() in ("*", "/", "%"):
            operator = self._current_kind()
            self.pos += 1
            right = self._parse_unary()

            if operator == "*":
                result *= right
            elif operator == "/":
                if right == 0.0:
                    raise ValueError("division by zero")
                result /= right
            else:
                if right == 0.0:
                    raise ValueError("modulo by zero")
                result %= right

        return result

    def _parse_unary(self) -> float:
        if self._current_kind() == "-":
            self.pos += 1
            return -self._parse_unary()
        return self._parse_power()

    def _parse_power(self) -> float:
        left = self._parse_primary()

        if self._current_kind() == "^":
            self.pos += 1
            right = self._parse_unary()
            try:
                return math.pow(left, right)
            except (ValueError, OverflowError, ZeroDivisionError) as exc:
                raise ValueError("invalid exponentiation") from exc

        return left

    def _parse_primary(self) -> float:
        kind, value = self.tokens[self.pos]

        if kind == "NUMBER":
            self.pos += 1
            try:
                return float(value)
            except ValueError as exc:
                raise ValueError("invalid number") from exc

        if kind == "NAME":
            self.pos += 1
            if value not in self.variables:
                raise ValueError(f"unknown variable: {value}")
            try:
                return float(self.variables[value])
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"invalid value for variable: {value}") from exc

        if kind == "(":
            self.pos += 1
            result = self._parse_expression()
            self._consume(")")
            return result

        raise ValueError("malformed expression")


def evaluate(
    expr: str,
    variables: dict[str, float] | None = None,
) -> float:
    if not isinstance(expr, str):
        raise ValueError("expression must be a string")
    return _Parser(expr, variables).parse()
