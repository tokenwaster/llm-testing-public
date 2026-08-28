from __future__ import annotations


def evaluate(expr: str, variables: dict | None = None) -> float:
    """Evaluate an arithmetic expression without eval/exec/ast/parsing libs."""
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("Empty expression")
    parser = _Parser(tokens, variables if variables is not None else {})
    return parser.parse()


def _tokenize(s):
    tokens = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c.isdigit() or (c == '.' and i + 1 < n and s[i + 1].isdigit()):
            j = i
            while j < n and (s[j].isdigit() or s[j] == '.'):
                j += 1
            tokens.append(('NUM', s[i:j]))
            i = j
            continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (s[j].isalnum() or s[j] == '_'):
                j += 1
            tokens.append(('VAR', s[i:j]))
            i = j
            continue
        if c in '+-*/%^()':
            tokens.append(('OP', c))
            i += 1
            continue
        raise ValueError(f"Unexpected character {c!r} at index {i}")
    return tokens


class _Parser:
    def __init__(self, tokens, variables):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return (None, None)

    def _advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self):
        result = self._parse_add_sub()
        if self.pos != len(self.tokens):
            raise ValueError(f"Unexpected token {self._peek()[1]!r}")
        return float(result)

    def _parse_add_sub(self):
        left = self._parse_mul_div()
        while True:
            typ, val = self._peek()
            if typ == 'OP' and val in ('+', '-'):
                self._advance()
                right = self._parse_mul_div()
                left = _add(left, right) if val == '+' else _sub(left, right)
            else:
                return left

    def _parse_mul_div(self):
        left = self._parse_unary()
        while True:
            typ, val = self._peek()
            if typ == 'OP' and val in ('*', '/', '%'):
                self._advance()
                right = self._parse_unary()
                left = _binop(val, left, right)
            else:
                return left

    def _parse_unary(self):
        typ, val = self._peek()
        if typ == 'OP' and val in ('-', '+'):
            self._advance()
            operand = self._parse_unary()
            return -operand if val == '-' else +operand
        return self._parse_power()

    def _parse_power(self):
        base = self._parse_atom()
        typ, val = self._peek()
        if typ == 'OP' and val == '^':
            self._advance()
            exponent = self._parse_unary()  # right-associative; sign allowed in exponent
            return _binop('^', base, exponent)
        return base

    def _parse_atom(self):
        typ, val = self._peek()
        if typ == 'NUM':
            self._advance()
            try:
                return float(val)
            except ValueError:
                raise ValueError(f"Invalid number {val!r}")
        if typ == 'VAR':
            self._advance()
            if val not in self.variables:
                raise ValueError(f"Unknown variable {val!r}")
            try:
                return float(self.variables[val])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid value for variable {val!r}")
        if typ == 'OP' and val == '(':
            self._advance()
            result = self._parse_add_sub()
            t2, v2 = self._peek()
            if not (t2 == 'OP' and v2 == ')'):
                raise ValueError("Missing closing parenthesis")
            self._advance()
            return result
        raise ValueError(f"Unexpected token {val!r}")


def _add(a, b):
    try:
        return a + b
    except OverflowError:
        if a > 0 and b > 0:
            return float('inf')
        if a < 0 and b < 0:
            return float('-inf')
        return float('nan')


def _sub(a, b):
    try:
        return a - b
    except OverflowError:
        if a > 0 and b < 0:
            return float('inf')
        if a < 0 and b > 0:
            return float('-inf')
        return float('nan')


def _mul(a, b):
    try:
        return a * b
    except OverflowError:
        if (a < 0) != (b < 0):
            return float('-inf')
        return float('inf')


def _binop(op, a, b):
    if op == '+':
        return _add(a, b)
    if op == '-':
        return _sub(a, b)
    if op == '*':
        return _mul(a, b)
    if op == '/':
        if b == 0:
            raise ValueError("division by zero")
        try:
            return a / b
        except OverflowError:
            return float('-inf') if (a < 0) != (b < 0) else float('inf')
    if op == '%':
        if b == 0:
            raise ValueError("modulo by zero")
        try:
            return a % b
        except OverflowError:
            return float('-inf') if b < 0 else float('inf')
    # op == '^'
    try:
        return a ** b
    except ZeroDivisionError:
        return float('inf')
    except OverflowError:
        if b < 0:
            return 0.0
        if a >= 0 or (b == int(b) and int(b) % 2 == 0):
            return float('inf')
        return float('-inf')
    except ValueError:
        return float('nan')
