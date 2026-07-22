def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression()
    
    if parser.pos < len(tokens):
        raise ValueError("Unexpected tokens after expression")
    
    return result


def tokenize(expr: str):
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i] in '()':
            tokens.append(expr[i])
            i += 1
        elif expr[i] in '+-*/%^':
            tokens.append(expr[i])
            i += 1
        elif expr[i].isdigit() or expr[i] == '.':
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(expr[i:j])
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
    
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self):
        token = self.peek()
        self.pos += 1
        return token
    
    def parse_expression(self):
        return self.parse_addition()
    
    def parse_addition(self):
        left = self.parse_multiplication()
        
        while self.peek() in ['+', '-']:
            op = self.consume()
            right = self.parse_multiplication()
            if op == '+':
                left = left + right
            else:
                left = left - right
        
        return left
    
    def parse_multiplication(self):
        left = self.parse_unary()
        
        while self.peek() in ['*', '/', '%']:
            op = self.consume()
            right = self.parse_unary()
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
    
    def parse_unary(self):
        if self.peek() == '-':
            self.consume()
            operand = self.parse_unary()
            return -operand
        
        return self.parse_exponentiation()
    
    def parse_exponentiation(self):
        base = self.parse_primary()
        
        if self.peek() == '^':
            self.consume()
            exponent = self.parse_exponentiation()
            return base ** exponent
        
        return base
    
    def parse_primary(self):
        token = self.peek()
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token == '(':
            self.consume()
            result = self.parse_expression()
            if self.peek() != ')':
                raise ValueError("Expected ')'")
            self.consume()
            return result
        
        if token[0].isdigit() or (token[0] == '.' and len(token) > 1):
            self.consume()
            return float(token)
        
        if token[0].isalpha() or token[0] == '_':
            self.consume()
            if token not in self.variables:
                raise ValueError(f"Unknown variable: {token}")
            return self.variables[token]
        
        raise ValueError(f"Unexpected token: {token}")
