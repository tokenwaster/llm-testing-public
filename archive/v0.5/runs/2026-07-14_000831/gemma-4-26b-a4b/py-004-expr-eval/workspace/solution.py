import re

class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected=None):
        token = self.peek()
        if token is None:
            raise ValueError("Malformed syntax")
        if expected and token != expected:
            raise ValueError("Malformed syntax")
        self.pos += 1
        return token

    def parse_expression(self):
        # expression -> term { ('+' | '-') term }
        node = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            right = self.parse_term()
            if op == '+':
                node += right
            else:
                node -= right
        return node

    def parse_term(self):
        # term -> factor { ('*' | '/' | '%') factor }
        node = self.parse_factor()
        while self.parse_check_op(('*', '/', '%')):
            op = self.consume()
            right = self.parse_factor()
            if op == '*':
                node *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                node /= right
            elif op == '%':
                if right == 0:
                    raise ValueError("Division by zero")
                node %= right
        return node

    def parse_check_op(self, ops):
        return self.peek() in ops

    def parse_factor(self):
        # factor -> unary_minus_level
        return self.parse_unary_minus_level()

    def parse_unary_minus_level(self):
        # unary_minus_level -> '-' unary_minus_level | power
        if self.peek() == '-':
            self.consume('-')
            return -self.parse_unary_minus_level()
        else:
            return self.parse_power()

    def parse_power(self):
        # power -> primary [ '^' power ] (Right-associative)
        node = self.parse_primary()
        if self.peek() == '^':
            selfron = self.consume('^')
            right = self.parse_power()
            try:
                return node ** right
            except OverflowError:
                # Python handles large floats by returning inf, which is fine for float return type
                return float('inf') if node > 0 else float('-inf')
        return node

    def parse_primary(self):
        # primary -> number | variable | '(' expression ')' | unary_minus_level
        token = self.peek()
        if token is None:
            raise ValueError("Malformed syntax")

        if token == '(':
            self.consume('(')
            node = self.parse_expression()
            if self.peek() != ')':
                raise ValueError("Unbalanced parentheses")
            self.consume(')')
            return node
        elif token[0].isdigit() or (len(token) > 1 and token[0] == '.'):
            # Number
            val = float(self.consume())
            return val
        elif re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
            # Variable
            var_name = self.consume()
            if var_name in self.variables:
                return float(self.variables[var_name])
            else:
                raise ValueError(f"Unknown variable: {var_name}")
        elif token == '-':
            # This allows the '2^-2' case by letting primary handle unary minus
            return self.parse_unary_minus_level()
        else:
            raise ValueError("Malformed syntax")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # Tokenize the expression
    token_pattern = re.compile(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\%\^\(\)]')
    tokens = []
    last_end = 0
    for match in token_pattern.finditer(expr):
        # Check for invalid characters between tokens
        if expr[last_end:match.start()].strip():
            raise ValueError("Malformed syntax")
        tokens.append(match.group())
        last_end = match.end()
    
    # Check if there's any leftover non-whitespace text at the end
    if expr[last_end:].strip():
        raise ValueError("Malformed syntax")

    if not tokens:
        raise ValueError("Malformed syntax")

    parser = Parser(tokens, variables)
    result = parser.parse_expression()

    # If there are leftover tokens in the stream, it's a syntax error
    if parser.pos < len(tokens):
        raise ValueError("Malformed syntax")

    return float(result)
