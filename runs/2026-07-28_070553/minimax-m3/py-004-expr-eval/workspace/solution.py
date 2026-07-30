def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # ---- Tokenization ----
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in '+-*/%^':
            tokens.append(('OP', c))
            i += 1
        elif c == '(':
            tokens.append(('LPAREN', None))
            i += 1
        elif c == ')':
            tokens.append(('RPAREN', None))
            i += 1
        elif c.isdigit() or c == '.':
            j = i
            has_dot = False
            seen_digit = False
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j].isdigit():
                    seen_digit = True
                elif has_dot:
                    raise ValueError("Invalid number: multiple decimal points")
                else:
                    has_dot = True
                j += 1
            if not seen_digit:
                raise ValueError("Invalid number")
            tokens.append(('NUMBER', float(expr[i:j])))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        else:
            raise ValueError(f"Unexpected character '{c}' in expression")

    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def advance():
        tok = peek()
        pos[0] += 1
        return tok

    # ---- Recursive descent parser ----
    # Precedence (lowest to highest):
    #   expr    : '+', '-'      (binary, left-assoc)
    #   term    : '*', '/', '%' (left-assoc)
    #   unary   : '-'           (prefix; binds LOOSER than '^')
    #   power   : '^'           (right-assoc)
    #   atom    : numbers, vars, parenthesized expressions

    def parse_expr():
        left = parse_term()
        while True:
            tok = peek()
            if tok is None or tok[0] != 'OP' or tok[1] not in ('+', '-'):
                break
            op = tok[1]
            advance()
            right = parse_term()
            left = left + right if op == '+' else left - right
        return left

    def parse_term():
        left = parse_unary()
        while True:
            tok = peek()
            if tok is None or tok[0] != 'OP' or tok[1] not in ('*', '/', '%'):
                break
            op = tok[1]
            advance()
            right = parse_unary()
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

    def parse_unary():
        tok = peek()
        if tok is not None and tok[0] == 'OP' and tok[1] == '-':
            advance()
            inner = parse_unary()
            return -inner
        return parse_power()

    def parse_power():
        # right-associative: atom '^' power
        base = parse_atom()
        tok = peek()
        if tok is not None and tok[0] == 'OP' and tok[1] == '^':
            advance()
            exp = parse_power()
            return base ** exp
        return base

    def parse_atom():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if tok[0] == 'NUMBER':
            advance()
            return tok[1]
        if tok[0] == 'VAR':
            advance()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(variables[name])
        if tok[0] == 'LPAREN':
            advance()
            inner = parse_expr()
            tok = peek()
            if tok is None or tok[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            advance()
            return inner
        raise ValueError("Malformed expression")

    result = parse_expr()
    if pos[0] != len(tokens):
        raise ValueError("Malformed expression")
    return float(result)
