"""Recursive-descent evaluator for arithmetic expressions (no eval/exec/ast)."""


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float.

    Supported: numbers, + - * / % ^ (right-associative), unary minus,
    parentheses, variables, and whitespace. Raises ValueError on malformed
    syntax, unbalanced parentheses, unknown variables, and division or
    modulo by zero.
    """
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables if variables is not None else {})
    result = parser.parse_expression()
    if parser.peek()[0] != "end":
        raise ValueError("malformed expression: unexpected trailing input")
    return float(result)


def _is_digit(ch: str) -> bool:
    return "0" <= ch <= "9"


def _is_alpha(ch: str) -> bool:
    return ("a" <= ch <= "z") or ("A" <= ch <= "Z") or ch == "_"


def _is_alnum(ch: str) -> bool:
    return _is_digit(ch) or _is_alpha(ch)


def _tokenize(expr: str) -> list[tuple[str, object]]:
    tokens: list[tuple[str, object]] = []
    i, n = 0, len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif _is_digit(ch):
            j = i
            while j < n and _is_digit(expr[j]):
                j += 1
            if j < n and expr[j] == ".":
                j += 1
                if j >= n or not _is_digit(expr[j]):
                    raise ValueError("malformed number")
                while j < n and _is_digit(expr[j]):
                    j += 1
            tokens.append(("num", float(expr[i:j])))
            i = j
        elif _is_alpha(ch):
            j = i + 1
            while j < n and _is_alnum(expr[j]):
                j += 1
            tokens.append(("id", expr[i:j]))
            i = j
        elif ch in "+-*/%^":
            tokens.append((ch, ch))
            i += 1
        elif ch == "(":
            tokens.append(("(", ch))
            i += 1
        elif ch == ")":
            tokens.append((")", ch))
            i += 1
        else:
            raise ValueError(f"unexpected character: {ch!r}")
    tokens.append(("end", None))
    return tokens


class _Parser:
    """Grammar (lowest to highest precedence):
        expression := term (('+' | '-') term)*
        term       := unary (('*' | '/' | '%') unary)*
        unary      := '-' unary | power
        power      := primary ('^' unary)?        # right-associative
        primary    := NUMBER | NAME | '(' expression ')'
    Making the operand of unary '-' another `unary` (hence a `power`)
    gives `-2^2 == -(2^2) == -4` while still allowing `--3` and `2^-3`.
    """

    def __init__(self, tokens: list[tuple[str, object]], variables: dict[str, float]):
        self._tokens = tokens
        self._pos = 0
        self._variables = variables

    def peek(self) -> tuple[str, object]:
        return self._tokens[self._pos]

    def advance(self) -> tuple[str, object]:
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def parse_expression(self) -> float:
        value = self.parse_term()
        while self.peek()[0] in ("+", "-"):
            op = self.advance()[0]
            rhs = self.parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_term(self) -> float:
        value = self.parse_unary()
        while self.peek()[0] in ("*", "/", "%"):
            op = self.advance()[0]
            rhs = self.parse_unary()
            if op == "*":
                value *= rhs
            elif op == "/":
                if rhs == 0:
                    raise ValueError("division by zero")
                value /= rhs
            else:
                if rhs == 0:
                    raise ValueError("modulo by zero")
                value %= rhs
        return value

    def parse_unary(self) -> float:
        if self.peek()[0] == "-":
            self.advance()
            return -self.parse_unary()
        return self.parse_power()

    def parse_power(self) -> float:
        base = self.parse_primary()
        if self.peek()[0] == "^":
            self.advance()
            exponent = self.parse_unary()
            try:
                return base ** exponent
            except ZeroDivisionError:  # e.g. 0 ^ -1
                raise ValueError("division by zero") from None
        return base

    def parse_primary(self) -> float:
        kind, value = self.peek()
        if kind == "num":
            self.advance()
            return value  # type: ignore[return-value]
        if kind == "id":
            self.advance()
            if value not in self._variables:
                raise ValueError(f"unknown variable: {value}")
            return float(self._variables[value])  # type: ignore[index]
        if kind == "(":
            self.advance()
            result = self.parse_expression()
            if self.peek()[0] != ")":
                raise ValueError("unbalanced parentheses")
            self.advance()
            return result
        raise ValueError("malformed expression")
