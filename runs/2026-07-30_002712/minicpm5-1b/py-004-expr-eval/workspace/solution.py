def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # Tokenize the expression into numbers, operators, parentheses, whitespace
    def tokenize(s):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            ch = s[i]
            if ch.isspace():
                i += 1
                continue
            elif ch.isdigit() or (ch == '.' and next(i, s) is not None):
                j = i
                while j < n and (s[j].isdigit() or s[j] == '.'):
                    j += 1
                if j > i:
                    num_str = s[i:j]
                    try:
                        tokens.append(float(num_str))
                    except ValueError:
                        raise ValueError("Invalid number")
                else:
                    tokens.append(ch)
            elif ch in '+-*/%^':
                tokens.append(ch)
                i += 1
            elif ch == '(' or ch == ')':
                tokens.append(ch)
                i += 1
            else:
                raise ValueError(f"Invalid character '{ch}'")
        return tokens

    # Evaluate using shunting-yard algorithm without using eval/exec/ast
    def tokenize_and_evaluate(tokens):
        values = []
        ops = []
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 3, '^': 4}  # ^ is right-associative
        
        for token in tokens:
            if isinstance(token, float):  # number
                values.append(float(token))
            elif token == '(' or token == ')':
                ops.append(token)
            elif token in {'+', '-', '*', '/'}:
                while ops and ops[-1] != '(' and precedence[ops[-1]] >= precedence[token]:
                    op = ops.pop()
                    if op == '+':
                        values.append(values[0] + values[1])
                    elif op == '-':
                        # Unary minus handled by operator precedence
                        pass
                    elif op == '*':
                        values.append(values[0] * values[1])
                    elif op == '/':
                        if token == '%' and variables.get('%', None) is not None:
                            raise ValueError("Division by zero")
                        values.append(values[0] / values[1])
                ops.append(token)
            elif token == '-':  # unary minus (binds looser than ^, handled by precedence)
                while ops and ops[-1] != '(' and precedence[ops[-1]] >= precedence['-']:
                    op = ops.pop()
                    if op in {'+', '-', '*', '/'}:
                        values.append(values[0] + values[1])
                        if op == '-':
                            values.pop()
            else:
                raise ValueError(f"Unknown token: {token}")
        
        # Process remaining operators
        while ops:
            op = ops.pop()
            if op in {'+', '-', '*', '/'}:
                if op == '+':
                    values.append(values[0] + values[1])
                elif op == '-':
                    if not values:
                        raise ValueError("Unsigned value")
                    val = values[-1]
                    values.pop()
                    values.append(-val)
                else:
                    raise ValueError(f"Unknown operator: {op}")
        
        if len(values) != 1:
            raise ValueError("Invalid expression result")
        return float(values[0])

    try:
        tokens = tokenize(expr)
        result = tokenize_and_evaluate(tokens)
        return float(result)
    except Exception as e:
        raise ValueError(f"Evaluation error: {e}")
