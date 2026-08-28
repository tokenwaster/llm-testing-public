def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    variables = {} if variables is None else variables
    tokens = []
    i = 0

    def is_name_start(ch: str) -> bool:
        return ("a" <= ch <= "z") or ("A" <= ch <= "Z") or ch == "_"

    def is_name_char(ch: str) -> bool:
        return is_name_start(ch) or ("0" <= ch <= "9")

    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif ch in "+-*/%^()":
            tokens.append(ch)
            i += 1
        elif "0" <= ch <= "9":
            start = i
            while i < len(expr) and "0" <= expr[i] <= "9":
                i += 1
            if i < len(expr) and expr[i] == ".":
                i += 1
                if i >= len(expr) or not ("0" <= expr[i] <= "9"):
                    raise ValueError("malformed number")
                while i < len(expr) and "0" <= expr[i] <= "9":
                    i += 1
            tokens.append(float(expr[start:i]))
        elif is_name_start(ch):
            start = i
            i += 1
            while i < len(expr) and is_name_char(expr[i]):
                i += 1
            tokens.append(expr[start:i])
        else:
            raise ValueError("invalid character")

    pos = 0

    def parse_expression() -> float:
        nonlocal pos
        value = parse_term()
        while pos < len(tokens) and tokens[pos] in ("+", "-"):
            op = tokens[pos]
            pos += 1
            right = parse_term()
            value = value + right if op == "+" else value - right
        return value

    def parse_term() -> float:
        nonlocal pos
        value = parse_unary()
        while pos < len(tokens) and tokens[pos] in ("*", "/", "%"):
            op = tokens[pos]
            pos += 1
            right = parse_unary()
            if op == "*":
                value *= right
            elif op == "/":
                if right == 0:
                    raise ValueError("division by zero")
                value /= right
            else:
                if right == 0:
                    raise ValueError("modulo by zero")
                value %= right
        return value

    def parse_unary() -> float:
        nonlocal pos
        if pos < len(tokens) and tokens[pos] == "-":
            pos += 1
            return -parse_unary()
        return parse_power()

    def parse_power() -> float:
        nonlocal pos
        value = parse_primary()
        if pos < len(tokens) and tokens[pos] == "^":
            pos += 1
            exponent = parse_unary()
            try:
                value = value ** exponent
            except (ZeroDivisionError, OverflowError, ValueError):
                raise ValueError("invalid exponentiation") from None
            if isinstance(value, complex):
                raise ValueError("invalid exponentiation")
        return value

    def parse_primary() -> float:
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("expected value")

        token = tokens[pos]
        pos += 1

        if isinstance(token, float):
            return token

        if token == "(":
            value = parse_expression()
            if pos >= len(tokens) or tokens[pos] != ")":
                raise ValueError("unbalanced parentheses")
            pos += 1
            return value

        if isinstance(token, str) and token not in "+-*/%^()":
            if token not in variables:
                raise ValueError("unknown variable")
            try:
                return float(variables[token])
            except (TypeError, ValueError):
                raise ValueError("invalid variable value") from None

        raise ValueError("malformed syntax")

    if not tokens:
        raise ValueError("malformed syntax")

    result = parse_expression()
    if pos != len(tokens):
        raise ValueError("malformed syntax")
    return float(result)
