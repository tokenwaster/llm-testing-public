def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # Tokenizer
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit():
            start = i
            int_part = ''
            # read integer part
            while i < n and expr[i].isdigit():
                int_part += expr[i]
                i += 1
            # check for decimal point
            if i < n and expr[i] == '.':
                i += 1
                frac_part = ''
                while i < n and expr[i].isdigit():
                    frac_part += expr[i]
                    i += 1
                num_str = int_part + '.' + frac_part
            else:
                num_str = int_part
            try:
                num_val = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number format: {num_str}")
            tokens.append(('NUMBER', num_val))
        elif ch.isalpha() or ch == '_':
            start = i
            name = ''
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                name += expr[i]
                i += 1
            tokens.append(('VARIABLE', name))
        elif ch in '+-*/%^()':
            token_type = {
                '+': 'PLUS',
                '-': 'MINUS',
                '*': 'STAR',
                '/': 'SLASH',
                '%': 'PERCENT',
                '^': 'CARET',
                '(': 'LPAREN',
                ')': 'RPAREN'
            }[ch]
            tokens.append((token_type, ch))
            i += 1
        else:
            raise ValueError(f"Unexpected character '{ch}'")

    # Parser state
    pos = 0
    n_tokens = len(tokens)

    def peek():
        nonlocal pos
        if pos < n_tokens:
            return tokens[pos]
        return None

    def consume():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        return token

    def parse_primary() -> float:
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of input")
        kind, val = token
        if kind == 'NUMBER':
            consume()
            return val
        elif kind == 'VARIABLE':
            name = val
            consume()
            if name not in variables:
                raise ValueError(f"Unknown variable '{name}'")
            return variables[name]
        elif kind == 'LPAREN':
            consume()  # '('
            result = parse_expr()
            token = peek()
            if token is None or token[0] != 'RPAREN':
                raise ValueError("Missing closing parenthesis")
            consume()  # ')'
            return result
        else:
            raise ValueError(f"Unexpected token {token}")

    def parse_unary() -> float:
        token = peek()
        if token is None:
            raise ValueError("Unexpected end of input")
        kind, val = token
        if kind in ('PLUS', 'MINUS'):
            op_kind = consume()[0]  # 'PLUS' or 'MINUS'
            value = parse_power()
            if op_kind == 'MINUS':
                return -value
            else:  # PLUS
                return value
        else:
            return parse_primary()

    def parse_power() -> float:
        left = parse_unary()
        token = peek()
        if token is not None and token[0] == 'CARET':
            consume()  # '^'
            right = parse_power()  # right-associative
            try:
                return left ** right
            except OverflowError:
                raise ValueError("Overflow in exponentiation")
        return left

    def parse_term() -> float:
        left = parse_power()
        while True:
            token = peek()
            if token is None or token[0] not in ('STAR', 'SLASH', 'PERCENT'):
                break
            op_kind = consume()[0]
            right = parse_power()
            if op_kind == 'STAR':
                left = left * right
            elif op_kind == 'SLASH':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif op_kind == 'PERCENT':
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_expr() -> float:
        left = parse_term()
        while True:
            token = peek()
            if token is None or token[0] not in ('PLUS', 'MINUS'):
                break
            op_kind = consume()[0]
            right = parse_term()
            if op_kind == 'PLUS':
                left = left + right
            else:  # MINUS
                left = left - right
        return left

    result = parse_expr()
    if peek() is not None:
        raise ValueError("Unexpected token after expression")
    return float(result)
