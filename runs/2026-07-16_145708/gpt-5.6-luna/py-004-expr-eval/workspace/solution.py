def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch.isdigit():
            start = i
            while i < n and expr[i].isdigit():
                i += 1
            if i < n and expr[i] == ".":
                i += 1
                while i < n and expr[i].isdigit():
                    i += 1
            tokens.append(("NUMBER", expr[start:i]))
            continue

        if ch.isalpha() or ch == "_":
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(("NAME", expr[start:i]))
            continue

        if ch in "+-*/%^()":
            tokens.append((ch, ch))
            i += 1
            continue

        raise ValueError(f"invalid character: {ch!r}")

    tokens.append(("EOF", ""))
    position = 0

    def current():
        return tokens[position][0]

    def consume(kind=None):
        nonlocal position
        token = tokens[position]
        if kind is not None and token[0] != kind:
            raise ValueError("malformed syntax")
        position += 1
        return token

    def parse_expression() -> float:
        value = parse_term()

        while current() in ("+", "-"):
            operator = consume()[0]
            right = parse_term()
            if operator == "+":
                value += right
            else:
                value -= right

        return value

    def parse_term() -> float:
        value = parse_unary()

        while current() in ("*", "/", "%"):
            operator = consume()[0]
            right = parse_unary()

            if operator == "*":
                value *= right
            elif operator == "/":
                try:
                    value /= right
                except ZeroDivisionError:
                    raise ValueError("division by zero") from None
            else:
                try:
                    value %= right
                except ZeroDivisionError:
                    raise ValueError("modulo by zero") from None

        return value

    def parse_unary() -> float:
        if current() == "-":
            consume("-")
            return -parse_unary()
        return parse_power()

    def parse_power() -> float:
        value = parse_primary()

        if current() == "^":
            consume("^")
            exponent = parse_unary()
            try:
                value = value ** exponent
                value = float(value)
            except (ZeroDivisionError, OverflowError, TypeError, ValueError):
                raise ValueError("invalid exponentiation") from None

        return value

    def parse_primary() -> float:
        token_type, token_value = tokens[position]

        if token_type == "NUMBER":
            consume("NUMBER")
            try:
                return float(token_value)
            except ValueError:
                raise ValueError("malformed number") from None

        if token_type == "NAME":
            consume("NAME")
            if variables is None or token_value not in variables:
                raise ValueError(f"unknown variable: {token_value}")
            try:
                return float(variables[token_value])
            except (TypeError, ValueError):
                raise ValueError(f"invalid value for variable: {token_value}") from None

        if token_type == "(":
            consume("(")
            value = parse_expression()
            if current() != ")":
                raise ValueError("unbalanced parentheses")
            consume(")")
            return value

        raise ValueError("malformed syntax")

    result = parse_expression()

    if current() != "EOF":
        if current() in (")", "("):
            raise ValueError("unbalanced parentheses")
        raise ValueError("malformed syntax")

    return float(result)
