def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    # Tokenizer
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i] in '()':
            tokens.append(expr[i])
            i += 1
        elif expr[i] in '+-*/%^':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit():
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    if has_dot:
                        break
                    has_dot = True
                j += 1
            tokens.append(float(expr[i:j]))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            raise ValueError(f"Invalid character: {expr[i]}")
    
    # Parser
    pos = 0
    
    def peek():
        return tokens[pos] if pos < len(tokens) else None
    
    def consume(expected=None):
        nonlocal pos
        if pos >= len(tokens):
            raise ValueError("Unexpected end of expression")
        token = tokens[pos]
        if expected is not None and token != expected:
            raise ValueError(f"Expected {expected}, got {token}")
        pos += 1
        return token
    
    def parse_expression():
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
                result *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                result %= right
        return result
    
    def parse_unary():
        if peek() == '-':
            consume()
            return -parse_unary()
        if peek() == '+':
            consume()
            return parse_unary()
        return parse_power()
    
    def parse_power():
        result = parse_primary()
        if peek() == '^':
            consume()
            result = result ** parse_power()
        return result
    
    def parse_primary():
        token = peek()
        if token == '(':
            consume()
            result = parse_expression()
            consume(')')
            return result
        if isinstance(token, float):
            consume()
            return token
        if isinstance(token, str):
            name = consume()
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return variables[name]
        raise ValueError("Expected number, variable, or '('")
    
    result = parse_expression()
    if pos < len(tokens):
        raise ValueError(f"Unexpected token: {tokens[pos]}")
    return result
