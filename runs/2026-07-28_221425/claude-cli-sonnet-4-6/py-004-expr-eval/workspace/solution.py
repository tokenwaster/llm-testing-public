def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # --- Tokenizer ---
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i].isdigit() or expr[i] == '.':
            j = i
            dot_count = 0
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    dot_count += 1
                    if dot_count > 1:
                        raise ValueError(f"Malformed number near position {j}")
                j += 1
            tokens.append(('NUMBER', expr[i:j]))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('NAME', expr[i:j]))
            i = j
        elif expr[i] in '+-*/%^()':
            tokens.append((expr[i], expr[i]))
            i += 1
        else:
            raise ValueError(f"Unknown character: {expr[i]!r}")

    # --- Recursive-descent parser ---
    pos = [0]

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    def expect(kind):
        tok = peek()
        if tok is None or tok[0] != kind:
            raise ValueError(f"Expected '{kind}', got {tok!r}")
        return consume()

    # additive: lowest precedence  (+  -)
    def parse_additive():
        left = parse_multiplicative()
        while peek() and peek()[0] in ('+', '-'):
            op = consume()[0]
            right = parse_multiplicative()
            left = left + right if op == '+' else left - right
        return left

    # multiplicative  (*  /  %)
    def parse_multiplicative():
        left = parse_unary()
        while peek() and peek()[0] in ('*', '/', '%'):
            op = consume()[0]
            right = parse_unary()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0.0:
                    raise ValueError("Division by zero")
                left /= right
            else:
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left %= right
        return left

    # unary minus — binds looser than ^, so it sits above multiplicative
    # but below additive; "below" here means closer to the atoms.
    def parse_unary():
        if peek() and peek()[0] == '-':
            consume()
            return -parse_unary()
        return parse_power()

    # ^ right-associative: base ^ (unary-level rhs)
    def parse_power():
        base = parse_atom()
        if peek() and peek()[0] == '^':
            consume()
            exp = parse_unary()   # right-associative: recurse at unary level
            return float(base ** exp)
        return base

    def parse_atom():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if tok[0] == 'NUMBER':
            consume()
            try:
                return float(tok[1])
            except ValueError:
                raise ValueError(f"Malformed number: {tok[1]!r}")

        if tok[0] == 'NAME':
            consume()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name!r}")
            return float(variables[name])

        if tok[0] == '(':
            consume()
            val = parse_additive()
            if peek() is None or peek()[0] != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            consume()
            return val

        raise ValueError(f"Unexpected token: {tok[1]!r}")

    if not tokens:
        raise ValueError("Empty expression")

    result = parse_additive()

    if pos[0] < len(tokens):
        raise ValueError(f"Unexpected token: {tokens[pos[0]][1]!r}")

    return float(result)
