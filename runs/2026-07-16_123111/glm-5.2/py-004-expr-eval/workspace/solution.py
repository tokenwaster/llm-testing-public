def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # ---------- Tokenizer ----------
    tokens = []
    i = 0
    n = len(expr)

    while i < n:
        c = expr[i]

        # Whitespace
        if c.isspace():
            i += 1
            continue

        # Numbers (integers and decimals, but not leading-dot like .5)
        if '0' <= c <= '9':
            start = i
            while i < n and '0' <= expr[i] <= '9':
                i += 1
            if i < n and expr[i] == '.':
                i += 1
                while i < n and '0' <= expr[i] <= '9':
                    i += 1
            num_str = expr[start:i]
            tokens.append(('NUMBER', float(num_str)))
            continue

        # Variable names: [a-zA-Z_][a-zA-Z0-9_]*
        if ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_':
            start = i
            while i < n and (
                ('a' <= expr[i] <= 'z') or
                ('A' <= expr[i] <= 'Z') or
                ('0' <= expr[i] <= '9') or
                expr[i] == '_'
            ):
                i += 1
            var = expr[start:i]
            tokens.append(('VARIABLE', var))
            continue

        # Operators and parentheses
        if c == '+':
            tokens.append(('PLUS', '+'))
            i += 1
        elif c == '-':
            tokens.append(('MINUS', '-'))
            i += 1
        elif c == '*':
            tokens.append(('STAR', '*'))
            i += 1
        elif c == '/':
            tokens.append(('SLASH', '/'))
            i += 1
        elif c == '%':
            tokens.append(('PERCENT', '%'))
            i += 1
        elif c == '^':
            tokens.append(('CARET', '^'))
            i += 1
        elif c == '(':
            tokens.append(('LPAREN', '('))
            i += 1
        elif c == ')':
            tokens.append(('RPAREN', ')'))
            i += 1
        else:
            raise ValueError(f"Unexpected character: {c!r}")

    tokens.append(('EOF', None))

    # ---------- Recursive descent parser ----------
    class Parser:
        def __init__(self, tokens, variables):
            self.tokens = tokens
            self.pos = 0
            self.variables = variables if variables is not None else {}

        def peek(self):
            return self.tokens[self.pos]

        def advance(self):
            tok = self.tokens[self.pos]
            self.pos += 1
            return tok

        def expect(self, type_):
            tok = self.peek()
            if tok[0] != type_:
                raise ValueError(f"Expected {type_}, got {tok[0]}")
            return self.advance()

        def parse(self):
            val = self.parse_expr()
            if self.peek()[0] != 'EOF':
                raise ValueError("Unexpected token after expression")
            return val

        # expr := term (('+' | '-') term)*
        def parse_expr(self):
            left = self.parse_term()
            while self.peek()[0] in ('PLUS', 'MINUS'):
                op = self.advance()[0]
                right = self.parse_term()
                if op == 'PLUS':
                    left = left + right
                else:
                    left = left - right
            return left

        # term := unary (('*' | '/' | '%') unary)*
        def parse_term(self):
            left = self.parse_unary()
            while self.peek()[0] in ('STAR', 'SLASH', 'PERCENT'):
                op = self.advance()[0]
                right = self.parse_unary()
                if op == 'STAR':
                    left = left * right
                elif op == 'SLASH':
                    if right == 0:
                        raise ValueError("Division by zero")
                    left = left / right
                else:  # PERCENT
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    left = left % right
            return left

        # unary := '-' unary | factor
        def parse_unary(self):
            if self.peek()[0] == 'MINUS':
                self.advance()
                return -self.parse_unary()
            return self.parse_factor()

        # factor := primary ('^' factor)?   (right-associative)
        def parse_factor(self):
            left = self.parse_primary()
            if self.peek()[0] == 'CARET':
                self.advance()
                right = self.parse_factor()
                try:
                    result = left ** right
                except ZeroDivisionError:
                    raise ValueError("Division by zero")
                if isinstance(result, complex):
                    raise ValueError("Complex result")
                return result
            return left

        # primary := number | variable | '(' expr ')'
        def parse_primary(self):
            tok = self.peek()
            if tok[0] == 'NUMBER':
                self.advance()
                return tok[1]
            elif tok[0] == 'VARIABLE':
                self.advance()
                var = tok[1]
                if var not in self.variables:
                    raise ValueError(f"Unknown variable: {var}")
                return float(self.variables[var])
            elif tok[0] == 'LPAREN':
                self.advance()
                val = self.parse_expr()
                self.expect('RPAREN')
                return val
            else:
                raise ValueError(f"Unexpected token: {tok[0]}")

    parser = Parser(tokens, variables)
    return float(parser.parse())
