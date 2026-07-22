def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # ---------- Tokenizer ----------
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            start = i
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                i += 1
            num_str = expr[start:i]
            try:
                val = float(num_str)
            except ValueError:
                raise ValueError(f"Malformed number: {num_str}")
            tokens.append(('NUMBER', val))
            continue
        if c.isalpha() or c == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            var = expr[start:i]
            tokens.append(('VAR', var))
            continue
        if c in '+-*/%^()':
            if c in '()':
                tokens.append(('PAREN', c))
            else:
                tokens.append(('OP', c))
            i += 1
            continue
        raise ValueError(f"Unexpected character: {c}")

    # ---------- Parser ----------
    pos = 0
    tok_len = len(tokens)

    def peek():
        return tokens[pos] if pos < tok_len else None

    def advance():
        nonlocal pos
        tok = peek()
        if tok is not None:
            pos += 1
        return tok

    def parse_expr():
        val = parse_term()
        while True:
            tok = peek()
            if tok is not None and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = advance()[1]
                right = parse_term()
                if op == '+':
                    val += right
                else:
                    val -= right
            else:
                break
        return val

    def parse_term():
        val = parse_factor()
        while True:
            tok = peek()
            if tok is not None and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = advance()[1]
                right = parse_factor()
                if op == '*':
                    val *= right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    val /= right
                else:  # '%'
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    val %= right
            else:
                break
        return val

    def parse_factor():
        tok = peek()
        if tok is not None and tok[0] == 'OP' and tok[1] == '-':
            advance()
            return -parse_factor()
        return parse_power()

    def parse_power():
        base = parse_atom()
        tok = peek()
        if tok is not None and tok[0] == 'OP' and tok[1] == '^':
            advance()
            exp = parse_factor()  # right-associative; allows unary minus in exponent
            try:
                return base ** exp
            except ZeroDivisionError:
                raise ValueError("Division by zero")
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
            var = tok[1]
            if var not in variables:
                raise ValueError(f"Unknown variable: {var}")
            return variables[var]
        if tok[0] == 'PAREN' and tok[1] == '(':
            advance()
            val = parse_expr()
            tok = peek()
            if tok is None or tok[0] != 'PAREN' or tok[1] != ')':
                raise ValueError("Unbalanced parentheses")
            advance()
            return val
        raise ValueError("Unexpected token")

    result = parse_expr()
    if peek() is not None:
        raise ValueError("Unexpected token after expression")
    return float(result)
