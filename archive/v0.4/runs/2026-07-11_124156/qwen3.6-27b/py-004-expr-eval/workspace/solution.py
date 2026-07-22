def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    class Parser:
        def __init__(self, expr: str, variables: dict[str, float] | None):
            self.expr = expr
            self.variables = variables or {}
            self.pos = 0
            self.length = len(expr)
            
        def advance(self) -> None:
            self.pos += 1
            
        def skip_whitespace(self) -> None:
            while self.pos < self.length and self.expr[self.pos].isspace():
                self.pos += 1
                
        def parse(self) -> float:
            self.skip_whitespace()
            result = self.parse_expr()
            self.skip_whitespace()
            if self.pos < self.length:
                raise ValueError("Malformed syntax")
            return result
            
        def parse_expr(self) -> float:
            left = self.parse_term()
            while True:
                self.skip_whitespace()
                if self.pos < self.length and self.expr[self.pos] in ('+', '-'):
                    op = self.expr[self.pos]
                    self.advance()
                    right = self.parse_term()
                    if op == '+':
                        left += right
                    else:
                        left -= right
                else:
                    break
            return left
            
        def parse_term(self) -> float:
            left = self.parse_unary()
            while True:
                self.skip_whitespace()
                if self.pos < self.length and self.expr[self.pos] in ('*', '/', '%'):
                    op = self.expr[self.pos]
                    self.advance()
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
                else:
                    break
            return left
            
        def parse_unary(self) -> float:
            self.skip_whitespace()
            if self.pos < self.length and self.expr[self.pos] == '-':
                self.advance()
                return -self.parse_unary()
            return self.parse_power()
            
        def parse_power(self) -> float:
            base = self.parse_factor()
            self.skip_whitespace()
            if self.pos < self.length and self.expr[self.pos] == '^':
                self.advance()
                exponent = self.parse_unary()
                return base ** exponent
            return base
            
        def parse_factor(self) -> float:
            self.skip_whitespace()
            if self.pos >= self.length:
                raise ValueError("Malformed syntax")
                
            char = self.expr[self.pos]
            if char == '(':
                self.advance()
                val = self.parse_expr()
                self.skip_whitespace()
                if self.pos >= self.length or self.expr[self.pos] != ')':
                    raise ValueError("Unbalanced parentheses")
                self.advance()
                return val
            elif char.isdigit() or char == '.':
                return self.parse_number()
            elif char.isalpha() or char == '_':
                return self.parse_variable()
            else:
                raise ValueError("Malformed syntax")
                
        def parse_number(self) -> float:
            start = self.pos
            has_dot = False
            while self.pos < self.length:
                char = self.expr[self.pos]
                if char.isdigit():
                    self.pos += 1
                elif char == '.':
                    if has_dot:
                        break
                    has_dot = True
                    self.pos += 1
                else:
                    break
            if self.pos == start:
                raise ValueError("Malformed syntax")
            return float(self.expr[start:self.pos])
            
        def parse_variable(self) -> float:
            start = self.pos
            while self.pos < self.length:
                char = self.expr[self.pos]
                if char.isalnum() or char == '_':
                    self.pos += 1
                else:
                    break
            var_name = self.expr[start:self.pos]
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(self.variables[var_name])

    return Parser(expr, variables).parse()
