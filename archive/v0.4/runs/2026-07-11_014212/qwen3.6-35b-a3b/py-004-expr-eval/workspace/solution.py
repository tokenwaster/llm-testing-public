class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.current_token = None
        self.advance()

    def advance(self):
        self.current_token = self.get_next_token()

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                continue
            if self.current_char.isdigit():
                start = self.pos
                while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
                    self.pos += 1
                    self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                try:
                    val = float(self.text[start:self.pos])
                except ValueError:
                    raise ValueError(f"Invalid number: {self.text[start:self.pos]}")
                return Token('NUMBER', val)
            if self.current_char.isalpha() or self.current_char == '_':
                start = self.pos
                while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
                    self.pos += 1
                    self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('NAME', self.text[start:self.pos])
            if self.current_char == '+':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('PLUS', '+')
            if self.current_char == '-':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('MINUS', '-')
            if self.current_char == '*':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('STAR', '*')
            if self.current_char == '/':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('SLASH', '/')
            if self.current_char == '%':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('PERCENT', '%')
            if self.current_char == '^':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('CIRCUMFLEX', '^')
            if self.current_char == '(':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('LPAREN', '(')
            if self.current_char == ')':
                self.pos += 1
                self.current_char = self.text[self.pos] if self.pos < len(self.text) else None
                return Token('RPAREN', ')')
            raise ValueError(f"Unexpected character: {self.current_char}")
        return Token('EOF', None)

class Parser:
    def __init__(self, lexer, variables):
        self.lexer = lexer
        self.variables = variables or {}
        self.current_token = self.lexer.current_token

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ValueError(f"Expected {token_type}, got {self.current_token.type}")

    def parse_expr(self):
        result = self.parse_term()
        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.type
            self.eat(op)
            right = self.parse_term()
            if op == 'PLUS':
                result += right
            else:
                result -= right
        return result

    def parse_term(self):
        result = self.parse_power()
        while self.current_token.type in ('STAR', 'SLASH', 'PERCENT'):
            op = self.current_token.type
            self.eat(op)
            right = self.parse_power()
            if op == 'STAR':
                result *= right
            elif op == 'SLASH':
                if right == 0:
                    raise ValueError("Division by zero")
                result /= right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                result %= right
        return result

    def parse_power(self):
        base = self.parse_unary()
        if self.current_token.type == 'CIRCUMFLEX':
            self.eat('CIRCUMFLEX')
            exponent = self.parse_power()
            return base ** exponent
        return base

    def parse_unary(self):
        if self.current_token.type == 'MINUS':
            self.eat('MINUS')
            return -self.parse_unary()
        if self.current_token.type == 'PLUS':
            self.eat('PLUS')
            return self.parse_unary()
        return self.parse_primary()

    def parse_primary(self):
        token = self.current_token
        if token.type == 'NUMBER':
            self.eat('NUMBER')
            return float(token.value)
        if token.type == 'NAME':
            self.eat('NAME')
            if token.value not in self.variables:
                raise ValueError(f"Unknown variable: {token.value}")
            return float(self.variables[token.value])
        if token.type == 'LPAREN':
            self.eat('LPAREN')
            result = self.parse_expr()
            self.eat('RPAREN')
            return result
        raise ValueError(f"Unexpected token: {token.type}")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    lexer = Lexer(expr)
    parser = Parser(lexer, variables)
    result = parser.parse_expr()
    if parser.current_token.type != 'EOF':
        raise ValueError("Unexpected token after expression")
    return result
