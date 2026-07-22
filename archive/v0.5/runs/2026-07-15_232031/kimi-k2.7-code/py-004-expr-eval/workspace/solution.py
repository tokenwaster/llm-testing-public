def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables)
    return parser.parse()


def _tokenize(s: str):
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or (c == '.' and i + 1 < n and s[i + 1].isdigit()):
            start = i
            if c.isdigit():
                i += 1
                while i < n and s[i].isdigit():
                    i += 1
            if i < n and s[i] == '.':
                i += 1
                while i < n and s[i].isdigit():
                    i += 1
            num_str = s[start:i]
            if num_str == '.':
                raise ValueError("Invalid number")
            tokens.append(('NUM', float(num_str)))
            continue
        if c.isalpha() or c == '_':
            start = i
            i += 1
            while i < n and (s[i].isalnum() or s[i] == '_'):
                i += 1
            tokens.append(('IDENT', s[start:i]))
            continue
        if c == '(':
            tokens.append(('LPAREN', c))
            i += 1
            continue
        if c == ')':
            tokens.append(('RPAREN', c))
            i += 1
            continue
        if c in '+-*/%^':
            tokens.append(('OP', c))
            i += 1
            continue
        raise ValueError(f"Invalid character: {c}")
    tokens.append(('EOF', None))
    return tokens


class _Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def _peek(self):
        return self.tokens[self.pos]

    def _eat(self, typ=None, val=None):
        tok = self._peek()
        if typ is not None and tok[0] != typ:
            raise ValueError("Unexpected token")
        if val is not None and tok[1] != val:
            raise ValueError("Unexpected token")
        self.pos += 1
        return tok

    def parse(self):
        if self._peek()[0] == 'EOF':
            raise ValueError("Empty expression")
        result = self._expr()
        if self._peek()[0] != 'EOF':
            raise ValueError("Unexpected token after end of expression")
        return result

    def _expr(self):
        value = self._term()
        while True:
            tok = self._peek()
            if tok[0] == 'OP' and tok[1] in ('+', '-'):
                self._eat()
                right = self._term()
                if tok[1] == '+':
                    value = value + right
                else:
                    value = value - right
            else:
                break
        return value

    def _term(self):
        value = self._unary()
        while True:
            tok = self._peek()
            if tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                self._eat()
                right = self._unary()
                if tok[1] == '*':
                    value = value * right
                elif tok[1] == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    value = value / right
                else:
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    value = value % right
            else:
                break
        return value

    def _unary(self):
        tok = self._peek()
        if tok[0] == 'OP' and tok[1] == '-':
            self._eat()
            return -self._unary()
        if tok[0] == 'OP' and tok[1] == '+':
            self._eat()
            return self._unary()
        return self._power()

    def _power(self):
        left = self._primary()
        tok = self._peek()
        if tok[0] == 'OP' and tok[1] == '^':
            self._eat()
            right = self._power()
            try:
                result = left ** right
            except ZeroDivisionError:
                raise ValueError("Division by zero in exponentiation")
            if isinstance(result, complex):
                raise ValueError("Complex result")
            return float(result)
        return left

    def _primary(self):
        tok = self._peek()
        if tok[0] == 'NUM':
            self._eat()
            return tok[1]
        if tok[0] == 'IDENT':
            self._eat()
            name = tok[1]
            if name not in self.variables:
                raise ValueError(f"Unknown variable: {name}")
            return float(self.variables[name])
        if tok[0] == 'LPAREN':
            self._eat()
            value = self._expr()
            self._eat('RPAREN')
            return value
        raise ValueError("Unexpected token")
