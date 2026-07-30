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

    def consume(expected):
        nonlocal pos
        skip_ws()
        if pos >= n:
            raise ValueError(f"Expected '{expected}' but reached end of expression")
        if expr[pos] != expected:
            raise ValueError(f"Expected '{expected}' but got '{expr[pos]}' at position {pos}")
        pos += 1

    def parse_number():
        nonlocal pos
        skip_ws()
        start = pos
        while pos < n and expr[pos].isdigit():
            pos += 1
        if pos < n and expr[pos] == '.':
            pos += 1
            while pos < n and expr[pos].isdigit():
                pos += 1
        if pos == start:
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
        if pos == start:
            raise ValueError(f"Expected identifier at position {pos}")
        return expr[start:pos]

    def parse_expr():
        left = parse_term()
        while True:
            ch = peek()
            if ch == '+':
                consume('+')
                left += parse_term()
            elif ch == '-':
                consume('-')
                left -= parse_term()
            else:
                break
        return left

    def parse_term():
        left = parse_unary()
        while True:
            ch = peek()
            if ch == '*':
                consume('*')
                left *= parse_unary()
            elif ch == '/':
                consume('/')
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Division by zero")
                left /= right
            elif ch == '%':
                consume('%')
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left %= right
            else:
                break
        return left

    def parse_unary():
        if peek() == '-':
            consume('-')
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_primary()
        if peek() == '^':
            consume('^')
            exp = parse_unary()
            return float(base ** exp)
        return base

    def parse_primary():
        ch = peek()
        if ch is None:
            raise ValueError("Unexpected end of expression")
        if ch == '(':
            consume('(')
            val = parse_expr()
            if peek() != ')':
                got = peek()
                raise ValueError(f"Unbalanced parentheses: expected ')' but got '{got}'")
            consume(')')
            return val
        if ch.isdigit():
            return parse_number()
        if ch.isalpha() or ch == '_':
            name = parse_name()
            if name not in variables:
                raise ValueError(f"Unknown variable: '{name}'")
            return float(variables[name])
        raise ValueError(f"Unexpected character '{ch}' at position {pos}")

    result = parse_expr()
    skip_ws()
    if pos < n:
        raise ValueError(f"Unexpected character '{expr[pos]}' at position {pos}")
    return float(result)
