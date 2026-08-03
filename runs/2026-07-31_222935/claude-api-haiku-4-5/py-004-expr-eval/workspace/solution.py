def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression()
    
    if parser.pos < len(parser.tokens):
        raise ValueError("Unexpected tokens after expression")
    
    return float(result)


def tokenize(expr: str) -> list[tuple[str, str]]:
    """Tokenize the expression into (type, value) pairs."""
    tokens = []
    i = 0
    
    while i < len(expr):
        # Skip whitespace
        if expr[i].isspace():
            i += 1
            continue
        
        # Numbers (integers and decimals)
        if expr[i].isdigit():
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(('NUMBER', expr[i:j]))
            i = j
            continue
        
        # Variable names and keywords
        if expr[i].isalpha() or expr[i] == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VARIABLE', expr[i:j]))
            i = j
            continue
        
        # Operators and delimiters
        if expr[i] in '+-*/%^()':
            tokens.append(('OP', expr[i]))
            i += 1
            continue
        
        raise ValueError(f"Unknown character: {expr[i]}")
    
    return tokens


class Parser:
    def __init__(self, tokens: list[tuple[str, str]], variables: dict[str, float]):
        self.tokens = tokens
        self.variables = variables
        self.pos = 0
    
    def current_token(self) -> tuple[str, str] | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self, expected: str | None = None) -> tuple[str, str]:
        token = self.current_token()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected and token[1] != expected:
            raise ValueError(f"Expected '{expected}', got '{token[1]}'")
        self.pos += 1
        return token
    
    def parse_expression(self) -> float:
        """Parse unary minus (lowest precedence after assignment)."""
        if self.current_token() and self.current_token()[1] == '-':
            self.consume('-')
            return -self.parse_expression()
        elif self.current_token() and self.current_token()[1] == '+':
            self.consume('+')
            return self.parse_expression()
        
        return self.parse_additive()
    
    def parse_additive(self) -> float:
        """Parse + and - (left-associative)."""
        left = self.parse_multiplicative()
        
        while self.current_token() and self.current_token()[1] in ['+', '-']:
            op = self.consume()[1]
            right = self.parse_multiplicative()
            if op == '+':
                left = left + right
            else:
                left = left - right
        
        return left
    
    def parse_multiplicative(self) -> float:
        """Parse *, /, % (left-associative)."""
        left = self.parse_exponentiation()
        
        while self.current_token() and self.current_token()[1] in ['*', '/', '%']:
            op = self.consume()[1]
            right = self.parse_exponentiation()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # %
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        
        return left
    
    def parse_exponentiation(self) -> float:
        """Parse ^ (right-associative)."""
        left = self.parse_primary()
        
        if self.current_token() and self.current_token()[1] == '^':
            self.consume('^')
            right = self.parse_exponentiation()  # Right-associative recursion
            return left ** right
        
        return left
    
    def parse_primary(self) -> float:
        """Parse numbers, variables, and parenthesized expressions."""
        token = self.current_token()
        
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        # Number
        if token[0] == 'NUMBER':
            self.consume()
            return float(token[1])
        
        # Variable
        if token[0] == 'VARIABLE':
            name = token[1]
            self.consume()
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return self.variables[name]
        
        # Parenthesized expression
        if token[1] == '(':
            self.consume('(')
            result = self.parse_expression()
            self.consume(')')
            return result
        
        raise ValueError(f"Unexpected token: {token[1]}")
