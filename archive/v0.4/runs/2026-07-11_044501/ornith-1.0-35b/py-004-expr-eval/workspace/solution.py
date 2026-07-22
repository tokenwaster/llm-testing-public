def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    # Tokenizer
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i+1].isdigit()):
            # Number (integer or decimal)
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUM', float(expr[i:j])))
            i = j
        elif c in '+-*/%^':
            tokens.append((c, c))
            i += 1
        elif c == '(':
            tokens.append(('(', '('))
            i += 1
        elif c == ')':
            tokens.append((')', ')'))
            i += 1
        elif c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        else:
            raise ValueError(f"Unexpected character: {c}")
    
    # Parser (recursive descent)
    pos = [0]
    
    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None
    
    def consume(expected_type=None):
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok}")
        pos[0] += 1
        return tok
    
    def parse_expression():
        # Expression = Term (('+' | '-') Term)*
        left = parse_term()
        while True:
            tok = peek()
            if tok and tok[0] in ('+', '-'):
                op = consume()[0]
                right = parse_term()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left
    
    def parse_term():
        # Term = Factor (('*' | '/' | '%') Factor)*
        left = parse_factor()
        while True:
            tok = peek()
            if tok and tok[0] in ('*', '/', '%'):
                op = consume()[0]
                right = parse_factor()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        return left
    
    def parse_factor():
        # Factor = ('-' | '+')* Power
        sign = 1
        while True:
            tok = peek()
            if tok and tok[0] in ('+', '-'):
                op = consume()[0]
                if op == '-':
                    sign *= -1
            else:
                break
        return sign * parse_power()
    
    def parse_power():
        # Power = Primary ('^' Factor)?  [right-associative]
        base = parse_primary()
        tok = peek()
        if tok and tok[0] == '^':
            consume()
            exponent = parse_factor()  # Right-associative, handles unary operators in exponent
            return base ** exponent
        return base
    
    def parse_primary():
        # Primary = Number | Variable | '(' Expression ')'
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        
        if tok[0] == 'NUM':
            consume()
            return tok[1]
        elif tok[0] == 'VAR':
            name = consume()[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(variables[name])
        elif tok[0] == '(':
            consume()  # consume '('
            result = parse_expression()
            closing = peek()
            if closing is None or closing[0] != ')':
                raise ValueError("Unbalanced parentheses")
            consume()  # consume ')'
            return result
        else:
            raise ValueError(f"Unexpected token: {tok}")
    
    result = parse_expression()
    
    # Check for extra tokens
    if pos[0] < len(tokens):
        raise ValueError("Extra tokens after expression")
    
    return float(result)
