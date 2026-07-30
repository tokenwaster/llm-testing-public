def tokenize(expr: str):
    """
    Convert the expression string into a list of tokens.
    Tokens are tuples: ('NUM', float), ('VAR', str), ('OP', str),
    ('LPAREN', '('), ('RPAREN', ')').
    """
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            # Parse a number: integer or decimal (e.g. 3, 4.5, 3.)
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                if expr[i] == '.':
                    has_dot = True
                i += 1
            num_str = expr[start:i]
            tokens.append(('NUM', float(num_str)))
        elif c.isalpha() or c == '_':
            # Parse a variable name: [a-zA-Z_][a-zA-Z0-9_]*
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('VAR', expr[start:i]))
        elif c in '+-*/%^':
            tokens.append(('OP', c))
            i += 1
        elif c == '(':
            tokens.append(('LPAREN', '('))
            i += 1
        elif c == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
        else:
            raise ValueError(f"Invalid character: {c}")
    return tokens


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}

    def peek(self):
        """Return the current token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        """Consume and return the current token."""
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        self.pos += 1
        return token

    def expect(self, typ, val=None):
        """Consume and check the next token."""
        token = self.advance()
        if token[0] != typ or (val is not None and token[1] != val):
            raise ValueError(f"Expected {typ} {val}, got {token}")
        return token

    def parse(self):
        """Entry point: parse the whole expression and check for trailing tokens."""
        value = self.parse_expression()
        if self.pos != len(self.tokens):
            raise ValueError("Unexpected token after expression")
        return value

    # --- Grammar rules ---

    def parse_expression(self):
        """expression ::= term ( ('+' | '-') term )*"""
        left = self.parse_term()
        while True:
            token = self.peek()
            if token and token[0] == 'OP' and token[1] in ('+', '-'):
                self.advance()
                right = self.parse_term()
                if token[1] == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    def parse_term(self):
        """term ::= unary ( ('*' | '/' | '%') unary )*"""
        left = self.parse_unary()
        while True:
            token = self.peek()
            if token and token[0] == 'OP' and token[1] in ('*', '/', '%'):
                self.advance()
                right = self.parse_unary()
                if token[1] == '*':
                    left = left * right
                elif token[1] == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                elif token[1] == '%':
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            else:
                break
        return left

    def parse_unary(self):
        """unary ::= '-' unary | power"""
        token = self.peek()
        if token and token[0] == 'OP' and token[1] == '-':
            self.advance()
            operand = self.parse_unary()
            return -operand
        return self.parse_power()

    def parse_power(self):
        """power ::= primary ('^' unary)?  (right‑associative)"""
        left = self.parse_primary()
        token = self.peek()
        if token and token[0] == 'OP' and token[1] == '^':
            self.advance()
            right = self.parse_unary()
            left = left ** right
        return left

    def parse_primary(self):
        """primary ::= NUMBER | VARIABLE | '(' expression ')'"""
        token = self.advance()
        if token[0] == 'NUM':
            return token[1]
        elif token[0] == 'VAR':
            name = token[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        elif token[0] == 'LPAREN':
            value = self.parse_expression()
            self.expect('RPAREN')
            return value
        else:
            raise ValueError(f"Unexpected token: {token}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluate an arithmetic expression without using eval, exec, ast, or any
    parsing library.

    Supported:
      - numbers (int / decimal)
      - binary operators: +, -, *, /, %, ^ (right‑associative)
      - unary minus (right‑assoc, binds looser than ^)
      - parentheses
      - variables
    """
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
