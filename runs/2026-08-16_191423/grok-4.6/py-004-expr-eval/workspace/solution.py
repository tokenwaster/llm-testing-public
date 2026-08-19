from __future__ import annotations


class _Tokenizer:
    def __init__(self, expr: str) -> None:
        self.s = expr
        self.n = len(expr)
        self.i = 0
        self.kind = ""
        self.value: float | str | None = None
        self.advance()

    def advance(self) -> None:
        s, n = self.s, self.n
        i = self.i
        while i < n and s[i].isspace():
            i += 1
        if i >= n:
            self.i = i
            self.kind = "EOF"
            self.value = None
            return
        c = s[i]
        if c in "+-*/%^()":
            self.i = i + 1
            self.kind = c
            self.value = c
            return
        if c.isdigit():
            start = i
            i += 1
            while i < n and s[i].isdigit():
                i += 1
            if i < n and s[i] == ".":
                i += 1
                while i < n and s[i].isdigit():
                    i += 1
            self.i = i
            self.kind = "NUM"
            self.value = float(s[start:i])
            return
        if c.isalpha() or c == "_":
            start = i
            i += 1
            while i < n and (s[i].isalnum() or s[i] == "_"):
                i += 1
            self.i = i
            self.kind = "VAR"
            self.value = s[start:i]
            return
        raise ValueError("malformed syntax")


class _Parser:
    def __init__(self, expr: str, variables: dict[str, float] | None) -> None:
        self.tok = _Tokenizer(expr)
        self.variables = variables if variables is not None else {}

    def parse(self) -> float:
        value = self._expr()
        if self.tok.kind != "EOF":
            raise ValueError("malformed syntax")
        return float(value)

    def _expr(self) -> float:
        left = self._term()
        while self.tok.kind in ("+", "-"):
            op = self.tok.kind
            self.tok.advance()
            right = self._term()
            left = left + right if op == "+" else left - right
        return left

    def _term(self) -> float:
        left = self._unary()
        while self.tok.kind in ("*", "/", "%"):
            op = self.tok.kind
            self.tok.advance()
            right = self._unary()
            if op == "*":
                left = left * right
            elif op == "/":
                if right == 0:
                    raise ValueError("division by zero")
                left = left / right
            else:
                if right == 0:
                    raise ValueError("modulo by zero")
                left = left % right
        return left

    def _unary(self) -> float:
        if self.tok.kind == "-":
            self.tok.advance()
            return -self._unary()
        return self._power()

    def _power(self) -> float:
        left = self._primary()
        if self.tok.kind == "^":
            self.tok.advance()
            right = self._unary()
            try:
                result = left ** right
            except ZeroDivisionError:
                raise ValueError("division by zero") from None
            if isinstance(result, complex):
                raise ValueError("invalid exponentiation")
            return float(result)
        return left

    def _primary(self) -> float:
        kind = self.tok.kind
        if kind == "NUM":
            value = float(self.tok.value)  # type: ignore[arg-type]
            self.tok.advance()
            return value
        if kind == "VAR":
            name = str(self.tok.value)
            self.tok.advance()
            if name not in self.variables:
                raise ValueError("unknown variable")
            return float(self.variables[name])
        if kind == "(":
            self.tok.advance()
            value = self._expr()
            if self.tok.kind != ")":
                raise ValueError("unbalanced parentheses")
            self.tok.advance()
            return value
        raise ValueError("malformed syntax")


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    return _Parser(expr, variables).parse()
