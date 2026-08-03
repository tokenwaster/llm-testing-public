def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluate an arithmetic expression string without using eval/exec/ast.
    
    Grammar (recursive descent):
        expression  := term (('+' | '-') term)*
        term        := factor (('*' | '/' | '%') factor)*
        factor      := unary ('^' factor)?   # right-associative
        unary       := '-' unary | primary
        primary     := number | variable | '(' expression ')'
    """
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    pos = [0]  # mutable position counter
    
    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None
    
    def consume(expected=None):
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if expected is not None and tok != expected:
            raise ValueError(f"Expected '{expected}', got '{tok}'")
        pos[0] += 1
        return tok
    
    def parse_expression():
        left = parse_term()
        while peek() in ('+', '-'):
            op = consume()
            right = parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left
    
    def parse_term():
        left = parse_factor()
        while peek() in ('*', '/', '%'):
            op = consume()
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
        return left
    
    def parse_factor():
        # unary first, then handle ^
        base = parse_unary()
        if peek() == '^':
            consume('^')
            exp = parse_factor()  # right-associative: recurse
            return float(base ** exp)
        return base
    
    def parse_unary():
        if peek() == '-':
            consume('-')
            operand = parse_unary()
            return -operand
        return parse_primary()
    
    def parse_primary():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        
        # Number
        if tok[0].isdigit() or (tok[0] == '.' and len(tok) > 1):
            consume()
            return float(tok)
        
        # Parenthesized expression
        if tok == '(':
            consume('(')
            val = parse_expression()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            consume(')')
            return val
        
        # Variable
        if tok[0].isalpha() or tok[0] == '_':
            consume()
            if tok not in variables:
                raise ValueError(f"Unknown variable: '{tok}'")
            return float(variables[tok])
        
        raise ValueError(f"Unexpected token: '{tok}'")
    
    result = parse_expression()
    
    # Check no tokens remain
    if pos[0] < len(tokens):
        raise ValueError(f"Unexpected token at end: '{tokens[pos[0]]}'")
    
    return float(result)


def tokenize(expr: str) -> list[str]:
    """
    Tokenize an arithmetic expression into a list of token strings.
    Tokens: numbers, identifiers, operators (+, -, *, /, %, ^), parentheses.
    Whitespace is skipped.
    """
    tokens = []
    i = 0
    n = len(expr)
    
    while i < n:
        c = expr[i]
        
        # Skip whitespace
        if c.isspace():
            i += 1
            continue
        
        # Number: digits possibly with decimal point
        if c.isdigit() or c == '.':
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            token = expr[i:j]
            if token == '.':
                raise ValueError(f"Invalid number: '.'")
            tokens.append(token)
            i = j
            continue
        
        # Identifier / variable
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        
        # Single-character operators and parentheses
        if c in '+-*/%^()':
            tokens.append(c)
            i += 1
            continue
        
        raise ValueError(f"Invalid character: '{c}'")
    
    return tokens
