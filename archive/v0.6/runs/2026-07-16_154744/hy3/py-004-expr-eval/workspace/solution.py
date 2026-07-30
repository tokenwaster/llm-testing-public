def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c == '(' or c == ')':
            tokens.append(('paren', c))
            i += 1
            continue
        if c in '+-*/%^':
            tokens.append(('op', c))
            i += 1
            continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('var', expr[i:j]))
            i = j
            continue
        if c.isdigit() or c == '.':
            j = i
            seen_dot = False
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    if seen_dot:
                        raise ValueError("malformed number")
                    seen_dot = True
                j += 1
            num_str = expr[i:j]
            if num_str == '.' or num_str.endswith('.'):
                raise ValueError("malformed number")
            try:
                val = float(num_str)
            except ValueError:
                raise ValueError("malformed number")
            tokens.append(('num', val))
            i = j
            continue
        raise ValueError("invalid character")

    # Parser: recursive descent
    pos = 0

    def peek():
        nonlocal pos
        if pos < len(tokens):
            return tokens[pos]
        return None

    def advance():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        return tok

    def parse_expression():
        # expression -> term (('+' | '-') term)*
        left = parse_term()
        while True:
            tok = peek()
            if tok and tok[0] == 'op' and tok[1] in ('+', '-'):
                advance()
                right = parse_term()
                if tok[1] == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    def parse_term():
        # term -> factor (('*' | '/' | '%') factor)*
        left = parse_factor()
        while True:
            tok = peek()
            if tok and tok[0] == 'op' and tok[1] in ('*', '/', '%'):
                advance()
                right = parse_factor()
                if tok[1] == '*':
                    left = left * right
                elif tok[1] == '/':
                    if right == 0:
                        raise ValueError("division by zero")
                    left = left / right
                else:
                    if right == 0:
                        raise ValueError("modulo by zero")
                    left = left % right
            else:
                break
        return left

    def parse_factor():
        # factor -> power
        return parse_power()

    def parse_power():
        # power -> unary ('^' power)*  (right-associative)
        left = parse_unary()
        tok = peek()
        if tok and tok[0] == 'op' and tok[1] == '^':
            advance()
            right = parse_power()
            return left ** right
        return left

    def parse_unary():
        # unary -> ('-' unary) | primary
        tok = peek()
        if tok and tok[0] == 'op' and tok[1] == '-':
            advance()
            val = parse_unary()
            return -val
        return parse_primary()

    def parse_primary():
        tok = peek()
        if tok is None:
            raise ValueError("unexpected end of input")
        if tok[0] == 'paren' and tok[1] == '(':
            advance()
            val = parse_expression()
            tok2 = peek()
            if not (tok2 and tok2[0] == 'paren' and tok2[1] == ')'):
                raise ValueError("unbalanced parentheses")
            advance()
            return val
        if tok[0] == 'num':
            advance()
            return tok[1]
        if tok[0] == 'var':
            advance()
            name = tok[1]
            if name not in variables:
                raise ValueError("unknown variable")
            return float(variables[name])
        if tok[0] == 'op' and tok[1] == '-':
            # handled by unary
            return parse_unary()
        raise ValueError("malformed syntax")

    if not tokens:
        raise ValueError("empty expression")

    result = parse_expression()
    if pos != len(tokens):
        raise ValueError("malformed syntax")
    return float(result)
