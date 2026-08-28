def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # ---------- tokenizer ----------
    def tokenize(s: str):
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
                dot = False
                while i < n and (s[i].isdigit() or s[i] == '.'):
                    if s[i] == '.':
                        if dot:
                            break
                        dot = True
                    i += 1
                num_str = s[start:i]
                try:
                    val = float(num_str)
                except ValueError:
                    raise ValueError(f'Invalid number {num_str}')
                tokens.append(('NUM', val))
                continue
            if c.isalpha() or c == '_':
                start = i
                i += 1
                while i < n and (s[i].isalnum() or s[i] == '_'):
                    i += 1
                name = s[start:i]
                tokens.append(('VAR', name))
                continue
            if c in '+-*/%^()':
                if c == '(':
                    tokens.append(('LPAREN', c))
                elif c == ')':
                    tokens.append(('RPAREN', c))
                else:
                    tokens.append(('OP', c))
                i += 1
                continue
            raise ValueError(f'Invalid character {c!r}')
        return tokens

    tokens = tokenize(expr)

    # ---------- parser ----------
    class Parser:
        def __init__(self, tokens, vars_):
            self.tokens = tokens
            self.pos = 0
            self.vars = vars_ or {}

        def peek(self):
            return self.tokens[self.pos] if self.pos < len(self.tokens) else None

        def consume(self):
            t = self.tokens[self.pos]
            self.pos += 1
            return t

        def parse(self):
            if not self.tokens:
                raise ValueError('Empty expression')
            val = self.parse_expr()
            if self.pos != len(self.tokens):
                raise ValueError('Unexpected token')
            return float(val)

        def parse_expr(self):
            val = self.parse_term()
            while True:
                t = self.peek()
                if t and t[0] == 'OP' and t[1] in ('+', '-'):
                    op = self.consume()[1]
                    right = self.parse_term()
                    val = val + right if op == '+' else val - right
                else:
                    break
            return val

        def parse_term(self):
            val = self.parse_unary()
            while True:
                t = self.peek()
                if t and t[0] == 'OP' and t[1] in ('*', '/', '%'):
                    op = self.consume()[1]
                    right = self.parse_unary()
                    if op == '*':
                        val = val * right
                    elif op == '/':
                        if right == 0:
                            raise ValueError('Division by zero')
                        val = val / right
                    else:
                        if right == 0:
                            raise ValueError('Modulo by zero')
                        val = val % right
                else:
                    break
            return val

        def parse_unary(self):
            t = self.peek()
            if t and t[0] == 'OP' and t[1] in ('+', '-'):
                op = self.consume()[1]
                v = self.parse_unary()
                return v if op == '+' else -v
            return self.parse_power()

        def parse_power(self):
            left = self.parse_primary()
            t = self.peek()
            if t and t[0] == 'OP' and t[1] == '^':
                self.consume()
                right = self.parse_unary()   # right operand may start with unary
                try:
                    left = left ** right
                except ZeroDivisionError:
                    raise ValueError('Division by zero')
                except ValueError:
                    raise ValueError('Invalid exponentiation')
            return left

        def parse_primary(self):
            t = self.peek()
            if not t:
                raise ValueError('Unexpected end of expression')
            if t[0] == 'NUM':
                self.consume()
                return t[1]
            if t[0] == 'VAR':
                self.consume()
                name = t[1]
                if name not in self.vars:
                    raise ValueError(f'Unknown variable {name}')
                return float(self.vars[name])
            if t[0] == 'LPAREN':
                self.consume()
                val = self.parse_expr()
                t2 = self.peek()
                if not t2 or t2[0] != 'RPAREN':
                    raise ValueError('Unbalanced parentheses')
                self.consume()
                return val
            raise ValueError('Unexpected token')

    return Parser(tokens, variables).parse()
