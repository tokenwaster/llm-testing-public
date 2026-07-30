from __future__ import annotations

def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    digits = set('0123456789')
    alpha = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
    alnum = digits | alpha

    def tokenize(s: str):
        tokens = []
        i = 0
        n = len(s)
        while i < n:
            c = s[i]
            if c.isspace():
                i += 1
                continue
            if c in digits:
                j = i
                while j < n and s[j] in digits:
                    j += 1
                if j < n and s[j] == '.':
                    j += 1
                    while j < n and s[j] in digits:
                        j += 1
                num_str = s[i:j]
                try:
                    val = float(num_str)
                except ValueError:
                    raise ValueError("malformed syntax")
                tokens.append(('NUM', val))
                i = j
                continue
            if c in alpha:
                j = i
                while j < n and s[j] in alnum:
                    j += 1
                tokens.append(('ID', s[i:j]))
                i = j
                continue
            if c in '+-*/%^':
                tokens.append(('OP', c))
                i += 1
                continue
            if c == '(':
                tokens.append(('LPAREN', '('))
                i += 1
                continue
            if c == ')':
                tokens.append(('RPAREN', ')'))
                i += 1
                continue
            raise ValueError("malformed syntax")
        return tokens

    class Parser:
        def __init__(self, tokens, vars):
            self.tokens = tokens
            self.pos = 0
            self.variables = vars if vars is not None else {}

        def peek(self):
            if self.pos < len(self.tokens):
                return self.tokens[self.pos]
            return None

        def consume(self):
            tok = self.peek()
            if tok is None:
                raise ValueError("malformed syntax")
            self.pos += 1
            return tok

        def parse_expression(self):
            return self.parse_additive()

        def parse_additive(self):
            left = self.parse_multiplicative()
            while True:
                tok = self.peek()
                if tok is not None and tok[0] == 'OP' and tok[1] in ('+', '-'):
                    op = tok[1]
                    self.consume()
                    right = self.parse_multiplicative()
                    if op == '+':
                        left += right
                    else:
                        left -= right
                else:
                    break
            return left

        def parse_multiplicative(self):
            left = self.parse_factor()
            while True:
                tok = self.peek()
                if tok is not None and tok[0] == 'OP' and tok[1] in ('*', '/', '%'):
                    op = tok[1]
                    self.consume()
                    right = self.parse_factor()
                    if op == '*':
                        left *= right
                    elif op == '/':
                        if right == 0:
                            raise ValueError("division by zero")
                        left /= right
                    elif op == '%':
                        if right == 0:
                            raise ValueError("modulo by zero")
                        left %= right
                else:
                    break
            return left

        def parse_factor(self):
            tok = self.peek()
            if tok is not None and tok[0] == 'OP' and tok[1] in ('-', '+'):
                op = tok[1]
                self.consume()
                val = self.parse_factor()
                return -val if op == '-' else val
            return self.parse_power()

        def parse_power(self):
            left = self.parse_primary()
            tok = self.peek()
            if tok is not None and tok[0] == 'OP' and tok[1] == '^':
                self.consume()
                right = self.parse_factor()
                if left == 0 and right < 0:
                    raise ValueError("division by zero")
                result = left ** right
                if isinstance(result, complex):
                    raise ValueError("malformed syntax")
                return result
            return left

        def parse_primary(self):
            tok = self.peek()
            if tok is None:
                raise ValueError("malformed syntax")
            if tok[0] == 'NUM':
                self.consume()
                return tok[1]
            if tok[0] == 'ID':
                self.consume()
                name = tok[1]
                if name not in self.variables:
                    raise ValueError("unknown variable")
                return float(self.variables[name])
            if tok[0] == 'LPAREN':
                self.consume()
                val = self.parse_additive()
                if self.peek() is None or self.peek()[0] != 'RPAREN':
                    raise ValueError("unbalanced parentheses")
                self.consume()
                return val
            raise ValueError("malformed syntax")

    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    result = parser.parse_expression()
    if parser.pos != len(tokens):
        raise ValueError("malformed syntax")
    return float(result)
