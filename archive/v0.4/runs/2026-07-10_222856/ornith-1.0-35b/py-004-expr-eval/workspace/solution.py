def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = _tokenize(expr)
    pos = [0]  # mutable index into token list

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def advance():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    # ── Grammar (lowest → highest precedence) ──────────────────────
    # expr       → additive
    # additive   → multiplicative (('+' | '-') multiplicative)*
    # multiplicative → unary (('*' | '/' | '%') unary)*
    # power      → primary ('^' power)?          # right-associative
    # unary      → '-' unary | power
    # primary    → NUMBER | IDENT | '(' expr ')'

    def parse_expr():
        result = _parse_additive()
        if pos[0] < len(tokens):
            raise ValueError(f"Unexpected token: {tokens[pos[0]]}")
        return result

    def _parse_additive():
        left = _parse_multiplicative()
        while peek() in ('+', '-'):
            op = advance()
            right = _parse_multiplicative()
            left = (left + right) if op == '+' else (left - right)
        return left

    def _parse_multiplicative():
        left = _parse_unary()
        while peek() in ('*', '/', '%'):
            op = advance()
            right = _parse_unary()
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

    def _parse_unary():
        if peek() == '-':
            advance()
            operand = _parse_unary()
            return -operand
        return _parse_power()

    def _parse_power():
        base = _parse_primary()
        if peek() == '^':
            advance()
            exponent = _parse_power()  # right-associative recursion
            return base ** exponent
        return base

    def _parse_primary():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if isinstance(tok, float):
            advance()
            return tok

        if isinstance(tok, str) and tok.isidentifier():
            advance()
            if tok not in variables:
                raise ValueError(f"Unknown variable: {tok}")
            return float(variables[tok])

        if tok == '(':
            advance()
            result = parse_expr()
            if peek() != ')':
                raise ValueError("Unbalanced parentheses")
            advance()
            return result

        raise ValueError(f"Unexpected token: {tok}")

    return float(parse_expr())


def _tokenize(expr: str):
    tokens: list[float | str] = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]

        # skip whitespace
        if c.isspace():
            i += 1
            continue

        # numbers (integer or decimal, must start with a digit)
        if c.isdigit():
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(float(expr[i:j]))
            i = j
            continue

        # identifiers: [a-zA-Z_][a-zA-Z0-9_]*
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue

        # operators and parentheses
        if c in '+-*/%^()':
            tokens.append(c)
            i += 1
            continue

        raise ValueError(f"Unexpected character: {c!r}")

    return tokens
