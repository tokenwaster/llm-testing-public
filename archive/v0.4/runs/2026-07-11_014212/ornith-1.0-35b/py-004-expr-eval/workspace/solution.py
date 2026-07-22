def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # --- Tokenizer ---
    tokens: list[tuple[str, object]] = []
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
            tokens.append(('NAME', expr[i:j]))
            i = j
        elif c == '+':
            tokens.append(('PLUS', '+'))
            i += 1
        elif c == '-':
            tokens.append(('MINUS', '-'))
            i += 1
        elif c == '*':
            tokens.append(('STAR', '*'))
            i += 1
        elif c == '/':
            tokens.append(('SLASH', '/'))
            i += 1
        elif c == '%':
            tokens.append(('PERCENT', '%'))
            i += 1
        elif c == '^':
            tokens.append(('CARET', '^'))
            i += 1
        elif c == '(':
            tokens.append(('LPAREN', '('))
            i += 1
        elif c == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c!r}")

    tokens.append(('EOF', None))

    # --- Parser (recursive descent) ---
    pos = [0]

    def peek() -> tuple[str, object]:
        return tokens[pos[0]]

    def advance() -> tuple[str, object]:
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    def expect(type_: str) -> tuple[str, object]:
        tok = peek()
        if tok[0] != type_:
            raise ValueError(f"Expected {type_}, got {tok[0]}")
        return advance()

    # expr → add_expr
    def parse_expr() -> float:
        return parse_add()

    # add_expr → mul_expr (('+' | '-') mul_expr)*
    def parse_add() -> float:
        left = parse_mul()
        while peek()[0] in ('PLUS', 'MINUS'):
            op = advance()[0]
            right = parse_mul()
            if op == 'PLUS':
                left += right
            else:
                left -= right
        return left

    # mul_expr → unary (('*' | '/' | '%') unary)*
    def parse_mul() -> float:
        left = parse_unary()
        while peek()[0] in ('STAR', 'SLASH', 'PERCENT'):
            op = advance()[0]
            right = parse_unary()
            if op == 'STAR':
                left *= right
            elif op == 'SLASH':
                if right == 0:
                    raise ValueError("Division by zero")
                left /= right
            else:  # PERCENT
                if right == 0:
                    raise ValueError("Modulo by zero")
                left %= right
        return left

    # unary → ('-' | '+') unary | pow_expr
    def parse_unary() -> float:
        if peek()[0] == 'MINUS':
            advance()
            return -parse_unary()
        elif peek()[0] == 'PLUS':
            advance()
            return +parse_unary()
        else:
            return parse_pow()

    # pow_expr → primary ('^' pow_expr)?   (right-associative)
    def parse_pow() -> float:
        base = parse_primary()
        if peek()[0] == 'CARET':
            advance()
            exp = parse_pow()  # right recursion for right-associativity
            return base ** exp
        return base

    # primary → NUMBER | NAME | '(' expr ')'
    def parse_primary() -> float:
        tok = peek()
        if tok[0] == 'NUMBER':
            advance()
            return tok[1]
        elif tok[0] == 'NAME':
            advance()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(variables[name])
        elif tok[0] == 'LPAREN':
            advance()
            result = parse_expr()
            expect('RPAREN')
            return result
        else:
            raise ValueError(f"Unexpected token: {tok[0]}")

    # --- Drive the parser ---
    if tokens[0][0] == 'EOF':
        raise ValueError("Empty expression")

    result = parse_expr()

    if pos[0] != len(tokens) - 1:
        raise ValueError(f"Unexpected token after expression: {tokens[pos[0]][0]}")

    return float(result)
