def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        if expr[i].isspace():
            i += 1
            continue
        if expr[i].isdigit():
            j = i
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(('NUM', expr[i:j]))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        elif expr[i] in '+-*/%^()':
            tokens.append(('OP', expr[i]))
            i += 1
        else:
            raise ValueError("Malformed syntax")
    tokens.append(('EOF', None))

    pos = 0
    variables = variables or {}

    def peek():
        return tokens[pos]

    def consume(expected_type=None):
        nonlocal pos
        token = tokens[pos]
        if expected_type and token[0] != expected_type:
            raise ValueError("Malformed syntax")
        pos += 1
        return token

    def parse_expr():
        left = parse_term()
        while peek()[0] == 'OP' and peek()[1] in ('+', '-'):
            op = consume()[1]
            right = parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def parse_term():
        left = parse_power()
        while peek()[0] == 'OP' and peek()[1] in ('*', '/', '%'):
            op = consume()[1]
            right = parse_power()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_power():
        left = parse_unary()
        if peek()[0] == 'OP' and peek()[1] == '^':
            consume()
            right = parse_power()
            left = left ** right
        return left

    def parse_unary():
        if peek()[0] == 'OP' and peek()[1] == '-':
            consume()
            return -parse_power()
        return parse_primary()

    def parse_primary():
        token = peek()
        if token[0] == 'NUM':
            consume()
            return float(token[1])
        elif token[0] == 'VAR':
            consume()
            if token[1] not in variables:
                raise ValueError("Unknown variable")
            return float(variables[token[1]])
        elif token[0] == 'OP' and token[1] == '(':
            consume()
            result = parse_expr()
            if peek()[0] != 'OP' or peek()[1] != ')':
                raise ValueError("Unbalanced parentheses")
            consume()
            return result
        else:
            raise ValueError("Malformed syntax")

    result = parse_expr()
    if peek()[0] != 'EOF':
        raise ValueError("Malformed syntax")
    return result
