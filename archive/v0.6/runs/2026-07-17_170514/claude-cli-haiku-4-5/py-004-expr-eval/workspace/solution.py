def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_additive()
    
    if parser.pos < len(tokens):
        raise ValueError("Unexpected tokens after expression")
    
    return float(result)


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables
        self.pos = 0
    
    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self):
        token = self.current_token()
        self.pos += 1
        return token
    
    def parse_additive(self):
        left = self.parse_multiplicative()
        
        while self.current_token() in ['+', '-']:
            op = self.consume()
            right = self.parse_multiplicative()
            if op == '+':
                left = left + right
            else:
                left = left - right
        
        return left
    
    def parse_multiplicative(self):
        left = self.parse_exponentiation()
        
        while self.current_token() in ['*', '/', '%']:
            op = self.consume()
            right = self.parse_exponentiation()
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
    
    def parse_exponentiation(self):
        base = self.parse_unary()
        
        if self.current_token() == '^':
            self.consume()
            exponent = self.parse_exponentiation()
            return base ** exponent
        
        return base
    
    def parse_unary(self):
        if self.current_token() in ['-', '+']:
            op = self.consume()
            operand = self.parse_unary()
            if op == '-':
                return -operand
            else:
                return operand
        
        return self.parse_primary()
    
    def parse_primary(self):
        token = self.current_token()
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        elif token == '(':
            self.consume()
            result = self.parse_additive()
            if self.current_token() != ')':
                raise ValueError("Unbalanced parentheses")
            self.consume()
            return result
        elif isinstance(token, float):
            self.consume()
            return token
        elif isinstance(token, str):
            self.consume()
            if token not in self.variables:
                raise ValueError(f"Unknown variable: {token}")
            return float(self.variables[token])
        else:
            raise ValueError("Unexpected token")


def tokenize(expr: str):
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
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
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
            raise ValueError(f"Invalid character: {expr[i]}")
    return tokens
