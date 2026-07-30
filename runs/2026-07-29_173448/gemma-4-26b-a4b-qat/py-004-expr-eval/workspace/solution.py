def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    def tokenize(expr):
        tokens = []
        i = 0
        while i < len(expr):
            char = expr[i]
            if char.isspace():
                i += 1
                continue
            if char.isdigit() or char == '.':
                j = i
                while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                    j += 1
                num_str = expr[i:j]
                if num_str == '.':
                    raise ValueError("Malformed syntax: invalid number")
                tokens.append(('NUM', float(num_str)))
                i = j
            elif char.isalpha() or char == '_':
                j = i
                while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                    j += 1
                tokens.append(('VAR', expr[i:j]))
                i = j
            elif char in '+-*/%^()':
                tokens.append(('OP', char))
                i += 1
            else:
                raise ValueError(f"Malformed syntax: unexpected character {char}")
        return tokens

    tokens = tokenize(expr)
    pos = 0

    def peek():
        nonlocal pos
        return tokens[pos] if pos < len(tokens) else None

    def consume(expected_type=None, expected_value=None):
        nonlocal pos
        token = peek()
        if not token:
            raise ValueError("Malformed syntax: unexpected end of expression")
        if expected_type and token[0] != expected_type:
            raise ValueError(f"Malformed syntax: expected {expected_type}, got {token[0]}")
        if expected_value and token[1] != expected_value:
            raise ValueError(f"Malformed syntax: expected {expected_value}, got {token[1]}")
        pos += 1
        return token

    def parse_primary():
        token = peek()
        if not token:
            raise ValueError("Malformed syntax: unexpected end of expression")
        if token[0] == 'NUM':
            return consume('NUM')[1]
        elif token[0] == 'VAR':
            var_name = consume('VAR')[1]
            if var_name not in variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(variables[var_name])
        elif token[0] == 'OP' and token[1] == '(':
            consume('OP', '(')
            val = parse_expr()
            if not peek() or peek()[1] != ')':
                raise ValueError("Malformed syntax: unbalanced parentheses")
            consume('OP', ')')
            return val
        else:
            raise ValueError("Malformed syntax: expected number, variable, or parenthesis")

    def parse_power():
        """Handles exponentiation (^) which is right-associative and has highest precedence."""
        val = parse_primary()
        if peek() and peek()[1] == '^':
            consume('OP', '^')
            # RHS is unary to allow 2^-2 and allow right-associative chain 2^3^2
            val = val ** parse_unary()
        return val

    def parse_unary():
        """Handles unary minus, which binds looser than exponentiation."""
        if peek() and peek()[1] == '-':
            consume('OP', '-')
            return -parse_unary()
        return parse_power()

    def parse_factor():
        """Handles multiplication (*), division (/), and modulo (%)."""
        val = parse_unary()
        while peek() and peek()[1] in ('*', '/', '%'):
            op = consume('OP')[1]
            right = parse_unary()
            if op == '*':
                val *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                val /= right
            elif op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                val %= right
        return val

    def parse_expr():
        """Handles addition (+) and subtraction (-)."""
        val = parse_factor()
        while peek() and peek()[1] in ('+', '-'):
            op = consume('OP')[1]
            right = parse_factor()
            if op == '+':
                val += right
            else:
                val -= right
        return val

    # Start parsing the expression
    result = parse_expr()

    # If there are remaining tokens, the expression was malformed (e.g., "1+2 3")
    if pos < len(tokens):
        raise ValueError("Malformed syntax: trailing tokens")

    return float(result)
