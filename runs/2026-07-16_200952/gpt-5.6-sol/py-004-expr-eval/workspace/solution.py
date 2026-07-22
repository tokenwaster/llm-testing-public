from __future__ import annotations


def evaluate(
    expr: str, variables: dict[str, float] | None = None
) -> float:
    variables = {} if variables is None else variables
    tokens: list[tuple[str, str]] = []
    index = 0
    length = len(expr)

    def is_letter(char: str) -> bool:
        return ("a" <= char <= "z") or ("A" <= char <= "Z") or char == "_"

    def is_digit(char: str) -> bool:
        return "0" <= char <= "9"

    while index < length:
        char = expr[index]

        if char.isspace():
            index += 1
            continue

        if is_digit(char):
            start = index
            while index < length and is_digit(expr[index]):
                index += 1

            if index < length and expr[index] == ".":
                index += 1
                if index >= length or not is_digit(expr[index]):
                    raise ValueError("Malformed number")
                while index < length and is_digit(expr[index]):
                    index += 1

            tokens.append(("NUMBER", expr[start:index]))
            continue

        if is_letter(char):
            start = index
            index += 1
            while index < length and (
                is_letter(expr[index]) or is_digit(expr[index])
            ):
                index += 1
            tokens.append(("IDENTIFIER", expr[start:index]))
            continue

        if char in "+-*/%^()":
            tokens.append((char, char))
            index += 1
            continue

        raise ValueError(f"Invalid character: {char!r}")

    tokens.append(("EOF", ""))
    position = 0

    def current_kind() -> str:
        return tokens[position][0]

    def consume(expected: str | None = None) -> tuple[str, str]:
        nonlocal position
        token = tokens[position]
        if expected is not None and token[0] != expected:
            raise ValueError("Malformed expression")
        position += 1
        return token

    def parse_expression() -> float:
        return parse_addition()

    def parse_addition() -> float:
        value = parse_multiplication()

        while current_kind() in ("+", "-"):
            operator = consume()[0]
            right = parse_multiplication()
            if operator == "+":
                value += right
            else:
                value -= right

        return float(value)

    def parse_multiplication() -> float:
        value = parse_unary()

        while current_kind() in ("*", "/", "%"):
            operator = consume()[0]
            right = parse_unary()

            if operator == "*":
                value *= right
            elif operator == "/":
                if right == 0.0:
                    raise ValueError("Division by zero")
                value /= right
            else:
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                value %= right

        return float(value)

    def parse_unary() -> float:
        if current_kind() == "-":
            consume("-")
            return float(-parse_unary())
        return parse_power()

    def parse_power() -> float:
        value = parse_primary()

        if current_kind() == "^":
            consume("^")
            exponent = parse_unary()
            try:
                result = value ** exponent
            except ZeroDivisionError as exc:
                raise ValueError("Division by zero") from exc
            except (OverflowError, TypeError) as exc:
                raise ValueError("Invalid exponentiation") from exc

            if isinstance(result, complex):
                raise ValueError("Expression has a non-real result")
            value = float(result)

        return float(value)

    def parse_primary() -> float:
        kind, text = tokens[position]

        if kind == "NUMBER":
            consume("NUMBER")
            return float(text)

        if kind == "IDENTIFIER":
            consume("IDENTIFIER")
            if text not in variables:
                raise ValueError(f"Unknown variable: {text}")
            try:
                return float(variables[text])
            except (TypeError, ValueError, OverflowError) as exc:
                raise ValueError(f"Invalid value for variable: {text}") from exc

        if kind == "(":
            consume("(")
            value = parse_expression()
            if current_kind() != ")":
                raise ValueError("Unbalanced parentheses")
            consume(")")
            return float(value)

        if kind == ")":
            raise ValueError("Unbalanced parentheses")

        raise ValueError("Malformed expression")

    result = parse_expression()

    if current_kind() != "EOF":
        if current_kind() in ("(", ")"):
            raise ValueError("Unbalanced parentheses")
        raise ValueError("Malformed expression")

    return float(result)
