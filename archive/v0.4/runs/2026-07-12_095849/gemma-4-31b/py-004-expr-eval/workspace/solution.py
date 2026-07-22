import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with support for basic operators, 
    unary minus, parentheses, and variable resolution.
    """
    
    def tokenize(text):
        # Token specifications: Number, Variable, Operator/Parenthesis, Whitespace, Mismatch
        token_specification = [
            ('NUMBER',   r'\d+(\.\d*)?'), 
            ('VAR',      r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OP',       r'[\+\-\*\/\%\^\(\)]'),
            ('SKIP',     r'\s+'),
            ('MISMATCH', r'.'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        for mo in re.finditer(tok_regex, text):
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
        def __init__(self, tokens, variables):
            self.tokens = list(tokens)
            self.pos = 0
            self.variables = variables if variables is not None else {}

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def consume(self):
            token = self.peek()
            if token is None:
                raise ValueError("Unexpected end of expression")
            self.pos += 1
            return token

        def parse_expression(self):
            # Level 1: Addition and Subtraction (Left-associative)
            node = self.parse_term()
            while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('+', '-'):
                op = self.consume()[1]
                right = self.parse_term()
                if op == '+': 
                    node += right
                else: 
                    node -= right
            return node

        def parse_term(self):
            # Level 2: Multiplication, Division, Modulo (Left-associative)
            node = self.parse_unary()
            while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('*', '/', '%'):
                op = self.consume()[1]
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
            # Level 3: Unary Minus (Right-associative/Prefix)
            if self.peek() and self.peek()[0] == 'OP' and self.peek()[1] == '-':
                self.consume()
                return -self.parse_unary()
            return self.parse_power()

        def parse_power(self):
            # Level 4: Exponentiation (Right-associative)
            node = self.parse_atom()
            if self.peek() and self.peek()[0] == 'OP' and self.peek()[1] == '^':
                self.consume()
                # Right associativity is achieved by calling parse_unary for the exponent
                node = node ** self.parse_unary()
            return node

        def parse_atom(self):
            # Level 5: Numbers, Variables, Parentheses
            token = self.consume()
            if token[0] == 'NUMBER':
                return token[1]
            elif token[0] == 'VAR':
                var_name = token[1]
                if var_name not in self.variables:
                    raise ValueError(f"Unknown variable: {var_name}")
                return float(self.variables[var_name])
            elif token[0] == 'OP' and token[1] == '(':
                node = self.parse_expression()
                token = self.consume()
                if token[0] != 'OP' or token[1] != ')':
                    raise ValueError("Unbalanced parentheses")
                return node
            else:
                raise ValueError(f"Unexpected token: {token[1]}")

    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    try:
        result = parser.parse_expression()
    except IndexError:
        raise ValueError("Malformed expression")
        
    if parser.pos < len(parser.tokens):
        raise ValueError("Unexpected tokens at end of expression")
    
    return float(result)
