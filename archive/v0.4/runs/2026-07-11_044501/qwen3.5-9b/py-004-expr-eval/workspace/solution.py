def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()


class Token:
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return f"Token({self.value!r})"


def tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)
    
    while i < n:
        c = expr[i]
        
        if c.isspace():
            i += 1
            continue
        
        if c in '+-*/%^()':
            tokens.append(Token(c))
            i += 1
            continue
        
        # Check for number (integer or decimal)
        if c.isdigit() or (c == '.' and i + 1 < n and expr[i+1].isdigit()):
            j = i
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                j += 1
            tokens.append(Token(expr[i:j]))
            i = j
            continue
        
        # Check for variable name
        if c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(Token(expr[i:j]))
            i = j
            continue
        
        raise ValueError(f"Invalid character: {c!r}")
    
    return tokens


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables
    
    def parse(self):
        result = self.expr()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.current()}")
        return result
    
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self, expected=None):
        token = self.current()
        if expected is not None and token.value != expected:
            raise ValueError(f"Expected {expected!r}, got {token.value!r}")
        self.pos += 1
        return token
    
    def expr(self):
        """expr -> term (('+' | '-') term)*"""
        left = self.term()
        while self.current() and self.current().value in ('+', '-'):
            op = self.consume()
            right = self.term()
            if op.value == '+':
                left = left + right
            else:
                left = left - right
        return left
    
    def term(self):
        """term -> factor (('*' | '/' | '%') factor)*"""
        left = self.factor()
        while self.current() and self.current().value in ('*', '/', '%'):
            op = self.consume()
            right = self.factor()
            if op.value == '*':
                left = left * right
            elif op.value == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # '%'
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left
    
    def factor(self):
        """factor -> ('^' factor) | unary_expr"""
        if self.current() and self.current().value == '^':
            # Right-associative exponentiation: a ^ b ^ c = a ^ (b ^ c)
            base = self.factor()
            exp = self.factor()
            return base ** exp
        
        # Unary minus/plus or primary
        if self.current() and self.current().value in ('+', '-'):
            op = self.consume()
            value = self.unary_expr()
            if op.value == '+':
                return value
            else:
                return -value
        
        return self.primary()
    
    def unary_expr(self):
        """unary_expr -> primary | ('-' | '+') unary_expr"""
        # Unary minus/plus handled in factor for proper precedence
        # This is just a fallback for cases where we need to handle it here
        if self.current() and self.current().value == '-':
            self.consume()
            return -self.unary_expr()
        elif self.current() and self.current().value == '+':
            self.consume()
            return self.unary_expr()
        else:
            return self.primary()
    
    def primary(self):
        """primary -> NUMBER | VARIABLE | '(' expr ')'"""
        token = self.consume()
        
        if token.value == '(':
            result = self.expr()
            self.consume(')')
            return result
        
        try:
            return float(token.value)
        except ValueError:
            if token.value in self.variables:
                val = self.variables[token.value]
                if not isinstance(val, (int, float)):
                    raise ValueError(f"Variable {token.value!r} must have numeric value")
                return float(val)
            else:
                raise ValueError(f"Unknown variable: {token.value!r}")
