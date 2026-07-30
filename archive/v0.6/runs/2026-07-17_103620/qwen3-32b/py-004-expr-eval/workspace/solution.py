def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    def tokenize(s):
        tokens = []
        i = 0
        while i < len(s):
            c = s[i]
            if c.isspace():
                i += 1
                continue
            # Handle numbers
            if c.isdigit() or c == '.':
                start = i
                dot_count = 0
                while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                    if s[i] == '.':
                        dot_count += 1
                        if dot_count > 1:
                            raise ValueError("Invalid number format")
                    i += 1
                num_str = s[start:i]
                # Validate decimal points
                if '.' in num_str:
                    parts = num_str.split('.')
                    if len(parts[0]) == 0 or len(parts[1]) == 0:
                        raise ValueError("Malformed syntax")
                try:
                    tokens.append(('NUMBER', float(num_str)))
                except ValueError:
                    raise ValueError(f"Invalid number: {num_str}")
                continue
            # Handle variables
            if c.isalpha() or c == '_':
                start = i
                while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                    i += 1
                name = s[start:i]
                if not (name[0].isalpha() or name[0] == '_') or not all(c.isalnum() or c == '_' for c in name):
                    raise ValueError(f"Invalid variable name: {name}")
                tokens.append(('VARIABLE', name))
                continue
            # Handle operators and parentheses
            if c in '+-*/%^()':
                token_type = 'OPERATOR' if c not in '()' else ('LPAREN' if c == '(' else 'RPAREN')
                tokens.append((token_type, c))
                i += 1
                continue
            raise ValueError(f"Unexpected character: {c}")
        return tokens

    tokens = tokenize(expr)
    pos = 0

    def current_token():
        nonlocal pos
        return tokens[pos] if pos < len(tokens) else None

    def advance():
        nonlocal pos
        pos += 1

    def parse_primary():
        token = current_token()
        if not token:
            raise ValueError("Unexpected end of input")
        t_type, t_value = token
        if t_type == 'NUMBER':
            advance()
            return t_value
        elif t_type == 'VARIABLE':
            var_name = t_value
            advance()
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return variables[var_name]
        elif t_type == 'LPAREN':
            advance()
            result = parse_additive()
            if current_token() and current_token()[0] == 'RPAREN':
                advance()
            else:
                raise ValueError("Unbalanced parentheses")
            return result
        else:
            raise ValueError(f"Unexpected token in primary: {t_type}")

    def parse_unary():
        if current_token() and current_token()[0] == 'OPERATOR' and current_token()[1] == '-':
            advance()
            val = parse_unary()
            return -val
        else:
            return parse_exponent()

    def parse_exponent():
        left = parse_primary()
        while current_token() and current_token()[0] == 'OPERATOR' and current_token()[1] == '^':
            advance()
            right = parse_exponent()
            left = left ** right
        return left

    def parse_multiplicative():
        left = parse_unary()
        while current_token() and current_token()[0] == 'OPERATOR' and current_token()[1] in ['*', '/', '%']:
            op_val = current_token()[1]
            advance()
            right = parse_unary()
            if op_val == '*':
                left = left * right
            elif op_val == '/':
                if right == 0.0:
                    raise ValueError("Division by zero")
                left = left / right
            elif op_val == '%':
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_additive():
        left = parse_multiplicative()
        while current_token() and current_token()[0] == 'OPERATOR' and current_token()[1] in ['+', '-']:
            op_val = current_token()[1]
            advance()
            right = parse_multiplicative()
            if op_val == '+':
                left = left + right
            else:
                left = left - right
        return left

    try:
        result = parse_additive()
        if pos < len(tokens):
            raise ValueError("Malformed syntax")
        return float(result)
    except Exception as e:
        raise ValueError(str(e))
