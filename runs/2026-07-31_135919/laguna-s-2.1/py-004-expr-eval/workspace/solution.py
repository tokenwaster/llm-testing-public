def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression without eval/exec/ast.

    Grammar (precedence, lowest to highest):
        expr  := term  (('+' | '-') term)*
        term  := unary (('*' | '/' | '%') unary)*
        unary := ('+' | '-') unary | power
        power := primary ('^' unary)?          # ^ right-associative; unary binds looser
        primary := NUMBER | VARIABLE | '(' expr ')'
    """
    if variables is None:
        variables = {}

    # ------------------------------------------------------------------
    # Tokenizer
    # ------------------------------------------------------------------
    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1
            continue
        if c.isdigit() or c == '.':
            j = i
            seen_dot = False
            while j < n:
                ch = expr[j]
                if ch.isdigit():
                    j += 1
                elif ch == '.':
                    if seen_dot:
                        break
                    seen_dot = True
                    j += 1
                else:
                    break
            tokens.append(('NUM', expr[i:j]))
            i = j
            continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
            continue
        raise ValueError(f"Unexpected character: {c!r}")

    # ------------------------------------------------------------------
    # Recursive-descent parser
    # ------------------------------------------------------------------
    pos = 0

    def peek() -> tuple[str, str] | None:
        return tokens[pos] if pos < len(tokens) else None

    def advance() -> tuple[str, str]:
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expr() -> float:
        nonlocal pos
        result = parse_term()
        while True:
            tok = peek()
            if tok is not None and tok[0] == 'OP' and tok[1] in '+-':
                op = advance()[1]
                b = parse_term()
                result = result + b if op == '+' else result - b
            else:
                break
        return result

    def parse_term() -> float:
        nonlocal pos
        result = parse_unary()
        while True:
            tok = peek()
            if tok is not None and tok[0] == 'OP' and tok[1] in '*/%':
                op = advance()[1]
                b = parse_unary()
                if op == '*':
                    result = result * b
                elif op == '/':
                    if b == 0:
                        raise ValueError("Division by zero")
                    result = result / b
                else:  # '%'
                    if b == 0:
                        raise ValueError("Modulo by zero")
                    result = result % b
            else:
                break
        return result

    def parse_unary() -> float:
        nonlocal pos
        tok = peek()
        if tok is not None and tok[0] == 'OP' and tok[1] in '+-':
            op = advance()[1]
            operand = parse_unary()
            return -operand if op == '-' else operand
        return parse_power()

    def parse_power() -> float:
        nonlocal pos
        base = parse_primary()
        tok = peek()
        if tok is not None and tok[0] == 'OP' and tok[1] == '^':
            advance()
            exp = parse_unary()  # right side is a unary expr
            try:
                return base ** exp
            except ZeroDivisionError:
                raise ValueError("Division by zero")
            except (ValueError, OverflowError) as exc:
                # e.g. negative base to a fractional exponent
                raise ValueError(str(exc))
        return base

    def parse_primary() -> float:
        nonlocal pos
        tok = peek()
        if tok is None:
            raise ValueError("Unexpected end of input")
        if tok[0] == 'NUM':
            advance()
            try:
                return float(tok[1])
            except ValueError:
                raise ValueError(f"Invalid number: {tok[1]!r}")
        if tok[0] == 'VAR':
            advance()
            name = tok[1]
            if name in variables:
                return float(variables[name])
            raise ValueError(f"Unknown variable: {name!r}")
        if tok[0] == 'OP' and tok[1] == '(':
            advance()
            result = parse_expr()
            closing = peek()
            if closing is None or closing[0] != 'OP' or closing[1] != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            advance()
            return result
        raise ValueError(f"Unexpected token: {tok}")

    value = parse_expr()
    if pos != len(tokens):
        raise ValueError(f"Unexpected token: {tokens[pos]}")
    return float(value)
