class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

def tokenize(expr: str) -> list:
    tokens = []
    i = 0
    while i < len(expr):
        if expr[i].isspace():
            i += 1
        elif expr[i] in '+-*/%^()':
            tokens.append(Token('OPERATOR', expr[i]))
            i += 1
        elif expr[i].isdigit():
            j = i
            has_dot = False
            while j < len(expr) and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(Token('NUMBER', float(expr[i:j])))
            i = j
        elif expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(Token('VARIABLE', expr[i:j]))
            i = j
        else:
            raise ValueError(f"Unexpected character: {expr[i]}")
    return tokens

class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables
        self.pos = 0
    
    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def advance(self):
        self.pos += 1
    
    def parse_expr(self):
        left = self.parse_unary_expr()
        while self.peek() and self.peek().type == 'OPERATOR' and self.peek().value in ('+', '-'):
            op = self.peek().value
            self.advance()
            right = self.parse_unary_expr()
            left = left + right if op == '+' else left - right
        return left
    
    def parse_unary_expr(self):
        if self.peek() and self.peek().type == 'OPERATOR' and self.peek().value == '-':
            self.advance()
            return -self.parse_unary_expr()
        return self.parse_multiplicative_expr()
    
    def parse_multiplicative_expr(self):
        left = self.parse_exponentiation_expr()
        while self.peek() and self.peek().type == 'OPERATOR' and self.peek().value in ('*', '/', '%'):
            op = self.peek().value
            self.advance()
            right = self.parse_exponentiation_expr()
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
    
    def parse_exponentiation_expr(self):
        left = self.parse_atom()
        if self.peek() and self.peek().type == 'OPERATOR' and self.peek().value == '^':
            self.advance()
            right = self.parse_exponentiation_expr()
            return left ** right
        return left
    
    def parse_atom(self):
        if self.peek() and self.peek().type == 'OPERATOR' and self.peek().value == '(':
            self.advance()
            result = self.parse_expr()
            if not (self.peek() and self.peek().type == 'OPERATOR' and self.peek().value == ')'):
                raise ValueError("Unbalanced parentheses")
            self.advance()
            return result
        
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token.type == 'NUMBER':
            self.advance()
            return token.value
        elif token.type == 'VARIABLE':
            self.advance()
            if token.value not in self.variables:
                raise ValueError(f"Unknown variable: {token.value}")
            return self.variables[token.value]
        else:
            raise ValueError(f"Unexpected token: {token}")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expr()
    
    if parser.pos != len(tokens):
        raise ValueError("Unexpected tokens after expression")
    
    return float(result)
