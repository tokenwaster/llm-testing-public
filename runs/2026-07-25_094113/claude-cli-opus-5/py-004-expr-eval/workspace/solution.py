"""Arithmetic expression evaluator with a hand-written recursive-descent parser.

No use of eval/exec/ast or any parsing library.

Grammar (lowest to highest precedence):

    expr    := term (('+' | '-') term)*
    term    := unary (('*' | '/' | '%') unary)*
    unary   := '-' unary | power
    power   := atom ('^' unary)?          # right-associative, and '-' binds looser
    atom    := NUMBER | NAME | '(' expr ')'
"""

from __future__ import annotations

_DIGITS = "0123456789"
_NAME_START = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_NAME_CHARS = _NAME_START | set(_DIGITS)
_OPERATORS = set("+-*/%^()")


class _Token:
    __slots__ = ("kind", "value", "pos")

    def __init__(self, kind: str, value, pos: int) -> None:
        self.kind = kind      # 'num' | 'name' | 'op' | 'end'
        self.value = value
        self.pos = pos

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"_Token({self.kind!r}, {self.value!r}, {self.pos})"


def _tokenize(expr: str) -> list[_Token]:
    if not isinstance(expr, str):
        raise ValueError("expression must be a string")

    tokens: list[_Token] = []
    i = 0
    n = len(expr)

    while i < n:
        ch = expr[i]

        if ch.isspace():
            i += 1
            continue

        if ch in _DIGITS or ch == ".":
            start = i
            seen_digit = False
            seen_dot = False
            while i < n and (expr[i] in _DIGITS or expr[i] == "."):
                if expr[i] == ".":
                    if seen_dot:
                        raise ValueError(
                            f"malformed number at position {start}: {expr[start:i + 1]!r}"
                        )
                    seen_dot = True
                else:
                    seen_digit = True
                i += 1
            text = expr[start:i]
            if not seen_digit:
                raise ValueError(f"malformed number at position {start}: {text!r}")
            try:
                value = float(text)
            except (ValueError, OverflowError):
                raise ValueError(f"malformed number at position {start}: {text!r}") from None
            tokens.append(_Token("num", value, start))
            continue

        if ch in _NAME_START:
            start = i
            while i < n and expr[i] in _NAME_CHARS:
                i += 1
            tokens.append(_Token("name", expr[start:i], start))
            continue

        if ch in _OPERATORS:
            tokens.append(_Token("op", ch, i))
            i += 1
            continue

        raise ValueError(f"unexpected character {ch!r} at position {i}")

    tokens.append(_Token("end", None, n))
    return tokens


class _Parser:
    def __init__(self, tokens: list[_Token], variables: dict) -> None:
        self.tokens = tokens
        self.pos = 0
        self.variables = variables

    # -- token helpers -----------------------------------------------------
    @property
    def current(self) -> _Token:
        return self.tokens[self.pos]

    def advance(self) -> _Token:
        tok = self.tokens[self.pos]
        if tok.kind != "end":
            self.pos += 1
        return tok

    def match_op(self, *ops: str) -> bool:
        tok = self.current
        return tok.kind == "op" and tok.value in ops

    # -- grammar rules -----------------------------------------------------
    def parse(self) -> float:
        value = self.parse_expr()
        tok = self.current
        if tok.kind != "end":
            if tok.kind == "op" and tok.value == ")":
                raise ValueError(f"unbalanced parenthesis at position {tok.pos}")
            raise ValueError(f"unexpected token {tok.value!r} at position {tok.pos}")
        return value

    def parse_expr(self) -> float:
        value = self.parse_term()
        while self.match_op("+", "-"):
            op = self.advance().value
            rhs = self.parse_term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def parse_term(self) -> float:
        value = self.parse_unary()
        while self.match_op("*", "/", "%"):
            tok = self.advance()
            rhs = self.parse_unary()
            if tok.value == "*":
                value = value * rhs
            elif tok.value == "/":
                if rhs == 0:
                    raise ValueError("division by zero")
                value = value / rhs
            else:
                if rhs == 0:
                    raise ValueError("modulo by zero")
                value = value % rhs
        return self._check(value)

    def parse_unary(self) -> float:
        if self.match_op("-"):
            self.advance()
            return -self.parse_unary()
        if self.match_op("+"):
            self.advance()
            return self.parse_unary()
        return self.parse_power()

    def parse_power(self) -> float:
        base = self.parse_atom()
        if self.match_op("^"):
            self.advance()
            # right-associative, and the exponent may carry unary minus
            exponent = self.parse_unary()
            try:
                result = base ** exponent
            except ZeroDivisionError:
                raise ValueError("division by zero") from None
            except OverflowError:
                raise ValueError("numeric overflow in exponentiation") from None
            if isinstance(result, complex):
                raise ValueError("complex result from exponentiation")
            return self._check(result)
        return base

    def parse_atom(self) -> float:
        tok = self.current

        if tok.kind == "num":
            self.advance()
            return float(tok.value)

        if tok.kind == "name":
            self.advance()
            name = tok.value
            if name not in self.variables:
                raise ValueError(f"unknown variable {name!r}")
            try:
                return float(self.variables[name])
            except (TypeError, ValueError):
                raise ValueError(f"variable {name!r} is not a number") from None

        if tok.kind == "op" and tok.value == "(":
            self.advance()
            value = self.parse_expr()
            if not self.match_op(")"):
                raise ValueError("unbalanced parenthesis: expected ')'")
            self.advance()
            return value

        if tok.kind == "end":
            raise ValueError("unexpected end of expression")

        raise ValueError(f"unexpected token {tok.value!r} at position {tok.pos}")

    @staticmethod
    def _check(value: float) -> float:
        result = float(value)
        return result


def evaluate(expr: str, variables: dict[str, float] | None = None) -> float:
    """Evaluate an arithmetic expression and return the result as a float.

    Raises ValueError on malformed syntax, unbalanced parentheses, unknown
    variables, or division/modulo by zero.
    """
    if variables is None:
        variables = {}
    elif not isinstance(variables, dict):
        raise ValueError("variables must be a dict or None")

    tokens = _tokenize(expr)
    if tokens[0].kind == "end":
        raise ValueError("empty expression")

    parser = _Parser(tokens, variables)
    try:
        result = parser.parse()
    except ZeroDivisionError:
        raise ValueError("division by zero") from None
    except OverflowError:
        raise ValueError("numeric overflow") from None
    except RecursionError:
        raise ValueError("expression nested too deeply") from None

    return float(result)
