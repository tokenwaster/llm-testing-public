"""Arithmetic expression evaluator with a hand-written recursive-descent parser.

Grammar (precedence low -> high):
    expr    := add
    add     := mul (('+' | '-') mul)*
    mul     := unary (('*' | '/' | '%') unary)*
    unary   := '-' unary | power
    power   := atom ('^' unary)?          # right-associative; RHS is unary so
                                          #   -2^2 == -4 and 2^-3 works
    atom    := number | name | '(' expr ')'
"""

from typing import Optional


# --- Token types ---------------------------------------------------------
_NUMBER = "NUMBER"
_NAME = "NAME"
_OP = "OP"
_LPAREN = "LPAREN"
_RPAREN = "RPAREN"
_EOF = "EOF"


class _Token:
    __slots__ = ("kind", "value", "pos")

    def __init__(self, kind: str, value, pos: int):
        self.kind = kind
        self.value = value
        self.pos = pos


def _tokenize(expr: str):
    tokens = []
    i = 0
    n = len(expr)
    while i < n:
        c = expr[i]

        # whitespace
        if c.isspace():
            i += 1
            continue

        # numbers: integers and decimals like 3, 4.5, 3.
        if c.isdigit() or c == ".":
            start = i
            seen_dot = False
            seen_digit = False
            while i < n and (expr[i].isdigit() or expr[i] == "."):
                if expr[i] == ".":
                    if seen_dot:
                        raise ValueError(f"Malformed number at position {start}")
                    seen_dot = True
                else:
                    seen_digit = True
                i += 1
            if not seen_digit:
                raise ValueError(f"Malformed number at position {start}")
            tokens.append(_Token(_NUMBER, float(expr[start:i]), start))
            continue

        # identifiers / variable names
        if c.isalpha() or c == "_":
            start = i
            while i < n and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(_Token(_NAME, expr[start:i], start))
            continue

        # operators and parens
        if c in "+-*/%^":
            tokens.append(_Token(_OP, c, i))
            i += 1
            continue
        if c == "(":
            tokens.append(_Token(_LPAREN, c, i))
            i += 1
            continue
        if c == ")":
            tokens.append(_Token(_RPAREN, c, i))
            i += 1
            continue

        raise ValueError(f"Unexpected character {c!r} at position {i}")

    tokens.append(_Token(_EOF, None, n))
    return tokens


class _Parser:
    def __init__(self, tokens, variables):
        self._tokens = tokens
        self._i = 0
        self._vars = variables

    # -- helpers ----------------------------------------------------------
    def _peek(self) -> _Token:
        return self._tokens[self._i]

    def _advance(self) -> _Token:
        tok = self._tokens[self._i]
        self._i += 1
        return tok

    def _expect(self, kind: str) -> _Token:
        tok = self._peek()
        if tok.kind != kind:
            raise ValueError(f"Expected {kind} at position {tok.pos}")
        return self._advance()

    # -- grammar rules ----------------------------------------------------
    def parse(self) -> float:
        value = self._add()
        if self._peek().kind != _EOF:
            raise ValueError(
                f"Unexpected token at position {self._peek().pos}"
            )
        return value

    def _add(self) -> float:
        value = self._mul()
        while self._peek().kind == _OP and self._peek().value in ("+", "-"):
            op = self._advance().value
            rhs = self._mul()
            value = value + rhs if op == "+" else value - rhs
        return value

    def _mul(self) -> float:
        value = self._unary()
        while self._peek().kind == _OP and self._peek().value in ("*", "/", "%"):
            op = self._advance().value
            rhs = self._unary()
            if op == "*":
                value = value * rhs
            elif op == "/":
                if rhs == 0:
                    raise ValueError("Division by zero")
                value = value / rhs
            else:  # %
                if rhs == 0:
                    raise ValueError("Modulo by zero")
                value = value % rhs
        return value

    def _unary(self) -> float:
        if self._peek().kind == _OP and self._peek().value == "-":
            self._advance()
            return -self._unary()
        # A stray unary plus is not part of the grammar; reject '+x'.
        if self._peek().kind == _OP and self._peek().value == "+":
            raise ValueError(f"Unexpected '+' at position {self._peek().pos}")
        return self._power()

    def _power(self) -> float:
        base = self._atom()
        if self._peek().kind == _OP and self._peek().value == "^":
            self._advance()
            # right operand is unary so ^ is right-associative and binds
            # tighter than unary minus: 2^3^2 == 512, 2^-1 works.
            exponent = self._unary()
            return float(base ** exponent)
        return base

    def _atom(self) -> float:
        tok = self._peek()
        if tok.kind == _NUMBER:
            self._advance()
            return float(tok.value)
        if tok.kind == _NAME:
            self._advance()
            if self._vars is None or tok.value not in self._vars:
                raise ValueError(f"Unknown variable {tok.value!r}")
            return float(self._vars[tok.value])
        if tok.kind == _LPAREN:
            self._advance()
            value = self._add()
            if self._peek().kind != _RPAREN:
                raise ValueError("Unbalanced parentheses")
            self._advance()
            return value
        raise ValueError(f"Unexpected token at position {tok.pos}")


def evaluate(expr: str, variables: Optional[dict] = None) -> float:
    if not isinstance(expr, str):
        raise ValueError("Expression must be a string")
    tokens = _tokenize(expr)
    parser = _Parser(tokens, variables)
    try:
        result = parser.parse()
    except ZeroDivisionError:
        raise ValueError("Division by zero")
    except OverflowError:
        raise ValueError("Numeric overflow")
    if isinstance(result, complex):
        # e.g. (-1) ** 0.5 produces a complex number
        raise ValueError("Result is not a real number")
    return float(result)
