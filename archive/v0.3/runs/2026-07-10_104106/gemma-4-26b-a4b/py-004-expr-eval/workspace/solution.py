import re

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with standard precedence and support for 
    exponentiation (right-associative), unary minus, and variables.
    """
    if variables is None:
        variables = {}

    # Tokenizer: matches numbers, variable names, operators, and parentheses.
    # It also identifies any characters that don't match the grammar as errors.
    token_pattern = re.compile(r'(\d+\.\d+|\d+|[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/%^()])')
    tokens = []
    last_end = 0
    for match in token_pattern.finditer(expr):
        # Check for any non-whitespace characters between tokens (malformed syntax)
        gap = expr[last_end:match.start()]
        if gap.strip():
            raise ValueError("Malformed syntax")
        tokens.append(match.group())
        last_end = match.end()
    # Check for any remaining non-whitespace characters at the end of the string
    gap = expr[last_end:]
    if gap.strip():
        raise ValueError("Malformed syntax")

    class Parser:
        def __init__(self, tokens, variables):
            self.tokens = tokens
            self.variables = variables
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

        def parse_expr(self):
            # expr : term { ('+' | '-') term } (Left-associative)
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
            # term : unary { ('*' | '/' | '%') unary } (Left-associative)
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
                        raise ValueError("Division by zero")
                    node %= right
            return node

        def parse_unary(self):
            # unary : '-' unary | factor (Unary minus binds looser than ^)
            if self.peek() == '-':
                self.consume('-')
                return -self.parse_unary()
            return self.parse_factor()

        def parse_factor(self):
            # factor : primary [ '^' factor ] (Right-associative)
            node = self.parse_primary()
            if self.peek() == '^':
                self.consume('^')
                right = self.parse_factor()
                try:
                    node = node ** right
                except ZeroDivisionError:
                    raise ValueError("Division by zero")
                except OverflowError:
                    # Handle potential overflow for large exponents
                    try:
                        node = node ** right
                    except OverflowError:
                        node = float('inf')
            return node

        def parse_primary(self):
            token = self.peek()
            if token is None:
                raise ValueError("Malformed syntax")
            
            if token == '(':
                self.consume('(')
                node = self.parse_expr()
                if self.peek() != ')':
                    raise ValueError("Unbalanced parentheses")
                self.consume(')')
                return node
            elif token[0].isdigit():
                # Numbers: integers and decimals (e.g., 3, 4.5)
                val_str = self.consume()
                try:
                    return float(val_str)
                except ValueError:
                    raise ValueError("Malformed syntax")
            elif token[0].isalpha() or token[0] == '_':
                # Variables: [a-zA-Z_][a-zA-Z0-9_]*
                var_name = self.consume()
                if var_name in self.variables:
                    return float(self.variables[var_name])
                else:
                    raise ValueError(f"Unknown variable: {var_name}")
            else:
                raise ValueError("Malformed syntax")

    parser = Parser(tokens, variables)
    result = parser.parse_expr()
    
    # If there are tokens left over, the expression was malformed (e.g., extra closing paren)
    if parser.pos < len(tokens):
        raise ValueError("Malformed syntax")
        
    return float(result)
