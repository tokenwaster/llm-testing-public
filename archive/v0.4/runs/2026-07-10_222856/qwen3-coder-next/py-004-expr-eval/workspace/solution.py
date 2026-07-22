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
            num_str = expr[i:j]
            # Validate number format: must have at least one digit before decimal point
            if '.' in num_str:
                parts = num_str.split('.')
                if len(parts[0]) == 0 or not parts[0].isdigit():
                    raise ValueError("Invalid number format")
                if len(parts[1]) == 0:
                    raise ValueError("Invalid number format")
            elif not num_str.isdigit():
                raise ValueError("Invalid number format")
            
            tokens.append(('NUMBER', float(num_str)))
            i = j
            continue
        
        # Check for variable names
        if c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            var_name = expr[i:j]
            
            # Check if it's a known keyword (like 'true'/'false') - not needed per spec
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
        raise ValueError(f"Invalid character: {c}")
    
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
    
    def parse_expression():
        """Parse expression with lowest precedence (addition/subtraction)"""
        left = parse_term()
        
        while True:
            token = peek()
            if token is None or token[0] not in ('OP',):
                break
            op = token[1]
            if op in '+-':
                consume()  # consume the operator
                right = parse_term()
                if op == '+':
                    left = left + right
                else:  # op == '-'
                    left = left - right
            else:
                break
        
        return left
    
    def parse_term():
        """Parse term with multiplication, division, modulo"""
        left = parse_power()
        
        while True:
            token = peek()
            if token is None or token[0] not in ('OP',):
                break
            op = token[1]
            if op in '*/%':
                consume()  # consume the operator
                right = parse_power()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # op == '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        
        return left
    
    def parse_power():
        """Parse power expressions (right-associative)"""
        base = parse_unary()
        
        token = peek()
        if token is not None and token[0] == 'OP' and token[1] == '^':
            consume()  # consume the operator
            exponent = parse_power()  # right associative: recurse immediately
            try:
                result = base ** exponent
                return float(result)
            except OverflowError:
                raise ValueError("Result too large")
        
        return base
    
    def parse_unary():
        """Parse unary minus"""
        token = peek()
        if token is not None and token[0] == 'OP' and token[1] == '-':
            consume()  # consume the operator
            value = parse_unary()  # allow multiple unary minuses
            return -value
        
        return parse_primary()
    
    def parse_primary():
        """Parse numbers, variables, parentheses"""
        token = peek()
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token[0] == 'NUMBER':
            consume()
            return float(token[1])
        
        if token[0] == 'VAR':
            consume()
            var_name = token[1]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(variables[var_name])
        
        if token[0] == 'LPAREN':
            consume()  # consume '('
            result = parse_expression()
            
            # Check for closing parenthesis
            token = peek()
            if token is None or token[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            consume()  # consume ')'
            return result
        
        # If we get here, it's an error
        if token[0] == 'OP' and token[1] in '+-*/%^':
            raise ValueError(f"Unexpected operator: {token[1]}")
        elif token[0] == 'RPAREN':
            raise ValueError("Unbalanced parentheses")
        else:
            raise ValueError("Invalid syntax")
    
    # Parse the entire expression
    result = parse_expression()
    
    # Check if there are remaining tokens (malformed expression)
    if peek() is not None:
        raise ValueError("Malformed expression")
    
    return float(result)
