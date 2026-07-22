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
        if c.isdigit() or c == '.':
            start = i
            dot_seen = False
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.':
                    if dot_seen:
                        raise ValueError(f"malformed number in {expr!r}")
                    dot_seen = True
                i += 1
            num_str = expr[start:i]
            if num_str == '.':
                raise ValueError("malformed number '.'")
            tokens.append(('NUM', float(num_str)))
            continue
        if c.isalpha() or c == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('NAME', expr[start:i]))
            continue
        if c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1
            continue
        raise ValueError(f"unexpected character {c!r}")

    # ---- Recursive descent parser ----
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else (None, None)

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    # expr    := add
    # add     := mul (('+'|'-') mul)*
    # mul     := unary (('*'|'/'|'%') unary)*
    # unary   := ('-')* power
    # power   := atom ('^' unary)?      (right-assoc; unary binds looser than ^)
    # atom    := NUM | NAME | '(' expr ')'

    def parse_add():
        val = parse_mul()
        while True:
            typ, v = peek()
            if typ == 'OP' and v in ('+', '-'):
                advance()
                rhs = parse_mul()
                val = val + rhs if v == '+' else val - rhs
            else:
                return val

    def parse_mul():
        val = parse_unary()
        while True:
            typ, v = peek()
            if typ == 'OP' and v in ('*', '/', '%'):
                advance()
                rhs = parse_unary()
                if v == '*':
                    val = val * rhs
                elif v == '/':
                    if rhs == 0:
                        raise ValueError("division by zero")
                    val = val / rhs
                else:
                    if rhs == 0:
                        raise ValueError("modulo by zero")
                    val = val % rhs
            else:
                return val

    def parse_unary():
        typ, v = peek()
        if typ == 'OP' and v == '-':
            advance()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_atom()
        typ, v = peek()
        if typ == 'OP' and v == '^':
            advance()
            exponent = parse_unary()  # right-assoc; unary allowed on rhs
            return float(base ** exponent)
        return base

    def parse_atom():
        typ, v = peek()
        if typ == 'NUM':
            advance()
            return float(v)
        if typ == 'NAME':
            advance()
            if v not in variables:
                raise ValueError(f"unknown variable {v!r}")
            return float(variables[v])
        if typ == 'OP' and v == '(':
            advance()
            val = parse_add()
            typ2, v2 = peek()
            if not (typ2 == 'OP' and v2 == ')'):
                raise ValueError("unbalanced parentheses")
            advance()
            return val
        raise ValueError("malformed syntax")

    if not tokens:
        raise ValueError("empty expression")

    result = parse_add()
    if pos != len(tokens):
        raise ValueError("malformed syntax: trailing tokens")

    try:
        return float(result)
    except (TypeError, ValueError):
        raise ValueError("result is not a real number")
