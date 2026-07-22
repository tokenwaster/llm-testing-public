def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()


def tokenize(expr: str):
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        
        if c.isspace():
            i += 1
            continue
        
        if c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1
            continue
        
        if c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
            continue
        
        if c.isdigit():
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            num_str = expr[i:j]
            
            if num_str.count('.') > 1:
                raise ValueError(f"Invalid number format: {num_str}")
            
            tokens.append(('NUM', float(num_str)))
            i = j
            continue
        
        raise ValueError(f"Invalid character: {c}")
    
    return tokens


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables
    
    def parse(self):
        if not self.tokens:
            raise ValueError("Empty expression")
        
        result = self.parse_expression()
        
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.pos]}")
        
        return result
    
    def current_token(self):
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]
    
    def consume(self):
        token = self.current_token()
        self.pos += 1
        return token
    
    def parse_expression(self):
        left = self.parse_term()
        
        while True:
            token = self.current_token()
            if token is None or token[0] != 'OP' or token[1] not in '+-':
                break
            
            op = token[1]
            self.consume()
            right = self.parse_term()
            
            if op == '+':
                left = left + right
            else:  # '-'
                left = left - right
        
        return left
    
    def parse_term(self):
        left = self.parse_factor()
        
        while True:
            token = self.current_token()
            if token is None or token[0] != 'OP' or token[1] not in '*/%':
                break
            
            op = token[1]
            self.consume()
            right = self.parse_factor()
            
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
    
    def parse_factor(self):
        token = self.current_token()
        
        # Check for unary minus
        if token and token[0] == 'OP' and token[1] == '-':
            self.consume()
            value = -self.parse_factor()
            return value
        
        # Get the primary expression (left side of potential ^)
        left = self.parse_primary()
        
        # Check for exponentiation (right-associative)
        if self.current_token() and self.current_token()[0] == 'OP' and self.current_token()[1] == '^':
            self.consume()
            right = self.parse_factor()  # Right-associative: parse recursively
            return left ** right
        
        return left
    
    def parse_primary(self):
        token = self.current_token()
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token[0] == 'NUM':
            self.consume()
            return token[1]
        
        elif token[0] == 'VAR':
            var_name = token[1]
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            value = self.variables[var_name]
            self.consume()
            return value
        
        elif token and token[0] == 'OP' and token[1] == '(':
            self.consume()  # consume '('
            result = self.parse_expression()
            
            if self.current_token() is None or self.current_token()[0] != 'OP' or self.current_token()[1] != ')':
                raise ValueError("Missing closing parenthesis")
            
            self.consume()  # consume ')'
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token}")
