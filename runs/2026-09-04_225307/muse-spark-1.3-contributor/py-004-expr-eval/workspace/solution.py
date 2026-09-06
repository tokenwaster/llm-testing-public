def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        vars_map = {}
    else:
        vars_map = variables
    s = expr
    n = len(s)
    pos = 0

    def skip():
        nonlocal pos
        while pos < n and s[pos] in " \t\n\r\f\v":
            pos += 1

    def is_digit(c):
        return "0" <= c <= "9"

    def is_alpha(c):
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"

    def is_alnum(c):
        return ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9") or c == "_"

    def parse_expr():
        nonlocal pos
        left = parse_term()
        while True:
            skip()
            if pos < n and (s[pos] == "+" or s[pos] == "-"):
                op = s[pos]
                pos += 1
                right = parse_term()
                if op == "+":
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    def parse_term():
        nonlocal pos
        left = parse_unary()
        while True:
            skip()
            if pos < n and (s[pos] == "*" or s[pos] == "/" or s[pos] == "%"):
                op = s[pos]
                pos += 1
                right = parse_unary()
                if op == "*":
                    left = left * right
                elif op == "/":
                    if right == 0:
                        raise ValueError("division by zero")
                    left = left / right
                else:
                    if right == 0:
                        raise ValueError("division by zero")
                    left = left % right
            else:
                break
        return left

    def parse_unary():
        nonlocal pos
        skip()
        if pos < n and s[pos] == "-":
            pos += 1
            v = parse_unary()
            return -v
        if pos < n and s[pos] == "+":
            pos += 1
            v = parse_unary()
            return v
        return parse_power()

    def parse_power():
        nonlocal pos
        base = parse_primary()
        skip()
        if pos < n and s[pos] == "^":
            pos += 1
            exp = parse_unary()
            try:
                r = base ** exp
            except ZeroDivisionError:
                raise ValueError("division by zero")
            if isinstance(r, complex):
                raise ValueError("invalid operation")
            return float(r)
        return base

    def parse_primary():
        nonlocal pos
        skip()
        if pos >= n:
            raise ValueError("unexpected end")
        c = s[pos]
        if c == "(":
            pos += 1
            v = parse_expr()
            skip()
            if pos >= n or s[pos] != ")":
                raise ValueError("unbalanced parentheses")
            pos += 1
            return v
        if is_alpha(c):
            return parse_name()
        if is_digit(c) or c == ".":
            return parse_number()
        raise ValueError("unexpected character")

    def parse_number():
        nonlocal pos
        skip()
        start = pos
        has_d = False
        while pos < n and is_digit(s[pos]):
            pos += 1
            has_d = True
        if pos < n and s[pos] == ".":
            pos += 1
            while pos < n and is_digit(s[pos]):
                pos += 1
                has_d = True
        if not has_d:
            raise ValueError("invalid number")
        text = s[start:pos]
        try:
            return float(text)
        except Exception:
            raise ValueError("invalid number")

    def parse_name():
        nonlocal pos
        skip()
        if pos >= n or not is_alpha(s[pos]):
            raise ValueError("expected name")
        start = pos
        pos += 1
        while pos < n and is_alnum(s[pos]):
            pos += 1
        name = s[start:pos]
        if name not in vars_map:
            raise ValueError("unknown variable")
        try:
            return float(vars_map[name])
        except Exception:
            raise ValueError("invalid variable value")

    skip()
    if pos >= n:
        raise ValueError("empty expression")
    result = parse_expr()
    skip()
    if pos != n:
        raise ValueError("trailing characters")
    return float(result)
