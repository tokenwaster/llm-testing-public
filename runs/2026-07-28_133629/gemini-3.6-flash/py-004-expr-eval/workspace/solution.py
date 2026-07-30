class Token:
    def __init__(self, type_: str, value: str | float):
        self.type = type_
        self.value = value


def tokenize(expr: str) -> list[Token]:
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in "()":
            tokens.append(Token("PAREN", c))
            i += 1
        elif c in "+-*/%^":
            tokens.append(Token("OP", c))
            i += 1
        elif c.isdigit() or (c == "." and i + 1 < n and expr[i + 1].isdigit()):
            start = i
            has_dot = False
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    if has_dot:
                        raise ValueError("Invalid number format in expression")
                    has_dot = True
                i += 1
            num_str = expr[start:i]
            try:
                val = float(num_str)
            except ValueError:
                raise ValueError(f"Invalid float: {num_str}")
            tokens.append(Token("NUMBER", val))
        elif c.isalpha() or c == "_":
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            var_str = expr[start:i]
            tokens.append(Token("VAR", var_str))
        else:
            raise ValueError(f"Unexpected character in expression: {c}")
    return tokens


class Parser:
    def __init__(self, tokens: list[Token], variables: dict[str, float] | None):
        self.tokens = tokens
        self.pos = 0
        self.variables = variables if variables is not None else {}

    def peek(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def get(self) -> Token | None:
        tok = self.peek()
        if tok is not None:
            self.pos += 1
        return tok

    def parse(self) -> float:
        if not self.tokens:
            raise ValueError("Empty expression")
        val = self.parse_expr()
        if self.pos < len(self.tokens):
            raise ValueError("Unexpected token in expression")
        return float(val)

    def parse_expr(self) -> float:
        val = self.parse_term()
        while True:
            tok = self.peek()
            if tok and tok.type == "OP" and tok.value in ("+", "-"):
                op = self.get().value
                right = self.parse_term()
                if op == "+":
                    val = val + right
                else:
                    val = val - right
            else:
                break
        return val

    def parse_term(self) -> float:
        val = self.parse_unary()
        while True:
            tok = self.peek()
            if tok and tok.type == "OP" and tok.value in ("*", "/", "%"):
                op = self.get().value
                right = self.parse_unary()
                if op == "*":
                    val = val * right
                elif op == "/":
                    if right == 0:
                        raise ValueError("Division by zero")
                    try:
                        val = val / right
                    except ZeroDivisionError:
                        raise ValueError("Division by zero")
                elif op == "%":
                    if right == 0:
                        raise ValueError("Modulo by zero")
                    try:
                        val = val % right
                    except ZeroDivisionError:
                        raise ValueError("Modulo by zero")
            else:
                break
        return val

    def parse_unary(self) -> float:
        tok = self.peek()
        if tok and tok.type == "OP" and tok.value in ("+", "-"):
            op = self.get().value
            right = self.parse_unary()
            if op == "-":
                return -right
            else:
                return right
        return self.parse_power()

    def parse_power(self) -> float:
        left = self.parse_primary()
        tok = self.peek()
        if tok and tok.type == "OP" and tok.value == "^":
            self.get()
            right = self.parse_unary()
            try:
                res = left**right
            except ZeroDivisionError:
                raise ValueError("Zero division in exponentiation")
            except OverflowError:
                raise ValueError("Overflow in exponentiation")
            if isinstance(res, complex):
                raise ValueError("Complex result not supported")
            return float(res)
        return left

    def parse_primary(self) -> float:
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of expression")

        if tok.type == "NUMBER":
            self.get()
            return tok.value
        elif tok.type == "VAR":
            self.get()
            var_name = tok.value
            if var_name not in self.variables:
                raise ValueError(f"Unknown variable: {var_name}")
            return float(self.variables[var_name])
        elif tok.type == "PAREN" and tok.value == "(":
            self.get()
            val = self.parse_expr()
            close_tok = self.get()
            if close_tok is None or close_tok.type != "PAREN" or close_tok.value != ")":
                raise ValueError("Unbalanced parentheses")
            return val
        else:
            raise ValueError(f"Unexpected token: {tok.value}")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    tokens = tokenize(expr)
    parser = Parser(tokens, variables)
    return parser.parse()
