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
        elif c.isdigit():
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUMBER', float(expr[i:j])))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            name = expr[i:j]
            if name in variables:
                tokens.append(('NUMBER', float(variables[name])))
            else:
                raise ValueError(f"Unknown variable: {name}")
            i = j
        elif c == '+':
            tokens.append(('PLUS',))
            i += 1
        elif c == '-':
            tokens.append(('MINUS',))
            i += 1
        elif c == '*':
            tokens.append(('STAR',))
            i += 1
        elif c == '/':
            tokens.append(('SLASH',))
            i += 1
        elif c == '%':
            tokens.append(('PERCENT',))
            i += 1
        elif c == '^':
            tokens.append(('CARET',))
            i += 1
        elif c == '(':
            tokens.append(('LPAREN',))
            i += 1
        elif c == ')':
            tokens.append(('RPAREN',))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c}")
    tokens.append(('EOF',))

    # Parser
    pos = [0]

    def peek():
        return tokens[pos[0]]

    def consume(expected_type=None):
        tok = tokens[pos[0]]
        if expected_type and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok}")
        pos[0] += 1
        return tok

    def parse_expr():
        return parse_addition()

    def parse_addition():
        left = parse_multiplication()
        while peek()[0] in ('PLUS', 'MINUS'):
            op = consume()[0]
            right = parse_multiplication()
            if op == 'PLUS':
                left = left + right
            else:
                left = left - right
        return left

    def parse_multiplication():
        left = parse_unary()
        while peek()[0] in ('STAR', 'SLASH', 'PERCENT'):
            op = consume()[0]
            right = parse_unary()
            if op == 'STAR':
                left = left * right
            elif op == 'SLASH':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # PERCENT
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_unary():
        if peek()[0] == 'MINUS':
            consume('MINUS')
            operand = parse_unary()
            return -operand
        return parse_power()

    def parse_power():
        base = parse_primary()
        if peek()[0] == 'CARET':
            consume('CARET')
            exponent = parse_unary()  # Right-associative; exponent can have unary minus
            return base ** exponent
        return base

    def parse_primary():
        tok = peek()
        if tok[0] == 'NUMBER':
            consume('NUMBER')
            return tok[1]
        elif tok[0] == 'LPAREN':
            consume('LPAREN')
            result = parse_expr()
            if peek()[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            consume('RPAREN')
            return result
        else:
            raise ValueError(f"Unexpected token: {tok}")

    result = parse_expr()
    if pos[0] < len(tokens) - 1:
        raise ValueError("Unexpected tokens after expression")
    return result
