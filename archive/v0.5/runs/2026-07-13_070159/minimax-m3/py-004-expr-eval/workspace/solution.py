def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    # Tokenizer
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
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(('NUM', expr[i:j]))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('IDENT', expr[i:j]))
            i = j
        elif c in '+-*/%^()':
            tokens.append((c, c))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c!r}")

    tokens.append(('EOF', None))

    pos = [0]

    def peek():
        return tokens[pos[0]]

    def advance():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    # Pratt parser (top-down operator precedence)
    # Precedences (higher = tighter binding):
    #   additive (+, -)       : lbp = 10, left-associative (rbp = 10)
    #   multiplicative (*,/,%): lbp = 20, left-associative (rbp = 20)
    #   exponentiation (^)     : lbp = 30, right-associative (rbp = 29)
    #   unary minus            : prefix bp = 25 (between * and ^)

    def nud():
        tok = peek()
        kind = tok[0]
        if kind == 'NUM':
            advance()
            return float(tok[1])
        elif kind == 'IDENT':
            advance()
            name = tok[1]
            if name not in variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(variables[name])
        elif kind == '-':
            advance()
            return -parse_expression(25)
        elif kind == '(':
            advance()
            val = parse_expression(0)
            if peek()[0] != ')':
                raise ValueError("Unbalanced parentheses: missing closing parenthesis")
            advance()
            return val
        else:
            raise ValueError(f"Unexpected token in expression: {tok[1]!r}")

    def led(left):
        op = advance()[0]
        if op == '+':
            return left + parse_expression(10)
        elif op == '-':
            return left - parse_expression(10)
        elif op == '*':
            return left * parse_expression(20)
        elif op == '/':
            right = parse_expression(20)
            if right == 0:
                raise ValueError("Division by zero")
            return left / right
        elif op == '%':
            right = parse_expression(20)
            if right == 0:
                raise ValueError("Modulo by zero")
            return left % right
        elif op == '^':
            return left ** parse_expression(29)

    def parse_expression(min_bp):
        left = nud()
        while True:
            tok = peek()
            op = tok[0]
            if op == '+' or op == '-':
                lbp = 10
            elif op == '*' or op == '/' or op == '%':
                lbp = 20
            elif op == '^':
                lbp = 30
            else:
                break
            if lbp <= min_bp:
                break
            left = led(left)
        return left

    result = parse_expression(0)
    if peek()[0] != 'EOF':
        raise ValueError(f"Unexpected token at end of expression: {peek()[1]!r}")
    return float(result)
