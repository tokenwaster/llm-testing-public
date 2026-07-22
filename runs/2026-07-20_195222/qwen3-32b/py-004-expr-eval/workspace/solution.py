def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            start = i
            while i < n and expr[i].isdigit():
                i += 1
            num_str = expr[start:i]
            if i < n and expr[i] == '.':
                i += 1
                start_frac = i
                if i < n and expr[i].isdigit():
                    while i < n and expr[i].isdigit():
                        i += 1
                    frac_digits = expr[start_frac:i]
                    num_str += '.' + frac_digits
                else:
                    raise ValueError("Invalid decimal format")
            tokens.append(('number', float(num_str)))
        elif c in '+-*/%^()':
            if c == '-':
                tokens.append(('operator', c))
            else:
                tokens.append(('operator', c))
            i += 1
        elif c.isalpha() or c == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            var_name = expr[start:i]
            tokens.append(('variable', var_name))
        else:
            raise ValueError(f"Unexpected character: {c} at position {i}")
    
    pos = [0]

    def get_current_token():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        else:
            return None

    def consume_token():
        pos[0] += 1

    def expect_token(token_type, value=None):
        token = get_current_token()
        if not token or token[0] != token_type or (value is not None and token[1] != value):
            raise ValueError(f"Expected {token_type} with value {value}, got {token}")
        consume_token()

    def parse_primary():
        nonlocal variables
        token = get_current_token()
        if not token:
            raise ValueError("Unexpected end of input")
        ttype, tval = token
        if ttype == 'number':
            consume_token()
            return tval
        elif ttype == 'variable':
            var_name = tval
            consume_token()
            if variables is None or var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return variables[var_name]
        elif ttype == 'operator' and tval == '(':
            consume_token()
            result = parse_additive()
            expect_token('operator', ')')
            return result
        else:
            raise ValueError(f"Expected primary expression, got {ttype} with value {tval}")

    def parse_unary():
        if get_current_token() and get_current_token()[0] == 'operator' and get_current_token()[1] == '-':
            consume_token()
            val = parse_unary()
            return -val
        else:
            return parse_primary()

    def parse_power():
        left = parse_unary()
        while get_current_token() and get_current_token()[0] == 'operator' and get_current_token()[1] == '^':
            consume_token()
            right = parse_power()
            left = left ** right
        return left

    def parse_multiplicative():
        left = parse_power()
        while get_current_token() and get_current_token()[0] == 'operator' and get_current_token()[1] in ['*', '/', '%']:
            op = get_current_token()[1]
            consume_token()
            right = parse_power()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0.0:
                    raise ValueError("Division by zero")
                left /= right
            elif op == '%':
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left %= right
        return left

    def parse_additive():
        left = parse_multiplicative()
        while get_current_token() and get_current_token()[0] == 'operator' and get_current_token()[1] in ['+', '-']:
            op = get_current_token()[1]
            consume_token()
            right = parse_multiplicative()
            if op == '+':
                left += right
            else:
                left -= right
        return left

    result = parse_additive()

    # Check that all tokens are consumed
    if pos[0] != len(tokens):
        raise ValueError("Unexpected token after expression")

    return float(result)
