def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression()
    
    if parser.pos < len(parser.tokens):
        raise ValueError("Unexpected tokens after expression")
    
    return result


def tokenize(expr: str) -> list:
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i] in '+-*/%^()':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            if j < len(expr) and expr[j] == '.':
                j += 1
                while j < len(expr) and expr[j].isdigit():
                    j += 1
            tokens.append(float(expr[i:j]))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            raise ValueError(f"Unknown character: {expr[i]}")
    return tokens


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables
        self.pos = 0
    
    def parse_expression(self):
        result = self.parse_term()
        while self.pos < len(self.tokens) and self.tokens[self.pos] in ['+', '-']:
            op = self.tokens[self.pos]
            self.pos += 1
            right = self.parse_term()
            if op == '+':
                result = result + right
            else:
                result = result - right
        return result
    
    def parse_term(self):
        result = self.parse_factor()
        while self.pos < len(self.tokens) and self.tokens[self.pos] in ['*', '/', '%']:
            op = self.tokens[self.pos]
            self.pos += 1
            right = self.parse_factor()
            if op == '*':
                result = result * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                result = result / right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                result = result % right
        return result
    
    def parse_factor(self):
        return self.parse_unary()
    
    def parse_unary(self):
        if self.pos < len(self.tokens) and self.tokens[self.pos] == '-':
            self.pos += 1
            return -self.parse_unary()
        return self.parse_power()
    
    def parse_power(self):
        base = self.parse_primary()
        if self.pos < len(self.tokens) and self.tokens[self.pos] == '^':
            self.pos += 1
            exp = self.parse_power()
            return base ** exp
        return base
    
    def parse_primary(self):
        if self.pos >= len(self.tokens):
            raise ValueError("Unexpected end of expression")
        
        token = self.tokens[self.pos]
        
        if isinstance(token, float):
            self.pos += 1
            return token
        elif isinstance(token, str):
            if token == '(':
                self.pos += 1
                result = self.parse_expression()
                if self.pos >= len(self.tokens) or self.tokens[self.pos] != ')':
                    raise ValueError("Unbalanced parentheses")
                self.pos += 1
                return result
            elif token[0].isalpha() or token[0] == '_':
                self.pos += 1
                if token not in self.variables:
                    raise ValueError(f"Unknown variable: {token}")
                return self.variables[token]
            else:
                raise ValueError(f"Unexpected token: {token}")
        else:
            raise ValueError(f"Unexpected token: {token}")
