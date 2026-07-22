def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    def tokenize(s):
        i = 0
        tokens = []
        while i < len(s):
            if s[i].isspace():
                i += 1
                continue
            # Identifier (variable)
            if s[i].isalpha() or s[i] == '_':
                start = i
                while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                    i += 1
                tokens.append(('variable', s[start:i]))
                continue
            # Number
            if s[i].isdigit() or s[i] == '.':
                start = i
                decimal_count = 0
                has_digit = False
                while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                    if s[i].isdigit():
                        has_digit = True
                    else:
                        decimal_count += 1
                    i += 1
                if not has_digit or decimal_count > 1:
                    raise ValueError("malformed syntax")
                num_str = s[start:i]
                try:
                    num = float(num_str)
                except ValueError:
                    raise ValueError("malformed syntax")
                tokens.append(('number', num))
                continue
            # Operator or parenthesis
            if s[i] in '+-*/%()^':
                tokens.append(s[i])
                i += 1
            else:
                raise ValueError(f"invalid character {s[i]}")
        return tokens

    def parse_expression(tokens, idx):
        return parse_additive(tokens, idx)

    def parse_additive(tokens, idx):
        left, new_idx = parse_multiplicative(tokens, idx)
        while new_idx < len(tokens) and tokens[new_idx] in ['+', '-']:
            op_token = tokens[new_idx]
            new_idx += 1
            right, new_new_idx = parse_multiplicative(tokens, new_idx)
            if op_token == '+':
                left = left + right
            else:
                left = left - right
            new_idx = new_new_idx
        return left, new_idx

    def parse_multiplicative(tokens, idx):
        left, new_idx = parse_unary(tokens, idx)
        while new_idx < len(tokens) and tokens[new_idx] in ['*', '/', '%']:
            op_token = tokens[new_idx]
            new_idx += 1
            right, new_new_idx = parse_unary(tokens, new_idx)
            if op_token == '*':
                left = left * right
            elif op_token == '/':
                if right == 0:
                    raise ValueError("division by zero")
                left = left / right
            else:  # '%'
                if right == 0:
                    raise ValueError("modulo by zero")
                left = left % right
            new_idx = new_new_idx
        return left, new_idx

    def parse_unary(tokens, idx):
        if idx < len(tokens) and tokens[idx] == '-':
            val, new_idx = parse_exponent(tokens, idx + 1)
            return -val, new_idx
        else:
            return parse_exponent(tokens, idx)

    def parse_exponent(tokens, idx):
        left, new_idx = parse_primary(tokens, idx)
        while new_idx < len(tokens) and tokens[new_idx] == '^':
            new_idx += 1
            right, new_new_idx = parse_exponent(tokens, new_idx)
            left = left ** right
            new_idx = new_new_idx
        return left, new_idx

    def parse_primary(tokens, idx):
        if idx >= len(tokens):
            raise ValueError("unexpected end of input")
        token = tokens[idx]
        if token == '(':
            val, new_idx = parse_expression(tokens, idx + 1)
            if new_idx < len(tokens) and tokens[new_idx] == ')':
                return val, new_idx + 1
            else:
                raise ValueError("unbalanced parentheses")
        elif isinstance(token, tuple):
            typ, value = token
            if typ == 'variable':
                var_name = value
                if variables is None or var_name not in variables:
                    raise ValueError(f"unknown variable {var_name}")
                return variables[var_name], idx + 1
            else:  # number
                return value, idx + 1
        raise ValueError("malformed syntax")

    tokens = tokenize(expr)
    result, idx = parse_expression(tokens, 0)
    if idx != len(tokens):
        raise ValueError("malformed syntax")
    return float(result)
