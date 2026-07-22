def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # Tokenizer
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i+1].isdigit()):
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUM', float(expr[i:j])))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        elif c in '+-*/%^()':
            tokens.append((c, c))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c}")

    # Recursive descent parser
    pos = [0]

    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None

    def consume(expected=None):
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if expected and tok[0] != expected:
            raise ValueError(f"Expected {expected}, got {tok}")
        pos[0] += 1
        return tok

    def parse_expr():
        return parse_additive()

    def parse_additive():
        left = parse_multiplicative()
        while True:
            tok = peek()
            if tok and tok[0] in ('+', '-'):
                op = consume()[0]
                right = parse_multiplicative()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    def parse_multiplicative():
        left = parse_unary()
        while True:
            tok = peek()
            if tok and tok[0] in ('*', '/', '%'):
                op = consume()[0]
                right = parse_unary()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # %
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        return left

    def parse_unary():
        sign = 1.0
        while True:
            tok = peek()
            if tok and tok[0] == '-':
                consume()
                sign = -sign
            elif tok and tok[0] == '+':
                consume()
            else:
                break
        return sign * parse_power()

    def parse_power():
        base = parse_primary()
        tok = peek()
        if tok and tok[0] == '^':
            consume()
            exp = parse_unary()  # right-associative, handle unary minus on RHS
            return base ** exp
        return base

    def parse_primary():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if tok[0] == 'NUM':
            consume()
            return tok[1]
        elif tok[0] == 'VAR':
            consume()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            val = float(variables[name])
            return val
        elif tok[0] == '(':
            consume()
            result = parse_expr()
            closing = peek()
            if closing is None or closing[0] != ')':
                raise ValueError("Unbalanced parentheses")
            consume()  # consume ')'
            return result
        else:
            raise ValueError(f"Unexpected token: {tok}")

    result = parse_expr()

    if pos[0] < len(tokens):
        raise ValueError("Extra tokens after expression")

    return float(result)
