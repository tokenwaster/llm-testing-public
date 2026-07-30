def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """
    Evaluates an arithmetic expression with support for numbers, binary operators (+, -, *, /, %, ^),
    unary minus (looser than ^), parentheses, and variable resolution.
    No eval, exec, ast, or parsing libraries are used.
    """
    if variables is None:
        variables = {}

    # --- Lexer ---
    def tokenize(expression):
        tokens = []
        i = 0
        n = len(expression)
        while i < n:
            c = expression[i]
            if c.isspace():
                i += 1
                continue
            if c.isdigit() or (c == '.' and i + 1 < n and expression[i+1].isdigit()):
                num_str = ""
                while i < n and (expression[i].isdigit() or expression[i] == '.'):
                    num_str += expression[i]
                    i += 1
                tokens.append(('NUMBER', float(num_str)))
            elif c.isalpha() or c == '_':
                var_str = ""
                while i < n and (expression[i].isalnum() or expression[i] == '_'):
                    var_str += expression[i]
                    i += 1
                tokens.append(('VAR', var_str))
            elif c in '+-*/%^()':
                tokens.append((c, c))
                i += 1
            else:
                raise ValueError(f"Unknown character: {c}")
        return tokens

    # --- Parser ---
    class Parser:
        def __init__(self, tokens, variables):
            self.tokens = tokens
            self.variables = variables
            self.pos = 0

        def current_token(self):
            if self.pos < len(self.tokens):
                return self.tokens[self.pos]
            return None

        def consume(self, expected_type=None):
            token = self.current_token()
            if token is None:
                raise ValueError("Unexpected end of expression")
            if expected_type and token[0] != expected_type:
                raise ValueError(f"Expected {expected_type}, got {token[0]}")
            self.pos += 1
            return token

        def parse_expression(self):
            # Level 1 (Lowest): + , - (Left-associative)
            node = self.parse_term()
            while self.current_token() and self.current_token()[0] in ('+', '-'):
                op = self.consume()[0]
                right = self.parse_term()
                if op == '+':
                    node += right
                else:
                    node -= right
            return node

        def parse_term(self):
            # Level 2: * , / , % (Left-associative)
            node = self.parse_unary()
            while self.current_token() and self.current_token()[0] in ('*', '/', '%'):
                op = self.consume()[0]
                right = self.parse_unary()
                if op == '*':
                    node *= right
                elif op == '/':
                    if right == 0: raise ValueError("Division by zero")
                    node /= right
                elif op == '%':
                    if right == 0: raise ValueError("Modulo by zero")
                    node %= right
            return node

        def parse_unary(self):
            # Level 3: Unary minus (Looser than ^)
            if self.current_token() and self.current_token()[0] == '-':
                self.consume('-')
                return -self.parse_unary()
            else:
                return self.parse_power()

        def parse_power(self):
            # Level 4: ^ (Right-associative)
            node = self.parse_primary()
            if self.current_token() and self.current_token()[0] == '^':
                self.consume('^')
                right = self.parse_power()  # Recursive call for right-associativity
                return node ** right
            return node

        def parse_primary(self):
            # Level 5 (Highest): Numbers, Variables, Parentheses
            token = self.current_token()
            if token is None:
                raise ValueError("Unexpected end of expression")
            
            if token[0] == 'NUMBER':
                return self.consume('NUMBER')[1]
            elif token[0] == 'VAR':
                var_name = self.consume('VAR')[1]
                if var_name not in self.variables:
                    raise ValueError(f"Unknown variable: {var_name}")
                return float(self.variables[var_name])
            elif token[0] == '(':
                self.consume('(')
                node = self.parse_expression()
                self.consume(')')
                return node
            else:
                raise ValueError(f"Unexpected token: {token[0]}")

        def parse(self):
            result = self.parse_expression()
            if self.pos < len(self.tokens):
                raise ValueError("Malformed expression")
            return float(result)

    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
