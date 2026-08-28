def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    variables = {} if variables is None else variables
    length = len(expr)
    pos = 0

    def skip_whitespace() -> None:
        nonlocal pos
        while pos < length and expr[pos].isspace():
            pos += 1

    def parse_expression() -> float:
        value = parse_term()
        while True:
            skip_whitespace()
            if pos < length and expr[pos] in "+-":
                operator = expr[pos]
                advance()
                right = parse_term()
                value = value + right if operator == "+" else value - right
            else:
                return value

    def parse_term() -> float:
        value = parse_unary()
        while True:
            skip_whitespace()
            if pos < length and expr[pos] in "*/%":
                operator = expr[pos]
                advance()
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("division or modulo by zero")
                if operator == "*":
                    value *= right
                elif operator == "/":
                    value /= right
                else:
                    value %= right
            else:
                return value

    def parse_unary() -> float:
        skip_whitespace()
        if pos < length and expr[pos] == "-":
            advance()
            return -parse_unary()
        return parse_power()

    def parse_power() -> float:
        value = parse_primary()
        skip_whitespace()
        if pos < length and expr[pos] == "^":
            advance()
            value = value ** parse_unary()
        return value

    def parse_primary() -> float:
        nonlocal pos
        skip_whitespace()

        if pos >= length:
            raise ValueError("malformed syntax")

        character = expr[pos]

        if character == "(":
            advance()
            value = parse_expression()
            skip_whitespace()
            if pos >= length or expr[pos] != ")":
                raise ValueError("unbalanced parentheses")
            advance()
            return value

        if character.isdigit():
            start = pos
            while pos < length and expr[pos].isdigit():
                pos += 1

            if pos < length and expr[pos] == ".":
                pos += 1
                while pos < length and expr[pos].isdigit():
                    pos += 1

            return float(expr[start:pos])

        if character.isalpha() or character == "_":
            start = pos
            pos += 1
            while pos < length and (expr[pos].isalnum() or expr[pos] == "_"):
                pos += 1
            name = expr[start:pos]
            if name not in variables:
                raise ValueError("unknown variable")
            return float(variables[name])

        raise ValueError("malformed syntax")

    def advance() -> None:
        nonlocal pos
        pos += 1

    skip_whitespace()
    if not expr or pos >= length:
        raise ValueError("malformed syntax")

    result = parse_expression()
    skip_whitespace()

    if pos != length:
        raise ValueError("malformed syntax")

    return float(result)
