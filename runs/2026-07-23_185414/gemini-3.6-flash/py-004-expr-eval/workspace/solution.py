from __future__ import annotations


def tokenize(expr: str) -> list[tuple[str, str | float]]:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in '()+-*/%^':
            tokens.append(('OP', c))
            i += 1
            continue
        if c.isdigit() or (c == '.' and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n:
                if expr[i].isdigit():
                    i += 1
                elif expr[i] == '.' and not has_dot:
                    has_dot = True
                    i += 1
                else:
                    break
            num_str = expr[start:i]
            try:
                val = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid number: '{num_str}'")
            tokens.append(('NUMBER', val))
            continue
        if c.isalpha() or c == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('IDENT', expr[start:i]))
            continue
        raise ValueError(f"Invalid character in expression: '{c}'")
    return tokens


class Parser:
    def __init__(self, tokens: list[tuple[str, str | float]], variables: dict[str, float] | None = None):
        self.tokens = tokens
        self.variables = variables if variables is not None else {}
        self.pos = 0

    def current_token(self) -> tuple[str, str | float] | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def parse(self) -> float:
        if not self.tokens:
            raise ValueError("Empty expression")
        result = self.parse_expr()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token at position {self.pos}: {self.tokens[self.pos][1]}")
        return float(result)

    def parse_expr(self) -> float:
        left = self.parse_term()
        while True:
            tok = self.current_token()
            if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
                op = tok[1]
                self.advance()
                right = self.parse_term()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            else:
                break
        return left

    def parse_term(self) -> float:
        left = self.parse_unary()
        while True:
            tok = self.current_token()
            if tok and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                op = tok[1]
                self.advance()
                right = self.parse_unary()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("Division by zero")
                    try:
                        left = left / right
                    except ZeroDivisionError:
                        raise ValueError("Division by zero")
                elif op == '%':
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    try:
                        left = left % right
                    except ZeroDivisionError:
                        raise ValueError("Modulo by zero")
            else:
                break
        return left

    def parse_unary(self) -> float:
        tok = self.current_token()
        if tok and tok[0] == 'OP' and tok[1] == '-':
            self.advance()
            val = self.parse_unary()
            return -val
        elif tok and tok[0] == 'OP' and tok[1] == '+':
            self.advance()
            val = self.parse_unary()
            return val
        else:
            return self.parse_power()

    def parse_power(self) -> float:
        left = self.parse_primary()
        tok = self.current_token()
        if tok and tok[0] == 'OP' and tok[1] == '^':
            self.advance()
            right = self.parse_unary()
            try:
                res = left ** right
            except ZeroDivisionError:
                raise ValueError("Zero raised to negative power")
            except OverflowError:
                raise ValueError("Overflow in exponentiation")
            if isinstance(res, complex):
                raise ValueError("Complex result from exponentiation")
            return float(res)
        return left

    def parse_primary(self) -> float:
        tok = self.current_token()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if tok[0] == 'NUMBER':
            self.advance()
            return float(tok[1])
        elif tok[0] == 'IDENT':
            self.advance()
            var_name = str(tok[1])
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: '{var_name}'")
            return float(self.variables[var_name])
        elif tok[0] == 'OP' and tok[1] == '(':
            self.advance()
            val = self.parse_expr()
            tok_close = self.current_token()
            if tok_close is None or tok_close[0] != 'OP' or tok_close[1] != ')':
                raise ValueError("Unbalanced parentheses: missing ')'")
            self.advance()
            return val
        else:
            raise ValueError(f"Unexpected token: {tok[1]}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    try:
        tokens = tokenize(expr)
        parser = Parser(tokens, variables)
        return parser.parse()
    except (OverflowError, ArithmeticError) as e:
        raise ValueError(str(e)) from e
