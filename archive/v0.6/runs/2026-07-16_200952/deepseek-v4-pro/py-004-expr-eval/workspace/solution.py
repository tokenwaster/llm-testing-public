def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression without using eval/exec/ast.
    Supports +, -, *, /, %, ^ (right-associative), unary minus,
    parentheses, variables, and whitespace.
    Raises ValueError on malformed syntax, unknown variables,
    division/modulo by zero, or unbalanced parentheses.
    """
    if variables is None:
        variables = {}

    # ------------------- Tokenizer -------------------
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            if j < n and expr[j] == '.':
                j += 1
                # optional fractional digits
                while j < n and expr[j].isdigit():
                    j += 1
            num_str = expr[i:j]
            tokens.append(('NUM', float(num_str)))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            var_name = expr[i:j]
            tokens.append(('VAR', var_name))
            i = j
        elif c in '+-*/%^':
            tokens.append(('OP', c))
            i += 1
        elif c == '(':
            tokens.append(('LPAREN', c))
            i += 1
        elif c == ')':
            tokens.append(('RPAREN', c))
            i += 1
        else:
            raise ValueError(f"Invalid character: {c}")

    # ------------------- Recursive Descent Parser -------------------
    pos = 0

    def peek():
        if pos < len(tokens):
            return tokens[pos]
        return None

    def consume():
        nonlocal pos
        token = tokens[pos]
        pos += 1
        return token

    def expr():
        left = term()
        while (tok := peek()) and tok[0] == 'OP' and tok[1] in ('+', '-'):
            op = consume()[1]
            right = term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def term():
        left = factor()
        while (tok := peek()) and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
            op = consume()[1]
            right = factor()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def factor():
        # Unary minus (binds looser than ^)
        minus_count = 0
        while (tok := peek()) and tok[0] == 'OP' and tok[1] == '-':
            consume()
            minus_count += 1
        val = exponentiation()
        if minus_count % 2 == 1:
            val = -val
        return val

    def exponentiation():
        left = primary()
        if (tok := peek()) and tok[0] == 'OP' and tok[1] == '^':
            consume()
            right = exponentiation()  # right-associative
            left = left ** right
        return left

    def primary():
        tok = peek()
        if tok is None:
            raise ValueError("Malformed expression")
        if tok[0] == 'NUM':
            return consume()[1]
        elif tok[0] == 'VAR':
            var_name = consume()[1]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return variables[var_name]
        elif tok[0] == 'LPAREN':
            consume()
            val = expr()
            if peek() is None or peek()[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            consume()  # consume ')'
            return val
        else:
            raise ValueError("Malformed expression")

    result = expr()
    if peek() is not None:
        raise ValueError("Malformed expression")
    return float(result)
