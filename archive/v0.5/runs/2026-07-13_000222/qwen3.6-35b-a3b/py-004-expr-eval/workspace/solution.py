def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        if expr[i].isspace():
            i += 1
            continue
        if expr[i].isdigit() or (expr[i] == '.' and i + 1 < n and expr[i+1].isdigit()):
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUMBER', float(expr[i:j])))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VARIABLE', expr[i:j]))
            i = j
        elif expr[i] in '+-*/%^()':
            tokens.append((expr[i], expr[i]))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {expr[i]}")
    tokens.append(('EOF', None))
    
    pos = 0
    
    def peek():
        return tokens[pos]
    
    def consume(expected_type=None, expected_val=None):
        nonlocal pos
        tok = tokens[pos]
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok[0]}")
        if expected_val and tok[1] != expected_val:
            raise ValueError(f"Expected '{expected_val}', got '{tok[1]}'")
        pos += 1
        return tok
    
    def parse_expr():
        left = parse_term()
        while peek()[0] in ('+', '-'):
            op = consume()[1]
            right = parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def parse_term():
        left = parse_power()
        while peek()[0] in ('*', '/', '%'):
            op = consume()[1]
            right = parse_power()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_power():
        base = parse_unary()
        if peek()[0] == '^':
            consume()
            return base ** parse_power()
        return base

    def parse_unary():
        if peek()[0] == '-':
            consume()
            return -parse_power()
        return parse_primary()

    def parse_primary():
        tok = peek()
        if tok[0] == 'NUMBER':
            consume()
            return tok[1]
        elif tok[0] == 'VARIABLE':
            consume()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return variables[name]
        elif tok[0] == '(':
            consume()
            val = parse_expr()
            if peek()[0] != ')':
                raise ValueError("Unbalanced parentheses")
            consume()
            return val
        elif tok[0] == 'EOF':
            raise ValueError("Unexpected end of expression")
        else:
            raise ValueError(f"Unexpected token: {tok}")

    result = parse_expr()
    if peek()[0] != 'EOF':
        raise ValueError("Unexpected tokens after expression")
    return result
