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
        if expr[i].isdigit():
            start = i
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                i += 1
            tokens.append(('NUMBER', float(expr[start:i])))
        elif expr[i].isalpha() or expr[i] == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('NAME', expr[start:i]))
        elif expr[i] in '+-*/%^()':
            tokens.append((expr[i], expr[i]))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {expr[i]}")
    tokens.append(('EOF', None))
    
    pos = 0
    
    def current():
        return tokens[pos]
        
    def consume(expected_type=None):
        nonlocal pos
        tok = tokens[pos]
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok[0]}")
        pos += 1
        return tok
        
    def parse_expr():
        nonlocal pos
        left = parse_term()
        while current()[0] in ('+', '-'):
            op = consume()[0]
            right = parse_term()
            if op == '+':
                left += right
            else:
                left -= right
        return left
        
    def parse_term():
        nonlocal pos
        left = parse_unary()
        while current()[0] in ('*', '/', '%'):
            op = consume()[0]
            right = parse_unary()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left /= right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                left %= right
        return left
        
    def parse_unary():
        nonlocal pos
        sign = 1
        while current()[0] in ('+', '-'):
            op = consume()[0]
            if op == '-':
                sign = -sign
        return sign * parse_power()
        
    def parse_power():
        nonlocal pos
        base = parse_primary()
        if current()[0] == '^':
            consume()
            exp = parse_power()
            return base ** exp
        return base
        
    def parse_primary():
        nonlocal pos
        tok = current()
        if tok[0] == 'NUMBER':
            consume()
            return tok[1]
        elif tok[0] == 'NAME':
            consume()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return variables[name]
        elif tok[0] == '(':
            consume()
            result = parse_expr()
            if current()[0] != ')':
                raise ValueError("Unbalanced parentheses")
            consume()
            return result
        elif tok[0] == 'EOF':
            raise ValueError("Unexpected end of input")
        else:
            raise ValueError(f"Unexpected token: {tok}")
            
    result = parse_expr()
    if current()[0] != 'EOF':
        raise ValueError(f"Unexpected token: {current()}")
    return result
