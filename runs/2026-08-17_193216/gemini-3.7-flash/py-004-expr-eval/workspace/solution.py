import re


def tokenize(expr: str):
    token_pattern = re.compile(
        r'\s*(?:'
        r'(?P<NUMBER>\d+(?:\.\d+)?)'
        r'|(?P<IDENT>[a-zA-Z_][a-zA-Z0-9_]*)'
        r'|(?P<OP>[+\-*/%^()])'
        r'|(?P<MISMATCH>\S)'
        r')'
    )
    tokens = []
    pos = 0
    while pos < len(expr):
        match = token_pattern.match(expr, pos)
        if not match:
            break
        kind = match.lastgroup
        value = match.group(kind)
        if kind == 'MISMATCH':
            raise ValueError(f"Invalid character: {value!r}")
        tokens.append((kind, value))
        pos = match.end()

    if pos < len(expr) and expr[pos:].strip():
        raise ValueError("Invalid character in expression")

    tokens.append(('EOF', ''))
    return tokens


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables if variables is not None else {}

    def current(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def match(self, expected_type, expected_val=None):
        tok = self.current()
        if tok[0] == expected_type and (expected_val is None or tok[1] == expected_val):
            self.advance()
            return tok
        return None

    def expect(self, expected_type, expected_val=None):
        tok = self.match(expected_type, expected_val)
        if tok is None:
            raise ValueError(f"Expected {expected_type} {expected_val}, got {self.current()}")
        return tok

    def parse(self):
        if self.current()[0] == 'EOF':
            raise ValueError("Empty expression")
        result = self.parse_expr()
        if self.current()[0] != 'EOF':
            raise ValueError(f"Unexpected trailing tokens: {self.current()}")
        return float(result)

    def parse_expr(self):
        node = self.parse_term()
        while True:
            if self.match('OP', '+'):
                node = node + self.parse_term()
            elif self.match('OP', '-'):
                node = node - self.parse_term()
            else:
                break
        return node

    def parse_term(self):
        node = self.parse_unary()
        while True:
            if self.match('OP', '*'):
                node = node * self.parse_unary()
            elif self.match('OP', '/'):
                denom = self.parse_unary()
                if denom == 0:
                    raise ValueError("Division by zero")
                node = node / denom
            elif self.match('OP', '%'):
                denom = self.parse_unary()
                if denom == 0:
                    raise ValueError("Modulo by zero")
                node = node % denom
            else:
                break
        return node

    def parse_unary(self):
        if self.match('OP', '+'):
            return self.parse_unary()
        elif self.match('OP', '-'):
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self):
        node = self.parse_atom()
        if self.match('OP', '^'):
            exponent = self.parse_unary()
            try:
                res = node ** exponent
                if isinstance(res, complex):
                    if res.imag != 0:
                        raise ValueError("Complex result from exponentiation")
                    res = res.real
                return res
            except ZeroDivisionError:
                raise ValueError("Zero to negative power")
            except OverflowError:
                raise ValueError("Overflow in exponentiation")
        return node

    def parse_atom(self):
        tok = self.current()
        if self.match('NUMBER'):
            return float(tok[1])
        elif self.match('IDENT'):
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        elif self.match('OP', '('):
            val = self.parse_expr()
            self.expect('OP', ')')
            return val
        else:
            raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
