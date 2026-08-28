def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    variables = {} if variables is None else variables
    tokens = []
    i = 0

    while i < len(expr):
        char = expr[i]

        if char.isspace():
            i += 1
        elif char.isdigit():
            start = i
            while i < len(expr) and expr[i].isdigit():
                i += 1
            if i < len(expr) and expr[i] == ".":
                i += 1
                if i >= len(expr) or not expr[i].isdigit():
                    raise ValueError("Malformed number")
                while i < len(expr) and expr[i].isdigit():
                    i += 1
            tokens.append(("number", float(expr[start:i])))
        elif char.isalpha() or char == "_":
            start = i
            i += 1
            while i < len(expr) and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(("name", expr[start:i]))
        elif char in "+-*/%^()":
            tokens.append((char, char))
            i += 1
        else:
            raise ValueError("Malformed syntax")

    tokens.append(("eof", None))
    position = 0

    def current():
        return tokens[position][0]

    def consume(kind=None):
        nonlocal position
        if kind is not None and current() != kind:
            raise ValueError("Malformed syntax")
        token = tokens[position]
        position += 1
        return token

    def parse_expression():
        value = parse_term()
        while current() in ("+", "-"):
            op = consume()[0]
            right = parse_term()
            value = value + right if op == "+" else value - right
        return value

    def parse_term():
        value = parse_unary()
        while current() in ("*", "/", "%"):
            op = consume()[0]
            right = parse_unary()
            if op == "/":
                if right == 0:
                    raise ValueError("Division by zero")
                value /= right
            elif op == "%":
                if right == 0:
                    raise ValueError("Modulo by zero")
                value %= right
            else:
                value *= right
        return value

    def parse_unary():
        if current() == "-":
            consume("-")
            return -parse_unary()
        return parse_power()

    def parse_power():
        value = parse_primary()
        if current() == "^":
            consume("^")
            value **= parse_unary()
        return value

    def parse_primary():
        kind, value = tokens[position]
        if kind == "number":
            consume("number")
            return value
        if kind == "name":
            consume("name")
            if value not in variables:
                raise ValueError("Unknown variable")
            return float(variables[value])
        if kind == "(":
            consume("(")
            value = parse_expression()
            consume(")")
            return value
        raise ValueError("Malformed syntax")

    result = parse_expression()
    if current() != "eof":
        raise ValueError("Malformed syntax")
    return float(result)
