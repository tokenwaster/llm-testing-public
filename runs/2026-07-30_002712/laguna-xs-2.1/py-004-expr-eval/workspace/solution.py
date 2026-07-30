class Parser:
    def __init__(self, expr, variables=None):
        self.expr = expr.replace(" ", "")  # Remove all whitespace for simplicity
        self.pos = 0
        self.variables = {} if variables is None else dict(variables)

    def _peek(self):
        return self.expr[self.pos] if self.pos < len(self.expr) else None

    def _consume_char(self, expected=None):
        c = self._peek()
        if c is None:
            raise ValueError(f"Unexpected end of expression at position {self.pos}")
        if expected is not None and c != expected:
            raise ValueError(f"Expected '{expected}' but got '{c}'")
        self.pos += 1
        return c

    def parse_expression(self):
        value = self.parse_term()
        while True:
            c = self._peek()
            if c in ('+', '-'):
                op = self._consume_char()
                right_val = self.parse_term()
                if op == '+':
                    value += right_val
                else:
                    value -= right_val
            else:
                break
        return float(value)

    def parse_term(self):
        value = self.parse_factor()
        while True:
            c = self._peek()
            if c in ('*', '/', '%'):
                op = self._consume_char()
                right_val = self.parse_factor()
                if op == '*':
                    value *= right_val
                elif op == '/':
                    if right_val == 0:
                        raise ValueError("Division by zero")
                    value /= right_val
                else:
                    if right_val == 0:
                        raise ValueError("Modulo division by zero")
                    value %= right_val
            else:
                break
        return float(value)

    def parse_factor(self):
        sign = 1.0
        while True:
            c = self._peek()
            if c == '-':
                sign *= -1
                self.pos += 1
            elif c == '+':
                self.pos += 1
            else:
                break
        base_val = self.parse_power()
        return sign * base_val

    def parse_power(self):
        left_val = self.parse_primary()
        while True:
            if self._peek() == '^':
                self.pos += 1
                right_val = self.parse_power()
                left_val **= right_val
            else:
                break
        return float(left_val)

    def parse_primary(self):
        c = self._peek()
        if c is None:
            raise ValueError("Unexpected end of expression")

        if c == '(':
            self.pos += 1
            val = self.parse_expression()
            if not self._match(')'):
                raise ValueError("Mismatched parentheses")
            return float(val)
        elif c.isdigit():
            start = self.pos
            while self.pos < len(self.expr):
                next_c = self._peek()
                if next_c is None: break
                if not (next_c.isdigit() or next_c == '.'):
                    break
                self.pos += 1
            try:
                return float(self.expr[start:self.pos])
            except ValueError:
                raise ValueError(f"Invalid number at position {start}")

        # Parse variables (letters/underscores)
        elif c.isalpha() or c == '_':
            start = self.pos
            while self.pos < len(self.expr):
                next_c = self._peek()
                if next_c is None: break
                if not (next_c.isalnum() or next_c == '_'):
                    break
                self.pos += 1
            var_name = self.expr[start:self.pos]
            val = self.variables.get(var_name)
            if val is None:
                raise ValueError(f"Unknown variable '{var_name}'")
            return float(val)

        else:
            raise ValueError(f"Unexpected character '{c}' at position {self.pos}")

    def _match(self, expected):
        c = self._peek()
        if c == expected:
            self.pos +=1
            return True
        return False

def evaluate(expr, variables=None):
    try:
        parser = Parser(expr, variables)
        result = parser.parse_expression()
        if parser.pos != len(parser.expr):
            raise ValueError("Invalid syntax")
        return float(result)
    except Exception as e:
        raise ValueError(str(e)) from None
