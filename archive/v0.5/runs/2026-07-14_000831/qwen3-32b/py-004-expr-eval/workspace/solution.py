def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # Preprocess the expression to remove all whitespace
    expr = ''.join(expr.split())
    
    # Tokenize the expression into tokens list
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isdigit() or c == '.':
            start = i
            decimal_count = 0
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    decimal_count += 1
                    if decimal_count > 1:
                        raise ValueError("Malformed number")
                i += 1
            num_str = expr[start:i]
            try:
                tokens.append(('number', float(num_str)))
            except ValueError:
                raise ValueError(f"Invalid number: {num_str}")
        elif c.isalpha() or c == '_':
            start = i
            while i < len(expr) and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            var_name = expr[start:i]
            tokens.append(('variable', var_name))
        elif c in '+-*/%()^':
            tokens.append((c, None))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c}")
    
    # Parser implementation using recursive descent
    pos = [0]  # Current position in the tokens list
    
    def error(msg):
        raise ValueError(msg)
    
    def current_token():
        if pos[0] >= len(tokens):
            return None
        return tokens[pos[0]]
    
    def parse_primary():
        token = current_token()
        if token is None:
            error("Unexpected end of input")
        token_type, value = token
        if token_type == '(':
            pos[0] += 1  # consume '('
            result = parse_expression()
            if pos[0] >= len(tokens) or tokens[pos[0]][0] != ')':
                error("Unbalanced parentheses: missing )")
            pos[0] += 1  # consume ')'
            return result
        elif token_type == 'number':
            val = value
            pos[0] += 1
            return val
        elif token_type == 'variable':
            var_name = value
            if variables is None or var_name not in variables:
                error(f"Unknown variable: {var_name}")
            pos[0] += 1
            return variables[var_name]
        else:
            error("Expected primary expression")
    
    def parse_unary():
        if current_token() and current_token()[0] == '-':
            pos[0] += 1  # consume '-'
            val = parse_power()
            return -val
        else:
            return parse_primary()
    
    def parse_power():
        left = parse_unary()
        while current_token() and current_token()[0] == '^':
            pos[0] += 1  # consume '^'
            right = parse_power()  # Right-associative: parse the rest recursively
            left = left ** right
        return left
    
    def parse_term():
        left = parse_power()
        while current_token() and current_token()[0] in ['*', '/', '%']:
            op_type, _ = current_token()
            pos[0] += 1  # consume operator
            right = parse_power()
            if op_type == '*':
                left = left * right
            elif op_type == '/':
                if right == 0.0:
                    error("Division by zero")
                left = left / right
            elif op_type == '%':
                if right == 0.0:
                    error("Modulo by zero")
                left = left % right
        return left
    
    def parse_expression():
        left = parse_term()
        while current_token() and current_token()[0] in ['+', '-']:
            op_type, _ = current_token()
            pos[0] += 1  # consume operator
            right = parse_term()
            if op_type == '+':
                left = left + right
            elif op_type == '-':
                left = left - right
        return left
    
    try:
        result = parse_expression()
        if pos[0] != len(tokens):
            error("Unexpected tokens after end of expression")
        return float(result)
    except ValueError as e:
        raise
