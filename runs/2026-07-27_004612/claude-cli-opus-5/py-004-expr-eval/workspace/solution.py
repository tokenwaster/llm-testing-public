"""A small self-contained arithmetic expression evaluator.

No `eval`, `exec`, `ast`, or third-party parsing library is used: the tokenizer
and recursive-descent parser below are hand-written.

Grammar (lowest to highest precedence):

    expression := term      (('+' | '-') term)*
    term       := unary     (('*' | '/' | '%') unary)*
    unary      := '-' unary | power
    power      := atom ('^' unary)?          # right-associative
    atom       := NUMBER | NAME | '(' expression ')'
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# Tokenizer
# --------------------------------------------------------------------------- #

_OPERATORS = frozenset("+-*/%^")
_DIGITS = frozenset("0123456789")


def _is_name_start(ch: str) -> bool:
    return ch == "_" or ch.isascii() and ch.isalpha()


def _is_name_part(ch: str) -> bool:
    return ch == "_" or ch.isascii() and ch.isalnum()


def _tokenize(expr: str) -> list[tuple[str, str]]:
    """Turn `expr` into a list of (kind, text) tokens.

    Kinds are: 'num', 'name', 'op', 'lparen', 'rparen'.
    """
    if not isinstance(expr, str):
        raise ValueError("expression must be a string")

    tokens: list[tuple[str, str]] = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch in _DIGITS:
            start = i
            while i < n and expr[i] in _DIGITS:
                i += 1
            if i < n and expr[i] == ".":
                i += 1
                if i >= n or expr[i] not in _DIGITS:
                    raise ValueError(f"malformed number at position {start}")
                while i < n and expr[i] in _DIGITS:
                    i += 1
            tokens.append(("num", expr[start:i]))
            continue

        if _is_name_start(ch):
            start = i
            while i < n and _is_name_part(expr[i]):
                i += 1
            tokens.append(("name", expr[start:i]))
            continue

        if ch in _OPERATORS:
            tokens.append(("op", ch))
            i += 1
            continue

        if ch == "(":
            tokens.append(("lparen", ch))
            i += 1
            continue

        if ch == ")":
            tokens.append(("rparen", ch))
            i += 1
            continue

        raise ValueError(f"unexpected character {ch!r} at position {i}")

    return tokens


# --------------------------------------------------------------------------- #
# Parser / evaluator
# --------------------------------------------------------------------------- #


class _Parser:
    def __init__(self, tokens: list[tuple[str, str]], variables: dict[str, float]):
        self._tokens = tokens
        self._pos = 0
        self._variables = variables

    # -- token helpers ----------------------------------------------------- #

    def _peek(self) -> tuple[str, str] | None:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _advance(self) -> tuple[str, str]:
        token = self._peek()
        if token is None:
            raise ValueError("unexpected end of expression")
        self._pos += 1
        return token

    def _match_op(self, *ops: str) -> str | None:
        token = self._peek()
        if token is not None and token[0] == "op" and token[1] in ops:
            self._pos += 1
            return token[1]
        return None

    # -- grammar rules ----------------------------------------------------- #

    def parse(self) -> float:
        value = self.expression()
        leftover = self._peek()
        if leftover is not None:
            if leftover[0] == "rparen":
                raise ValueError("unbalanced parentheses")
            raise ValueError(f"unexpected token {leftover[1]!r}")
        return value

    def expression(self) -> float:
        value = self.term()
        while True:
            op = self._match_op("+", "-")
            if op is None:
                return value
            right = self.term()
            value = value + right if op == "+" else value - right

    def term(self) -> float:
        value = self.unary()
        while True:
            op = self._match_op("*", "/", "%")
            if op is None:
                return value
            right = self.unary()
            if op == "*":
                value = value * right
            elif op == "/":
                if right == 0.0:
                    raise ValueError("division by zero")
                value = value / right
            else:
                if right == 0.0:
                    raise ValueError("modulo by zero")
                value = value % right

    def unary(self) -> float:
        if self._match_op("-") is not None:
            return -self.unary()
        return self.power()

    def power(self) -> float:
        base = self.atom()
        if self._match_op("^") is not None:
            # Right-associative, and the exponent may itself be negated.
            exponent = self.unary()
            return self._pow(base, exponent)
        return base

    @staticmethod
    def _pow(base: float, exponent: float) -> float:
        try:
            result = base**exponent
        except (OverflowError, ZeroDivisionError) as exc:
            raise ValueError(f"invalid exponentiation: {exc}") from exc
        if isinstance(result, complex):
            raise ValueError("exponentiation produced a complex result")
        return float(result)

    def atom(self) -> float:
        token = self._peek()
        if token is None:
            raise ValueError("unexpected end of expression")

        kind, text = token

        if kind == "num":
            self._advance()
            return float(text)

        if kind == "name":
            self._advance()
            if text not in self._variables:
                raise ValueError(f"unknown variable {text!r}")
            try:
                return float(self._variables[text])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"variable {text!r} is not a number") from exc

        if kind == "lparen":
            self._advance()
            value = self.expression()
            closing = self._peek()
            if closing is None or closing[0] != "rparen":
                raise ValueError("unbalanced parentheses")
            self._advance()
            return value

        if kind == "rparen":
            raise ValueError("unbalanced parentheses")

        raise ValueError(f"unexpected token {text!r}")


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float.

    Raises ValueError on malformed syntax, unbalanced parentheses, unknown
    variables, and division or modulo by zero.
    """
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("empty expression")
    return float(_Parser(tokens, variables or {}).parse())
