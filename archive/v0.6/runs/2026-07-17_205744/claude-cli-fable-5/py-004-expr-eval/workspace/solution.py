import re


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # --- Tokenizer ---
    token_re = re.compile(r"""
        \s*(?:
            (?P<num>\d+(?:\.\d+)?)      |
            (?P<name>[a-zA-Z_][a-zA-Z0-9_]*) |
            (?P<op>[+\-*/%^()])
        )
    """, re.VERBOSE)

    tokens = []
    pos = 0
    while pos < len(expr):
        m = token_re.match(expr, pos)
        if not m:
            # remaining might be only whitespace
            if expr[pos:].strip() == "":
                break
            raise ValueError(f"invalid character at position {pos}: {expr[pos]!r}")
        if m.lastgroup == "num":
            tokens.append(("num", float(m.group("num"))))
        elif m.lastgroup == "name":
            tokens.append(("name", m.group("name")))
        else:
            tokens.append(("op", m.group("op")))
        pos = m.end()

    # --- Recursive-descent parser/evaluator ---
    # grammar:
    #   expr    := term (('+'|'-') term)*
    #   term    := factor (('*'|'/'|'%') factor)*
    #   factor  := '-' factor | power
    #   power   := atom ('^' factor)?        (right-assoc; unary minus allowed on rhs)
    #   atom    := number | name | '(' expr ')'
    idx = 0

    def peek():
        return tokens[idx] if idx < len(tokens) else (None, None)

    def parse_expr():
        nonlocal idx
        value = parse_term()
        while peek() == ("op", "+") or peek() == ("op", "-"):
            op = tokens[idx][1]
            idx += 1
            rhs = parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_term():
        nonlocal idx
        value = parse_factor()
        while peek() in (("op", "*"), ("op", "/"), ("op", "%")):
            op = tokens[idx][1]
            idx += 1
            rhs = parse_factor()
            if op == "*":
                value = value * rhs
            else:
                if rhs == 0:
                    raise ValueError("division by zero" if op == "/" else "modulo by zero")
                value = value / rhs if op == "/" else value % rhs
        return value

    def parse_factor():
        nonlocal idx
        if peek() == ("op", "-"):
            idx += 1
            return -parse_factor()
        return parse_power()

    def parse_power():
        nonlocal idx
        base = parse_atom()
        if peek() == ("op", "^"):
            idx += 1
            # right-associative; exponent may itself carry unary minus
            exponent = parse_factor()
            return float(base ** exponent)
        return base

    def parse_atom():
        nonlocal idx
        kind, val = peek()
        if kind == "num":
            idx += 1
            return val
        if kind == "name":
            idx += 1
            if val not in variables:
                raise ValueError(f"unknown variable: {val}")
            return float(variables[val])
        if (kind, val) == ("op", "("):
            idx += 1
            value = parse_expr()
            if peek() != ("op", ")"):
                raise ValueError("unbalanced parentheses")
            idx += 1
            return value
        raise ValueError(f"unexpected token: {val!r}" if kind else "unexpected end of expression")

    if not tokens:
        raise ValueError("empty expression")
    result = parse_expr()
    if idx != len(tokens):
        raise ValueError(f"unexpected token: {tokens[idx][1]!r}")
    return float(result)
