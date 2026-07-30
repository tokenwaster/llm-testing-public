def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluate an arithmetic expression string without using eval/exec/ast.

    Grammar (lowest to highest precedence):
        additive      : multiplicative (('+' | '-') multiplicative)*
        multiplicative: unary (('*' | '/' | '%') unary)*
        unary         : '-' unary | power
        power         : atom ('^' unary)?   # right-associative
        atom          : NUMBER | IDENT | '(' additive ')'
    """
    if variables is None:
        variables = {}

    pos = 0
    n = len(expr)

    # ------------------------------------------------------------------
    # Lexer helpers
    # ------------------------------------------------------------------

    def skip_ws() -> None:
        nonlocal pos
        while pos < n and expr[pos].isspace():
            pos += 1

    def peek() -> str | None:
        skip_ws()
        return expr[pos] if pos < n else None

    def consume() -> str:
        skip_ws()
        if pos >= n:
            raise ValueError("Unexpected end of expression")
        nonlocal pos
        ch = expr[pos]
        pos += 1
        return ch

    def expect(ch: str) -> None:
        skip_ws()
        if pos >= n or expr[pos] != ch:
            got = expr[pos] if pos < n else "EOF"
            raise ValueError(f"Expected '{ch}', got '{got}' at position {pos}")
        nonlocal pos
        pos += 1

    # ------------------------------------------------------------------
    # Recursive-descent parser
    # ------------------------------------------------------------------

    def parse_number() -> float:
        nonlocal pos
        skip_ws()
        start = pos
        has_dot = False
        if pos < n and expr[pos] == '.':
            has_dot = True
            pos += 1
        while pos < n and expr[pos].isdigit():
            pos += 1
        if not has_dot and pos < n and expr[pos] == '.':
            pos += 1
            while pos < n and expr[pos].isdigit():
                pos += 1
        if pos == start:
            raise ValueError(f"Expected number at position {pos}")
        raw = expr[start:pos]
        try:
            return float(raw)
        except ValueError:
            raise ValueError(f"Malformed number '{raw}' at position {start}")

    def parse_name() -> str:
        nonlocal pos
        skip_ws()
        start = pos
        if pos >= n or not (expr[pos].isalpha() or expr[pos] == '_'):
            raise ValueError(f"Expected identifier at position {pos}")
        while pos < n and (expr[pos].isalnum() or expr[pos] == '_'):
            pos += 1
        return expr[start:pos]

    def parse_atom() -> float:
        ch = peek()
        if ch is None:
            raise ValueError("Unexpected end of expression")

        if ch == '(':
            consume()
            val = parse_additive()
            expect(')')
            return val

        if ch.isdigit() or ch == '.':
            return parse_number()

        if ch.isalpha() or ch == '_':
            name = parse_name()
            if name not in variables:
                raise ValueError(f"Unknown variable: '{name}'")
            return float(variables[name])

        raise ValueError(f"Unexpected character '{ch}' at position {pos}")

    def parse_power() -> float:
        base = parse_atom()
        if peek() == '^':
            consume()
            exp = parse_unary()
            try:
                return float(base ** exp)
            except ZeroDivisionError:
                raise ValueError("Zero raised to a negative power")
        return base

    def parse_unary() -> float:
        if peek() == '-':
            consume()
            return -parse_unary()
        return parse_power()

    def parse_multiplicative() -> float:
        left = parse_unary()
        while True:
            op = peek()
            if op == '*':
                consume()
                left *= parse_unary()
            elif op == '/':
                consume()
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Division by zero")
                left /= right
            elif op == '%':
                consume()
                right = parse_unary()
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left %= right
            else:
                break
        return left

    def parse_additive() -> float:
        left = parse_multiplicative()
        while True:
            op = peek()
            if op == '+':
                consume()
                left += parse_multiplicative()
            elif op == '-':
                consume()
                left -= parse_multiplicative()
            else:
                break
        return left

    result = parse_additive()

    trailing = peek()
    if trailing is not None:
        raise ValueError(f"Unexpected character '{trailing}' at position {pos}")

    return float(result)
