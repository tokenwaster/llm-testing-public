def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens: list[str] = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == '.':
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif ch.isalpha() or ch == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif ch in '+-*/%^()':
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"Invalid character: {ch!r}")

    pos = 0

    def peek() -> str | None:
        return tokens[pos] if pos < len(tokens) else None

    def consume() -> str:
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expr() -> float:
        return parse_additive()

    def parse_additive() -> float:
        left = parse_multiplicative()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_multiplicative()
            left = left + right if op == '+' else left - right
        return left

    def parse_multiplicative() -> float:
        left = parse_unary()
        while peek() in ('*', '/', '%'):
            op = consume()
            right = parse_unary()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0.0:
                    raise ValueError("Division by zero")
                left = left / right
            else:
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_unary() -> float:
        if peek() == '-':
            consume()
            return -parse_unary()
        return parse_power()

    def parse_power() -> float:
        base = parse_primary()
        if peek() == '^':
            consume()
            exp = parse_unary()
            return float(base ** exp)
        return base

    def parse_primary() -> float:
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if tok == '(':
            consume()
            val = parse_expr()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            consume()
            return val
        if tok == ')':
            raise ValueError("Unbalanced parentheses: unexpected ')'")
        # Try number
        if tok[0].isdigit() or tok[0] == '.':
            consume()
            try:
                return float(tok)
            except ValueError:
                raise ValueError(f"Malformed number: {tok!r}")
        # Try variable
        if tok[0].isalpha() or tok[0] == '_':
            consume()
            if tok not in variables:
                raise ValueError(f"Unknown variable: {tok!r}")
            return float(variables[tok])
        raise ValueError(f"Unexpected token: {tok!r}")

    result = parse_expr()
    if pos < len(tokens):
        raise ValueError(f"Unexpected token: {tokens[pos]!r}")
    return float(result)
