def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    pos = 0
    n = len(expr)

    def skip_ws():
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1

    def peek():
        skip_ws()
        return expr[pos] if pos < n else None

    def consume():
        ch = peek()
        nonlocal pos
        if ch is not None:
            pos += 1
        return ch

    def parse_number():
        nonlocal pos
        skip_ws()
        start = pos
        if pos < n and expr[pos] == '.':
            pos += 1
            if pos >= n or not expr[pos].isdigit():
                raise ValueError(f"Malformed number at position {start}")
            while pos < n and expr[pos].isdigit():
                pos += 1
        elif pos < n and expr[pos].isdigit():
            while pos < n and expr[pos].isdigit():
                pos += 1
            if pos < n and expr[pos] == '.':
                pos += 1
                while pos < n and expr[pos].isdigit():
                    pos += 1
        else:
            raise ValueError(f"Expected number at position {pos}")
        return float(expr[start:pos])

    def parse_name():
        nonlocal pos
        skip_ws()
        start = pos
        if pos < n and (expr[pos].isalpha() or expr[pos] == '_'):
            pos += 1
            while pos < n and (expr[pos].isalnum() or expr[pos] == '_'):
                pos += 1
            return expr[start:pos]
        raise ValueError(f"Expected identifier at position {pos}")

    def parse_expr():
        left = parse_term()
        while True:
            ch = peek()
            if ch == '+':
                consume()
                left = left + parse_term()
            elif ch == '-':
                consume()
                left = left - parse_term()
            else:
                break
        return left

    def parse_term():
        left = parse_unary()
        while True:
            ch = peek()
            if ch == '*':
                consume()
                left = left * parse_unary()
            elif ch == '/':
                consume()
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Division by zero")
                left = left / right
            elif ch == '%':
                consume()
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left = left % right
            else:
                break
        return left

    def parse_unary():
        if peek() == '-':
            consume()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_primary()
        if peek() == '^':
            consume()
            exp = parse_unary()
            result = base ** exp
            if isinstance(result, complex):
                raise ValueError("Complex result from exponentiation")
            return result
        return base

    def parse_primary():
        ch = peek()
        if ch is None:
            raise ValueError("Unexpected end of expression")
        if ch == '(':
            consume()
            val = parse_expr()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses: expected ')'")
            consume()
            return val
        if ch.isdigit() or ch == '.':
            return parse_number()
        if ch.isalpha() or ch == '_':
            name = parse_name()
            if name not in variables:
                raise ValueError(f"Unknown variable: '{name}'")
            return float(variables[name])
        raise ValueError(f"Unexpected character: {ch!r} at position {pos}")

    result = parse_expr()
    remaining = peek()
    if remaining is not None:
        raise ValueError(f"Unexpected character: {remaining!r} at position {pos}")
    return float(result)
