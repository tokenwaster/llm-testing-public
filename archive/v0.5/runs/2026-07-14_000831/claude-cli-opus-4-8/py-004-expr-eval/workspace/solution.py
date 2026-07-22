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
            tokens.append((c, c))
            i += 1
            continue
        if c.isdigit() or c == ".":
            start = i
            dot_seen = False
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    if dot_seen:
                        raise ValueError("malformed number")
                    dot_seen = True
                i += 1
            num_str = expr[start:i]
            if num_str == ".":
                raise ValueError("malformed number")
            tokens.append(("num", float(num_str)))
            continue
        if c.isalpha() or c == "_":
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(("name", expr[start:i]))
            continue
        raise ValueError(f"unexpected character: {c!r}")

    # ---- Recursive descent parser ----
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else (None, None)

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    # expr := add
    # add  := mul (('+'|'-') mul)*
    # mul  := unary (('*'|'/'|'%') unary)*
    # unary := '-' unary | power
    # power := atom ('^' unary)?     (right-assoc; RHS is unary so -2^2 handled at higher level)
    # atom := num | name | '(' add ')'

    def parse_add():
        value = parse_mul()
        while True:
            typ, _ = peek()
            if typ == "+":
                advance()
                value = value + parse_mul()
            elif typ == "-":
                advance()
                value = value - parse_mul()
            else:
                break
        return value

    def parse_mul():
        value = parse_unary()
        while True:
            typ, _ = peek()
            if typ == "*":
                advance()
                value = value * parse_unary()
            elif typ == "/":
                advance()
                rhs = parse_unary()
                if rhs == 0:
                    raise ValueError("division by zero")
                value = value / rhs
            elif typ == "%":
                advance()
                rhs = parse_unary()
                if rhs == 0:
                    raise ValueError("modulo by zero")
                value = value % rhs
            else:
                break
        return value

    def parse_unary():
        typ, _ = peek()
        if typ == "-":
            advance()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_atom()
        typ, _ = peek()
        if typ == "^":
            advance()
            # right-associative; RHS binds unary so 2^-3 works and 2^3^2 chains right
            exponent = parse_unary()
            return float(base ** exponent)
        return base

    def parse_atom():
        typ, val = peek()
        if typ == "num":
            advance()
            return float(val)
        if typ == "name":
            advance()
            if val not in variables:
                raise ValueError(f"unknown variable: {val}")
            return float(variables[val])
        if typ == "(":
            advance()
            value = parse_add()
            typ2, _ = peek()
            if typ2 != ")":
                raise ValueError("unbalanced parentheses")
            advance()
            return value
        raise ValueError("malformed syntax")

    if not tokens:
        raise ValueError("empty expression")

    result = parse_add()
    if pos != len(tokens):
        raise ValueError("malformed syntax")

    try:
        return float(result)
    except (TypeError, ValueError):
        raise ValueError("invalid result")
