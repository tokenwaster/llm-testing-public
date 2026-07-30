from __future__ import annotations

class Token:
    __slots__ = ('type', 'value')
    def __init__(self, type: str, value: str | None) -> None:
        self.type = type
        self.value = value

def tokenize(expr: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit():
            start = i
            i += 1
            while i < n and expr[i].isdigit():
                i += 1
            if i < n and expr[i] == '.':
                if i + 1 < n and expr[i+1].isdigit():
                    i += 1
                    while i < n and expr[i].isdigit():
                        i += 1
                else:
                    raise ValueError(f"Malformed number at position {start}")
            tokens.append(Token('NUMBER', expr[start:i]))
            continue
        if c.isalpha() or c == '_':
            start = i
            i += 1
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(Token('VARIABLE', expr[start:i]))
            continue
        if c in '+-*/%^':
            tokens.append(Token('OP', c))
            i += 1
            continue
        if c == '(':
            tokens.append(Token('LPAREN', c))
            i += 1
            continue
        if c == ')':
            tokens.append(Token('RPAREN', c))
            i += 1
            continue
        raise ValueError(f"Unexpected character: {c!r} at position {i}")
    tokens.append(Token('EOF', None))
    return tokens

class Parser:
    def __init__(self, tokens: list[Token], variables: dict[str, float]):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type: str, value: str | None = None) -> Token:
        tok = self.peek()
        if tok.type != type or (value is not None and tok.value != value):
            raise ValueError(f"Expected {type} {value if value is not None else ''}, got {tok.type} {tok.value}")
        return self.advance()

    def parse(self) -> float:
        val = self.parse_expr()
        if self.peek().type != 'EOF':
            raise ValueError("Unexpected trailing tokens")
        return val

    def parse_expr(self) -> float:
        left = self.parse_term()
        while self.peek().type == 'OP' and self.peek().value in ('+', '-'):
            op = self.advance().value
            right = self.parse_term()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def parse_term(self) -> float:
        left = self.parse_factor()
        while self.peek().type == 'OP' and self.peek().value in ('*', '/', '%'):
            op = self.advance().value
            right = self.parse_factor()
            if op == '*':
                left = left * right
            elif op == '/':
                if right == 0.0:
                    raise ValueError("Division by zero")
                left = left / right
            else:  # '%'
                if right == 0.0:
                    raise ValueError("Modulo by zero")
                left = left % right
        return left

    def parse_factor(self) -> float:
        return self.parse_unary()

    def parse_unary(self) -> float:
        if self.peek().type == 'OP' and self.peek().value == '-':
            self.advance()
            operand = self.parse_unary()
            return -operand
        return self.parse_power()

    def parse_power(self) -> float:
        left = self.parse_atom()
        if self.peek().type == 'OP' and self.peek().value == '^':
            self.advance()
            right = self.parse_unary()
            try:
                result = left ** right
            except ZeroDivisionError:
                raise ValueError("Exponentiation by zero")
            if isinstance(result, complex):
                raise ValueError("Complex result not supported")
            return float(result)
        return left

    def parse_atom(self) -> float:
        tok = self.peek()
        if tok.type == 'NUMBER':
            self.advance()
            return float(tok.value)
        elif tok.type == 'VARIABLE':
            self.advance()
            if tok.value not in self.variables:
                raise ValueError(f"Unknown variable: {tok.value}")
            return float(self.variables[tok.value])
        elif tok.type == 'LPAREN':
            self.advance()
            val = self.parse_expr()
            self.expect('RPAREN')
            return val
        else:
            raise ValueError(f"Unexpected token: {tok.type} {tok.value}")

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
