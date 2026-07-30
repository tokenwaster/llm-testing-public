def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    if variables is None:
        variables = {}

    class Parser:
        def __init__(self, text: str, variables: dict[str, float]):
            self.text = text
            self.variables = variables
            self.pos = 0
            self.len = len(text)
            self.current_char = text[0] if text else None

        def advance(self) -> None:
            self.pos += 1
            if self.pos < self.len:
                self.current_char = self.text[self.pos]
            else:
                self.current_char = None

        def skip_whitespace(self) -> None:
            while self.current_char is not None and self.current_char.isspace():
                self.advance()

        def parse(self) -> float:
            self.skip_whitespace()
            if self.current_char is None:
                raise ValueError("Empty expression")
            result = self.parse_expression()
            self.skip_whitespace()
            if self.current_char is not None:
                raise ValueError("Malformed syntax")
            return result

        def parse_expression(self) -> float:
            self.skip_whitespace()
            left = self.parse_term()
            while True:
                self.skip_whitespace()
                if self.current_char in ('+', '-'):
                    op = self.current_char
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
            self.skip_whitespace()
            left = self.parse_factor()
            while True:
                self.skip_whitespace()
                if self.current_char in ('*', '/', '%'):
                    op = self.current_char
                    self.advance()
                    right = self.parse_factor()
                    if op == '*':
                        left = left * right
                    elif op == '/':
                        if right == 0:
                            raise ValueError("Division by zero")
                        left = left / right
                    elif op == '%':
                        if right == 0:
                            raise ValueError("Modulo by zero")
                        left = left % right
                else:
                    break
            return left

        def parse_factor(self) -> float:
            self.skip_whitespace()
            if self.current_char == '-':
                self.advance()
                val = self.parse_factor()
                return -val
            return self.parse_power()

        def parse_power(self) -> float:
            self.skip_whitespace()
            left = self.parse_primary()
            self.skip_whitespace()
            if self.current_char == '^':
                self.advance()
                right = self.parse_power()  # right-associative
                left = left ** right
            return left

        def parse_primary(self) -> float:
            self.skip_whitespace()
            if self.current_char == '(':
                self.advance()
                val = self.parse_expression()
                self.skip_whitespace()
                if self.current_char != ')':
                    raise ValueError("Unbalanced parentheses")
                self.advance()
                return val
            elif self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
                return self.parse_number()
            elif self.current_char is not None and (self.current_char.isalpha() or self.current_char == '_'):
                return self.parse_variable()
            else:
                raise ValueError("Malformed syntax")

        def parse_number(self) -> float:
            start = self.pos
            has_digits = False
            # integer part
            while self.current_char is not None and self.current_char.isdigit():
                self.advance()
                has_digits = True
            # fractional part
            if self.current_char == '.':
                self.advance()
                while self.current_char is not None and self.current_char.isdigit():
                    self.advance()
                    has_digits = True
            if not has_digits:
                raise ValueError("Malformed number")
            num_str = self.text[start:self.pos]
            try:
                return float(num_str)
            except ValueError:
                raise ValueError("Malformed number")

        def parse_variable(self) -> float:
            start = self.pos
            self.advance()
            while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
                self.advance()
            var_name = self.text[start:self.pos]
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(self.variables[var_name])

    parser = Parser(expr, variables)
    return parser.parse()
