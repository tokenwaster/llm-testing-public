def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")
    
    parser = _Parser(tokens, variables)
    result = parser.parse()
    return float(result)


def _tokenize(expr):
    """Break the expression into a list of (type, value) tuples."""
    tokens = []
    i = 0
    n = len(expr)
    
    while i < n:
        c = expr[i]
        
        if c.isspace():
            i += 1
        
        elif c.isdigit():
            # Parse a number (integer or decimal, e.g., "3", "4.5", "3.")
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUMBER', float(expr[i:j])))
            i = j
        
        elif c.isalpha() or c == '_':
            # Parse an identifier (variable name)
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('IDENTIFIER', expr[i:j]))
            i = j
        
        elif c in '+-*/%^':
            tokens.append(('OPERATOR', c))
            i += 1
        
        elif c == '(':
            tokens.append(('LPAREN', '('))
            i += 1
        
        elif c == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
        
        else:
            raise ValueError(f"Unexpected character: {c!r}")
    
    return tokens


class _Parser:
    """Recursive descent parser for arithmetic expressions."""
    
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.variables = variables or {}
        self.pos = 0
    
    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self, expected_type=None):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        if expected_type and token[0] != expected_type:
            raise ValueError(f"Expected {expected_type}, got {token}")
        self.pos += 1
        return token
    
    def parse(self):
        result = self.expression()
        if self.pos < len(self.tokens):
            raise ValueError(
                f"Unexpected token after expression: {self.tokens[self.pos]}"
            )
        return result
    
    # expression → additive_expr (('+' | '-') additive_expr)*
    def expression(self):
        left = self.additive_expr()
        while (
            self.peek() is not None
            and self.peek()[0] == 'OPERATOR'
            and self.peek()[1] in '+-'
        ):
            op = self.consume()[1]
            right = self.additive_expr()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left
    
    # additive_expr → multiplicative_expr (('*' | '/' | '%') multiplicative_expr)*
    def additive_expr(self):
        left = self.multiplicative_expr()
        while (
            self.peek() is not None
            and self.peek()[0] == 'OPERATOR'
            and self.peek()[1] in '*/%'
        ):
            op = self.consume()[1]
            right = self.multiplicative_expr()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # '%'
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left
    
    # multiplicative_expr → power_expr ('^' power_expr)?   (right-associative)
    def multiplicative_expr(self):
        base = self.power_expr()
        if (
            self.peek() is not None
            and self.peek()[0] == 'OPERATOR'
            and self.peek()[1] == '^'
        ):
            self.consume()  # consume '^'
            exponent = self.multiplicative_expr()  # right-associative: recurse
            return base ** exponent
        return base
    
    # power_expr → '-' power_expr | atom
    def power_expr(self):
        if (
            self.peek() is not None
            and self.peek()[0] == 'OPERATOR'
            and self.peek()[1] == '-'
        ):
            self.consume()  # consume '-'
            operand = self.power_expr()
            return -operand
        return self.atom()
    
    # atom → NUMBER | IDENTIFIER | '(' expression ')'
    def atom(self):
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        
        if token[0] == 'NUMBER':
            self.consume()
            return token[1]
        
        elif token[0] == 'IDENTIFIER':
            name = self.consume()[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        
        elif token[0] == 'LPAREN':
            self.consume()  # consume '('
            result = self.expression()
            if (
                self.peek() is None
                or self.peek()[0] != 'RPAREN'
            ):
                raise ValueError(
                    "Unbalanced parentheses: missing closing ')'"
                )
            self.consume()  # consume ')'
            return result
        
        else:
            raise ValueError(f"Unexpected token: {token}")
