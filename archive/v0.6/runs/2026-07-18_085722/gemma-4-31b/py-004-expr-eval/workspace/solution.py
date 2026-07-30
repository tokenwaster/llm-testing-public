import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression based on the provided grammar and precedence rules.
    Supported operators: +, -, *, /, %, ^ (exponentiation).
    Precedence: Parentheses > Exponentiation (^) > Unary Minus (-) > Mul/Div/Mod (*, /, %) > Add/Sub (+, -).
    Exponentiation is right-associative; others are left-associative.
    """
    if variables is None:
        variables = {}

    # Tokenizer specification
    token_specification = [
        ('NUMBER',   r'\d+(\.\d*)?'), 
        ('VARIABLE', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('PLUS',     r'\+'),
        ('MINUS',    r'-'),
        ('MUL',      r'\*'),
        ('DIV',      r'/'),
        ('MOD',      r'%'),
        ('POW',      r'\^'),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('SKIP',     r'\s+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            tokens.append(('NUMBER', float(value)))
        elif kind == 'VARIABLE':
            tokens.append(('VARIABLE', value))
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise ValueError(f"Unexpected character: {value}")
        else:
            tokens.append((kind, value))

    pos = 0

    def peek():
        nonlocal pos
        return tokens[pos] if pos < len(tokens) else (None, None)

    def consume():
        nonlocal pos
        t = peek()
        pos += 1
        return t

    def parse_expression() -> float:
        # Level 1: Addition and Subtraction (Left-associative)
        node = parse_term()
        while peek()[0] in ('PLUS', 'MINUS'):
            op = consume()[0]
            right = parse_term()
            if op == 'PLUS':
                node += right
            else:
                node -= right
        return node

    def parse_term() -> float:
        # Level 2: Multiplication, Division, and Modulo (Left-associative)
        node = parse_unary()
        while peek()[0] in ('MUL', 'DIV', 'MOD'):
            op = consume()[0]
            right = parse_unary()
            if op == 'MUL':
                node *= right
            elif op == 'DIV':
                if right == 0:
                    raise ValueError("Division by zero")
                node /= right
            elif op == 'MOD':
                if right == 0:
                    raise ValueError("Modulo by zero")
                node %= right
        return node

    def parse_unary() -> float:
        # Level 3: Unary Minus (Binds looser than ^)
        if peek()[0] == 'MINUS':
            consume()
            return -parse_unary()
        return parse_power()

    def parse_power() -> float:
        # Level 4: Exponentiation (Right-associative)
        node = parse_primary()
        if peek()[0] == 'POW':
            consume()
            right = parse_power()  # Recursive call for right-associativity
            try:
                node = node ** right
            except OverflowError:
                # Handle cases where result is too large for float
                node = float('inf') if (node > 0 or right % 2 == 0) else float('-inf')
        return node

    def parse_primary() -> float:
        # Level 5: Numbers, Variables, and Parentheses
        kind, value = consume()
        if kind == 'NUMBER':
            return value
        elif kind == 'VARIABLE':
            if value not in variables:
                raise ValueError(f"Unknown variable: {value}")
            return float(variables[value])
        elif kind == 'LPAREN':
            node = parse_expression()
            next_kind, _ = consume()
            if next_kind != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            return node
        else:
            raise ValueError(f"Unexpected token: {kind if kind else 'EOF'}")

    # Start parsing from the lowest precedence level
    try:
        result = parse_expression()
    except IndexError:
        raise ValueError("Malformed syntax")

    if pos < len(tokens):
        raise ValueError("Malformed syntax: trailing tokens found")

    return float(result)
