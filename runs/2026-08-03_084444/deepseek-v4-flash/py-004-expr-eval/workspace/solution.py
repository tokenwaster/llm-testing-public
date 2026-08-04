def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    # ---------- tokenizer ----------
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit():
            start = i
            while i < n and (expr[i].isdigit() or expr[i] == '.'):
                i += 1
            try:
                val = float(expr[start:i])
            except ValueError:
                raise ValueError("Invalid number literal")
            tokens.append(('NUMBER', val))
        elif ch.isalpha() or ch == '_':
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == '_'):
                i += 1
            tokens.append(('VARIABLE', expr[start:i]))
        elif ch in '+-*/%^()':
            tokens.append(('OP', ch))
            i += 1
        else:
            raise ValueError(f"Invalid character: {ch}")
    tokens.append(('END', None))

    # ---------- parser ----------
    PREC = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 4}
    UNARY_PREC = 3

    class Parser:
        def __init__(self, tokens, variables):
            self.tokens = tokens
            self.pos = 0
            self.variables = variables if variables is not None else {}

        def current(self):
            return self.tokens[self.pos]

        def consume(self):
            tok = self.current()
            self.pos += 1
            return tok

        def parse_expression(self, min_prec):
            left = self.parse_primary()
            while True:
                tok = self.current()
                if tok[0] == 'OP' and tok[1] in PREC:
                    op = tok[1]
                    prec = PREC[op]
                    if prec < min_prec:
                        break
                    self.consume()
                    next_prec = prec if op == '^' else prec + 1
                    right = self.parse_expression(next_prec)
                    left = self.apply_op(left, op, right)
                else:
                    break
            return left

        def parse_primary(self):
            tok = self.current()
            if tok[0] == 'NUMBER':
                self.consume()
                return tok[1]
            elif tok[0] == 'VARIABLE':
                self.consume()
                name = tok[1]
                if name not in self.variables:
                    raise ValueError(f"Unknown variable: {name}")
                return self.variables[name]
            elif tok[0] == 'LPAREN':
                self.consume()
                expr = self.parse_expression(0)
                if self.current()[0] != 'RPAREN':
                    raise ValueError("Missing closing parenthesis")
                self.consume()
                return expr
            elif tok[0] == 'OP' and tok[1] == '-':
                self.consume()
                operand = self.parse_expression(UNARY_PREC)
                return -operand
            else:
                raise ValueError("Unexpected token")

        def apply_op(self, left, op, right):
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right
            elif op == '%':
                if right == 0:
                    raise ValueError("Modulo by zero")
                return left % right
            elif op == '^':
                return left ** right
            else:
                raise ValueError("Unknown operator")

    parser = Parser(tokens, variables)
    result = parser.parse_expression(0)
    if parser.current()[0] != 'END':
        raise ValueError("Unexpected token after expression")
    return float(result)
