def tokenize(expr: str):
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]

        # Skip whitespace
        if c.isspace():
            i += 1
            continue

        # Numbers (integers and decimals)
        if c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i + 1].isdigit()):
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUMBER', expr[i:j]))
            i = j
            continue

        # Variable names: [a-zA-Z_][a-zA-Z0-9_]*
        if c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VARIABLE', expr[i:j]))
            i = j
            continue

        # Operators and parentheses
        if c in '+-*/%^()':
            tokens.append((c, c))
            i += 1
            continue

        raise ValueError(f"malformed syntax at character '{c}'")

    return tokens


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = tokenize(expr)
    pos = [0]  # mutable index for parsing state

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else ('EOF', '')

    def advance():
        tok = tokens[pos[0]]
        pos[0] += 1
        return tok

    def parse_expr():
        """expr → term (('+' | '-') term)*"""
        left = parse_term()
        while True:
            tok = peek()
            if tok[0] in ('+', '-'):
                op, _ = advance()
                right = parse_term()
                left = left + right if op == '+' else left - right
            else:
                break
        return float(left)

    def parse_term():
        """term → unary (('*' | '/' | '%') unary)*"""
        left = parse_unary()
        while True:
            tok = peek()
            if tok[0] in ('*', '/', '%'):
                op, _ = advance()
                right = parse_unary()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("division by zero")
                    left = left / right
                else:
                    if right == 0:
                        raise ValueError("modulo by zero")
                    left = left % right
            else:
                break
        return float(left)

    def parse_unary():
        """unary → '-' unary | '+' unary | power"""
        tok = peek()
        if tok[0] == '-':
            advance()
            val = parse_unary()  # handles --3 etc.
            return -val
        elif tok[0] == '+':
            advance()
            return parse_unary()
        else:
            return parse_power()

    def parse_power():
        """power → atom ('^' power)?   (right-associative)"""
        base = parse_atom()
        if peek()[0] == '^':
            advance()
            exp = parse_power()  # right recursion for right-associativity
            return float(base) ** float(exp)
        return float(base)

    def parse_atom():
        """atom → NUMBER | VARIABLE | '(' expr ')'"""
        tok = peek()
        if tok[0] == '(':
            advance()  # consume '('
            val = parse_expr()
            rtok = peek()
            if rtok[0] != ')':
                raise ValueError("unbalanced parentheses")
            advance()  # consume ')'
            return val
        elif tok[0] in ('NUMBER', 'VARIABLE'):
            _, name = advance()
            try:
                return float(name)
            except ValueError:
                pass
            if name not in variables:
                raise ValueError(f"unknown variable '{name}'")
            return float(variables[name])
        else:
            tok_name, _ = peek()
            raise ValueError(f"malformed syntax at token {tok_name}")

    result = parse_expr()

    # Check for leftover tokens (should be none)
    if pos[0] < len(tokens):
        tok_name, _ = peek()
        raise ValueError(f"unexpected token: {tok_name}")

    return result
