def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # Tokenizer
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        if expr[i].isspace():
            i += 1
            continue
        if expr[i].isdigit():
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUMBER', float(expr[i:j])))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VARIABLE', expr[i:j]))
            i = j
        elif expr[i] == '+':
            tokens.append(('PLUS', '+'))
            i += 1
        elif expr[i] == '-':
            tokens.append(('MINUS', '-'))
            i += 1
        elif expr[i] == '*':
            tokens.append(('STAR', '*'))
            i += 1
        elif expr[i] == '/':
            tokens.append(('SLASH', '/'))
            i += 1
        elif expr[i] == '%':
            tokens.append(('PERCENT', '%'))
            i += 1
        elif expr[i] == '^':
            tokens.append(('CARET', '^'))
            i += 1
        elif expr[i] == '(':
            tokens.append(('LPAREN', '('))
            i += 1
        elif expr[i] == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {expr[i]!r}")

    tokens.append(('EOF', None))

    pos = 0

    def peek():
        return tokens[pos]

    def consume():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def expect(token_type):
        tok = consume()
        if tok[0] != token_type:
            raise ValueError(f"Expected {token_type}, got {tok[0]}")
        return tok

    def parse_expr():
        result = parse_term()
        while peek()[0] in ('PLUS', 'MINUS'):
            op = consume()
            right = parse_term()
            if op[0] == 'PLUS':
                result = result + right
            else:
                result = result - right
        return result

    def parse_term():
        result = parse_unary()
        while peek()[0] in ('STAR', 'SLASH', 'PERCENT'):
            op = consume()
            right = parse_unary()
            if op[0] == 'STAR':
                result = result * right
            elif op[0] == 'SLASH':
                if right == 0:
                    raise ValueError("Division by zero")
                result = result / right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                result = result % right
        return result

    def parse_unary():
        if peek()[0] == 'MINUS':
            consume()
            operand = parse_unary()
            return -operand
        return parse_power()

    def parse_power():
        base = parse_atom()
        if peek()[0] == 'CARET':
            consume()
            exp = parse_unary()
            return base ** exp
        return base

    def parse_atom():
        tok = peek()
        if tok[0] == 'NUMBER':
            consume()
            return tok[1]
        elif tok[0] == 'VARIABLE':
            consume()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(variables[name])
        elif tok[0] == 'LPAREN':
            consume()
            result = parse_expr()
            expect('RPAREN')
            return result
        else:
            raise ValueError(f"Unexpected token: {tok[0]}")

    result = parse_expr()
    if peek()[0] != 'EOF':
        raise ValueError(f"Unexpected token after expression: {peek()[0]}")
    return float(result)
