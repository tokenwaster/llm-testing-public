def evaluate(expr, variables=None):
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
            j = i
            dot_count = 0
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    dot_count += 1
                j += 1
            num_str = expr[i:j]
            if dot_count > 1:
                raise ValueError("malformed number: {!r}".format(num_str))
            if num_str == '.':
                raise ValueError("malformed number: {!r}".format(num_str))
            tokens.append(('num', float(num_str)))
            i = j
            continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('name', expr[i:j]))
            i = j
            continue
        if c in '+-*/%^()':
            tokens.append(('op', c))
            i += 1
            continue
        raise ValueError("unexpected character: {!r}".format(c))

    # ---- Parser (recursive descent) ----
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def expect_op(ch):
        tok = peek()
        if tok is None or tok != ('op', ch):
            raise ValueError("expected {!r}".format(ch))
        advance()

    # Precedence:
    #   expr    -> add
    #   add     -> mul (('+'|'-') mul)*        left-assoc
    #   mul     -> unary (('*'|'/'|'%') unary)* left-assoc
    #   unary   -> '-' unary | power           unary minus binds looser than ^
    #   power   -> atom ('^' unary)?           right-assoc, RHS allows unary
    #   atom    -> num | name | '(' expr ')'

    def parse_expr():
        return parse_add()

    def parse_add():
        left = parse_mul()
        while True:
            tok = peek()
            if tok == ('op', '+'):
                advance()
                left = left + parse_mul()
            elif tok == ('op', '-'):
                advance()
                left = left - parse_mul()
            else:
                return left

    def parse_mul():
        left = parse_unary()
        while True:
            tok = peek()
            if tok == ('op', '*'):
                advance()
                left = left * parse_unary()
            elif tok == ('op', '/'):
                advance()
                right = parse_unary()
                if right == 0:
                    raise ValueError("division by zero")
                left = left / right
            elif tok == ('op', '%'):
                advance()
                right = parse_unary()
                if right == 0:
                    raise ValueError("modulo by zero")
                left = left % right
            else:
                return left

    def parse_unary():
        tok = peek()
        if tok == ('op', '-'):
            advance()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_atom()
        tok = peek()
        if tok == ('op', '^'):
            advance()
            exponent = parse_unary()  # right-assoc; RHS allows unary minus
            return base ** exponent
        return base

    def parse_atom():
        tok = peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        kind, val = tok
        if kind == 'num':
            advance()
            return float(val)
        if kind == 'name':
            advance()
            if val not in variables:
                raise ValueError("unknown variable: {!r}".format(val))
            return float(variables[val])
        if tok == ('op', '('):
            advance()
            inner = parse_expr()
            expect_op(')')
            return inner
        raise ValueError("unexpected token: {!r}".format(val))

    if not tokens:
        raise ValueError("empty expression")

    result = parse_expr()
    if pos != len(tokens):
        raise ValueError("unexpected trailing tokens")

    try:
        return float(result)
    except (TypeError, ValueError):
        raise ValueError("could not produce a numeric result")
