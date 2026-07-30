def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    variables = variables or {}
    pos = 0
    n = len(expr)

    def peek():
        return expr[pos] if pos < n else None

    def consume():
        nonlocal pos
        tok = expr[pos]
        pos += 1
        return tok

    def skip_ws():
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1

    def parse_number():
        nonlocal pos
        start = pos
        while pos < n and expr[pos].isdigit():
            pos += 1
        if pos < n and expr[pos] == '.':
            pos += 1
            while pos < n and expr[pos].isdigit():
                pos += 1
        return float(expr[start:pos])

    def parse_var():
        nonlocal pos
        start = pos
        while pos < n and (expr[pos].isalnum() or expr[pos] == '_'):
            pos += 1
        name = expr[start:pos]
        if name not in variables:
            raise ValueError(f"unknown variable: {name}")
        return float(variables[name])

    def parse_primary():
        skip_ws()
        p = peek()
        if p is None:
            raise ValueError("unexpected end of expression")
        if p == '(':
            consume()
            val = parse_expr()
            skip_ws()
            if peek() != ')':
                raise ValueError("unbalanced parentheses")
            consume()
            return val
        if p.isdigit() or p == '.':
            return parse_number()
        if p.isalpha() or p == '_':
            return parse_var()
        raise ValueError(f"unexpected character: {p}")

    def parse_power():
        left = parse_primary()
        skip_ws()
        if peek() == '^':
            consume()
            skip_ws()
            right = parse_unary()
            return left ** right
        return left

    def parse_unary():
        skip_ws()
        neg = False
        while peek() == '-':
            consume()
            neg = not neg
        val = parse_power()
        return -val if neg else val

    def parse_term():
        skip_ws()
        left = parse_unary()
        while True:
            skip_ws()
            op = peek()
            if op in ('*', '/', '%'):
                consume()
                skip_ws()
                right = parse_unary()
                if op == '*':
                    left *= right
                elif op == '/':
                    if right == 0:
                        raise ValueError("division by zero")
                    left /= right
                else:
                    if right == 0:
                        raise ValueError("modulo by zero")
                    left %= right
            else:
                break
        return left

    def parse_expr():
        skip_ws()
        left = parse_term()
        while True:
            skip_ws()
            op = peek()
            if op in ('+', '-'):
                consume()
                skip_ws()
                right = parse_term()
                if op == '+':
                    left += right
                else:
                    left -= right
            else:
                break
        return left

    skip_ws()
    result = parse_expr()
    skip_ws()
    if pos < n:
        raise ValueError("unexpected character after expression")
    return float(result)
