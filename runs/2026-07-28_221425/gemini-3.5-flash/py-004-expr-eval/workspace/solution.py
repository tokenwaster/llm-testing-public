import re

def tokenize(expr: str):
    token_specification = [
        ('NUMBER',   r'\d+(?:\.\d+)?'),
        ('ID',       r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('OP',       r'[+\-*/%^]'),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('WS',       r'\s+'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tok_re = re.compile(tok_regex)
    pos = 0
    tokens = []
    limit = len(expr)
    while pos < limit:
        match = tok_re.match(expr, pos)
        if not match:
            raise ValueError(f"Invalid character at position {pos}")
        kind = match.lastgroup
        value = match.group(kind)
        if kind != 'WS':
            tokens.append((kind, value))
        pos = match.end()
    return tokens

class Parser:
    def __init__(self, tokens, variables=None):
        self.tokens = tokens
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_kind=None):
        tok = self.current_token()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        kind, value = tok
        if expected_kind and kind != expected_kind:
            raise ValueError(f"Expected {expected_kind}, got {kind}")
        self.pos += 1
        return value

    def parse(self):
        val = self.expr()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token {self.tokens[self.pos]}")
        return val

    def expr(self):
        # expr -> term { ('+' | '-') term }
        val = self.term()
        while True:
            tok = self.current_token()
            if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = self.consume('OP')
                right = self.term()
                if op == '+':
                    val = val + right
                else:
                    val = val - right
            else:
                break
        return val

    def term(self):
        # term -> factor { ('*' | '/' | '%') factor }
        val = self.factor()
        while True:
            tok = self.current_token()
            if tok and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = self.consume('OP')
                right = self.factor()
                if op == '*':
                    val = val * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    val = val / right
                elif op == '%':
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    val = val % right
            else:
                break
        return val

    def factor(self):
        # factor -> '-' factor | '+' factor | power
        tok = self.current_token()
        if tok and tok[0] == 'OP' and tok[1] == '-':
            self.consume('OP')
            return -self.factor()
        elif tok and tok[0] == 'OP' and tok[1] == '+':
            self.consume('OP')
            return self.factor()
        return self.power()

    def power(self):
        # power -> primary [ '^' factor ]
        val = self.primary()
        tok = self.current_token()
        if tok and tok[0] == 'OP' and tok[1] == '^':
            self.consume('OP')
            right = self.factor()
            try:
                val = val ** right
            except ZeroDivisionError:
                raise ValueError("Division by zero")
            if isinstance(val, complex):
                raise ValueError("Complex result is not supported")
        return val

    def primary(self):
        # primary -> NUMBER | ID | '(' expr ')'
        tok = self.current_token()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        
        kind, value = tok
        if kind == 'NUMBER':
            self.consume('NUMBER')
            return float(value)
        elif kind == 'ID':
            self.consume('ID')
            if value not in self.variables:
                raise ValueError(f"Unknown variable: {value}")
            return float(self.variables[value])
        elif kind == 'LPAREN':
            self.consume('LPAREN')
            val = self.expr()
            self.consume('RPAREN')
            return val
        else:
            raise ValueError(f"Unexpected token: {value}")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return float(parser.parse())
