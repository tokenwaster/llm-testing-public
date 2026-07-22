def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # --- Tokenizer ---
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or c == '.':
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            raw = expr[i:j]
            try:
                tokens.append(('NUM', float(raw)))
            except ValueError:
                raise ValueError(f"Malformed number: {raw!r}")
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        elif c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c!r}")

    # --- Recursive-descent parser ---
    # Precedence (low → high):
    #   additive  (+, -)
    #   multiplicative  (*, /, %)
    #   unary  (-)          ← sits ABOVE mul but BELOW power, so -2^2 = -(2^2)
    #   power  (^, right-associative)
    #   primary  (number | variable | '(' expr ')')

    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def consume():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def expect(kind, val):
        tok = peek()
        if tok is None or tok[0] != kind or tok[1] != val:
            raise ValueError(f"Expected '{val}', got {tok!r}")
        consume()

    def parse_expr():
        return parse_additive()

    def parse_additive():
        left = parse_multiplicative()
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = consume()[1]
                right = parse_multiplicative()
                left = left + right if op == '+' else left - right
            else:
                break
        return left

    def parse_multiplicative():
        left = parse_unary()
        while True:
            tok = peek()
            if tok and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = consume()[1]
                right = parse_unary()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0.0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:
                    if right == 0.0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        return left

    def parse_unary():
        tok = peek()
        if tok and tok[0] == 'OP' and tok[1] == '-':
            consume()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_primary()
        tok = peek()
        if tok and tok[0] == 'OP' and tok[1] == '^':
            consume()
            # Right-associative: right operand goes through unary so that
            # -2^2 = -(2^2) but 2^-1 works too.
            exp = parse_unary()
            return float(base ** exp)
        return base

    def parse_primary():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if tok[0] == 'NUM':
            consume()
            return tok[1]
        if tok[0] == 'VAR':
            consume()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name!r}")
            return float(variables[name])
        if tok[0] == 'OP' and tok[1] == '(':
            consume()
            val = parse_expr()
            closing = peek()
            if closing is None or closing[1] != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            consume()
            return val
        raise ValueError(f"Unexpected token: {tok!r}")

    result = parse_expr()

    if pos != len(tokens):
        raise ValueError(f"Unexpected token: {tokens[pos]!r}")

    return float(result)
