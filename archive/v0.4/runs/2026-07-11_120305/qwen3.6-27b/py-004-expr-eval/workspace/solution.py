def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    def tokenize(s: str) -> list[str]:
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            if s[i].isspace():
                i += 1
                continue
            if s[i] in '+-*/%^()':
                tokens.append(s[i])
                i += 1
            elif s[i].isdigit() or s[i] == '.':
                j = i
                has_dot = False
                while j < n and (s[j].isdigit() or s[j] == '.'):
                    if s[j] == '.':
                        if has_dot:
                            raise ValueError("malformed syntax")
                        has_dot = True
                    j += 1
                tokens.append(s[i:j])
                i = j
            elif s[i].isalpha() or s[i] == '_':
                j = i
                while j < n and (s[j].isalnum() or s[j] == '_'):
                    j += 1
                tokens.append(s[i:j])
                i = j
            else:
                raise ValueError("malformed syntax")
        return tokens

    class Parser:
        def __init__(self, tokens: list[str], variables: dict[str, float] | None):
            self.tokens = tokens
            self.pos = 0
            self.variables = variables or {}

        def peek(self) -> str | None:
            if self.pos < len(self.tokens):
                return self.tokens[self.pos]
            return None

        def consume(self) -> str:
            token = self.tokens[self.pos]
            self.pos += 1
            return token

        def parse(self) -> float:
            if not self.tokens:
                raise ValueError("malformed syntax")
            result = self.parse_expr()
            if self.pos < len(self.tokens):
                raise ValueError("malformed syntax")
            return result

        def parse_expr(self) -> float:
            left = self.parse_term()
            while self.peek() in ('+', '-'):
                op = self.consume()
                right = self.parse_term()
                if op == '+':
                    left = left + right
                else:
                    left = left - right
            return left

        def parse_term(self) -> float:
            left = self.parse_unary()
            while self.peek() in ('*', '/', '%'):
                op = self.consume()
                right = self.parse_unary()
                if op == '*':
                    left = left * right
                elif op == '/':
                    if right == 0:
                        raise ValueError("division by zero")
                    left = left / right
                else:
                    if right == 0:
                        raise ValueError("division by zero")
                    left = left % right
            return left

        def parse_unary(self) -> float:
            count = 0
            while self.peek() == '-':
                self.consume()
                count += 1
            val = self.parse_power()
            if count % 2 == 1:
                val = -val
            return val

        def parse_power(self) -> float:
            left = self.parse_primary()
            if self.peek() == '^':
                self.consume()
                right = self.parse_power()
                left = left ** right
            return left

        def parse_primary(self) -> float:
            token = self.peek()
            if token is None:
                raise ValueError("malformed syntax")
            
            if token == '(':
                self.consume()
                val = self.parse_expr()
                if self.peek() != ')':
                    raise ValueError("unbalanced parentheses")
                self.consume()
                return val
            elif token == ')':
                raise ValueError("unbalanced parentheses")
            elif token[0].isdigit() or token[0] == '.':
                self.consume()
                return float(token)
            elif token[0].isalpha() or token[0] == '_':
                self.consume()
                if token not in self.variables:
                    raise ValueError("unknown variable")
                return float(self.variables[token])
            else:
                raise ValueError("malformed syntax")

    return Parser(tokenize(expr), variables).parse()
