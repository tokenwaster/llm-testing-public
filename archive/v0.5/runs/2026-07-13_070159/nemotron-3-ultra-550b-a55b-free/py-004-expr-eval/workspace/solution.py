def _tokenize(expr: str) -> list:
    """Convert the expression string into a list of tokens."""
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or c == '.':
            start = i
            if c == '.':
                i += 1
                while i < n and expr[i].isdigit():
                    i += 1
            else:
                while i < n and expr[i].isdigit():
                    i += 1
                if i < n and expr[i] == '.':
                    i += 1
                    while i < n and expr[i].isdigit():
                        i += 1
            num_str = expr[start:i]
            try:
                value = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number: {num_str}")
            tokens.append(value)
        elif c.isalpha() or c == '_':
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(expr[start:i])
        elif c in '+-*/%^()':
            tokens.append(c)
            i += 1
        else:
            raise ValueError(f"Invalid character: {c}")
    return tokens


class _Parser:
    def __init__(self, tokens: list, variables: dict[str, float]):
        self.tokens = tokens
        self.variables = variables
        self.pos = 0
        self.current = tokens[0] if tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None

    def parse(self) -> float:
        if self.current is None:
            raise ValueError("Empty expression")
        result = self.parse_expression()
        if self.current is not None:
            raise ValueError(f"Unexpected token: {self.current}")
        return result

    def parse_expression(self) -> float:
        return self.parse_additive()

    def parse_additive(self) -> float:
        left = self.parse_multiplicative()
        while self.current in ('+', '-'):
            op = self.current
            self.advance()
            right = self.parse_multiplicative()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def parse_multiplicative(self) -> float:
        left = self.parse_unary()
        while self.current in ('*', '/', '%'):
            op = self.current
            self.advance()
            right = self.parse_unary()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # '%'
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_unary(self) -> float:
        sign = 1
        while self.current == '-':
            sign *= -1
            self.advance()
        value = self.parse_power()
        return sign * value

    def parse_power(self) -> float:
        left = self.parse_primary()
        if self.current == '^':
            self.advance()
            right = self.parse_unary()
            try:
                left = left ** right
            except ZeroDivisionError:
                raise ValueError("Division by zero")
        return left

    def parse_primary(self) -> float:
        token = self.current
        if token is None:
            raise ValueError("Unexpected end of expression")
        if isinstance(token, float):
            self.advance()
            return token
        if isinstance(token, str) and token not in ('+', '-', '*', '/', '%', '^', '(', ')'):
            self.advance()
            if token not in self.variables:
                raise ValueError(f"Unknown variable: {token}")
            return float(self.variables[token])
        if token == '(':
            self.advance()
            value = self.parse_expression()
            if self.current != ')':
                raise ValueError("Unbalanced parentheses")
            self.advance()
            return value
        raise ValueError(f"Unexpected token: {token}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression without using eval, exec, ast, or any parsing library."""
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables or {})
    return parser.parse()
