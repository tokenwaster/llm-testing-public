def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = _tokenize(expr)
    pos = [0]  # mutable index into tokens list

    def peek() -> str | None:
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume() -> str:
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    # Grammar (lowest → highest precedence):
    #   expression → term (('+' | '-') term)*          left-associative
    #   term       → power (('*' | '/' | '%') power)*  left-associative
    #   power      → unary ('^' power)?                 right-associative
    #   unary      → '-' unary | primary
    #   primary    → NUMBER | IDENTIFIER | '(' expression ')'

    def parse_expression() -> float:
        left = _parse_term()
        while peek() in ('+', '-'):
            op = consume()
            right = _parse_term()
            if op == '+':
                left += right
            else:
                left -= right
        return left

    def parse_term() -> float:
        left = _parse_power()
        while peek() in ('*', '/', '%'):
            op = consume()
            right = _parse_power()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("division by zero")
                left /= right
            else:  # '%'
                if right == 0:
                    raise ValueError("modulo by zero")
                left %= right
        return left

    def parse_power() -> float:
        base = _parse_unary()
        if peek() == '^':
            consume()
            exp = _parse_power()  # right-associative recursion
            return base ** exp
        return base

    def parse_unary() -> float:
        if peek() == '-':
            consume()
            operand = _parse_unary()
            return -operand
        return _parse_primary()

    def parse_primary() -> float:
        tok = peek()
        if tok is None:
            raise ValueError("unexpected end of expression")

        if tok == '(':
            consume()
            val = parse_expression()
            if peek() != ')':
                raise ValueError("unbalanced parentheses")
            consume()
            return val

        # Number token (digits, possibly with embedded '.')
        if tok.isdigit():
            consume()
            try:
                return float(tok)
            except ValueError as e:
                raise ValueError(f"invalid number '{tok}'") from e

        # Variable name token
        if tok.isalpha() or tok == '_':
            consume()
            name = tok
            if name not in variables:
                raise ValueError(f"unknown variable '{name}'")
            return float(variables[name])

        raise ValueError(f"unexpected token '{tok}'")

    result = parse_expression()

    if pos[0] < len(tokens):
        remaining = tokens[pos[0]]
        raise ValueError(f"unexpected token '{remaining}' after expression")

    return result


def _tokenize(expr: str) -> list[str]:
    """Split *expr* into a flat list of non-whitespace tokens."""
    tokens: list[str] = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]

        # Skip whitespace
        if c.isspace():
            i += 1
            continue

        # Number token — digit or '.' followed by a digit
        if c.isdigit() or (c == '.' and i + 1 < n and expr[i + 1].isdigit()):
            j = i
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue

        # Identifier / variable name token
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue

        # Operators and parentheses — single-character tokens
        if c in '+-*/%^()':
            tokens.append(c)
            i += 1
            continue

        raise ValueError(f"unexpected character '{c}'")

    return tokens
