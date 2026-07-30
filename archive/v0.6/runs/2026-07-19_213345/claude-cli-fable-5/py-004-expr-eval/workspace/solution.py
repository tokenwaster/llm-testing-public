class _Parser:
    def __init__(self, expr: str, variables: dict):
        self.tokens = self._tokenize(expr)
        self.pos = 0
        self.variables = variables

    @staticmethod
    def _tokenize(expr: str):
        tokens = []
        i = 0
        n = len(expr)
        while i < n:
            c = expr[i]
            if c.isspace():
                i += 1
            elif c.isdigit() or (c == '.' and i + 1 < n and expr[i + 1].isdigit() and False):
                # (the '.'-leading branch is disabled: leading-dot numbers unsupported)
                start = i
                while i < n and expr[i].isdigit():
                    i += 1
                if i < n and expr[i] == '.':
                    i += 1
                    if i >= n or not expr[i].isdigit():
                        raise ValueError(f"malformed number at position {start}")
                    while i < n and expr[i].isdigit():
                        i += 1
                tokens.append(('num', float(expr[start:i])))
            elif c.isalpha() or c == '_':
                start = i
                while i < n and (expr[i].isalnum() or expr[i] == '_'):
                    i += 1
                tokens.append(('name', expr[start:i]))
            elif c in '+-*/%^()':
                tokens.append(('op', c))
                i += 1
            else:
                raise ValueError(f"unexpected character {c!r} at position {i}")
        return tokens

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def take(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def expect_op(self, op: str):
        kind, val = self.take()
        if kind != 'op' or val != op:
            raise ValueError(f"expected {op!r}")

    # expr := term (('+'|'-') term)*
    def parse_expr(self) -> float:
        value = self.parse_term()
        while True:
            kind, val = self.peek()
            if kind == 'op' and val in ('+', '-'):
                self.pos += 1
                rhs = self.parse_term()
                value = value + rhs if val == '+' else value - rhs
            else:
                return value

    # term := unary (('*'|'/'|'%') unary)*
    def parse_term(self) -> float:
        value = self.parse_unary()
        while True:
            kind, val = self.peek()
            if kind == 'op' and val in ('*', '/', '%'):
                self.pos += 1
                rhs = self.parse_unary()
                if val == '*':
                    value = value * rhs
                else:
                    if rhs == 0:
                        raise ValueError("division by zero" if val == '/' else "modulo by zero")
                    value = value / rhs if val == '/' else value % rhs
            else:
                return value

    # unary := '-' unary | power        (unary minus binds looser than '^')
    def parse_unary(self) -> float:
        kind, val = self.peek()
        if kind == 'op' and val == '-':
            self.pos += 1
            return -self.parse_unary()
        return self.parse_power()

    # power := atom ('^' unary)?        (right-associative; exponent may be negative)
    def parse_power(self) -> float:
        base = self.parse_atom()
        kind, val = self.peek()
        if kind == 'op' and val == '^':
            self.pos += 1
            exponent = self.parse_unary()
            try:
                result = base ** exponent
            except ZeroDivisionError:
                raise ValueError("zero raised to a negative power")
            if isinstance(result, complex):
                raise ValueError("exponentiation produced a non-real result")
            return float(result)
        return base

    # atom := number | name | '(' expr ')'
    def parse_atom(self) -> float:
        kind, val = self.take()
        if kind == 'num':
            return val
        if kind == 'name':
            if val not in self.variables:
                raise ValueError(f"unknown variable {val!r}")
            return float(self.variables[val])
        if kind == 'op' and val == '(':
            value = self.parse_expr()
            self.expect_op(')')
            return value
        raise ValueError("malformed expression")

    def parse(self) -> float:
        if not self.tokens:
            raise ValueError("empty expression")
        value = self.parse_expr()
        if self.pos != len(self.tokens):
            raise ValueError("unexpected trailing tokens")
        return float(value)


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    return _Parser(expr, variables or {}).parse()
