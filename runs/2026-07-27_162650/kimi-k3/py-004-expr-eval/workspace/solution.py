"""A hand-written recursive-descent evaluator for arithmetic expressions.

Grammar (lowest to highest precedence):
    expression : term (('+' | '-') term)*
    term       : factor (('*' | '/' | '%') factor)*
    factor     : '-' factor | power
    power      : atom ('^' factor)?          # right-associative
    atom       : NUMBER | NAME | '(' expression ')'

Unary minus binds looser than '^', so -2^2 == -(2^2) == -4, while the
right operand of '^' is parsed as a factor, so 2^-3 == 0.125.
"""

from __future__ import annotations

_OPERATORS = "+-*/%^"


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate *expr* and return the result as a float."""
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables if variables is not None else {})
    try:
        result = parser.parse_expression()
    except ZeroDivisionError as exc:
        # e.g. 0.0 ** -1
        raise ValueError(str(exc)) from None
    if parser.peek() is not None:
        raise ValueError("Malformed expression: unexpected trailing input")
    return float(result)


def _tokenize(expr: str) -> list[tuple]:
    tokens: list[tuple] = []
    i, n = 0, len(expr)
    while i < n:
        c = expr[i]
        if c.isspace():
            i += 1
        elif c.isdigit() or (c == "." and i + 1 < n and expr[i + 1].isdigit()):
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            if j < n and expr[j] == ".":
                j += 1
                while j < n and expr[j].isdigit():
                    j += 1
            tokens.append(("num", float(expr[i:j])))
            i = j
        elif c.isalpha() or c == "_":
            j = i
            while j < n and (expr[j].isalnum() or expr[j] == "_"):
                j += 1
            tokens.append(("var", expr[i:j]))
            i = j
        elif c in _OPERATORS:
            tokens.append(("op", c))
            i += 1
        elif c == "(":
            tokens.append(("lparen", c))
            i += 1
        elif c == ")":
            tokens.append(("rparen", c))
            i += 1
        else:
            raise ValueError(f"Invalid character in expression: {c!r}")
    return tokens


class _Parser:
    def __init__(self, tokens: list[tuple], variables: dict[str, float]):
        self._tokens = tokens
        self._pos = 0
        self._variables = variables

    def peek(self) -> tuple | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _advance(self) -> tuple:
        token = self.peek()
        self._pos += 1
        return token

    # expression : term (('+' | '-') term)*
    def parse_expression(self) -> float:
        value = self._parse_term()
        while self.peek() in (("op", "+"), ("op", "-")):
            op = self._advance()[1]
            rhs = self._parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    # term : factor (('*' | '/' | '%') factor)*
    def _parse_term(self) -> float:
        value = self._parse_factor()
        while self.peek() in (("op", "*"), ("op", "/"), ("op", "%")):
            op = self._advance()[1]
            rhs = self._parse_factor()
            if op == "*":
                value = value * rhs
            elif op == "/":
                if rhs == 0:
                    raise ValueError("Division by zero")
                value = value / rhs
            else:
                if rhs == 0:
                    raise ValueError("Modulo by zero")
                value = value % rhs
        return value

    # factor : '-' factor | power
    def _parse_factor(self) -> float:
        if self.peek() == ("op", "-"):
            self._advance()
            return -self._parse_factor()
        return self._parse_power()

    # power : atom ('^' factor)?   (right-associative)
    def _parse_power(self) -> float:
        base = self._parse_atom()
        if self.peek() == ("op", "^"):
            self._advance()
            exponent = self._parse_factor()
            result = base ** exponent
            if isinstance(result, complex):
                raise ValueError("Exponentiation produced a non-real result")
            return result
        return base

    # atom : NUMBER | NAME | '(' expression ')'
    def _parse_atom(self) -> float:
        token = self.peek()
        if token is None:
            raise ValueError("Malformed expression: unexpected end of input")
        kind, value = token
        if kind == "num":
            self._advance()
            return value
        if kind == "var":
            self._advance()
            if value not in self._variables:
                raise ValueError(f"Unknown variable: {value!r}")
            return float(self._variables[value])
        if kind == "lparen":
            self._advance()
            result = self.parse_expression()
            if self.peek() != ("rparen", ")"):
                raise ValueError("Unbalanced parentheses: missing ')'")
            self._advance()
            return result
        raise ValueError(f"Malformed expression: unexpected token {value!r}")
