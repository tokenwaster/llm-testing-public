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
            # Make sure we didn't stop at an incomplete number
            if j > i:
                num_str = expr[i:j]
                try:
                    tokens.append(('NUM', float(num_str)))
                except ValueError:
                    raise ValueError("Invalid number format")
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
            tokens.append(('LPAREN', '('))
            i += 1
            continue
        
        if c == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
            continue
        
        raise ValueError(f"Unknown character: {c}")
    
    # Recursive descent parser for the grammar:
    # expr   : term ( ('+' | '-') term )*
    # term   : power ( ('*' | '/' | '%') power )*
    # power  : unary ( '^' power )?
    # unary  : ( '-' )+ primary
    # primary: NUM | VAR | '(' expr ')'
    
    pos = [0]  # Use a list to make it mutable in nested functions
    
    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None
    
    def consume():
        tok = peek()
        pos[0] += 1
        return tok
    
    def parse_expr():
        left = parse_term()
        
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = tok[1]
                consume()
                right = parse_term()
                if op == '+':
                    left = left + right
                else:  # op == '-'
                    left = left - right
            else:
                break
        
        return left
    
    def parse_term():
        left = parse_power()
        
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = tok[1]
                consume()
                right = parse_power()
                
                # Check for division or modulo by zero
                if op in ('/', '%') and right == 0:
                    raise ValueError("Division or modulo by zero")
                
                if op == '*':
                    left = left * right
                elif op == '/':
                    left = left / right
                else:  # op == '%'
                    left = left % right
            else:
                break
        
        return left
    
    def parse_power():
        base = parse_unary()
        
        tok = peek()
        if tok and tok[0] == 'OP' and tok[1] == '^':
            consume()  # consume ^
            # Right-associative: parse the rest of the power expression recursively
            exp = parse_power()
            return base ** exp
        
        return base
    
    def parse_unary():
        neg_count = 0
        while peek() and peek()[0] == 'OP' and peek()[1] == '-':
            consume()
            neg_count += 1
        
        primary_val = parse_primary()
        
        if neg_count % 2 == 1:
            return -primary_val
        else:
            return primary_val
    
    def parse_primary():
        tok = peek()
        if not tok:
            raise ValueError("Unexpected end of expression")
        
        # Handle numbers
        if tok[0] == 'NUM':
            consume()
            return tok[1]
        
        # Handle variables
        if tok[0] == 'VAR':
            consume()
            var_name = tok[1]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return variables[var_name]
        
        # Handle parentheses
        if tok[0] == 'LPAREN':
            consume()  # consume (
            val = parse_expr()
            
            next_tok = peek()
            if not next_tok or next_tok[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            consume()  # consume )
            return val
        
        raise ValueError(f"Unexpected token: {tok}")
    
    # Parse the expression
    result = parse_expr()
    
    # Make sure there are no leftover tokens
    if pos[0] < len(tokens):
        raise ValueError("Malformed syntax")
    
    return float(result)
