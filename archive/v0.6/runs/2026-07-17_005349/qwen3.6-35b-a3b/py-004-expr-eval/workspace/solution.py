def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
        
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c in '+-*/%^()':
            tokens.append(c)
            i += 1
        elif c.isdigit() or c == '.':
            j = i
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(float(expr[i:j]))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            raise ValueError(f"Unexpected character: {c}")
    tokens.append(None) # EOF
    
    pos = 0
    
    def parse_expr():
        nonlocal pos
        pos, left = parse_term()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            pos, right = parse_term()
            if op == '+': left += right
            else: left -= right
        return pos, left

    def parse_term():
        nonlocal pos
        pos, left = parse_power()
        while pos < len(tokens) and tokens[pos] in ('*', '/', '%'):
            op = tokens[pos]
            pos += 1
            pos, right = parse_power()
            if op == '*': left *= right
            elif op == '/':
                if right == 0.0: raise ValueError("division by zero")
                left /= right
            else:
                if right == 0.0: raise ValueError("modulo by zero")
                left %= right
        return pos, left

    def parse_power():
        nonlocal pos
        pos, base = parse_unary()
        if pos < len(tokens) and tokens[pos] == '^':
            pos += 1
            pos, exp = parse_power()
            return pos, base ** exp
        return pos, base

    def parse_unary():
        nonlocal pos
        if pos < len(tokens) and tokens[pos] in ('-', '+'):
            op = tokens[pos]
            pos += 1
            pos, val = parse_unary()
            return pos, val if op == '+' else -val
        return parse_primary()

    def parse_primary():
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")
        tok = tokens[pos]
        if tok == '(':
            pos += 1
            pos, val = parse_expr()
            if pos >= len(tokens) or tokens[pos] != ')':
                raise ValueError("Unbalanced parentheses")
            pos += 1
            return pos, val
        elif isinstance(tok, float):
            pos += 1
            return pos, tok
        elif isinstance(tok, str):
            pos += 1
            if tok in variables:
                return pos, variables[tok]
            else:
                raise ValueError(f"Unknown variable: {tok}")
        else:
            raise ValueError(f"Unexpected token: {tok}")

    pos, result = parse_expr()
    if pos < len(tokens) and tokens[pos] is not None:
        raise ValueError("Unexpected tokens after expression")
    return result
