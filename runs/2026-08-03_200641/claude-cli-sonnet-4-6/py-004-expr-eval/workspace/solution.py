def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or c == '.':
            j = i
            dot_count = 0
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    dot_count += 1
                    if dot_count > 1:
                        raise ValueError(f"Invalid number near position {j}")
                j += 1
            raw = expr[i:j]
            try:
                tokens.append(('NUM', float(raw)))
            except ValueError:
                raise ValueError(f"Invalid number: {raw!r}")
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        elif c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1
        else:
            raise ValueError(f"Invalid character: {c!r} at position {i}")

    pos = 0
    total = len(tokens)

    def peek():
        return tokens[pos] if pos < total else None

    def consume():
        nonlocal pos
        t = tokens[pos]
        pos += 1
        return t

    def peek_op(op):
        t = peek()
        return t is not None and t[0] == 'OP' and t[1] == op

    def peek_ops(*ops):
        t = peek()
        return t is not None and t[0] == 'OP' and t[1] in ops

    # Grammar (precedence low → high):
    #   expr    : term   (('+' | '-') term)*
    #   term    : unary  (('*' | '/' | '%') unary)*
    #   unary   : '-' unary | power
    #   power   : primary ('^' unary)?        ← right-assoc via recursion
    #   primary : NUMBER | VARIABLE | '(' expr ')'

    def parse_expr():
        left = parse_term()
        while peek_ops('+', '-'):
            op = consume()[1]
            right = parse_term()
            left = left + right if op == '+' else left - right
        return left

    def parse_term():
        left = parse_unary()
        while peek_ops('*', '/', '%'):
            op = consume()[1]
            right = parse_unary()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0.0:
                    raise ValueError("Division by zero")
                left /= right
            else:
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left %= right
        return left

    def parse_unary():
        if peek_op('-'):
            consume()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_primary()
        if peek_op('^'):
            consume()
            exp = parse_unary()
            return float(base ** exp)
        return base

    def parse_primary():
        t = peek()
        if t is None:
            raise ValueError("Unexpected end of expression")
        if t == ('OP', '('):
            consume()
            val = parse_expr()
            if not peek_op(')'):
                raise ValueError("Unbalanced parentheses: missing ')'")
            consume()
            return val
        if t[0] == 'NUM':
            consume()
            return t[1]
        if t[0] == 'VAR':
            consume()
            name = t[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name!r}")
            return float(variables[name])
        raise ValueError(f"Unexpected token: {t[1]!r}")

    result = parse_expr()
    if pos < total:
        raise ValueError(f"Unexpected token: {tokens[pos][1]!r}")
    return float(result)
