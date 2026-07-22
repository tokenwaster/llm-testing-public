def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
        
    pos = 0
    n = len(expr)
    
    def peek():
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1
        if pos < n:
            return expr[pos]
        return None
        
    def consume():
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1
        if pos < n:
            ch = expr[pos]
            pos += 1
            return ch
        return None
        
    def parse_number():
        nonlocal pos
        start = pos
        while pos < n and (expr[pos].isdigit() or expr[pos] == '.'):
            pos += 1
        if pos == start:
            raise ValueError("malformed syntax")
        return float(expr[start:pos])
        
    def parse_variable():
        nonlocal pos
        start = pos
        while pos < n and (expr[pos].isalnum() or expr[pos] == '_'):
            pos += 1
        name = expr[start:pos]
        if name not in variables:
            raise ValueError("unknown variable")
        return float(variables[name])
        
    def parse_primary():
        nonlocal pos
        ch = peek()
        if ch is None:
            raise ValueError("malformed syntax")
        if ch == '(':
            consume()
            val = parse_expr()
            if peek() != ')':
                raise ValueError("unbalanced parentheses")
            consume()
            return val
        if ch.isdigit():
            return parse_number()
        if ch.isalpha() or ch == '_':
            return parse_variable()
        raise ValueError("malformed syntax")
        
    def parse_unary():
        nonlocal pos
        if peek() == '-':
            consume()
            return -parse_power()
        return parse_primary()
        
    def parse_power():
        nonlocal pos
        base = parse_unary()
        if peek() == '^':
            consume()
            exponent = parse_power()
            return base ** exponent
        return base
        
    def parse_term():
        nonlocal pos
        left = parse_power()
        while peek() in ('*', '/', '%'):
            op = consume()
            right = parse_power()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("division by zero")
                left /= right
            elif op == '%':
                if right == 0:
                    raise ValueError("modulo by zero")
                left %= right
        return left
        
    def parse_expr():
        nonlocal pos
        left = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_term()
            if op == '+':
                left += right
            else:
                left -= right
        return left
        
    result = parse_expr()
    
    if peek() is not None:
        raise ValueError("malformed syntax")
        
    return result
