def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # ---- Tokenizer ----
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in "+-*/%^()":
            tokens.append(("op", c))
            i += 1
            continue
        if c.isdigit() or c == ".":
            start = i
            seen_dot = False
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    if seen_dot:
                        raise ValueError(f"Malformed number in expression: {expr!r}")
                    seen_dot = True
                i += 1
            num_str = expr[start:i]
            if num_str == ".":
                raise ValueError(f"Malformed number in expression: {expr!r}")
            tokens.append(("num", float(num_str)))
            continue
        if c.isalpha() or c == "_":
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(("name", expr[start:i]))
            continue
        raise ValueError(f"Unexpected character {c!r} in expression")

    # ---- Recursive descent parser ----
    # grammar (lowest to highest precedence):
    #   expr    := term (('+' | '-') term)*
    #   term    := factor (('*' | '/' | '%') factor)*
    #   factor  := unary
    #   unary   := '-' unary | power
    #   power   := atom ('^' unary)?      (right-assoc; '^' binds tighter than unary minus)
    #   atom    := number | name | '(' expr ')'
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expr():
        value = parse_term()
        while True:
            tok = peek()
            if tok is not None and tok[0] == "op" and tok[1] in "+-":
                advance()
                rhs = parse_term()
                if tok[1] == "+":
                    value = value + rhs
                else:
                    value = value - rhs
            else:
                break
        return value

    def parse_term():
        value = parse_unary()
        while True:
            tok = peek()
            if tok is not None and tok[0] == "op" and tok[1] in "*/%":
                advance()
                rhs = parse_unary()
                if tok[1] == "*":
                    value = value * rhs
                elif tok[1] == "/":
                    if rhs == 0:
                        raise ValueError("Division by zero")
                    value = value / rhs
                else:
                    if rhs == 0:
                        raise ValueError("Modulo by zero")
                    value = value % rhs
            else:
                break
        return value

    def parse_unary():
        tok = peek()
        if tok is not None and tok[0] == "op" and tok[1] == "-":
            advance()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_atom()
        tok = peek()
        if tok is not None and tok[0] == "op" and tok[1] == "^":
            advance()
            # right-associative; exponent allows unary minus (-2^2 handled at unary level,
            # but 2^-3 must work here)
            exponent = parse_unary()
            return float(base ** exponent)
        return base

    def parse_atom():
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        kind, val = tok
        if kind == "num":
            advance()
            return float(val)
        if kind == "name":
            advance()
            if val not in variables:
                raise ValueError(f"Unknown variable: {val}")
            return float(variables[val])
        if kind == "op" and val == "(":
            advance()
            value = parse_expr()
            closing = peek()
            if closing is None or closing != ("op", ")"):
                raise ValueError("Unbalanced parentheses")
            advance()
            return value
        raise ValueError(f"Unexpected token: {val!r}")

    if not tokens:
        raise ValueError("Empty expression")

    result = parse_expr()
    if pos != len(tokens):
        raise ValueError("Malformed expression: unexpected trailing tokens")

    try:
        return float(result)
    except (TypeError, ValueError):
        raise ValueError("Expression did not evaluate to a number")
