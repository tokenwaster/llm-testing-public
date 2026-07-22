class Tokenizer:
    def __init__(self, expr):
        self.expr = expr
        self.pos = 0
        self.tokens = []
        self._tokenize()

    def _tokenize(self):
        while self.pos < len(self.expr):
            ch = self.expr[self.pos]
            if ch.isspace():
                self.pos += 1
            elif ch.isdigit() or (ch == '.' and self.pos + 1 < len(self.expr) and self.expr[self.pos + 1].isdigit()):
                start = self.pos
                while self.pos < len(self.expr) and (self.expr[self.pos].isdigit() or self.expr[self.pos] == '.'):
                    self.pos += 1
                num_str = self.expr[start:self.pos]
                if '.' in num_str:
                    self.tokens.append(('NUMBER', float(num_str)))
                else:
                    self.tokens.append(('NUMBER', int(num_str)))
            elif ch.isalpha() or ch == '_':
                start = self.pos
                while self.pos < len(self.expr) and (self.expr[self.pos].isalnum() or self.expr[self.pos] == '_'):
                    self.pos += 1
                name = self.expr[start:self.pos]
                self.tokens.append(('IDENT', name))
            elif ch in '+-*/%^()':
                self.tokens.append((ch, ch))
                self.pos += 1
            else:
                raise ValueError(f"Unexpected character: {ch}")


class Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables or {}

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse_expr(self):
        left = self.parse_term()
        while self.peek() and self.peek()[0] in ('+', '-'):
            op = self.consume()[0]
            right = self.parse_term()
            if op == '+':
                left += right
            else:
                left -= right
        return left

    def parse_term(self):
        left = self.parse_unary()
        while self.peek() and self.peek()[0] in ('*', '/', '%'):
            op = self.consume()[0]
            right = self.parse_unary()
            if op == '*':
                left *= right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                left /= right
            else:
                if right == 0:
                    raise ValueError("Modulo by zero")
                left %= right
        return left

    def parse_unary(self):
        if self.peek() and self.peek()[0] == '-':
            self.consume()
            operand = self.parse_unary()
            return -operand
        return self.parse_power()

    def parse_power(self):
        base = self.parse_atom()
        while self.peek() and self.peek()[0] == '^':
            self.consume()
            exp = self.parse_power()
            left = base ** exp
            base = left
        return base

    def parse_atom(self):
        tok = self.peek()
        if not tok:
            raise ValueError("Unexpected end of expression")
        if tok[0] == 'NUMBER':
            self.consume()
            return tok[1]
        elif tok[0] == 'IDENT':
            name = tok[1]
            self.consume()
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        elif tok[0] == '(':
            self.consume()
            result = self.parse_expr()
            if not self.peek() or self.peek()[0] != ')':
                raise ValueError("Unbalanced parentheses")
            self.consume()
            return result
        else:
            raise ValueError(f"Unexpected token: {tok}")


def evaluate(expr, variables=None):
    tokenizer = Tokenizer(expr)
    parser = Parser(tokenizer.tokens, variables)
    result = parser.parse_expr()
    if parser.pos < len(parser.tokens):
        raise ValueError("Unexpected tokens after expression")
    return float(result)
