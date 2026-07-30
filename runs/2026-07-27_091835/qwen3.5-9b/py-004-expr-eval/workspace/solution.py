def tokenize(expr: str) -> list[str]:
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in '+-*/%^()':
            tokens.append(c)
            i += 1
        elif c.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif c == '.' and (i == 0 or expr[i-1] != '.') and (i+1 < len(expr) and expr[i+1].isdigit()):
            j = i + 1
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < len(expr) and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(expr[i:j])
            i = j
        else:
            raise ValueError(f"Invalid character: {c!r}")
    return tokens


class Parser:
    def __init__(self, tokens: list[str], variables: dict | None):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}

    def peek(self) -> str | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self) -> str:
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of expression")
        self.pos += 1
        return token

    def parse_primary(self) -> float:
        token = self.consume()
        
        # Parentheses
        if token == '(':
            value = self.parse_expression()
            self.consume(')')
            return value
        
        # Number
        if token.replace('.', '', 1).isdigit():
            return float(token)
        
        # Variable
        if self.variables and token in self.variables:
            return self.variables[token]
        
        raise ValueError(f"Unexpected token: {token!r}")

    def parse_unary(self) -> float:
        if self.peek() == '-':
            self.consume('-')
            value = self.parse_unary()
            return -value
        elif self.peek() == '+':
            self.consume('+')
            return self.parse_unary()
        else:
            return self.parse_primary()

    def parse_power(self) -> float:
        base = self.parse_unary()
        while self.peek() == '^':
            self.consume('^')
            exponent = self.parse_power()  # right associative
            base = base ** exponent
        return base

    def parse_term(self) -> float:
        value = self.parse_power()
        while self.peek() in ('*', '/', '%'):
            op = self.consume()
            rhs = self.parse_power()
            if op == '*':
                value = value * rhs
            elif op == '/':
                if rhs == 0:
                    raise ValueError("division by zero")
                value = value / rhs
            elif op == '%':
                if rhs == 0:
                    raise ValueError("modulo by zero")
                value = value % rhs
        return value

    def parse_expression(self) -> float:
        value = self.parse_term()
        while self.peek() in ('+', '-'):
            op = self.consume()
            rhs = self.parse_term()
            if op == '+':
                value = value + rhs
            elif op == '-':
                value = value - rhs
        return value

    def parse(self) -> float:
        result = self.parse_expression()
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected token at end: {self.tokens[self.pos]!r}")
        return result


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
