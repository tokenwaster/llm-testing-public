def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # ── Tokenizer ──────────────────────────────────────────────────────
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
            tokens.append(('NUM', float(expr[i:j])))
            i = j

        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j

        elif c in '+-*/%^()':
            tokens.append((c, c))
            i += 1

        else:
            raise ValueError(f"Unexpected character: {c!r}")

    # ── Recursive-descent parser ───────────────────────────────────────
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume(expected=None):
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if expected and tok[0] != expected:
            raise ValueError(f"Expected {expected!r}, got {tok[0]!r}")
        pos[0] += 1
        return tok

    def parse_expr():
        return _additive()

    def _additive():
        left = _multiplicative()
        while True:
            tok = peek()
            if tok and tok[0] in ('+', '-'):
                op = consume()[0]
                right = _multiplicative()
                left = (left + right) if op == '+' else (left - right)
            else:
                break
        return left

    def _multiplicative():
        left = _exponentiation()
        while True:
            tok = peek()
            if tok and tok[0] in ('*', '/', '%'):
                op = consume()[0]
                right = _exponentiation()
                if op == '*':
                    left *= right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left /= right
                else:
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left %= right
            else:
                break
        return left

    def _exponentiation():
        base = _unary()
        tok = peek()
        if tok and tok[0] == '^':
            consume('^')
            exp = _exponentiation()          # right-associative via recursion
            return base ** exp
        return base

    def _unary():
        tok = peek()
        if tok and tok[0] == '-':
            consume('-')
            return -_unary()
        return _primary()

    def _primary():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if tok[0] == 'NUM':
            consume('NUM')
            return tok[1]

        if tok[0] == 'VAR':
            name = consume('VAR')[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(variables[name])

        if tok[0] == '(':
            consume('(')
            val = parse_expr()
            close = peek()
            if close is None or close[0] != ')':
                raise ValueError("Unbalanced parentheses")
            consume(')')
            return val

        raise ValueError(f"Unexpected token: {tok[0]!r}")

    # ── Drive the parser ───────────────────────────────────────────────
    result = parse_expr()

    if pos[0] < len(tokens):
        raise ValueError("Unexpected token after expression")

    return float(result)
