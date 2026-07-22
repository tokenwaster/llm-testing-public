class _Parser:
    def __init__(self, s: str):
        self.s = s
        self.i = 0
        self.n = len(s)

    def _skip_ws(self):
        while self.i < self.n and self.s[self.i].isspace():
            self.i += 1

    def _peek(self):
        self._skip_ws()
        if self.i >= self.n:
            return None
        return self.s[self.i]

    def _advance(self):
        self._skip_ws()
        ch = self.s[self.i]
        self.i += 1
        return ch

    def _expect(self, ch):
        self._skip_ws()
        if self.i >= self.n or self.s[self.i] != ch:
            raise ValueError(f"Expected '{ch}' at position {self.i}")
        self.i += 1

    def parse(self, variables):
        result = self._expr(variables)
        self._skip_ws()
        if self.i != self.n:
            raise ValueError(
                f"Unexpected trailing input at position {self.i}: '{self.s[self.i]}'"
            )
        return float(result)

    def _expr(self, variables):
        left = self._term(variables)
        while True:
            ch = self._peek()
            if ch == "+":
                self._advance()
                right = self._term(variables)
                left = left + right
            elif ch == "-":
                self._advance()
                right = self._term(variables)
                left = left - right
            else:
                break
        return left

    def _term(self, variables):
        left = self._unary(variables)
        while True:
            ch = self._peek()
            if ch == "*":
                self._advance()
                right = self._unary(variables)
                left = left * right
            elif ch == "/":
                self._advance()
                right = self._unary(variables)
                if right == 0:
                    raise ValueError("Division by zero")
                left = left / right
            elif ch == "%":
                self._advance()
                right = self._unary(variables)
                if right == 0:
                    raise ValueError("Modulo by zero")
                left = left % right
            else:
                break
        return left

    def _unary(self, variables):
        ch = self._peek()
        if ch == "-":
            self._advance()
            return -self._unary(variables)
        if ch == "+":
            self._advance()
            return self._unary(variables)
        return self._power(variables)

    def _power(self, variables):
        left = self._atom(variables)
        if self._peek() == "^":
            self._advance()
            right = self._unary(variables)
            if left == 0 and right < 0:
                raise ValueError("Division by zero")
            return left ** right
        return left

    def _atom(self, variables):
        ch = self._peek()
        if ch is None:
            raise ValueError("Unexpected end of expression")
        if ch == "(":
            self._advance()
            result = self._expr(variables)
            self._expect(")")
            return result
        if ch.isdigit():
            return self._number()
        if ch.isalpha() or ch == "_":
            return self._ident(variables)
        raise ValueError(f"Unexpected character: '{ch}'")

    def _number(self):
        start = self.i
        while self.i < self.n and self.s[self.i].isdigit():
            self.i += 1
        if (
            self.i < self.n
            and self.s[self.i] == "."
            and self.i + 1 < self.n
            and self.s[self.i + 1].isdigit()
        ):
            self.i += 1
            while self.i < self.n and self.s[self.i].isdigit():
                self.i += 1
        if self.i == start:
            raise ValueError("Expected number")
        return float(self.s[start : self.i])

    def _ident(self, variables):
        start = self.i
        while self.i < self.n and (self.s[self.i].isalnum() or self.s[self.i] == "_"):
            self.i += 1
        name = self.s[start : self.i]
        if not variables or name not in variables:
            raise ValueError(f"Unknown variable: '{name}'")
        return float(variables[name])


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    parser = _Parser(expr)
    return parser.parse(variables if variables is not None else {})
