def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    lexer = Lexer(expr)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens, variables)
    result = parser.parse_expr()
    
    if parser.pos < len(parser.tokens):
        raise ValueError("Unexpected token after expression")
    
    return result


class Lexer:
    def __init__(self, expr: str):
        self.expr = expr
        self.pos = 0
    
    def tokenize(self) -> list[tuple[str, str]]:
        tokens = []
        while self.pos < len(self.expr):
            if self.expr[self.pos].isspace():
                self.pos += 1
            elif self.expr[self.pos] in '+-*/%^()':
                tokens.append(('OP', self.expr[self.pos]))
                self.pos += 1
            elif self.expr[self.pos].isdigit():
                start = self.pos
                has_dot = False
                while self.pos < len(self.expr) and (self.expr[self.pos].isdigit() or (self.expr[self.pos] == '.' and not has_dot)):
                    if self.expr[self.pos] == '.':
                        has_dot = True
                    self.pos += 1
                tokens.append(('NUM', self.expr[start:self.pos]))
            elif self.expr[self.pos] == '.' and self.pos + 1 < len(self.expr) and self.expr[self.pos + 1].isdigit():
                start = self.pos
                self.pos += 1
                while self.pos < len(self.expr) and self.expr[self.pos].isdigit():
                    self.pos += 1
                tokens.append(('NUM', self.expr[start:self.pos]))
            elif self.expr[self.pos].isalpha() or self.expr[self.pos] == '_':
                start = self.pos
                while self.pos < len(self.expr) and (self.expr[self.pos].isalnum() or self.expr[self.pos] == '_'):
                    self.pos += 1
                tokens.append(('VAR', self.expr[start:self.pos]))
            else:
                raise ValueError(f"Unknown character: {self.expr[self.pos]}")
        return tokens


class Parser:
    def __init__(self, tokens: list[tuple[str, str]], variables: dict[str, float]):
        self.tokens = tokens
        self.variables = variables
        self.pos = 0
    
    def peek(self) -> tuple[str, str] | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self, expected_type: str | None = None, expected_value: str | None = None) -> tuple[str, str]:
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected_type and token[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token[0]}")
        if expected_value and token[1] != expected_value:
            raise ValueError(f"Expected '{expected_value}', got '{token[1]}'")
        self.pos += 1
        return token
    
    def parse_expr(self) -> float:
        return self.parse_unary()
    
    def parse_unary(self) -> float:
        if self.peek() and self.peek()[0] == 'OP' and self.peek()[1] == '-':
            self.consume('OP', '-')
            return -self.parse_unary()
        return self.parse_additive()
    
    def parse_additive(self) -> float:
        result = self.parse_multiplicative()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ['+', '-']:
            op = self.consume()[1]
            right = self.parse_multiplicative()
            if op == '+':
                result += right
            else:
                result -= right
        return result
    
    def parse_multiplicative(self) -> float:
        result = self.parse_power()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ['*', '/', '%']:
            op = self.consume()[1]
            right = self.parse_power()
            if op == '*':
                result *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                result %= right
        return result
    
    def parse_power(self) -> float:
        result = self.parse_primary()
        if self.peek() and self.peek()[0] == 'OP' and self.peek()[1] == '^':
            self.consume('OP', '^')
            right = self.parse_power()
            result = result ** right
        return result
    
    def parse_primary(self) -> float:
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token[0] == 'NUM':
            self.consume()
            return float(token[1])
        elif token[0] == 'VAR':
            self.consume()
            if token[1] not in self.variables:
                raise ValueError(f"Unknown variable: {token[1]}")
            return self.variables[token[1]]
        elif token[0] == 'OP' and token[1] == '(':
            self.consume('OP', '(')
            result = self.parse_expr()
            self.consume('OP', ')')
            return result
        else:
            raise ValueError(f"Unexpected token: {token}")
