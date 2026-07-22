def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    pos = [0]

    def skip_ws():
        while pos[0] < len(expr) and expr[pos[0]].isspace():
            pos[0] += 1

    def parse_primary():
        skip_ws()
        if pos[0] >= len(expr):
            raise ValueError("Unexpected end of expression")
        ch = expr[pos[0]]
        if ch == '(':
            pos[0] += 1
            val = parse_expr()
            skip_ws()
            if pos[0] >= len(expr) or expr[pos[0]] != ')':
                raise ValueError("Unbalanced parentheses")
            pos[0] += 1
            return val
        elif ch.isdigit() or ch == '.':
            start = pos[0]
            while pos[0] < len(expr) and expr[pos[0]].isdigit():
                pos[0] += 1
            if pos[0] < len(expr) and expr[pos[0]] == '.':
                pos[0] += 1
                while pos[0] < len(expr) and expr[pos[0]].isdigit():
                    pos[0] += 1
            s = expr[start:pos[0]]
            if not s or s == '.':
                raise ValueError(f"Malformed number at position {start}")
            return float(s)
        elif ch.isalpha() or ch == '_':
            start = pos[0]
            while pos[0] < len(expr) and (expr[pos[0]].isalnum() or expr[pos[0]] == '_'):
                pos[0] += 1
            name = expr[start:pos[0]]
            if name not in variables:
                raise ValueError(f"Unknown variable: '{name}'")
            return float(variables[name])
        else:
            raise ValueError(f"Unexpected character '{ch}' at position {pos[0]}")

    def parse_power():
        # right-associative: base ^ parse_unary (which can recurse into parse_power)
        base = parse_primary()
        skip_ws()
        if pos[0] < len(expr) and expr[pos[0]] == '^':
            pos[0] += 1
            exp = parse_unary()
            return float(base ** exp)
        return base

    def parse_unary():
        # unary minus binds looser than ^, so it delegates to parse_power
        skip_ws()
        if pos[0] < len(expr) and expr[pos[0]] == '-':
            pos[0] += 1
            return -parse_unary()
        return parse_power()

    def parse_mul():
        left = parse_unary()
        while True:
            skip_ws()
            if pos[0] < len(expr) and expr[pos[0]] in ('*', '/', '%'):
                op = expr[pos[0]]
                pos[0] += 1
                right = parse_unary()
                if op == '*':
                    left *= right
                elif op == '/':
                    if right == 0.0:
                        raise ValueError("Division by zero")
                    left /= right
                else:
                    if right == 0.0:
                        raise ValueError("Modulo by zero")
                    left %= right
            else:
                break
        return left

    def parse_expr():
        left = parse_mul()
        while True:
            skip_ws()
            if pos[0] < len(expr) and expr[pos[0]] in ('+', '-'):
                op = expr[pos[0]]
                pos[0] += 1
                right = parse_mul()
                if op == '+':
                    left += right
                else:
                    left -= right
            else:
                break
        return left

    result = parse_expr()
    skip_ws()
    if pos[0] != len(expr):
        raise ValueError(f"Unexpected character '{expr[pos[0]]}' at position {pos[0]}")
    return float(result)
