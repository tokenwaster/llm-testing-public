class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        else:
            return None

    def advance(self):
        token = self.peek()
        if token is not None:
            self.pos += 1
        return token

    def parse_expr(self):
        return self.parse_additive()

    def parse_additive(self):
        left = self.parse_multiplicative()
        while True:
            token = self.peek()
            if token is None:
                break
            t_type, _ = token
            if t_type in ('+', '-'):
                op = t_type
                self.advance()
                right = self.parse_multiplicative()
                if op == '+':
                    left += right
                else:
                    left -= right
            else:
                break
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while True:
            token = self.peek()
            if token is None:
                break
            t_type, _ = token
            if t_type in ('*', '/', '%'):
                op = t_type
                self.advance()
                right_val = self.parse_unary()
                if right_val == 0 and (op == '/' or op == '%'):
                    raise ValueError("Division or modulo by zero")
                if op == '*':
                    left *= right_val
                elif op == '/':
                    left /= right_val
                elif op == '%':
                    left %= right_val
            else:
                break
        return left

    def parse_unary(self):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of input")
        t_type, _ = token
        if t_type == '-':
            self.advance()
            operand = self.parse_unary()
            return -operand
        else:
            return self.parse_power()

    def parse_power(self):
        left = self.parse_primary()
        while True:
            token = self.peek()
            if token is None:
                break
            t_type, _ = token
            if t_type == '^':
                self.advance()
                right = self.parse_power()
                left = pow(left, right)
            else:
                break
        return left

    def parse_primary(self):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of input")
        t_type, value = token
        if t_type == 'number':
            self.advance()
            return value
        elif t_type == 'variable':
            var_name = value
            self.advance()
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return self.variables[var_name]
        elif t_type == '(':
            self.advance()
            result = self.parse_expr()
            if self.peek() is None:
                raise ValueError("Unbalanced parentheses")
            next_token = self.peek()
            if next_token[0] != ')':
                raise ValueError(f"Expected ')', got {next_token[0]}")
            self.advance()
            return result
        else:
            raise ValueError(f"Unexpected token in primary: {t_type}")


def tokenize(s: str) -> list:
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or c == '.':
            start = i
            decimal_count = 0
            while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                if s[i] == '.':
                    decimal_count += 1
                    if decimal_count > 1:
                        raise ValueError("Invalid number format")
                i += 1
            num_str = s[start:i]
            try:
                tokens.append(('number', float(num_str)))
            except ValueError:
                raise ValueError(f"Invalid number: {num_str}")
        elif c.isalpha() or c == '_':
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                i += 1
            var_name = s[start:i]
            tokens.append(('variable', var_name))
        else:
            if c in '+-*/%()^':
                tokens.append((c, None))
                i += 1
            else:
                raise ValueError(f"Invalid character: {c}")
    return tokens


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    try:
        tokens = tokenize(expr)
    except Exception as e:
        raise ValueError(str(e))
    parser = Parser(tokens, variables)
    try:
        result = parser.parse_expr()
        # Ensure all tokens are consumed
        if parser.pos < len(parser.tokens):
            raise ValueError("Unexpected token at end")
        return float(result)
    except Exception as e:
        # Re-raise exceptions with context or original error
        if isinstance(e, ValueError):
            raise e
        else:
            raise ValueError(f"Evaluation error: {e}")
