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
            raise ValueError("Unexpected end of expression")
        if expected and token != expected:
            raise ValueError(f"Expected {expected}, but found {token}")
        self.pos += 1
        return token

    def parse_expression(self):
        # Handles binary + and - (left-associative)
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
        # Handles binary *, /, and % (left-associative)
        node = self.parse_unary()
        while self.peek() in ('*', '/', '%'):
            op = self.consume()
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
        # Handles unary minus (can be repeated)
        if self.peek() == '-':
            self.consume('-')
            # Unary minus binds looser than ^, so we call parse_unary recursively 
            # to handle multiple minuses and then apply it after exponentiation.
            return -self.parse_unary()
        return self.parse_exponent()

    def parse_exponent(self):
        # Handles binary ^ (right-associative)
        node = self.parse_primary()
        if self.peek() == '^':
            self.consume('^')
            # To allow 2^-3, the exponent part must be able to include unary minus.
            # We call parse_unary here instead of parse_primary.
            right = self.parse_unary()
            try:
                node = node ** right
            except OverflowError:
                raise ValueError("Result too large")
            except ZeroDivisionError:
                raise ValueError("Division by zero")
        return node

    def parse_primary(self):
        # Handles numbers, variables, and parentheses
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")

        if token == '(':
            self.consume('(')
            node = self.parse_expression()
            self.consume(')')
            return node
        
        # Check if it's a number (integer or decimal)
        try:
            # We use the current token and move forward
            val_str = self.consume()
            # The tokenizer ensures this is a valid numeric string format
            return float(val_str)
        except ValueError:
            # If not a number, check if it's a variable
            if re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
                var_name = self.consume()
                if var_name in self.variables:
                    return float(self.variables[var_name])
                else:
                    raise ValueError(f"Unknown variable: {var_name}")
            else:
                raise ValueError(f"Unexpected token: {token}")

def tokenize(expr):
    # Regex to identify numbers, variables, and operators/parentheses
    token_pattern = re.compile(r'\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/%^()]')
    tokens = []
    last_end = 0
    for match in token_pattern.finditer(expr):
        # Check for invalid characters between tokens
        if expr[last_end:match.start()].strip():
            raise ValueError("Invalid character in expression")
        tokens.append(match.group())
        last_end = match.end()
    # Check if there's any junk left at the end of the string
    if expr[last_end:].strip():
        raise ValueError("Invalid character in expression")
    return tokens

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    try:
        tokens = tokenize(expr)
    except ValueError as e:
        raise e
    
    parser = Parser(tokens, variables)
    result = parser.parse_expression()
    
    # If there are leftover tokens, the syntax is malformed (e.g., "2 + 3 4")
    if parser.pos < len(tokens):
        raise ValueError("Malformed syntax: extra tokens found")
        
    return float(result)
