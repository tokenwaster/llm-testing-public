def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if not expr.strip():
        raise ValueError("Empty expression")
    
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables or {})
    return parser.parse()


def _tokenize(expr):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit():
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or (expr[j] == '.' and not has_dot)):
                if expr[j] == '.':
                    has_dot = True
                j += 1
            tokens.append(('NUM', float(expr[i:j])))
            i = j
        elif c.isalpha() or c == '_':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == '_'):
                j += 1
            tokens.append(('VAR', expr[i:j]))
            i = j
        elif c in '+-*/%^()':
            tokens.append((c, c))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c!r}")
    if not tokens:
        raise ValueError("Empty expression")
    return tokens


class _Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")
        self.pos += 1
        return tok

    def parse(self):
        result = self._addition()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token after expression: {self.tokens[self.pos]}")
        return result

    def _addition(self):
        left = self._multiplication()
        while self.peek() and self.peek()[0] in ('+', '-'):
            op = self.consume()[0]
            right = self._multiplication()
            if op == '+':
                left = left + right
            else:
                left = left - right
        return left

    def _multiplication(self):
        left = self._factor()
        while self.peek() and self.peek()[0] in ('*', '/', '%'):
            op = self.consume()[0]
            right = self._factor()
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

    def _factor(self):
        if self.peek() and self.peek()[0] == '-':
            self.consume()
            operand = self._factor()
            return -operand
        return self._power()

    def _power(self):
        base = self._primary()
        if self.peek() and self.peek()[0] == '^':
            self.consume()
            exponent = self._factor()  # right-associative; factor handles unary on RHS
            return base ** exponent
        return base

    def _primary(self):
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if tok[0] == 'NUM':
            self.consume()
            return tok[1]
        elif tok[0] == 'VAR':
            self.consume()
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        elif tok[0] == '(':
            self.consume()
            result = self._addition()
            if not self.peek() or self.peek()[0] != ')':
                raise ValueError("Unbalanced parentheses")
            self.consume()  # consume ')'
            return result
        else:
            raise ValueError(f"Unexpected token: {tok}")
