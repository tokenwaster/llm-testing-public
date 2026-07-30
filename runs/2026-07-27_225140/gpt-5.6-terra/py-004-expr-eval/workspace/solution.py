def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    def is_letter(char: str) -> bool:
        return ("a" <= char <= "z") or ("A" <= char <= "Z")

    def is_digit(char: str) -> bool:
        return "0" <= char <= "9"

    def tokenize(text: str) -> list[tuple[str, object]]:
        tokens: list[tuple[str, object]] = []
        i = 0

        while i < len(text):
            char = text[i]

            if char.isspace():
                i += 1
                continue

            if is_digit(char):
                start = i
                while i < len(text) and is_digit(text[i]):
                    i += 1

                if i < len(text) and text[i] == ".":
                    i += 1
                    if i >= len(text) or not is_digit(text[i]):
                        raise ValueError("Malformed number")

                    while i < len(text) and is_digit(text[i]):
                        i += 1

                tokens.append(("NUMBER", float(text[start:i])))
                continue

            if is_letter(char) or char == "_":
                start = i
                i += 1
                while i < len(text) and (
                    is_letter(text[i]) or is_digit(text[i]) or text[i] == "_"
                ):
                    i += 1
                tokens.append(("NAME", text[start:i]))
                continue

            if char in "+-*/%^()":
                tokens.append((char, char))
                i += 1
                continue

            raise ValueError("Invalid character in expression")

        tokens.append(("EOF", None))
        return tokens

    class Parser:
        def __init__(self, tokens: list[tuple[str, object]], values: dict[str, float]):
            self.tokens = tokens
            self.values = values
            self.index = 0

        def current(self) -> tuple[str, object]:
            return self.tokens[self.index]

        def consume(self, kind: str) -> object:
            if self.current()[0] != kind:
                raise ValueError("Malformed syntax")
            value = self.current()[1]
            self.index += 1
            return value

        def parse(self) -> float:
            value = self.parse_additive()
            if self.current()[0] != "EOF":
                raise ValueError("Malformed syntax")
            return float(value)

        def parse_additive(self) -> float:
            value = self.parse_multiplicative()

            while self.current()[0] in ("+", "-"):
                operator = self.current()[0]
                self.index += 1
                right = self.parse_multiplicative()

                if operator == "+":
                    value += right
                else:
                    value -= right

            return float(value)

        def parse_multiplicative(self) -> float:
            value = self.parse_unary()

            while self.current()[0] in ("*", "/", "%"):
                operator = self.current()[0]
                self.index += 1
                right = self.parse_unary()

                if operator == "*":
                    value *= right
                elif operator == "/":
                    if right == 0:
                        raise ValueError("Division by zero")
                    value /= right
                else:
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    value %= right

            return float(value)

        def parse_unary(self) -> float:
            if self.current()[0] == "-":
                self.index += 1
                return -self.parse_unary()

            return self.parse_power()

        def parse_power(self) -> float:
            base = self.parse_primary()

            if self.current()[0] == "^":
                self.index += 1
                exponent = self.parse_unary()
                try:
                    result = base ** exponent
                except (ZeroDivisionError, OverflowError, ValueError):
                    raise ValueError("Invalid exponentiation") from None

                if isinstance(result, complex):
                    raise ValueError("Exponentiation produced a non-real result")

                return float(result)

            return float(base)

        def parse_primary(self) -> float:
            kind, value = self.current()

            if kind == "NUMBER":
                self.index += 1
                return float(value)

            if kind == "NAME":
                self.index += 1
                name = str(value)
                if name not in self.values:
                    raise ValueError("Unknown variable")
                try:
                    return float(self.values[name])
                except (TypeError, ValueError, OverflowError):
                    raise ValueError("Invalid variable value") from None

            if kind == "(":
                self.index += 1
                result = self.parse_additive()
                self.consume(")")
                return float(result)

            raise ValueError("Malformed syntax")

    return Parser(tokenize(expr), variables if variables is not None else {}).parse()
