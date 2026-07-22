class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.tokens = []
        self._tokenize()

    def _tokenize(self):
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch.isspace():
                self.pos += 1
                continue
            if ch.isdigit() or ch == '.':
                self._read_number()
            elif ch.isalpha() or ch == '_':
                self._read_variable()
            elif ch in '+-*/%^()':
                self.tokens.append(Token(ch, ch))
                self.pos += 1
            else:
                raise ValueError(f"Invalid character: {ch}")
        self.tokens.append(Token('EOF', None))

    def _read_number(self):
        start = self.pos
        has_dot = False
        while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
            if self.text[self.pos] == '.':
                if has_dot:
                    raise ValueError("Invalid number format")
                has_dot = True
            self.pos += 1
        num_str = self.text[start:self.pos]
        if not num_str.replace('.', '').isdigit():
            raise ValueError("Invalid number format")
        self.tokens.append(Token('NUMBER', float(num_str)))

    def _read_variable(self):
        start = self.pos
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            self.pos += 1
        name = self.text[start:self.pos]
        self.tokens.append(Token('VAR', name))

class Parser:
    def __init__(self, tokenizer, variables):
        self.tokens = tokenizer.tokens
        self.pos = 0
        self.variables = variables or {}

    def current_token(self):
        return self.tokens[self.pos]

    def eat(self, token_type):
        if self.current_token().type == token_type:
            token = self.current_token()
            self.pos += 1
            return token
        raise ValueError(f"Expected {token_type}, got {self.current_token().type}")

    def parse(self):
        result = self.parse_expression()
        if self.current_token().type != 'EOF':
            raise ValueError("Unexpected token after expression")
        return result

    def parse_expression(self):
        left = self.parse_term()
        while self.current_token().type in ('+', '-'):
            op = self.current_token().type
            self.pos += 1
            right = self.parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def parse_term(self):
        left = self.parse_power()
        while self.current_token().type in ('*', '/', '%'):
            op = self.current_token().type
            self.pos += 1
            right = self.parse_power()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_power(self):
        base = self.parse_unary()
        if self.current_token().type == '^':
            self.pos += 1
            exp = self.parse_power()
            return base ** exp
        return base

    def parse_unary(self):
        if self.current_token().type == '-':
            self.pos += 1
            return -self.parse_power()
        return self.parse_primary()

    def parse_primary(self):
        token = self.current_token()
        if token.type == 'NUMBER':
            self.pos += 1
            return token.value
        elif token.type == 'VAR':
            self.pos += 1
            if token.value not in self.variables:
                raise ValueError(f"Unknown variable: {token.value}")
            return float(self.variables[token.value])
        elif token.type == '(':
            self.pos += 1
            result = self.parse_expression()
            self.eat(')')
            return result
        else:
            raise ValueError(f"Unexpected token: {token.type}")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokenizer = Tokenizer(expr)
    parser = Parser(tokenizer, variables)
    return parser.parse()
