def evaluate(expr, variables=None):
    if variables is None:
        variables = {}

    # ---- Tokenizer ----
    tokens = []
    i = 0
    n = len(expr)
    ops = set("+-*/%^()")
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or c == ".":
            j = i
            seen_dot = False
            while j < n and (expr[j].isdigit() or expr[j] == "."):
                if expr[j] == ".":
                    if seen_dot:
                        raise ValueError("malformed number")
                    seen_dot = True
                j += 1
            num_str = expr[i:j]
            if num_str == ".":
                raise ValueError("malformed number")
            tokens.append(("num", float(num_str)))
            i = j
            continue
        if c.isalpha() or c == "_":
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append(("name", expr[i:j]))
            i = j
            continue
        if c in ops:
            tokens.append(("op", c))
            i += 1
            continue
        raise ValueError("unexpected character: " + c)

    # ---- Parser (recursive descent) ----
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_add():
        value = parse_mul()
        while True:
            tok = peek()
            if tok and tok[0] == "op" and tok[1] in ("+", "-"):
                advance()
                rhs = parse_mul()
                value = value + rhs if tok[1] == "+" else value - rhs
            else:
                return value

    def parse_mul():
        value = parse_unary()
        while True:
            tok = peek()
            if tok and tok[0] == "op" and tok[1] in ("*", "/", "%"):
                advance()
                rhs = parse_unary()
                if tok[1] == "*":
                    value = value * rhs
                elif tok[1] == "/":
                    if rhs == 0:
                        raise ValueError("division by zero")
                    value = value / rhs
                else:
                    if rhs == 0:
                        raise ValueError("modulo by zero")
                    value = value % rhs
            else:
                return value

    def parse_unary():
        tok = peek()
        if tok and tok[0] == "op" and tok[1] == "-":
            advance()
            return -parse_unary()
        return parse_power()

    def parse_power():
        base = parse_primary()
        tok = peek()
        if tok and tok[0] == "op" and tok[1] == "^":
            advance()
            exponent = parse_unary()  # right-associative; allows unary in exponent
            try:
                result = base ** exponent
            except (ValueError, OverflowError, ZeroDivisionError):
                raise ValueError("invalid exponentiation")
            if isinstance(result, complex):
                raise ValueError("complex result")
            return result
        return base

    def parse_primary():
        tok = peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        if tok[0] == "num":
            advance()
            return tok[1]
        if tok[0] == "name":
            advance()
            if tok[1] not in variables:
                raise ValueError("unknown variable: " + tok[1])
            return float(variables[tok[1]])
        if tok[0] == "op" and tok[1] == "(":
            advance()
            value = parse_add()
            closing = peek()
            if not (closing and closing[0] == "op" and closing[1] == ")"):
                raise ValueError("unbalanced parentheses")
            advance()
            return value
        raise ValueError("unexpected token: " + str(tok[1]))

    if not tokens:
        raise ValueError("empty expression")

    result = parse_add()
    if pos != len(tokens):
        raise ValueError("unexpected trailing input")
    return float(result)
