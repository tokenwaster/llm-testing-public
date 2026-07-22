def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        # Number: integer or decimal (leading dot allowed for completeness)
        if c.isdigit() or (c == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            if c == '.':
                has_dot = True
                i += 1
            while i < n and expr[i].isdigit():
                i += 1
            if i < n and expr[i] == '.' and not has_dot:
                has_dot = True
                i += 1
                while i < n and expr[i].isdigit():
                    i += 1
            num_str = expr[start:i]
            try:
                value = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number: {num_str}")
            tokens.append(('NUMBER', value))
            continue
        # Identifier / variable
        if c.isalpha() or c == '_':
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            ident = expr[start:i]
            tokens.append(('IDENT', ident))
            continue
        # Single-character tokens
        if c == '+':
            tokens.append(('PLUS', None))
        elif c == '-':
            tokens.append(('MINUS', None))
        elif c == '*':
            tokens.append(('MUL', None))
        elif c == '/':
            tokens.append(('DIV', None))
        elif c == '%':
            tokens.append(('MOD', None))
        elif c == '^':
            tokens.append(('POW', None))
        elif c == '(':
            tokens.append(('LPAREN', None))
        elif c == ')':
            tokens.append(('RPAREN', None))
        else:
            raise ValueError(f"Invalid character: {c}")
        i += 1
    tokens.append(('EOF', None))
    return tokens


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}

    @property
    def current_token(self):
        return self.tokens[self.pos]

    def consume(self, expected_type):
        if self.current_token[0] == expected_type:
            self.pos += 1
        else:
            raise ValueError(f"Expected {expected_type}, got {self.current_token[0]}")

    def parse_expression(self):
        left = self.parse_term()
        while self.current_token[0] in ('PLUS', 'MINUS'):
            op = self.current_token[0]
            self.consume(op)
            right = self.parse_term()
            if op == 'PLUS':
                left = left + right
            else:
                left = left - right
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.current_token[0] in ('MUL', 'DIV', 'MOD'):
            op = self.current_token[0]
            self.consume(op)
            right = self.parse_factor()
            if op == 'MUL':
                left = left * right
            elif op == 'DIV':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # MOD
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_factor(self):
        if self.current_token[0] == 'MINUS':
            self.consume('MINUS')
            operand = self.parse_factor()
            return -operand
        return self.parse_power()

    def parse_power(self):
        left = self.parse_primary()
        if self.current_token[0] == 'POW':
            self.consume('POW')
            right = self.parse_factor()   # right-associative: factor includes power
            try:
                return left ** right
            except ZeroDivisionError:
                raise ValueError("Division by zero")
        return left

    def parse_primary(self):
        token_type, value = self.current_token
        if token_type == 'NUMBER':
            self.consume('NUMBER')
            return value
        elif token_type == 'IDENT':
            self.consume('IDENT')
            if value not in self.variables:
                raise ValueError(f"Unknown variable: {value}")
            return float(self.variables[value])
        elif token_type == 'LPAREN':
            self.consume('LPAREN')
            expr_val = self.parse_expression()
            if self.current_token[0] != 'RPAREN':
                raise ValueError("Unbalanced parentheses")
            self.consume('RPAREN')
            return expr_val
        else:
            raise ValueError(f"Unexpected token: {token_type}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression()
    if parser.current_token[0] != 'EOF':
        raise ValueError("Malformed syntax: extra tokens")
    return float(result)
