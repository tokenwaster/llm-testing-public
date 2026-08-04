def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or c == '.':
            j = i
            dot = False
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    if dot:
                        raise ValueError("malformed number")
                    dot = True
                j += 1
            num_str = expr[i:j]
            if num_str == '.':
                raise ValueError("malformed number")
            tokens.append(('num', float(num_str)))
            i = j
            continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('var', expr[i:j]))
            i = j
            continue
        if c in '+-*/%^()':
            tokens.append(('op', c))
            i += 1
            continue
        raise ValueError(f"invalid character: {c}")

    pos = 0

    def peek():
        if pos < len(tokens):
            return tokens[pos]
        return None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expr():
        return parse_add()

    def parse_add():
        left = parse_mul()
        while True:
            tok = peek()
            if tok is not None and tok[0] == 'op' and tok[1] in ('+', '-'):
                advance()
                right = parse_mul()
                if tok[1] == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    def parse_mul():
        left = parse_unary()
        while True:
            tok = peek()
            if tok is not None and tok[0] == 'op' and tok[1] in ('*', '/', '%'):
                advance()
                right = parse_unary()
                if tok[1] == '*':
                    left = left * right
                elif tok[1] == '/':
                    if right == 0:
                        raise ValueError("division by zero")
                    left = left / right
                else:
                    if right == 0:
                        raise ValueError("modulo by zero")
                    left = left % right
            else:
                break
        return left

    def parse_unary():
        tok = peek()
        if tok is not None and tok[0] == 'op' and tok[1] == '-':
            advance()
            return -parse_unary()
        if tok is not None and tok[0] == 'op' and tok[1] == '+':
            advance()
            return parse_unary()
        return parse_power()

    def parse_power():
        base = parse_atom()
        tok = peek()
        if tok is not None and tok[0] == 'op' and tok[1] == '^':
            advance()
            exponent = parse_unary()
            return base ** exponent
        return base

    def parse_atom():
        tok = peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        if tok[0] == 'num':
            advance()
            return tok[1]
        if tok[0] == 'var':
            advance()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"unknown variable: {name}")
            return float(variables[name])
        if tok[0] == 'op' and tok[1] == '(':
            advance()
            val = parse_expr()
            closing = peek()
            if closing is None or closing != ('op', ')'):
                raise ValueError("unbalanced parentheses")
            advance()
            return val
        raise ValueError(f"unexpected token: {tok[1]}")

    if not tokens:
        raise ValueError("empty expression")

    result = parse_expr()
    if pos != len(tokens):
        raise ValueError("malformed syntax")

    return float(result)
