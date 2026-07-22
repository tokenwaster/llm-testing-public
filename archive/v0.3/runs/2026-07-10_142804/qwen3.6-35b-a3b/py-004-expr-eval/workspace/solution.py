def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    # Tokenizer
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        if expr[i].isspace():
            i += 1
            continue
        if expr[i].isdigit() or (expr[i] == '.' and i + 1 < n and expr[i+1].isdigit()):
            j = i
            if expr[j] == '.':
                j += 1
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(('NUM', expr[i:j]))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('NAME', expr[i:j]))
            i = j
        elif expr[i] in '+-*/%^()':
            tokens.append(('OP', expr[i]))
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
        pos += 1
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok[0]}")
        if expected_val is not None and tok[1] != expected_val:
            raise ValueError(f"Expected '{expected_val}', got '{tok[1]}'")
        return tok
    
    def parse_expr():
        left = parse_term()
        while peek()[0] == 'OP' and peek()[1] in '+-':
            op = consume()[1]
            right = parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def parse_term():
        left = parse_unary()
        while peek()[0] == 'OP' and peek()[1] in '*/%':
            op = consume()[1]
            right = parse_unary()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_unary():
        if peek()[0] == 'OP' and peek()[1] in '-+':
            op = consume()[1]
            val = parse_unary()
            if op == '-':
                return -val
            else:
                return val
        return parse_power()

    def parse_power():
        base = parse_primary()
        if peek()[0] == 'OP' and peek()[1] == '^':
            consume()
            exp = parse_unary()
            if base == 0 and exp < 0:
                raise ValueError("Division by zero")
            return base ** exp
        return base

    def parse_primary():
        tok = peek()
        if tok[0] == 'NUM':
            consume()
            return float(tok[1])
        elif tok[0] == 'NAME':
            consume()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return variables[name]
        elif tok[0] == 'OP' and tok[1] == '(':
            consume()
            val = parse_expr()
            if peek()[0] != 'OP' or peek()[1] != ')':
                raise ValueError("Unbalanced parentheses")
            consume()
            return val
        else:
            raise ValueError(f"Unexpected token: {tok}")

    result = parse_expr()
    if pos != len(tokens) - 1:
        raise ValueError("Unexpected tokens after expression")
    return result
