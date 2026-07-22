def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    tokens = _tokenize(expr)

    def parse_expr():
        return _parse_additive()

    def _parse_additive():
        left = _parse_multiplicative()
        while tokens and tokens[0] in ('+', '-'):
            op = tokens.pop(0)
            right = _parse_multiplicative()
            if op == '+':
                left += right
            else:
                left -= right
        return left

    def _parse_multiplicative():
        left = _parse_factor()
        while tokens and tokens[0] in ('*', '/', '%'):
            op = tokens.pop(0)
            right = _parse_factor()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("division by zero")
                left /= right
            else:
                if right == 0:
                    raise ValueError("modulo by zero")
                left %= right
        return left

    def _parse_factor():
        sign = 1
        while tokens and tokens[0] in ('-', '+'):
            op = tokens.pop(0)
            if op == '-':
                sign *= -1
        return sign * _parse_power()

    def _parse_power():
        left = _parse_primary()
        if tokens and tokens[0] == '^':
            tokens.pop(0)
            right = _parse_factor()
            return left ** right
        else:
            return left

    def _parse_primary():
        if not tokens:
            raise ValueError("unexpected end of expression")
        token = tokens.pop(0)
        if token == '(':
            val = parse_expr()
            if not tokens or tokens[0] != ')':
                raise ValueError("unbalanced parentheses")
            tokens.pop(0)
            return val
        elif _is_number(token):
            try:
                return float(token)
            except ValueError:
                raise ValueError(f"invalid number: {token}")
        elif _is_variable_name(token):
            if token in variables:
                return variables[token]
            else:
                raise ValueError(f"unknown variable: {token}")
        else:
            raise ValueError(f"unexpected token: {token}")

    result = parse_expr()
    if tokens:
        raise ValueError("unexpected trailing tokens")
    return float(result)


def _tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i + 1].isdigit()):
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif c in '+-*/%^()':
            tokens.append(c)
            i += 1
        elif c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            raise ValueError(f"unexpected character: {c}")
    return tokens


def _is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def _is_variable_name(s):
    if not s:
        return False
    if not (s[0].isalpha() or s[0] == '_'):
        return False
    for c in s[1:]:
        if not (c.isalnum() or c == '_'):
            return False
    return True
