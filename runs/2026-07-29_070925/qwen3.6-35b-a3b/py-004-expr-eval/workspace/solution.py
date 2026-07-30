def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = []
    pos = 0
    length = len(expr)
    
    while pos < length:
        if expr[pos].isspace():
            pos += 1
            continue
        if expr[pos].isdigit() or (expr[pos] == '.' and pos + 1 < length and expr[pos+1].isdigit()):
            start = pos
            while pos < length and (expr[pos].isdigit() or expr[pos] == '.'):
                pos += 1
            tokens.append(('NUM', float(expr[start:pos])))
        elif expr[pos].isalpha() or expr[pos] == '_':
            start = pos
            while pos < length and (expr[pos].isalnum() or expr[pos] == '_'):
                pos += 1
            tokens.append(('VAR', expr[start:pos]))
        elif expr[pos] in '+-*/%^()':
            tok = expr[pos]
            pos += 1
            tokens.append((tok, None))
        else:
            raise ValueError(f"Unexpected character '{expr[pos]}' at index {pos}")
    tokens.append(('EOF', None))
    
    parser_pos = 0
    vars_dict = variables if variables is not None else {}

    def parse_expr():
        nonlocal parser_pos
        left = parse_term()
        while True:
            tok = tokens[parser_pos]
            if tok[0] in ('+', '-'):
                op = tok[0]
                parser_pos += 1
                right = parse_term()
                if op == '+':
                    left += right
                else:
                    left -= right
            else:
                break
        return left

    def parse_term():
        nonlocal parser_pos
        left = parse_factor()
        while True:
            tok = tokens[parser_pos]
            if tok[0] in ('*', '/', '%'):
                op = tok[0]
                parser_pos += 1
                right = parse_factor()
                if op == '*':
                    left *= right
                elif op == '/':
                    if right == 0.0: raise ValueError("Division by zero")
                    left /= right
                else: # '%'
                    if right == 0.0: raise ValueError("Modulo by zero")
                    left %= right
            else:
                break
        return left

    def parse_factor():
        nonlocal parser_pos
        tok = tokens[parser_pos]
        if tok[0] in ('+', '-'):
            op = tok[0]
            parser_pos += 1
            val = parse_factor()
            if op == '-':
                return -val
            else:
                return val
        else:
            return parse_power()

    def parse_power():
        nonlocal parser_pos
        base = parse_atom()
        tok = tokens[parser_pos]
        if tok[0] == '^':
            parser_pos += 1
            exp = parse_power()
            return base ** exp
        else:
            return base

    def parse_atom():
        nonlocal parser_pos
        tok = tokens[parser_pos]
        if tok[0] == 'NUM':
            parser_pos += 1
            return tok[1]
        elif tok[0] == 'VAR':
            name = tok[1]
            parser_pos += 1
            if name in vars_dict:
                val = vars_dict[name]
                return float(val)
            else:
                raise ValueError(f"Unknown variable '{name}'")
        elif tok[0] == '(':
            parser_pos += 1
            val = parse_expr()
            if tokens[parser_pos][0] != ')':
                raise ValueError("Unbalanced parentheses")
            parser_pos += 1 # consume ')'
            return val
        else:
            raise ValueError(f"Unexpected token {tok[0]} at index {parser_pos}")

    result = parse_expr()
    if tokens[parser_pos][0] != 'EOF':
        raise ValueError("Expression not fully consumed")
    return float(result)
