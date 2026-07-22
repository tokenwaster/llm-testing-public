def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    pos = 0

    def skip_ws():
        nonlocal pos
        while pos < len(expr) and expr[pos].isspace():
            pos += 1

    def peek():
        skip_ws()
        return expr[pos] if pos < len(expr) else None

    def consume_char():
        skip_ws()
        if pos >= len(expr):
            raise ValueError("Unexpected end of expression")
        nonlocal pos
        ch = expr[pos]
        pos += 1
        return ch

    def parse_number():
        nonlocal pos
        skip_ws()
        start = pos
        if pos >= len(expr) or not expr[pos].isdigit():
            raise ValueError(f"Expected digit at position {pos}")
        while pos < len(expr) and expr[pos].isdigit():
            pos += 1
        if pos < len(expr) and expr[pos] == '.':
            pos += 1
            while pos < len(expr) and expr[pos].isdigit():
                pos += 1
        return float(expr[start:pos])

    def parse_name():
        nonlocal pos
        skip_ws()
        start = pos
        if pos >= len(expr) or not (expr[pos].isalpha() or expr[pos] == '_'):
            raise ValueError(f"Expected identifier at position {pos}")
        while pos < len(expr) and (expr[pos].isalnum() or expr[pos] == '_'):
            pos += 1
        return expr[start:pos]

    def parse_primary():
        ch = peek()
        if ch is None:
            raise ValueError("Unexpected end of expression")
        if ch == '(':
            consume_char()
            val = parse_additive()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses: expected ')'")
            consume_char()
            return val
        if ch.isdigit():
            return parse_number()
        if ch.isalpha() or ch == '_':
            name = parse_name()
            if name not in variables:
                raise ValueError(f"Unknown variable: '{name}'")
            return float(variables[name])
        raise ValueError(f"Unexpected character '{ch}' at position {pos}")

    def parse_power():
        # power = primary ('^' unary)?   right-associative via recursive unary call
        base = parse_primary()
        if peek() == '^':
            consume_char()
            exp = parse_unary()
            return float(base ** exp)
        return float(base)

    def parse_unary():
        # unary minus binds looser than ^: -2^2 = -(2^2) = -4
        if peek() == '-':
            consume_char()
            return -parse_unary()
        return parse_power()

    def parse_multiplicative():
        left = parse_unary()
        while True:
            ch = peek()
            if ch == '*':
                consume_char()
                left *= parse_unary()
            elif ch == '/':
                consume_char()
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Division by zero")
                left /= right
            elif ch == '%':
                consume_char()
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left %= right
            else:
                break
        return left

    def parse_additive():
        left = parse_multiplicative()
        while True:
            ch = peek()
            if ch == '+':
                consume_char()
                left += parse_multiplicative()
            elif ch == '-':
                consume_char()
                left -= parse_multiplicative()
            else:
                break
        return left

    result = parse_additive()
    remaining = peek()
    if remaining is not None:
        raise ValueError(f"Unexpected character '{remaining}' at position {pos}")
    return float(result)
