def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    # Tokenize the expression
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        
        # Skip whitespace
        if c.isspace():
            i += 1
            continue
        
        # Check for numbers (integers and decimals)
        if c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i+1].isdigit()):
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUMBER', float(expr[i:j])))
            i = j
            continue
        
        # Check for variable names
        if c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            var_name = expr[i:j]
            tokens.append(('VAR', var_name))
            i = j
            continue
        
        # Check for operators and parentheses
        if c in '+-*/%^':
            tokens.append(('OP', c))
            i += 1
            continue
        
        if c == '(':
            tokens.append(('LPAREN', c))
            i += 1
            continue
        
        if c == ')':
            tokens.append(('RPAREN', c))
            i += 1
            continue
        
        # Unknown character
        raise ValueError(f"Unknown character: {c}")
    
    # Parse and evaluate using recursive descent parser
    pos = [0]  # Use list to allow modification in nested functions
    
    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None
    
    def consume():
        token = peek()
        pos[0] += 1
        return token
    
    def parse_primary():
        token = peek()
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        # Handle numbers and variables
        if token[0] == 'NUMBER':
            consume()
            return token[1]
        
        if token[0] == 'VAR':
            var_name = token[1]
            consume()
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return variables[var_name]
        
        # Handle parentheses
        if token[0] == 'LPAREN':
            consume()  # consume '('
            result = parse_expression()
            if peek() is None or peek()[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            consume()  # consume ')'
            return result
        
        # Handle unary minus (only when it's at the beginning or after an operator/parenthesis)
        if token[0] == 'OP' and token[1] == '-':
            consume()
            # Check for double unary minus
            next_token = peek()
            if next_token is not None and next_token[0] == 'OP' and next_token[1] == '-':
                consume()
                return parse_primary()  # --x = x
                
            return -parse_primary()
        
        raise ValueError(f"Unexpected token: {token}")
    
    def parse_power():
        left = parse_primary()
        
        while peek() is not None and peek()[0] == 'OP' and peek()[1] == '^':
            consume()  # consume '^'
            right = parse_power()  # Right-associative, so recurse
            left = left ** right
        
        return left
    
    def parse_term():
        left = parse_power()
        
        while peek() is not None and peek()[0] == 'OP' and peek()[1] in ('*', '/', '%'):
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
    
    def parse_expression():
        left = parse_term()
        
        while peek() is not None and peek()[0] == 'OP' and peek()[1] in ('+', '-'):
            op = consume()[1]
            right = parse_term()
            
            if op == '+':
                left = left + right
            elif op == '-':
                left = left - right
        
        return left
    
    # Start parsing from the top level
    result = parse_expression()
    
    # Check for leftover tokens (malformed expression)
    if peek() is not None:
        raise ValueError("Malformed expression")
    
    return float(result)
