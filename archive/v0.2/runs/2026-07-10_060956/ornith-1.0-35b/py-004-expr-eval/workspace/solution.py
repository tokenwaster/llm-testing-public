def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # ── Lexer ────────────────────────────────────────────────────────────────
    tokens: list[tuple] = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == '.' and i + 1 < n and expr[i + 1].isdigit()):
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUMBER', float(expr[i:j])))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            name = expr[i:j]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            tokens.append(('VARIABLE', float(variables[name])))
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
            raise ValueError(f"Unexpected character: {c!r}")

    tokens.append(('EOF',))

    # ── Recursive-descent parser ─────────────────────────────────────────────
    pos = [0]  # mutable cursor into tokens list

    def peek():
        return tokens[pos[0]]

    def consume(expected_type: str | None = None) -> tuple:
        tok = tokens[pos[0]]
        if expected_type is not None and tok[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {tok[0]}")
        pos[0] += 1
        return tok

    def parse_expr():
        return parse_add()

    def parse_add():
        left = parse_mul()
        while peek()[0] in ('PLUS', 'MINUS'):
            op = consume()[0]
            right = parse_mul()
            left = (left + right) if op == 'PLUS' else (left - right)
        return left

    def parse_mul():
        left = parse_pow()
        while peek()[0] in ('STAR', 'SLASH', 'PERCENT'):
            op = consume()[0]
            right = parse_pow()
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

    def parse_pow():
        base = parse_unary()
        if peek()[0] == 'CARET':
            consume('CARET')
            exp = parse_unary()  # right-associative: recurse into unary, not pow
            return base ** exp
        return base

    def parse_unary():
        if peek()[0] == 'MINUS':
            consume('MINUS')
            operand = parse_unary()
            return -operand
        return parse_atom()

    def parse_atom():
        tok = peek()
        if tok[0] == 'NUMBER':
            consume('NUMBER')
            return tok[1]
        elif tok[0] == 'VARIABLE':
            consume('VARIABLE')
            return tok[1]
        elif tok[0] == 'LPAREN':
            consume('LPAREN')
            result = parse_expr()
            if peek()[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            consume('RPAREN')
            return result
        else:
            raise ValueError(f"Unexpected token: {tok[0]}")

    # ── Drive the parser ─────────────────────────────────────────────────────
    result = parse_expr()

    if pos[0] < len(tokens) - 1:
        raise ValueError("Unbalanced parentheses or extra tokens after expression")

    return float(result)
