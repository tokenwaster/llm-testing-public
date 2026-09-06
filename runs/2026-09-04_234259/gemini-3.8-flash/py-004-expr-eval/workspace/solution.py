def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # Tokenize input
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in '+-*/%^()':
            tokens.append((c, c))
            i += 1
            continue
        if c.isdigit():
            start = i
            while i < n and expr[i].isdigit():
                i += 1
            if i < n and expr[i] == '.':
                i += 1
                if i >= n or not expr[i].isdigit():
                    raise ValueError(f"Malformed number at position {start}")
                while i < n and expr[i].isdigit():
                    i += 1
            if i < n and expr[i] in 'eE':
                i += 1
                if i < n and expr[i] in '+-':
                    i += 1
                if i >= n or not expr[i].isdigit():
                    raise ValueError(f"Malformed number at position {start}")
                while i < n and expr[i].isdigit():
                    i += 1
            num_str = expr[start:i]
            tokens.append(('NUMBER', float(num_str)))
            continue
        if c.isalpha() or c == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('IDENT', expr[start:i]))
            continue
        raise ValueError(f"Invalid character: {c!r}")

    if not tokens:
        raise ValueError("Empty expression")

    pos = 0

    def peek():
        if pos < len(tokens):
            return tokens[pos]
        return None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_primary() -> float:
        nonlocal pos
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        tok_type, tok_val = tok
        if tok_type == 'NUMBER':
            advance()
            return float(tok_val)
        if tok_type == 'IDENT':
            advance()
            if variables is None or tok_val not in variables:
                raise ValueError(f"Unknown variable: '{tok_val}'")
            try:
                return float(variables[tok_val])
            except (ValueError, TypeError):
                raise ValueError(f"Variable '{tok_val}' cannot be converted to float")
        if tok_type == '(':
            advance()
            val = parse_expr()
            closing = peek()
            if closing is None or closing[0] != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            advance()
            return val
        raise ValueError(f"Unexpected token: '{tok_val}'")

    def parse_power() -> float:
        val = parse_primary()
        tok = peek()
        if tok is not None and tok[0] == '^':
            advance()
            rhs = parse_unary()
            try:
                val = val ** rhs
            except ZeroDivisionError:
                raise ValueError("Division by zero in exponentiation")
            if isinstance(val, complex):
                if val.imag != 0:
                    raise ValueError("Complex result")
                val = val.real
        return val

    def parse_unary() -> float:
        tok = peek()
        if tok is not None and tok[0] == '-':
            advance()
            return -parse_unary()
        return parse_power()

    def parse_term() -> float:
        val = parse_unary()
        while True:
            tok = peek()
            if tok is not None and tok[0] in ('*', '/', '%'):
                op = advance()[0]
                rhs = parse_unary()
                if op == '*':
                    val = val * rhs
                elif op == '/':
                    if rhs == 0.0:
                        raise ValueError("Division by zero")
                    val = val / rhs
                elif op == '%':
                    if rhs == 0.0:
                        raise ValueError("Modulo by zero")
                    val = val % rhs
            else:
                break
        return val

    def parse_expr() -> float:
        val = parse_term()
        while True:
            tok = peek()
            if tok is not None and tok[0] in ('+', '-'):
                op = advance()[0]
                rhs = parse_term()
                if op == '+':
                    val = val + rhs
                else:
                    val = val - rhs
            else:
                break
        return val

    result = parse_expr()

    if pos < len(tokens):
        extra = tokens[pos][1]
        raise ValueError(f"Unexpected token after expression: '{extra}'")

    return float(result)
