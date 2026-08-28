def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    variables = {} if variables is None else variables
    position = 0
    length = len(expr)

    def skip_whitespace() -> None:
        nonlocal position
        while position < length and expr[position].isspace():
            position += 1

    def consume(symbol: str) -> bool:
        nonlocal position
        skip_whitespace()
        if position < length and expr[position] == symbol:
            position += 1
            return True
        return False

    def parse_expression() -> float:
        value = parse_term()
        while True:
            if consume("+"):
                value += parse_term()
            elif consume("-"):
                value -= parse_term()
            else:
                return value

    def parse_term() -> float:
        value = parse_unary()
        while True:
            if consume("*"):
                value *= parse_unary()
            elif consume("/"):
                divisor = parse_unary()
                if divisor == 0:
                    raise ValueError("division by zero")
                value /= divisor
            elif consume("%"):
                divisor = parse_unary()
                if divisor == 0:
                    raise ValueError("modulo by zero")
                value %= divisor
            else:
                return value

    def parse_unary() -> float:
        if consume("-"):
            return -parse_unary()
        return parse_power()

    def parse_power() -> float:
        value = parse_primary()
        if consume("^"):
            exponent = parse_unary()
            try:
                result = value ** exponent
            except (ArithmeticError, ValueError, TypeError) as error:
                raise ValueError("invalid exponentiation") from error
            if isinstance(result, complex):
                raise ValueError("expression has no real result")
            value = float(result)
        return value

    def parse_primary() -> float:
        nonlocal position
        skip_whitespace()

        if position >= length:
            raise ValueError("unexpected end of expression")

        if consume("("):
            value = parse_expression()
            if not consume(")"):
                raise ValueError("unbalanced parentheses")
            return value

        character = expr[position]

        if character.isdigit():
            start = position
            while position < length and expr[position].isdigit():
                position += 1

            if position < length and expr[position] == ".":
                position += 1
                while position < length and expr[position].isdigit():
                    position += 1

            try:
                return float(expr[start:position])
            except ValueError as error:
                raise ValueError("invalid number") from error

        if character.isalpha() or character == "_":
            start = position
            position += 1
            while position < length and (
                expr[position].isalnum() or expr[position] == "_"
            ):
                position += 1

            name = expr[start:position]
            if name not in variables:
                raise ValueError(f"unknown variable: {name}")

            try:
                return float(variables[name])
            except (TypeError, ValueError, OverflowError) as error:
                raise ValueError(f"invalid value for variable: {name}") from error

        if character == ")":
            raise ValueError("unbalanced parentheses")

        raise ValueError(f"unexpected character: {character}")

    if not isinstance(expr, str):
        raise ValueError("expression must be a string")

    result = parse_expression()
    skip_whitespace()

    if position != length:
        if expr[position] == ")":
            raise ValueError("unbalanced parentheses")
        raise ValueError("malformed syntax")

    return float(result)
