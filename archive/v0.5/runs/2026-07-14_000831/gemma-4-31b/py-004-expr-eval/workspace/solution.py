import re

def tokenize(expr):
    """Tokenizes the input expression into numbers, variables, operators and parentheses."""
    token_specification = [
        ('NUMBER',   r'\d+(\.\d+)?'), 
        ('VAR',      r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('OP',       r'[\+\-\*\/\%\^\(\)]'),
        ('SKIP',     r'\s+'),
        ('MISMATCH', r'.'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    for mo in re.finditer(tok_regex, expr):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            yield ('NUMBER', float(value))
        elif kind == 'VAR':
            yield ('VAR', value)
        elif kind == 'OP':
            yield ('OP', value)
        elif kind == 'SKIP':
            continue
        else:
            raise ValueError(f"Unexpected character: {value}")

class Parser:
    """Recursive descent parser for arithmetic expressions."""
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected=None):
        tok = self.current_token()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        if expected and tok[1] != expected:
            raise ValueError(f"Expected {expected}, got {tok[1]}")
        self.pos += 1
        return tok

    def parse_expr(self):
        """expr -> term { (+|-) term } (Left-associative)"""
        node = self.parse_term()
        while self.current_token() and self.current_token()[1] in ('+', '-'):
            op = self.eat()[1]
            right = self.parse_term()
            if op == '+': 
                node += right
            else: 
                node -= right
        return node

    def parse_term(self):
        """term -> unary { (*|/|%) unary } (Left-associative)"""
        node = self.parse_unary()
        while self.current_token() and self.current_token()[1] in ('*', '/', '%'):
            op = self.eat()[1]
            right = self.parse_unary()
            if op == '*': 
                node *= right
            elif op == '/':
                if right == 0: 
                    raise ValueError("Division by zero")
                node /= right
            elif op == '%':
                if right == 0: 
                    raise ValueError("Modulo by zero")
                node %= right
        return node

    def parse_unary(self):
        """unary -> - unary | power (Right-associative, binds looser than ^)"""
        if self.current_token() and self.current_token()[1] == '-':
            self.eat()
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        """power -> atom [ ^ power ] (Right-associative)"""
        node = self.parse_atom()
        if self.current_token() and self.current_token()[1] == '^':
            self.eat()
            right = self.parse_power() 
            node = node ** right
        return node

    def parse_atom(self):
        """atom -> number | variable | ( expr )"""
        tok = self.current_token()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        
        if tok[0] == 'NUMBER':
            return self.eat()[1]
        elif tok[0] == 'VAR':
            var_name = self.eat()[1]
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(self.variables[var_name])
        elif tok[1] == '(':
            self.eat('(')
            node = self.parse_expr()
            self.eat(')')
            return node
        else:
            raise ValueError(f"Unexpected token: {tok[1]}")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluates an arithmetic expression based on the specified grammar."""
    try:
        tokens = list(tokenize(expr))
    except ValueError as e:
        raise ValueError(str(e))

    parser = Parser(tokens, variables)
    result = parser.parse_expr()
    
    if parser.pos < len(tokens):
        raise ValueError("Unexpected tokens at end of expression")
        
    return float(result)
