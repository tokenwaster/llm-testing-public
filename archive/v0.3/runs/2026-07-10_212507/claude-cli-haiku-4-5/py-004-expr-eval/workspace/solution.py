def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    # Tokenize
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i] in '()+-*/%^':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit() or expr[i] == '.':
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUM', float(expr[i:j])))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        else:
            raise ValueError(f"Unexpected character: {expr[i]}")
    
    # Parse
    pos = 0
    
    def peek():
        return tokens[pos] if pos < len(tokens) else None
    
    def consume(expected=None):
        nonlocal pos
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected is not None and token != expected:
            raise ValueError(f"Expected {expected}, got {token}")
        pos += 1
        return token
    
    def parse_expr():
        result = parse_term()
        while peek() in ['+', '-']:
            op = consume()
            right = parse_term()
            result = result + right if op == '+' else result - right
        return result
    
    def parse_term():
        result = parse_unary()
        while peek() in ['*', '/', '%']:
            op = consume()
            right = parse_unary()
            if op == '*':
                result = result * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                result = result / right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                result = result % right
        return result
    
    def parse_unary():
        if peek() == '-':
            consume('-')
            return -parse_unary()
        return parse_exponent()
    
    def parse_exponent():
        result = parse_primary()
        if peek() == '^':
            consume('^')
            result = result ** parse_exponent()
        return result
    
    def parse_primary():
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token == '(':
            consume('(')
            result = parse_expr()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses")
            consume(')')
            return result
        elif isinstance(token, tuple) and token[0] == 'NUM':
            consume()
            return token[1]
        elif isinstance(token, tuple) and token[0] == 'VAR':
            consume()
            var_name = token[1]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return variables[var_name]
        else:
            raise ValueError(f"Unexpected token: {token}")
    
    result = parse_expr()
    if pos < len(tokens):
        raise ValueError("Unexpected token after expression")
    return float(result)
